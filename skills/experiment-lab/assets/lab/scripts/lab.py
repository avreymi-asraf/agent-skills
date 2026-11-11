#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""lab.py - the mechanical steps of a research lab, standard library only.

It clones target repos, opens an experiment (branch, worktree, notes, lab folder, a row in the
journal's matrix), runs commands in a worktree, runs the final evaluation and records a verdict.
It makes no judgment: the plan, the experiment log, the cortex and the journal's Frontier, Sparks
and Banlist are written by the agent.
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
# What the lab itself copies into every worktree: its skills. They are not part of an experiment's
# change, even when the target repo tracks its own copies (then provisioning overwrites them).
LAB_PROVISIONED = (".agents", ".claude")
CORTEX_DIR = LAB_ROOT / "cortex"
EXPS_DIR = LAB_ROOT / "experiments"
JOURNAL_PATH = LAB_ROOT / "JOURNAL.md"
REPOS_YAML_PATH = LAB_ROOT / "repos.yaml"
# An experiment has two homes. Next to the code, on its branch in the target repo:
#   notes/<exp-name>/{plan.md, log.md, runs/}   (the experiment's own working memory)
# In the lab: experiments/<exp-name>/{results.json, postmortem.md, patch.diff, evaluate.log}  (what is told to everyone)
# The two homes have different names on purpose: `experiments/` exists only in the lab.
NOTES_TEMPLATE_DIR = "notes"  # subfolder of experiments/_TEMPLATE copied into the worktree
NOTES_DIR = "notes"           # folder inside the target repo that holds plan.md and log.md
MATRIX_HEADING = "Experiment Matrix"  # the section of JOURNAL.md that lists every experiment, one row each
OPEN_MARK = "**OPEN**"                # in the Verdict column of that row until `record-verdict`
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


def append_cortex_log(operation: str, target: str, summary: str) -> None:
    log_path = CORTEX_DIR / "log.md"
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
    for layer in ("claims", "findings", "tensions", "systems", "sources/text"):
        (CORTEX_DIR / layer).mkdir(parents=True, exist_ok=True)
    EXPS_DIR.mkdir(parents=True, exist_ok=True)
    append_cortex_log("init", "workspace", "Verified .targets/repos, .targets/worktrees, cortex, and experiments directories")
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
        note_missing_system_page(name)
    append_cortex_log("sync-repos", args.repo or "all", "Synchronized target repositories")


def cmd_check_drift(_args: argparse.Namespace) -> None:
    """0-Token Code Drift Detection: checks Fingerprint & Monitored headers in cortex/."""
    fp_pattern = re.compile(r"^>\s*Repo:\s*(\S+)\s*\|\s*Fingerprint:\s*git:(\S+)", re.MULTILINE)
    mon_pattern = re.compile(r"^>\s*Monitored:\s*(.+)$", re.MULTILINE)
    # Optional: the shared components the page describes live on an experiment branch, not on the default branch.
    branch_pattern = re.compile(r"^>\s*Branch:\s*(\S+)", re.MULTILINE)

    checked = 0
    drifted = 0
    print("=== 0-Token Cortex-to-Code Drift Check ===")
    for md_file in sorted(CORTEX_DIR.rglob("*.md")):
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

    print(f"Summary: {checked} fingerprinted cortex page(s) checked, {drifted} drifted.")


# context-pack: how much of each source goes into the pack. Whatever does not fit is cut at a line
# boundary and the cut is marked in the pack with the file to open, so a reader never takes a part for
# the whole. The budgets are generous for what is written by hand (purpose, Frontier, Sparks, Banlist):
# in an ordinary lab only the experiment matrix and the resolved gaps are shortened.
PACK_LIMITS = {"purpose": 3000, "gap_map": 4000, "journal_section": 6000, "index": 3000}
PACK_CLOSED_ROWS = 12  # most recent closed experiments shown from the matrix; open ones are always shown


def clip(text: str, limit: int, where: str, cuts: list) -> str:
    """`text`, or its first lines up to about `limit` characters followed by a line that says what was left out and where it is."""
    text = text.strip()
    if len(text) <= limit:
        return text
    lines, kept, size = text.splitlines(), [], 0
    for line in lines:
        if size + len(line) + 1 > limit:
            break
        kept.append(line)
        size += len(line) + 1
    left = len(lines) - len(kept)
    cuts.append(f"{where}: {left} line(s)")
    return "\n".join(kept) + f"\n\n> **[CUT]** {left} more line(s) are not shown. Read {where} for the rest."


def embed(text: str) -> str:
    """A file's text as a part of the pack: without its own title, its sections one level down."""
    return re.sub(r"(?m)^## ", "### ", re.sub(r"\A# .*\n", "", text.strip())).strip()


def journal_for_pack(text: str, cuts: list) -> str:
    """The journal, section by section, each with its own budget. From the experiment matrix: the open experiments and the most recent closed ones."""
    out = []
    for part in re.split(r"(?m)^(?=### )", embed(text)):
        heading = part.splitlines()[0].lstrip("# ") if part.startswith("### ") else ""
        where = f"`JOURNAL.md` → {heading}" if heading else "`JOURNAL.md`"
        if MATRIX_HEADING in heading:
            lines = part.rstrip().splitlines()
            closed = [i for i, l in enumerate(lines) if l.startswith("| `[[") and OPEN_MARK not in l]
            dropped = set(closed[:-PACK_CLOSED_ROWS]) if len(closed) > PACK_CLOSED_ROWS else set()
            if dropped:
                lines = [l for i, l in enumerate(lines) if i not in dropped]
                lines += ["", f"> **[CUT]** {len(dropped)} earlier closed experiment(s) are not shown. Read {where} for all rows."]
                cuts.append(f"{where}: {len(dropped)} earlier closed experiment(s)")
            part = "\n".join(lines)
        if part.strip():
            out.append(clip(part, PACK_LIMITS["journal_section"], where, cuts))
    return "\n\n".join(out)


def cmd_context_pack(_args: argparse.Namespace) -> None:
    """Compile query_pack.md: purpose, gap map, journal and cortex index in one file, for orientation before planning."""
    cuts = []
    sections = [f"# Compiled Pre-Planning Context Pack (`query_pack.md`)\n> Auto-generated on `{now_iso()}` by `scripts/lab.py context-pack`. "
                "Read this before planning a new experiment. A part that did not fit ends with a line marked **[CUT]** that names the file to open."]

    def whole_file(title: str, path: Path, limit: int) -> None:
        if path.exists():
            rel = path.relative_to(LAB_ROOT).as_posix()
            sections.append(f"## {title} (`{rel}`)\n" + clip(embed(path.read_text(encoding="utf-8")), limit, f"`{rel}`", cuts))

    whole_file("1. Lab Purpose", CORTEX_DIR / "purpose.md", PACK_LIMITS["purpose"])
    whole_file("2. Gap Map", CORTEX_DIR / "gap_map.md", PACK_LIMITS["gap_map"])
    if JOURNAL_PATH.exists():
        sections.append("## 3. Journal (`JOURNAL.md`)\n" + journal_for_pack(JOURNAL_PATH.read_text(encoding="utf-8"), cuts))
    whole_file("4. Cortex Page Catalog", CORTEX_DIR / "index.md", PACK_LIMITS["index"])

    sections.append(
        "## Planning Reminders\n"
        "* **Cross the idea with what the lab knows:** purpose, open gaps, Sparks, open experiments, the Anti-Repeat Banlist, findings, open tensions and earlier postmortems.\n"
        "* **Same Experiment Language:** the idea goes in at an extension point and uses the shared components of `cortex/systems/<repo>.md`.\n"
        "* **The loop itself** (plan, rounds, conclusions, final evaluation) is in the `experiment-lab-loop` skill."
    )
    out_text = "\n\n".join(sections) + "\n"
    out_path = CORTEX_DIR / "query_pack.md"
    out_path.write_text(out_text, encoding="utf-8")
    append_cortex_log("context-pack", "cortex/query_pack.md", f"Compiled context pack ({len(out_text)} chars)")
    print(f"[OK] Context pack written to {out_path.relative_to(LAB_ROOT)} ({len(out_text)} chars)")
    if cuts:
        print("[CUT] Not everything fits in the pack; each cut is marked in it. Left out: " + "; ".join(cuts))


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


def known_exp_names() -> list:
    """Names of the experiments that have a folder in this clone of the lab."""
    if not EXPS_DIR.exists():
        return []
    return sorted(exp_name_of(p.parent) for p in EXPS_DIR.rglob("results.json") if "_TEMPLATE" not in p.parts)


def resolve_exp_dir(exp: str) -> Path:
    """Find an experiment folder by its hex id ('0a') or full name ('0a-model-rl/grpo'). Exits with one line if there is none."""
    exp_id = exp[:2].lower()
    if not re.match(r"^[0-9a-f]{2}$", exp_id) or (len(exp) > 2 and not EXP_NAME_RE.match(exp)):
        sys.exit(f"[ERROR] '{exp}' is not an experiment: give the two hex digits of its id (e.g. 0a) or its full name (e.g. 0a-model-rl/grpo).")
    names = [n for n in known_exp_names() if n.startswith(f"{exp_id}-")]
    if len(names) != 1 or (len(exp) > 2 and exp != names[0]):
        found = f"Id '{exp_id}' belongs to '{names[0]}'." if len(names) == 1 else (
            f"Id '{exp_id}' matches {len(names)} folders: {', '.join(names)}." if names else
            f"Experiments here: {', '.join(known_exp_names()) or 'none'}.")
        sys.exit(f"[ERROR] No experiment '{exp}' in {EXPS_DIR.relative_to(LAB_ROOT)}/. {found} "
                 "An experiment opened in another clone is here only after that clone committed and pushed the lab repo.")
    return EXPS_DIR / names[0]


def provision_static_skills(wt_path: Path, repo_path: Path) -> None:
    """Copy the lab's skills into a worktree (.agents/skills/, linked from .claude/skills/) and keep them out of git."""
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
        for pattern in (f"{p}/" for p in LAB_PROVISIONED):
            if pattern not in existing.splitlines():
                added.append(pattern)
        if added:
            with exclude_path.open("a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("# Skills copied in by the lab (not part of the target repo)\n")
                for pattern in added:
                    f.write(f"{pattern}\n")


def set_matrix_row(exp_name: str, cells: list) -> bool:
    """Write an experiment's row in the journal's matrix: replace the row it has, or add one at the end of the table.

    `new-exp` adds the row (verdict OPEN) and `record-verdict` completes it, so the matrix lists every
    experiment, open or closed. Returns False when the journal has no matrix section to write into.
    """
    if not JOURNAL_PATH.exists():
        return False
    row = "| " + " | ".join(cells) + " |"
    lines = JOURNAL_PATH.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("## ") and MATRIX_HEADING in l), None)
    if start is None:
        return False
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    own = next((i for i in range(start, end) if lines[i].startswith(f"| `[[{exp_name}]]`")), None)
    if own is not None:
        lines[own] = row
    else:
        table = [i for i in range(start, end) if lines[i].startswith("|")]
        lines.insert(table[-1] + 1 if table else end, row)
    JOURNAL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def matrix_cells(exp_name: str, meta: dict, closed: str = "", delta: str = "", verdict: str = OPEN_MARK, takeaway: str = "") -> list:
    return [f"`[[{exp_name}]]`", meta.get("opened") or "", closed,
            f"`{meta.get('target_repo', '')}` (`{meta.get('exp_branch', '')}`)", meta.get("title") or exp_name,
            f"`{delta}`" if delta else "", verdict, takeaway]


def system_page_of(repo: str) -> Path | None:
    """The system page of a target repo: cortex/systems/<repo>.md, or a page there whose header says `> Repo: <repo>`."""
    systems = CORTEX_DIR / "systems"
    pages = [p for p in sorted(systems.glob("*.md")) if not p.name.startswith("_")] if systems.exists() else []
    header = re.compile(rf"^>\s*Repo:\s*{re.escape(repo)}(\s|\||$)", re.MULTILINE)
    return next((p for p in pages if p.stem == repo or header.search(p.read_text(encoding="utf-8"))), None)


def note_missing_system_page(repo: str) -> None:
    if system_page_of(repo) is None:
        print(f"[NOTE] Target '{repo}' has no system page yet (cortex/systems/{repo}.md), so no Experiment Language is written down for it. "
              "Write the page from cortex/systems/_TEMPLATE.md before any experiment code; the template says what to do when the target is new or empty.")


LAB_REPO_REMINDER = ("Commit and push the lab repo as well: another session, or `mount-exp` in a fresh clone, "
                     "finds this experiment only through what the lab repo holds.")


def exp_meta(exp_dir: Path) -> dict:
    """results.json of an experiment (target repo, branches, title)."""
    meta = json.loads((exp_dir / "results.json").read_text(encoding="utf-8"))
    if not meta.get("exp_branch"):
        meta["exp_branch"] = f"exp/{exp_name_of(exp_dir)}"
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
    res_data.update(exp_name=folder_name, title=title, target_repo=args.repo, base_branch=base_branch,
                    exp_branch=exp_branch, base_commit=base_sha, opened=dt.date.today().isoformat(), timestamp=now_iso())
    res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")
    in_matrix = set_matrix_row(folder_name, matrix_cells(folder_name, res_data))

    append_cortex_log("new-exp", folder_name, f"Opened experiment on {args.repo} ({title})")
    print(f"[WORKTREE] {wt_path.relative_to(LAB_ROOT)} (branch: {exp_branch}, base: {start_point}@{base_sha}, skills provisioned)")
    print(f"[NOTES]    {(notes_dir).relative_to(LAB_ROOT)}/ (not committed yet: write the plan, then commit on the experiment branch)")
    print(f"[LAB]      {exp_dir.relative_to(LAB_ROOT)}/ (results.json, postmortem.md)" + (", and a row marked OPEN in the JOURNAL.md matrix" if in_matrix else ""))
    if not in_matrix:
        print(f"[WARN] JOURNAL.md has no '{MATRIX_HEADING}' section, so this experiment is not listed there.")
    print(f"[NEXT]     {LAB_REPO_REMINDER}")
    note_missing_system_page(args.repo)


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

    LAB_ROOT (the lab) and EXP_DIR (the experiment's lab folder, experiments/<exp-name>/) let commands
    reach lab folders without absolute paths in plans or docs.
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
    """Closing measurement of an experiment: save its code change, run the target repo's evaluate.py if it has one, record what it measured."""
    exp_dir = resolve_exp_dir(args.exp)
    folder_name = exp_name_of(exp_dir)
    wt_path = WORKTREES_DIR / folder_name

    if not wt_path.exists():
        sys.exit(f"[ERROR] Worktree not found at {wt_path.relative_to(LAB_ROOT)}. Run: uv run scripts/lab.py mount-exp --exp {folder_name[:2]}")
    res_path = exp_dir / "results.json"
    res_data = json.loads(res_path.read_text(encoding="utf-8"))
    base_commit = res_data.get("base_commit") or "HEAD~1"

    def git(*cmd: str) -> str:
        return subprocess.run(["git", "-C", str(wt_path), *cmd], capture_output=True, text=True, check=False).stdout

    # The experiment's code change: without the skills the lab copied in, and without its notes folder
    # (plan, log, run files), which is read on the branch and not as part of the change.
    code_change = [".", *(f":(exclude){p}" for p in (*LAB_PROVISIONED, f"{NOTES_DIR}/{folder_name}"))]
    (exp_dir / "patch.diff").write_text(git("diff", base_commit, "--", *code_change) or "# No code change against the base commit\n", encoding="utf-8")
    measured_at = {"exp_commit": git("rev-parse", "--short", "HEAD").strip(),
                   "uncommitted_changes": bool(git("status", "--porcelain", "--", *code_change).strip())}
    uncommitted_warning = "[WARN] The worktree has uncommitted code changes: patch.diff and any metrics do not belong to a commit. Commit and re-run."

    eval_path = wt_path / EVAL_SCRIPT
    original = eval_path.read_bytes() if eval_path.exists() else None
    if args.eval_from:
        # Re-measure this experiment's code with the evaluation script of another branch.
        borrowed = subprocess.run(["git", "-C", str(wt_path), "show", f"{args.eval_from}:{EVAL_SCRIPT}"], capture_output=True, check=False)
        if borrowed.returncode != 0:
            sys.exit(f"[ERROR] No {EVAL_SCRIPT} on '{args.eval_from}' (try origin/<branch>, or mount that experiment first).")
        eval_path.write_bytes(borrowed.stdout)
    if not eval_path.exists():
        # A target repo with no final evaluation yet is a normal state: the experiment closes with its conclusion and no number.
        res_data.update(measured_at, timestamp=now_iso())
        res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")
        append_cortex_log("evaluate", folder_name, f"No {EVAL_SCRIPT} in the target repo: patch.diff saved at {res_data['exp_commit']}, no metrics")
        print(f"[OK] Saved patch.diff at {res_data['exp_commit']}. No metrics: there is no {EVAL_SCRIPT} at the root of the worktree, "
              "so this repo has no final evaluation yet. The experiment closes with its conclusion and no number.")
        if res_data["uncommitted_changes"]:
            print(uncommitted_warning)
        return

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
    # The evaluation version: the git hash of the script that ran, and the version the script itself
    # reports for an external benchmark, if any. Two numbers are comparable only when it is the same.
    version = git("hash-object", EVAL_SCRIPT).strip()[:12]
    if metrics and metrics.get("eval_version"):
        version += f"+{metrics['eval_version']}"
    restore_eval_script()
    old_metrics = res_data.get("metrics")
    if problem:
        if old_metrics is not None or args.eval_from:
            # A re-evaluation that could not run: the earlier number stays, under its earlier version,
            # and the record says which evaluation it could not be measured with.
            res_data.setdefault("failed_evaluations", []).append({
                "evaluation_version": version, "eval_from": args.eval_from, "problem": problem, "timestamp": now_iso(),
            })
            res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")
        append_cortex_log("evaluate", folder_name, f"Final evaluation failed ({problem})")
        sys.exit(f"[FAIL] {EVAL_SCRIPT}: {problem}. Output saved to {(exp_dir / 'evaluate.log').relative_to(LAB_ROOT)}; no metrics written.")

    # A re-evaluation (after evaluate.py changed) keeps the earlier measurement beside the new one.
    if old_metrics is not None:
        res_data.setdefault("earlier_evaluations", []).append({
            "metrics": old_metrics, "evaluation_version": res_data.get("evaluation_version"),
            "exp_commit": res_data.get("exp_commit"), "timestamp": res_data.get("timestamp"),
        })
    res_data.update(measured_at, metrics=metrics, eval_from=args.eval_from, evaluation_version=version, timestamp=now_iso())
    res_path.write_text(json.dumps(res_data, indent=2) + "\n", encoding="utf-8")
    append_cortex_log("evaluate", folder_name, f"Final evaluation at {res_data['exp_commit']} (evaluation version {version})")
    print(f"[OK] Metrics: {json.dumps(metrics)}")
    print(f"[OK] Evaluation version: {version}")
    print(f"[OK] Saved patch.diff, evaluate.log and {res_path.relative_to(LAB_ROOT)}")
    if res_data["uncommitted_changes"]:
        print(uncommitted_warning)


def cmd_record_verdict(args: argparse.Namespace) -> None:
    exp_dir = resolve_exp_dir(args.exp)
    folder_name = exp_name_of(exp_dir)
    meta = exp_meta(exp_dir)
    meta["verdict"] = args.verdict
    (exp_dir / "results.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    in_matrix = set_matrix_row(folder_name, matrix_cells(folder_name, meta, closed=dt.date.today().isoformat(), delta=args.metric_delta,
                                                         verdict=f"**{args.verdict}**", takeaway=args.summary))
    append_cortex_log("verdict", folder_name, f"{args.verdict}: {args.summary} ({args.metric_delta})")
    print(f"[OK] Recorded verdict {args.verdict} for {folder_name} in results.json, cortex/log.md"
          + (" and its row of the JOURNAL.md matrix" if in_matrix else ""))
    if not in_matrix:
        print(f"[WARN] JOURNAL.md has no '{MATRIX_HEADING}' section: the verdict is not in the journal.")
    print(f"[NEXT] {LAB_REPO_REMINDER}")


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
        append_cortex_log("cleanup-worktree", folder_name, "Removed the worktree; the branch and the lab folder stay")
        print(f"[OK] Removed worktree {wt_path.relative_to(LAB_ROOT)}. The branch {fm.get('exp_branch')} and {exp_dir.relative_to(LAB_ROOT)}/ stay.")
    else:
        print(f"[INFO] No worktree at {wt_path.relative_to(LAB_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research lab controller (stdlib only)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Initialize .targets/ and verify lab directory structure")

    p_sync = sub.add_parser("sync-repos", help="Clone or fetch external repositories from repos.yaml")
    p_sync.add_argument("--repo", help="Sync only a specific repository name")

    sub.add_parser("check-drift", help="0-token check for code drift on fingerprinted cortex pages")
    sub.add_parser("context-pack", help="Compile cortex/query_pack.md (purpose, gap map, journal, cortex index) for planning; a section that does not fit is cut at a marked line")

    p_new = sub.add_parser("new-exp", help="Open an experiment: branch and worktree in the target repo with its notes, the lab folder, and a row marked OPEN in the JOURNAL.md matrix")
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

    p_eval = sub.add_parser("evaluate", help=f"Closing measurement: save the experiment's code change to patch.diff and, when the target repo has an {EVAL_SCRIPT}, run it and save metrics and evaluate.log")
    p_eval.add_argument("--exp", required=True, help="Experiment id or full name (e.g. 0a or 0a-model-rl/grpo)")
    p_eval.add_argument("--eval-from", help=f"Run the {EVAL_SCRIPT} of this branch on the experiment's code (re-measure after the evaluation changed)")
    p_eval.add_argument("--timeout", type=int, default=3600, help="Seconds before the evaluation is stopped (default 3600)")

    p_verdict = sub.add_parser("record-verdict", help="Record the verdict in results.json, in the experiment's row of the JOURNAL.md matrix and in cortex/log.md")
    p_verdict.add_argument("--exp", required=True, help="Experiment id or full name (e.g. 0a or 0a-model-rl/grpo)")
    p_verdict.add_argument("--verdict", required=True, choices=["HYPOTHESIS_SUPPORTED", "HYPOTHESIS_REFUTED", "INFRA_INCONCLUSIVE"])
    p_verdict.add_argument("--metric-delta", required=True, help="Short metric change string (e.g. '+4.2%% F1', or 'no metric')")
    p_verdict.add_argument("--summary", required=True, help="One-line takeaway for the matrix row")

    p_clean = sub.add_parser("cleanup-worktree", help="Remove the experiment's worktree; the branch and the lab folder stay")
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
