#!/usr/bin/env python3
"""lab.py - the mechanical steps of a research lab, standard library only.

It clones target repos, opens an experiment (branch, worktree, notes, lab folder), runs commands
in a worktree, runs the final evaluation and records a verdict. It makes no judgment: the plan,
the log, the wiki and the journal's Frontier, Sparks and Banlist are written by the agent.
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = LAB_ROOT / ".targets"
REPOS_DIR = TARGETS_DIR / "repos"
WORKTREES_DIR = TARGETS_DIR / "worktrees"
# Files the lab itself provisions into every worktree. They are not part of an experiment's change,
# even when the target repo tracks its own copies (then provisioning overwrites them).
LAB_PROVISIONED = (".agents", ".claude", "skills-lock.json", "CODE-STANDARDS.md")
WIKI_DIR = LAB_ROOT / "wiki-llm"
EXPS_DIR = LAB_ROOT / "experiments"
JOURNAL_PATH = LAB_ROOT / "JOURNAL.md"
REPOS_YAML_PATH = LAB_ROOT / "repos.yaml"
# An experiment has two homes. Next to the code, on its branch in the target repo:
#   notes/<exp-name>/{plan.md, log.md, runs/}   (the experiment's own working memory)
# In the lab: experiments/<exp-name>/{results.json, postmortem.md, patch.diff, evaluate.log}  (what is told to everyone)
# The two homes have different names on purpose: `experiments/` exists only in the lab.
NOTES_TEMPLATE_DIR = "notes"  # subfolder of experiments/_TEMPLATE copied into the worktree
NOTES_DIR = "notes"           # folder inside the target repo that holds plan.md and log.md
# The one evaluation API: every target repo's final evaluation is this script at its root.
# Contract: `uv run evaluate.py` in the worktree, last stdout line = one JSON object of metrics.
EVAL_SCRIPT = "evaluate.py"

# Experiment names: <id>-<repo short name>-<worktree name>, e.g. "0a-model-rl/grpo".
#   id        two lowercase hex digits, unique across the lab
#   short     repos.yaml `short_name`: lowercase letters/digits, no hyphen
#   worktree  1-3 segments joined by "/", each lowercase words joined by "-"
# The "/" levels become nested folders (experiments/, .targets/worktrees/) and the branch exp/<name>.
EXP_SEGMENT = r"[a-z0-9]+(?:-[a-z0-9]+)*"
EXP_NAME_RE = re.compile(rf"^([0-9a-f]{{2}})-([a-z0-9]+)-({EXP_SEGMENT}(?:/{EXP_SEGMENT})*)$")
SHORT_NAME_RE = re.compile(r"^[a-z0-9]{1,12}$")
WORKTREE_NAME_RE = re.compile(rf"^{EXP_SEGMENT}(?:/{EXP_SEGMENT}){{0,2}}$")
MAX_SEGMENT_LEN = 16
MAX_WORKTREE_NAME_LEN = 32


def load_env_file(path: Path = LAB_ROOT / ".env") -> dict:
    """Return os.environ plus KEY=VALUE pairs from the lab's .env (if present), for the evaluation script.

    Values already set in the environment win, so cloud-injected secrets are never overridden.
    Only names are ever printed, never values.
    """
    env = dict(os.environ)
    if not path.exists():
        return env
    loaded = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if value and key not in env:
            env[key] = value
            loaded.append(key)
    if loaded:
        print(f"[ENV] Loaded from .env: {', '.join(sorted(loaded))}")
    return env


def now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def append_wiki_log(operation: str, target: str, summary: str) -> None:
    log_path = WIKI_DIR / "log.md"
    if not log_path.exists():
        return
    entry = f"## [{now_iso()}] {operation} | {target} — {summary}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def parse_simple_repos_yaml(path: Path) -> dict:
    """Lightweight parser for repos.yaml using Python stdlib only."""
    if not path.exists():
        return {}
    repos = {}
    current = None
    current_list_key = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("- name:"):
            name = stripped.split(":", 1)[1].strip().strip('"')
            current = {
                "name": name,
                "url": "",
                "short_name": "",
                "default_branch": "main",
            }
            repos[name] = current
            current_list_key = None
        elif current is not None and indent >= 4:
            if stripped.startswith("- ") and current_list_key:
                val = stripped[2:].strip().strip('"')
                current[current_list_key].append(val)
            elif ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"')
                if not v:
                    current[k] = []
                    current_list_key = k
                else:
                    current[k] = v
                    current_list_key = None
    return repos


def cmd_init(_args: argparse.Namespace) -> None:
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    WORKTREES_DIR.mkdir(parents=True, exist_ok=True)
    (WIKI_DIR / "systems").mkdir(parents=True, exist_ok=True)
    (WIKI_DIR / "findings").mkdir(parents=True, exist_ok=True)
    (WIKI_DIR / "literature").mkdir(parents=True, exist_ok=True)
    EXPS_DIR.mkdir(parents=True, exist_ok=True)
    append_wiki_log("init", "workspace", "Verified .targets/repos, .targets/worktrees, wiki-llm, and experiments directories")
    print(f"[OK] Lab workspace initialized at: {LAB_ROOT}")
    print(f"     Target clones dir : {REPOS_DIR}")
    print(f"     Worktrees dir     : {WORKTREES_DIR}")


def cmd_sync_repos(args: argparse.Namespace) -> None:
    repos = parse_simple_repos_yaml(REPOS_YAML_PATH)
    if not repos:
        print("[WARN] No repositories found in repos.yaml")
        return
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    for name, cfg in repos.items():
        if args.repo and args.repo != name:
            continue
        target_path = REPOS_DIR / name
        url = cfg.get("url", "")
        if url.startswith(("./", "../")):
            # A relative local path in repos.yaml is relative to the lab root, not the caller's cwd.
            url = str((LAB_ROOT / url).resolve())
        if target_path.exists() and (target_path / ".git").exists():
            # repos.yaml is the source of truth for where a repo lives; follow it if the url changed.
            current = subprocess.run(["git", "-C", str(target_path), "remote", "get-url", "origin"],
                                     capture_output=True, text=True, check=False).stdout.strip()
            if url and "your-org/" not in url and current != url:
                print(f"[SYNC] origin for {name} changed: {current} -> {url}")
                subprocess.run(["git", "-C", str(target_path), "remote", "set-url", "origin", url], check=True)
            print(f"[SYNC] Fetching latest changes for {name}...")
            subprocess.run(["git", "-C", str(target_path), "fetch", "--all", "--prune"], check=False)
            # The base clone is never edited (experiments run in worktrees), so it only ever fast-forwards.
            # Without this, `new-exp` would branch from a stale local `default_branch`.
            branch = cfg.get("default_branch", "main")
            subprocess.run(["git", "-C", str(target_path), "checkout", "-q", branch], check=True)
            subprocess.run(["git", "-C", str(target_path), "merge", "--ff-only", "-q", f"origin/{branch}"], check=True)
        else:
            if "your-org/" in url or not url:
                print(f"[SKIP] {name} has placeholder URL ({url}). Update repos.yaml or clone into {target_path}.")
                continue
            print(f"[CLONE] Cloning {name} from {url} -> {target_path}...")
            subprocess.run(["git", "clone", url, str(target_path)], check=False)
    append_wiki_log("sync-repos", args.repo or "all", "Synchronized target repositories")


def cmd_check_drift(_args: argparse.Namespace) -> None:
    """0-Token Code Drift Detection: checks Fingerprint & Monitored headers in wiki-llm/."""
    fp_pattern = re.compile(r"^>\s*Repo:\s*(\S+)\s*\|\s*Fingerprint:\s*git:(\S+)", re.MULTILINE)
    mon_pattern = re.compile(r"^>\s*Monitored:\s*(.+)$", re.MULTILINE)
    # Optional: the frame lives on a kept experiment branch, not on the default branch.
    branch_pattern = re.compile(r"^>\s*Branch:\s*(\S+)", re.MULTILINE)

    checked = 0
    drifted = 0
    print("=== 0-Token Wiki-to-Code Drift Check ===")
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue  # page templates
        content = md_file.read_text(encoding="utf-8")
        fp_match = fp_pattern.search(content)
        if not fp_match:
            continue
        checked += 1
        repo_name, commit_sha = fp_match.group(1).strip(), fp_match.group(2).strip()
        mon_match = mon_pattern.search(content)
        monitored_paths = [p.strip() for p in mon_match.group(1).split(",")] if mon_match else []
        repo_path = REPOS_DIR / repo_name
        rel_md = md_file.relative_to(LAB_ROOT)

        if not (repo_path / ".git").exists():
            print(f"  [UNMOUNTED] {rel_md} -> Target repo '{repo_name}' not cloned yet in .targets/repos/{repo_name}")
            continue

        if commit_sha == "HEAD":
            head_proc = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=False
            )
            print(f"  [UNPINNED]  {rel_md} -> Fingerprint is git:HEAD (current repo HEAD is {head_proc.stdout.strip()})")
            continue

        ref = "HEAD"
        branch_match = branch_pattern.search(content)
        if branch_match:
            ref = branch_match.group(1).strip()
            has_local = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "--verify", "-q", ref],
                                       capture_output=True, check=False).returncode == 0
            if not has_local:
                ref = f"origin/{ref}"  # fresh clone: the branch exists only on the remote

        cmd = ["git", "-C", str(repo_path), "diff", "--name-only", commit_sha, ref, "--"] + monitored_paths
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        changed_files = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if proc.returncode != 0:
            print(f"  [WARN]      {rel_md} -> Could not diff {commit_sha}..{ref} in {repo_name}")
        elif changed_files:
            drifted += 1
            print(f"  [DRIFTED!]  {rel_md} -> Monitored files changed since {commit_sha}: {', '.join(changed_files)}")
        else:
            print(f"  [FRESH]     {rel_md} -> 0 changes in monitored paths since {commit_sha}")

    print(f"Summary: {checked} fingerprinted wiki page(s) checked, {drifted} drifted.")


def cmd_context_pack(_args: argparse.Namespace) -> None:
    """Compile a compact (<8000 chars) query_pack.md for fast pre-planning orientation."""
    sections = []
    sections.append(f"# Compiled Pre-Planning Context Pack (`query_pack.md`)\n> Auto-generated on `{now_iso()}` by `scripts/lab.py context-pack`. Read this before planning a new experiment.\n")

    purpose_path = WIKI_DIR / "purpose.md"
    if purpose_path.exists():
        sections.append("## 1. Lab Purpose & Rules\n" + purpose_path.read_text(encoding="utf-8").strip()[:1200])

    gap_path = WIKI_DIR / "gap_map.md"
    if gap_path.exists():
        sections.append("## 2. Open System Gaps (`gap_map.md`)\n" + gap_path.read_text(encoding="utf-8").strip()[:2000])

    if JOURNAL_PATH.exists():
        j_text = JOURNAL_PATH.read_text(encoding="utf-8")
        sections.append("## 3. Journal Snapshot (Frontier, Active Sparks & Banlist)\n" + j_text.strip()[:3000])

    index_path = WIKI_DIR / "index.md"
    if index_path.exists():
        sections.append("## 4. Wiki Page Catalog (`index.md`)\n" + index_path.read_text(encoding="utf-8").strip()[:1500])

    out_text = "\n\n".join(sections)[:8000] + "\n"
    # Planning reminders are appended after truncation so they are always present.
    out_text += (
        "\n## Planning Reminders\n"
        "* **Cross the idea with what the lab knows:** purpose, open gaps, Sparks, the Anti-Repeat Banlist, findings and earlier postmortems.\n"
        "* **Same experiment language:** reuse the concepts, structure, and mental model of previous experiments (`Experiment Language` in `wiki-llm/systems/<repo>.md`).\n"
        "* **The loop itself** (plan, rounds, conclusions, final evaluation) is in the `experiment-lab-loop` skill.\n"
    )
    out_path = WIKI_DIR / "query_pack.md"
    out_path.write_text(out_text, encoding="utf-8")
    append_wiki_log("context-pack", "wiki-llm/query_pack.md", f"Compiled context pack ({len(out_text)} chars)")
    print(f"[OK] Compiled context pack written to: {out_path} ({len(out_text)} chars)")


def exp_name_of(exp_dir: Path) -> str:
    """Full experiment name from its folder, e.g. experiments/0a-model-rl/grpo -> '0a-model-rl/grpo'."""
    return exp_dir.relative_to(EXPS_DIR).as_posix()


def used_exp_ids() -> set:
    """Hex ids already taken by an experiment folder or a worktree."""
    ids = set()
    for root in (EXPS_DIR, WORKTREES_DIR):
        if root.exists():
            ids.update(p.name[:2] for p in root.iterdir() if p.is_dir() and re.match(r"^[0-9a-f]{2}-", p.name))
    return ids


def next_exp_id() -> str:
    used = used_exp_ids()
    nxt = max((int(i, 16) for i in used), default=-1) + 1
    if nxt > 0xFF:
        raise SystemExit("[ERROR] All 256 experiment ids are used; pass a free one with --id.")
    return f"{nxt:02x}"


def worktree_name_errors(name: str) -> list:
    errors = []
    if not WORKTREE_NAME_RE.match(name):
        errors.append("use 1-3 '/'-separated segments of lowercase letters/digits joined by '-' (e.g. 'rl/grpo')")
    if len(name) > MAX_WORKTREE_NAME_LEN:
        errors.append(f"keep it at most {MAX_WORKTREE_NAME_LEN} characters")
    if any(len(seg) > MAX_SEGMENT_LEN for seg in name.split("/")):
        errors.append(f"keep each segment at most {MAX_SEGMENT_LEN} characters")
    return errors


def resolve_exp_dir(exp: str) -> Path:
    """Find an experiment folder by its hex id ('0a') or full name ('0a-model-rl/grpo')."""
    exp_id = exp[:2].lower()
    tops = [p for p in EXPS_DIR.glob(f"{exp_id}-*") if p.is_dir()] if re.match(r"^[0-9a-f]{2}$", exp_id) else []
    if len(tops) != 1:
        raise FileNotFoundError(f"Expected one experiment with id '{exp_id}' in {EXPS_DIR}, found {len(tops)}")
    posts = sorted(tops[0].rglob("postmortem.md"))
    if len(posts) != 1:
        raise FileNotFoundError(f"Expected one postmortem.md under {tops[0]}, found {len(posts)}")
    exp_dir = posts[0].parent
    if len(exp) > 2 and exp != exp_name_of(exp_dir):
        raise FileNotFoundError(f"Id '{exp_id}' belongs to '{exp_name_of(exp_dir)}', not '{exp}'")
    return exp_dir


def provision_static_skills(wt_path: Path, repo_path: Path) -> None:
    """Ensure skills-lock.json, static .agents/skills/ copies, and .claude/skills/ symlinks exist in a worktree."""
    lock_src = LAB_ROOT / "skills-lock.json"
    if lock_src.exists() and not (wt_path / "skills-lock.json").exists():
        shutil.copy2(lock_src, wt_path / "skills-lock.json")

    standards_src = LAB_ROOT / "CODE-STANDARDS.md"
    if standards_src.exists():
        shutil.copy2(standards_src, wt_path / "CODE-STANDARDS.md")

    src_agents_skills = LAB_ROOT / ".agents" / "skills"
    dst_agents_skills = wt_path / ".agents" / "skills"
    dst_claude_skills = wt_path / ".claude" / "skills"
    if src_agents_skills.exists():
        dst_agents_skills.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_agents_skills, dst_agents_skills, symlinks=False, dirs_exist_ok=True)
        dst_claude_skills.mkdir(parents=True, exist_ok=True)
        for skill_dir in sorted(dst_agents_skills.iterdir()):
            if not skill_dir.is_dir():
                continue
            link_path = dst_claude_skills / skill_dir.name
            if not link_path.exists() and not link_path.is_symlink():
                link_path.symlink_to(Path("../../.agents/skills") / skill_dir.name)

    exclude_path = repo_path / ".git" / "info" / "exclude"
    if exclude_path.parent.exists():
        existing = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
        added = []
        for pattern in (f"{p}/" if p in (".agents", ".claude") else p for p in LAB_PROVISIONED):
            if pattern not in existing.splitlines():
                added.append(pattern)
        if added:
            with exclude_path.open("a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("# Lab-provisioned static skills (do not commit to target repo)\n")
                for pattern in added:
                    f.write(f"{pattern}\n")


def exp_meta(exp_dir: Path) -> dict:
    """results.json of an experiment (target repo, branches, title)."""
    meta = json.loads((exp_dir / "results.json").read_text(encoding="utf-8"))
    meta.setdefault("exp_branch", f"exp/{exp_name_of(exp_dir)}")
    return meta


def fill_template(path: Path, values: dict) -> None:
    text = path.read_text(encoding="utf-8")
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    path.write_text(text, encoding="utf-8")


def cmd_new_exp(args: argparse.Namespace) -> None:
    repos = parse_simple_repos_yaml(REPOS_YAML_PATH)
    repo_cfg = repos.get(args.repo, {})
    short = repo_cfg.get("short_name", "")
    if not SHORT_NAME_RE.match(short):
        sys.exit(f"[ERROR] Repo '{args.repo}' needs a `short_name` in repos.yaml (1-12 lowercase letters/digits, no hyphen).")
    errors = worktree_name_errors(args.name)
    if errors:
        sys.exit(f"[ERROR] Bad worktree name '{args.name}': " + "; ".join(errors))
    exp_id = (args.id or next_exp_id()).lower()
    if not re.match(r"^[0-9a-f]{2}$", exp_id):
        sys.exit(f"[ERROR] --id must be two hex digits (e.g. '0a'), got '{exp_id}'")
    if exp_id in used_exp_ids():
        sys.exit(f"[ERROR] Experiment id '{exp_id}' is already used")
    repo_path = REPOS_DIR / args.repo
    if not (repo_path / ".git").exists():
        sys.exit(f"[ERROR] Target repo '{args.repo}' is not cloned. Run: uv run scripts/lab.py sync-repos --repo {args.repo}")

    folder_name = f"{exp_id}-{short}-{args.name}"
    assert EXP_NAME_RE.match(folder_name), folder_name
    title = args.title or args.name
    base_branch = args.base_branch or repo_cfg.get("default_branch", "main")
    exp_branch = f"exp/{folder_name}"
    template_dir = EXPS_DIR / "_TEMPLATE"

    # 1. Worktree and branch in the target repo.
    wt_path = WORKTREES_DIR / folder_name
    WORKTREES_DIR.mkdir(parents=True, exist_ok=True)
    has_local = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "--verify", "-q", base_branch],
                               capture_output=True, check=False).returncode == 0
    start_point = base_branch if has_local else f"origin/{base_branch}"  # fresh clone: only the remote branch exists
    subprocess.run(["git", "-C", str(repo_path), "worktree", "add", "-b", exp_branch, str(wt_path), start_point], check=True)
    base_sha = subprocess.run(["git", "-C", str(wt_path), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=False).stdout.strip() or "unknown"
    provision_static_skills(wt_path, repo_path)

    values = {
        "<exp-name>": folder_name,
        "<target-repo>": args.repo,
        "<base-branch>": base_branch,
        "<base-sha>": base_sha,
        "<title>": title,
        "YYYY-MM-DD HH:MM": now_iso(),
        "YYYY-MM-DD": dt.date.today().isoformat(),
    }

    # 2. Next to the code: plan.md and log.md, committed on the experiment branch by the agent.
    notes_dir = wt_path / NOTES_DIR / folder_name
    notes_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_dir / NOTES_TEMPLATE_DIR, notes_dir)
    for f in notes_dir.glob("*.md"):
        fill_template(f, values)

    # 3. In the lab: the record that is told to everyone (results, postmortem, patch).
    exp_dir = EXPS_DIR / folder_name
    exp_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_dir, exp_dir, ignore=shutil.ignore_patterns(NOTES_TEMPLATE_DIR))
    fill_template(exp_dir / "postmortem.md", values)
    res_path = exp_dir / "results.json"
    res_data = json.loads(res_path.read_text(encoding="utf-8"))
    res_data.update(exp_id=folder_name, title=title, target_repo=args.repo, base_branch=base_branch,
                    exp_branch=exp_branch, base_commit=base_sha, timestamp=now_iso())
    res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")

    append_wiki_log("new-exp", folder_name, f"Opened experiment on {args.repo} ({title})")
    print(f"[WORKTREE] {wt_path.relative_to(LAB_ROOT)} (branch: {exp_branch}, base: {start_point}@{base_sha}, skills provisioned)")
    print(f"[NOTES]    {(notes_dir).relative_to(LAB_ROOT)}/ (not committed yet: write the plan, then commit on the experiment branch)")
    print(f"[LAB]      {exp_dir.relative_to(LAB_ROOT)}/ (results.json, postmortem.md)")


def cmd_mount_exp(args: argparse.Namespace) -> None:
    """Re-create the worktree of an existing experiment from its branch (new session, fresh clone)."""
    exp_dir = resolve_exp_dir(args.exp)
    folder_name = exp_name_of(exp_dir)
    meta = exp_meta(exp_dir)
    repo_path = REPOS_DIR / meta.get("target_repo", "")
    wt_path = WORKTREES_DIR / folder_name
    if wt_path.exists():
        print(f"[OK] Worktree already mounted at {wt_path.relative_to(LAB_ROOT)}")
        return
    if not (repo_path / ".git").exists():
        sys.exit(f"[ERROR] Target repo '{meta.get('target_repo')}' is not cloned. Run: uv run scripts/lab.py sync-repos")
    subprocess.run(["git", "-C", str(repo_path), "fetch", "--all", "--prune"], check=False)
    WORKTREES_DIR.mkdir(parents=True, exist_ok=True)
    # With no local branch, git creates it from the matching remote branch.
    subprocess.run(["git", "-C", str(repo_path), "worktree", "add", str(wt_path), meta["exp_branch"]], check=True)
    provision_static_skills(wt_path, repo_path)
    print(f"[OK] Mounted {meta['exp_branch']} at {wt_path.relative_to(LAB_ROOT)}")


def exp_run_env(exp_dir: Path) -> dict:
    """Environment for commands run in an experiment's worktree: the lab's .env plus lab paths.

    LAB_ROOT and EXP_DIR let commands reach lab folders without absolute paths in plans or docs.
    """
    env = load_env_file()
    env["LAB_ROOT"] = str(LAB_ROOT)
    env["EXP_DIR"] = str(exp_dir)
    return env


def cmd_run(args: argparse.Namespace) -> None:
    """Run any command of a round in the experiment's worktree, output streamed, nothing recorded."""
    exp_dir = resolve_exp_dir(args.exp)
    wt_path = WORKTREES_DIR / exp_name_of(exp_dir)
    if not wt_path.exists():
        sys.exit(f"[ERROR] Worktree not found at {wt_path}.")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        sys.exit("[ERROR] Give the command after `--`, e.g. run --exp 0a -- uv run python -m pkg.check")
    proc = subprocess.run(" ".join(command) if len(command) == 1 else command, shell=len(command) == 1,
                          cwd=str(wt_path), env=exp_run_env(exp_dir), check=False)
    sys.exit(proc.returncode)


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Final evaluation of an experiment: run the target repo's evaluate.py and record what it measured."""
    exp_dir = resolve_exp_dir(args.exp)
    folder_name = exp_name_of(exp_dir)
    wt_path = WORKTREES_DIR / folder_name

    if not wt_path.exists():
        sys.exit(f"[ERROR] Worktree not found at {wt_path}. Run: uv run scripts/lab.py mount-exp --exp {folder_name[:2]}")
    res_path = exp_dir / "results.json"
    res_data = json.loads(res_path.read_text(encoding="utf-8"))
    base_commit = res_data.get("base_commit") or "HEAD~1"

    def git(*cmd: str) -> str:
        return subprocess.run(["git", "-C", str(wt_path), *cmd], capture_output=True, text=True, check=False).stdout

    # The branch's own change, without the files the lab copied in.
    own_changes = [".", *(f":(exclude){p}" for p in LAB_PROVISIONED)]
    (exp_dir / "patch.diff").write_text(git("diff", base_commit, "--", *own_changes) or "# No changes against base commit\n", encoding="utf-8")

    eval_path = wt_path / EVAL_SCRIPT
    original = eval_path.read_bytes() if eval_path.exists() else None
    if args.eval_from:
        # Re-measure this experiment's code with the evaluation script of another branch.
        borrowed = subprocess.run(["git", "-C", str(wt_path), "show", f"{args.eval_from}:{EVAL_SCRIPT}"], capture_output=True, check=False)
        if borrowed.returncode != 0:
            sys.exit(f"[ERROR] No {EVAL_SCRIPT} on '{args.eval_from}' (try origin/<branch>, or mount that experiment first).")
        eval_path.write_bytes(borrowed.stdout)
    if not eval_path.exists():
        sys.exit(f"[ERROR] No {EVAL_SCRIPT} at the root of the worktree. This repo has no final evaluation yet: "
                 "close the experiment with its conclusion and no number, or build the evaluation as an experiment.")

    def restore_eval_script() -> None:
        if args.eval_from:
            eval_path.write_bytes(original) if original is not None else eval_path.unlink()

    run_env = exp_run_env(exp_dir)

    cmd = f"uv run {EVAL_SCRIPT}"
    print(f"[EVAL] Running `{cmd}` in the worktree (timeout {args.timeout}s)")
    try:
        proc = subprocess.run(cmd, shell=True, cwd=str(wt_path), timeout=args.timeout, capture_output=True, text=True, check=False, env=run_env)
        stdout, stderr, exit_code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        as_text = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
        stdout, stderr, exit_code = as_text(exc.stdout), as_text(exc.stderr), None
    (exp_dir / "evaluate.log").write_text(
        f"$ {cmd}\nexit code: {exit_code if exit_code is not None else f'timeout after {args.timeout}s'}\n\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}",
        encoding="utf-8",
    )

    # Contract: the last stdout line is one JSON object of metrics.
    metrics = None
    lines = [l.strip() for l in stdout.splitlines() if l.strip()]
    if lines:
        try:
            parsed = json.loads(lines[-1])
            metrics = parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass

    problem = None
    if exit_code is None:
        problem = f"timed out after {args.timeout}s"
    elif exit_code != 0:
        problem = f"exit code {exit_code}"
    elif metrics is None:
        problem = "last stdout line is not a JSON object"
    eval_sha = git("hash-object", EVAL_SCRIPT).strip()[:12]
    restore_eval_script()
    if problem:
        append_wiki_log("evaluate", folder_name, f"Final evaluation failed ({problem})")
        sys.exit(f"[FAIL] {EVAL_SCRIPT}: {problem}. Output saved to {exp_dir / 'evaluate.log'}; no metrics written.")

    # A re-evaluation (after evaluate.py changed) keeps the earlier measurement beside the new one.
    old_metrics = res_data.get("metrics")
    if old_metrics is not None:
        res_data.setdefault("earlier_evaluations", []).append({
            "metrics": old_metrics, "eval_script_sha": res_data.get("eval_script_sha"),
            "exp_commit": res_data.get("exp_commit"), "timestamp": res_data.get("timestamp"),
        })
    res_data["metrics"] = metrics
    res_data["eval_from"] = args.eval_from
    res_data["exp_commit"] = git("rev-parse", "--short", "HEAD").strip()
    # Two results are comparable only when this (and the script's own eval_version, if any) match.
    res_data["eval_script_sha"] = eval_sha
    res_data["uncommitted_changes"] = bool(git("status", "--porcelain", "--", *own_changes).strip())
    res_data["timestamp"] = now_iso()
    res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")
    append_wiki_log("evaluate", folder_name, f"Final evaluation at {res_data['exp_commit']} (eval {res_data['eval_script_sha']})")
    print(f"[OK] Metrics: {json.dumps(metrics)}")
    print(f"[OK] Saved patch.diff, evaluate.log and {res_path}")
    if res_data["uncommitted_changes"]:
        print("[WARN] The worktree has uncommitted changes: the metrics do not belong to a commit. Commit and re-run.")


def cmd_record_verdict(args: argparse.Namespace) -> None:
    exp_dir = resolve_exp_dir(args.exp)
    folder_name = exp_name_of(exp_dir)
    fm = exp_meta(exp_dir)
    res_path = exp_dir / "results.json"
    res_data = json.loads(res_path.read_text(encoding="utf-8"))
    res_data["verdict"] = args.verdict
    res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")

    # Append row to JOURNAL.md Section 3 table
    if JOURNAL_PATH.exists():
        j_text = JOURNAL_PATH.read_text(encoding="utf-8")
        row = (
            f"| `[[{folder_name}]]` | {dt.date.today().isoformat()} | "
            f"`{fm.get('target_repo', 'repo')}` (`{fm.get('exp_branch', 'exp')}`) | "
            f"{fm.get('title', folder_name)} | `{args.metric_delta}` | "
            f"**{args.verdict}** | {args.summary} |\n"
        )
        marker = "## 4. Anti-Repeat Banlist"
        if marker in j_text and f"[[{folder_name}]]" not in j_text:
            # Attach the row to the matrix table: no blank line between the table and the new row.
            head, tail = j_text.split(marker, 1)
            j_text = head.rstrip("\n") + "\n" + row + "\n" + marker + tail
            JOURNAL_PATH.write_text(j_text, encoding="utf-8")

    append_wiki_log("verdict", folder_name, f"{args.verdict}: {args.summary} ({args.metric_delta})")
    print(f"[OK] Recorded verdict {args.verdict} for {folder_name} in JOURNAL.md and wiki-llm/log.md")


def cmd_cleanup_worktree(args: argparse.Namespace) -> None:
    exp_dir = resolve_exp_dir(args.exp)
    folder_name = exp_name_of(exp_dir)
    fm = exp_meta(exp_dir)
    repo_path = REPOS_DIR / fm.get("target_repo", "")
    wt_path = WORKTREES_DIR / folder_name

    if wt_path.exists() and (repo_path / ".git").exists():
        subprocess.run(["git", "-C", str(repo_path), "worktree", "remove", "--force", str(wt_path)], check=False)
        # Drop the now-empty parent folders of a nested name (e.g. worktrees/0a-model-rl/).
        parent = wt_path.parent
        while parent != WORKTREES_DIR and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
        append_wiki_log("cleanup-worktree", folder_name, "Removed temporary worktree after archiving patch.diff")
        print(f"[OK] Removed worktree {wt_path}. Experiment artifacts remain safely in {exp_dir}")
    else:
        print(f"[INFO] No active worktree found at {wt_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research lab controller (stdlib only)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Initialize .targets/ and verify lab directory structure")

    p_sync = sub.add_parser("sync-repos", help="Clone or fetch external repositories from repos.yaml")
    p_sync.add_argument("--repo", help="Sync only a specific repository name")

    sub.add_parser("check-drift", help="0-token check for code drift on fingerprinted wiki-llm pages")
    sub.add_parser("context-pack", help="Compile compact wiki-llm/query_pack.md for experiment planning")

    p_new = sub.add_parser("new-exp", help="Scaffold a new experiment folder and spawn an isolated git worktree")
    p_new.add_argument("--repo", required=True, help="Target repository name from repos.yaml")
    p_new.add_argument("--name", required=True, help="Worktree name, 1-3 '/'-separated short segments (e.g. 'rl/grpo')")
    p_new.add_argument("--id", help="Two hex digits (e.g. '0a'); default: next free id")
    p_new.add_argument("--title", help="Human-readable title (default: --name)")
    p_new.add_argument("--base-branch", help="Override default base branch")

    p_mount = sub.add_parser("mount-exp", help="Re-create the worktree of an existing experiment from its branch (new session, fresh clone)")
    p_mount.add_argument("--exp", required=True, help="Experiment id or full name")

    p_run = sub.add_parser("run", help="Run a round's command in the experiment worktree with .env, $LAB_ROOT and $EXP_DIR set")
    p_run.add_argument("--exp", required=True, help="Experiment id or full name (e.g. 0a or 0a-model-rl/grpo)")
    p_run.add_argument("command", nargs=argparse.REMAINDER, help="The command, after `--`")

    p_eval = sub.add_parser("evaluate", help=f"Final evaluation: run the target repo's {EVAL_SCRIPT} in the worktree, save metrics, evaluate.log and patch.diff")
    p_eval.add_argument("--exp", required=True, help="Experiment id or full name (e.g. 0a or 0a-model-rl/grpo)")
    p_eval.add_argument("--eval-from", help=f"Run the {EVAL_SCRIPT} of this branch on the experiment's code (re-measure after the evaluation changed)")
    p_eval.add_argument("--timeout", type=int, default=3600, help="Seconds before the evaluation is stopped (default 3600)")

    p_verdict = sub.add_parser("record-verdict", help="Record experiment verdict into results.json, JOURNAL.md, and log.md")
    p_verdict.add_argument("--exp", required=True, help="Experiment id or full name (e.g. 0a or 0a-model-rl/grpo)")
    p_verdict.add_argument("--verdict", required=True, choices=["HYPOTHESIS_SUPPORTED", "HYPOTHESIS_REFUTED", "INFRA_INCONCLUSIVE"])
    p_verdict.add_argument("--metric-delta", required=True, help="Short metric change string (e.g. '+4.2%% F1', or 'no metric')")
    p_verdict.add_argument("--summary", required=True, help="One-line takeaway for JOURNAL.md")

    p_clean = sub.add_parser("cleanup-worktree", help="Remove temporary git worktree after patch.diff is saved")
    p_clean.add_argument("--exp", required=True, help="Experiment id or full name (e.g. 0a or 0a-model-rl/grpo)")

    args = parser.parse_args()
    dispatch = {
        "init": cmd_init,
        "sync-repos": cmd_sync_repos,
        "check-drift": cmd_check_drift,
        "context-pack": cmd_context_pack,
        "new-exp": cmd_new_exp,
        "mount-exp": cmd_mount_exp,
        "run": cmd_run,
        "evaluate": cmd_evaluate,
        "record-verdict": cmd_record_verdict,
        "cleanup-worktree": cmd_cleanup_worktree,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
