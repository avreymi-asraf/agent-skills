#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""lab.py - the mechanical steps of a research lab, standard library only.

It clones experiment repos, opens an experiment (lab folder, journal row, start branch), opens a try
(a line in the map of tries, a try branch with its brief), prints the map, shows what a try has to
tell the lab, runs a command or the evaluation on a try, and records the verdict.

It makes no judgment. The plans, the logs, the lab step records, the cortex and the journal's
Frontier, Sparks and Banlist are written by hand.

Two rules it holds to, so that the lab's records stay the truth:
  - A record is published to the lab's default branch before the branch it describes is created.
  - Whether a try is live is read from the map of tries, never from git.
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
REPOS_DIR = LAB_ROOT / ".repos"
CLONES_DIR = REPOS_DIR / "clones"          # one clone per experiment repo; never edited
WORKTREES_DIR = REPOS_DIR / "worktrees"    # <repo short name>/<experiment name>/<try name>/
CORTEX_DIR = LAB_ROOT / "cortex"
EXPS_DIR = LAB_ROOT / "experiments"        # <repo short name>/<experiment name>/ : the lab folder of an experiment
LAB_FOLDER_TEMPLATE = EXPS_DIR / "_TEMPLATE"
START_BRANCH_DIR = LAB_ROOT / "start-branch"   # the experiment template: what a start branch is given
JOURNAL_PATH = LAB_ROOT / "JOURNAL.md"
REPOS_YAML_PATH = LAB_ROOT / "repos.yaml"

NOTES_DIR = "notes"                # on a branch of the experiment repo: notes/<experiment name>/{plan.md, log.md, runs/}
START_TRY = "main"                 # the start branch is <experiment name>/main; no try may take this name
# The lab kit: what the lab commits on a start branch. It is not part of a try's code change.
LAB_KIT = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".agents/skills", ".claude/skills")
POINTER_FILES = ("CLAUDE.md", "GEMINI.md")   # for tools that do not read AGENTS.md by themselves
MATRIX_HEADING = "Experiment Matrix"
OPEN = "OPEN"
VERDICTS = ("HYPOTHESIS_SUPPORTED", "HYPOTHESIS_REFUTED", "INFRA_INCONCLUSIVE")
EVAL_SCRIPT = "evaluate.py"        # the one evaluation API: this script at the root of the experiment repo
SIGNALS = ("working", "ready", "failed", "blocked")
MAX_COMMENT = 100

SEGMENT = r"[a-z0-9]+(?:-[a-z0-9]+)*"
SEGMENT_RE = re.compile(rf"^{SEGMENT}$")
EXP_NAME_RE = re.compile(rf"^[0-9a-f]{{2}}-{SEGMENT}$")     # <id>-<idea>, e.g. 02-probes
SHORT_NAME_RE = re.compile(r"^[a-z0-9]{1,12}$")
MAX_NAME_LEN = 32

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"   # git's empty tree: the base of an experiment opened on an empty repo
NO_PUBLISH = False   # set by --no-publish: commit the lab's records, do not pull or push


# ---------------------------------------------------------------------------------------------- basics

def fail(message: str) -> None:
    sys.exit(f"[ERROR] {message}")


def now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def today() -> str:
    return dt.date.today().isoformat()


def rel(path: Path) -> str:
    return path.relative_to(LAB_ROOT).as_posix()


def git(cwd: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    """Run git in `cwd`, output captured. With check=True a failure stops the command with git's own message."""
    proc = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False)
    if check and proc.returncode != 0:
        fail(f"git {' '.join(args)} failed in {cwd}:\n{(proc.stderr or proc.stdout).strip()}")
    return proc


def git_out(cwd: Path, *args: str) -> str:
    return git(cwd, *args).stdout.strip()


def ref_exists(repo: Path, ref: str) -> bool:
    return git(repo, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}").returncode == 0


def has_origin(repo: Path) -> bool:
    return git(repo, "remote", "get-url", "origin").returncode == 0


def fetch(repo: Path) -> None:
    if has_origin(repo):
        git(repo, "fetch", "--prune", "-q", "origin")


def remote_or_local(repo: Path, branch: str) -> str | None:
    """The ref to read a branch from: what was pushed, when the repo has a remote; else the local branch."""
    for ref in (f"origin/{branch}", branch):
        if ref_exists(repo, ref):
            return ref
    return None


def load_env_file(path: Path = LAB_ROOT / ".env") -> dict:
    """os.environ plus KEY=VALUE pairs from the lab's .env. Values already set win. Only names are printed."""
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


def append_cortex_log(operation: str, target: str, summary: str) -> Path | None:
    """Add a line to cortex/log.md: only when an experiment is opened, evaluated or closed."""
    log_path = CORTEX_DIR / "log.md"
    if not log_path.exists():
        return None
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"## [{now_iso()}] {operation} | {target} — {summary}\n")
    return log_path


def parse_repos_yaml(path: Path = REPOS_YAML_PATH) -> dict:
    """repos.yaml as {name: {url, short_name, default_branch}}. A small parser, so the lab needs no dependency."""
    if not path.exists():
        return {}
    repos, current = {}, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- name:"):
            current = {"name": stripped.split(":", 1)[1].strip().strip('"'), "url": "", "short_name": "", "default_branch": "main"}
            repos[current["name"]] = current
        elif current is not None and ":" in stripped and line.startswith(" "):
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip().strip('"')
    return repos


def strip_comments(text: str) -> str:
    """Markdown without its HTML comments: the templates keep their example entries inside comments."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def fill(text: str, values: dict) -> str:
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    return text


# ------------------------------------------------------------------------------ publishing the lab's records

RECORD_PATHS = ("experiments", "cortex", "JOURNAL.md")   # the lab's records: what `publish` commits

def lab_default_branch() -> str:
    """The lab's default branch as its remote names it; without a remote, the branch that is checked out."""
    head = git_out(LAB_ROOT, "symbolic-ref", "--short", "-q", "refs/remotes/origin/HEAD")
    if not head and has_origin(LAB_ROOT):   # a lab made by `git init` and `remote add` has no origin/HEAD yet: ask the remote
        git(LAB_ROOT, "remote", "set-head", "origin", "--auto")
        head = git_out(LAB_ROOT, "symbolic-ref", "--short", "-q", "refs/remotes/origin/HEAD")
    return head.split("/", 1)[1] if head else git_out(LAB_ROOT, "rev-parse", "--abbrev-ref", "HEAD")


def need_default_branch_checkout() -> None:
    """Publishing pushes this checkout's commits to the lab's default branch, so it may hold nothing else.

    A cloud session is checked out on its own session branch; that is fine while the branch holds no commit of its own.
    """
    branch, current = lab_default_branch(), git_out(LAB_ROOT, "rev-parse", "--abbrev-ref", "HEAD")
    if current == branch:
        return
    if not ref_exists(LAB_ROOT, f"origin/{branch}"):
        fail(f"The lab's remote has no branch '{branch}' yet. Push the lab there first: git push -u origin {branch}")
    foreign = git_out(LAB_ROOT, "log", "--oneline", f"origin/{branch}..HEAD")
    if foreign:
        fail(f"This checkout is on '{current}', which holds commits that are not on the lab's default branch '{branch}':\n{foreign}\n"
             f"Lab operations publish to '{branch}', so they run from a checkout of it (git checkout {branch}). "
             "Changes to how the lab works stay on their own branch.")


def lab_can_publish() -> bool:
    return not NO_PUBLISH and has_origin(LAB_ROOT)


def lab_pull() -> None:
    """Bring the lab's records up to date before a command reserves an id or a try name."""
    if not lab_can_publish():
        return
    git(LAB_ROOT, "fetch", "-q", "origin")
    need_default_branch_checkout()
    proc = git(LAB_ROOT, "pull", "--rebase", "--autostash", "-q", "origin", lab_default_branch())
    if proc.returncode != 0:
        git(LAB_ROOT, "rebase", "--abort")
        fail("Could not bring the lab up to date (git pull --rebase). Make this checkout a clean checkout of the lab's "
             f"default branch, then run again.\n{(proc.stderr or proc.stdout).strip()}")


def begin_record() -> None:
    """Called by a command before it writes a record: bring the lab up to date, and commit what was written by hand.

    Records written by hand and not committed yet (a lab step record, a postmortem, a claim) get a commit of their own,
    so that the command's commit holds only what the command wrote and can be taken back without touching them.
    They are published together with the command's record.
    """
    lab_pull()
    names = [name for name in RECORD_PATHS if (LAB_ROOT / name).exists()]
    if git(LAB_ROOT, "rev-parse", "--git-dir").returncode != 0 or not git_out(LAB_ROOT, "status", "--porcelain", "--", *names):
        return
    git(LAB_ROOT, "add", "--", *names, check=True)
    git(LAB_ROOT, "commit", "-q", "-m", "Lab records written by hand", "--", *names, check=True)
    print("[LAB] Records written by hand were not committed yet; committed them first, and they are published with this command.")


def publish(paths: list, message: str, recheck=None, written_by_hand: bool = False) -> None:
    """Commit the lab's change and put it on the lab's default branch: pull with rebase, push, again when rejected.

    `recheck` is called after other sessions' changes came in; when it returns a problem (the id or the try name
    was taken meanwhile) the commit is taken back and the command stops, before any branch is created.
    What a command wrote is removed with its commit, so it can simply be run again. What was written by hand
    (`written_by_hand`) is never removed: the commit is undone and the files stay as they were written.
    """
    if git(LAB_ROOT, "rev-parse", "--git-dir").returncode != 0:
        fail("The lab is not a git repository: its records cannot be recorded. Run `git init` and commit the lab first.")
    names = [rel(p) for p in paths if p is not None]
    git(LAB_ROOT, "add", "--", *names, check=True)
    if git(LAB_ROOT, "diff", "--cached", "--quiet").returncode == 0:
        return
    git(LAB_ROOT, "commit", "-q", "-m", message, "--", *names, check=True)

    def take_back(problem: str) -> None:
        git(LAB_ROOT, "reset", "-q", "HEAD~1")
        for name in () if written_by_hand else names:   # one path at a time: a path that is new has nothing to check out, and is removed
            git(LAB_ROOT, "checkout", "-q", "HEAD", "--", name)
            git(LAB_ROOT, "clean", "-fdq", "--", name)
        fail(problem)

    if not lab_can_publish():
        reason = "--no-publish was given" if NO_PUBLISH else "the lab has no remote named origin"
        print(f"[LAB] Committed, not published ({reason}): {message}")
        print("      Nobody else sees this record until it is on the lab's default branch.")
        return
    branch = lab_default_branch()
    last = ""
    for _ in range(4):
        push = git(LAB_ROOT, "push", "-q", "origin", f"HEAD:{branch}")
        if push.returncode == 0:
            print(f"[LAB] Published to {branch}: {message}")
            return
        last = (push.stderr or push.stdout).strip()
        pull = git(LAB_ROOT, "pull", "--rebase", "--autostash", "-q", "origin", branch)
        if pull.returncode != 0:
            git(LAB_ROOT, "rebase", "--abort")
            take_back(("Another session changed the same lines of the lab's records, so nothing was published. Your changes are "
                       "still in the files, not committed. Run `git pull --rebase --autostash`, settle the lines git marks, "
                       "and publish again." if written_by_hand else
                       "Another session changed the same lines of the lab's records, so nothing was published and nothing "
                       "was created. Run the command again.") + "\n" + ((pull.stderr or pull.stdout).strip().splitlines() or [""])[0])
        if recheck and (problem := recheck()):
            take_back(problem)
    take_back(f"Could not push the lab's record to {branch}; nothing was published. Does this session have the right to "
              f"push there?\n{last}")


def cmd_publish(args: argparse.Namespace) -> None:
    """Commit every change in the lab's records and put it on the lab's default branch. For what is written by hand."""
    paths = [LAB_ROOT / name for name in RECORD_PATHS if (LAB_ROOT / name).exists()]
    changed = git_out(LAB_ROOT, "status", "--porcelain", "--", *(rel(p) for p in paths))
    if not changed:
        print("[LAB] Nothing to publish: the lab's records have no change.")
        return
    print(changed)
    lab_pull()
    publish(paths, args.message, written_by_hand=True)


# ------------------------------------------------------------------------------------- experiments and tries

class Experiment:
    """An experiment as the lab records it: its lab folder and what `results.json` says."""

    def __init__(self, folder: Path):
        self.folder = folder
        self.name = folder.name
        self.short = folder.parent.name
        self.meta = json.loads((folder / "results.json").read_text(encoding="utf-8"))
        self.repo = self.meta.get("experiment_repo", "")
        self.clone = CLONES_DIR / self.repo
        self.start_branch = f"{self.name}/{START_TRY}"
        self.notes = f"{NOTES_DIR}/{self.name}"
        self.tries_path = folder / "tries.md"
        self.steps_path = folder / "lab-steps.md"

    def branch(self, try_name: str) -> str:
        return f"{self.name}/{try_name}"

    def worktree(self, try_name: str) -> Path:
        return WORKTREES_DIR / self.short / self.name / try_name

    def is_open(self) -> bool:
        return self.meta.get("verdict", OPEN) == OPEN

    def save_meta(self) -> None:
        (self.folder / "results.json").write_text(json.dumps(self.meta, indent=2) + "\n", encoding="utf-8")

    def need_clone(self) -> None:
        if not (self.clone / ".git").exists():
            fail(f"Experiment repo '{self.repo}' is not cloned here. Run: uv run scripts/lab.py sync-repos --repo {self.repo}")

    # The map of tries: one line per try in tries.md -> | `<try branch>` | <status> | <comment> |
    ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|\s*$")

    def tries(self) -> list:
        """[{try, branch, status, into, comment}], in the order of the map."""
        rows = []
        if not self.tries_path.exists():
            return rows
        for line in strip_comments(self.tries_path.read_text(encoding="utf-8")).splitlines():
            match = self.ROW_RE.match(line)
            if not match or not match.group(1).startswith(f"{self.name}/"):
                continue
            status, _, into = (part.strip() for part in match.group(2).partition("→"))
            rows.append({"try": match.group(1).split("/", 1)[1], "branch": match.group(1),
                         "status": status, "into": into, "comment": match.group(3)})
        return rows

    def try_row(self, try_name: str) -> dict | None:
        return next((row for row in self.tries() if row["try"] == try_name), None)

    def write_try_row(self, try_name: str, status: str, into: str, comment: str) -> None:
        """Add the try's line to the map, or replace the line it has."""
        cell = f"{status} → {into}" if into else status
        row = f"| `{self.branch(try_name)}` | {cell} | {comment} |"
        lines = self.tries_path.read_text(encoding="utf-8").splitlines()
        own = next((i for i, line in enumerate(lines)
                    if (m := self.ROW_RE.match(line)) and m.group(1) == self.branch(try_name)), None)
        if own is not None:
            lines[own] = row
        else:
            table = [i for i, line in enumerate(lines) if line.startswith("|")]
            lines.insert(table[-1] + 1 if table else len(lines), row)
        self.tries_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Lab step records: entries of lab-steps.md headed -> ## `<try name>` · Lab step <n> · <date> · commit `<sha>`
    STEP_RE = re.compile(r"^## `?([^`·\n]+?)`? · Lab step (\d+) · (\S+) · commit `?([0-9a-f]{4,40})`?", re.MULTILINE)

    def lab_steps(self, try_name: str) -> list:
        """[{n, date, commit, read_up_to}] for one try, oldest first."""
        if not self.steps_path.exists():
            return []
        text = strip_comments(self.steps_path.read_text(encoding="utf-8"))
        marks = list(self.STEP_RE.finditer(text))
        steps = []
        for i, mark in enumerate(marks):
            if mark.group(1) != try_name:
                continue
            body = text[mark.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
            read = re.search(r"\*\*Notes read up to:\*\*\s*`([0-9a-f]+)`", body)
            steps.append({"n": int(mark.group(2)), "date": mark.group(3), "commit": mark.group(4),
                          "read_up_to": read.group(1) if read else mark.group(4)})
        return steps


def all_experiments() -> list:
    if not EXPS_DIR.exists():
        return []
    return [Experiment(p.parent) for p in sorted(EXPS_DIR.glob("*/*/results.json")) if EXP_NAME_RE.match(p.parent.name)]


def find_experiment(exp: str) -> Experiment:
    """An experiment by its id ('02') or its full name ('02-probes'). Stops with one line when there is none."""
    exp_id = exp[:2].lower()
    if not re.match(r"^[0-9a-f]{2}$", exp_id) or (len(exp) > 2 and not EXP_NAME_RE.match(exp)):
        fail(f"'{exp}' is not an experiment: give the two hex digits of its id (e.g. 02) or its full name (e.g. 02-probes).")
    found = [e for e in all_experiments() if e.name.startswith(f"{exp_id}-")]
    if len(found) != 1 or (len(exp) > 2 and exp != found[0].name):
        known = ", ".join(e.name for e in all_experiments()) or "none"
        hint = f"Id '{exp_id}' belongs to '{found[0].name}'." if len(found) == 1 else (
            f"Id '{exp_id}' is used by {len(found)} lab folders: {', '.join(e.name for e in found)}." if found else f"Experiments here: {known}.")
        fail(f"No experiment '{exp}' in {rel(EXPS_DIR)}/. {hint} An experiment opened by another session is here only after "
             "this checkout of the lab pulled the lab's default branch.")
    return found[0]


def need_try(exp: Experiment, try_name: str, live: bool = False) -> dict:
    row = exp.try_row(try_name)
    if row is None:
        known = ", ".join(r["try"] for r in exp.tries()) or "none"
        fail(f"'{try_name}' is not a try of {exp.name}: it has no line in {rel(exp.tries_path)}. Tries on the map: {known}. "
             "A try is opened with `new-try`.")
    if live and row["status"] != "live":
        fail(f"Try '{try_name}' of {exp.name} is not live (the map says: {row['status']}"
             + (f" → {row['into']}" if row["into"] else "") + "). A try that ended is not worked again.")
    return row


def name_problem(name: str, what: str) -> str | None:
    if not SEGMENT_RE.match(name):
        return f"{what} '{name}' must be lowercase words and digits joined by hyphens, in one segment (no '/')."
    if len(name) > MAX_NAME_LEN:
        return f"{what} '{name}' is longer than {MAX_NAME_LEN} characters."
    return None


def comment_problem(comment: str) -> str | None:
    if len(comment) > MAX_COMMENT:
        return f"The comment is {len(comment)} characters; the map takes at most {MAX_COMMENT}. What is longer belongs in the brief."
    if "|" in comment or "\n" in comment:
        return "The comment is one cell of a table: no '|' and no line break."
    if not comment.strip():
        return "The comment is empty. Say in a few words what the try tries, or how it ended."
    return None


def read_log(exp: Experiment, ref: str) -> str:
    """The try log as it is at a ref of the experiment repo, without the template's commented examples."""
    return strip_comments(git(exp.clone, "show", f"{ref}:{exp.notes}/log.md").stdout)


def signal_of(log_text: str) -> str:
    found = re.findall(r"^\* \*\*Signal:\*\*\s*`?([a-z]+)`?\s*$", log_text, flags=re.MULTILINE)
    return found[-1] if found and found[-1] in SIGNALS else "—"


def log_entries(log_text: str) -> list:
    """The entries of a log: [(heading, body)]."""
    parts = re.split(r"(?m)^(?=## )", log_text)
    return [(p.splitlines()[0][3:].strip(), "\n".join(p.splitlines()[1:]).strip()) for p in parts if p.startswith("## ")]


def notes_to_lab(body: str) -> str:
    """The `For the lab` item of a log entry with its sub-lines, or '' when it says None."""
    lines, out, inside = body.splitlines(), [], False
    for line in lines:
        if line.startswith("* **For the lab:**"):
            inside = True
            out.append(line[len("* **For the lab:**"):].strip())
        elif inside and line.startswith("* **"):
            break
        elif inside:
            out.append(line.rstrip())
    text = "\n".join(l for l in out if l.strip())
    return "" if re.fullmatch(r"\[?[Nn]one\.?\]?", text.strip() or "none") else text


# --------------------------------------------------------------------------------------------- the journal

def set_matrix_row(exp_name: str, cells: list) -> bool:
    """Write an experiment's row in the journal's matrix: replace its row, or add one at the end of the table."""
    if not JOURNAL_PATH.exists():
        return False
    lines = JOURNAL_PATH.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("## ") and MATRIX_HEADING in l), None)
    if start is None:
        return False
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    row = "| " + " | ".join(cells) + " |"
    own = next((i for i in range(start, end) if lines[i].startswith(f"| `{exp_name}`")), None)
    if own is not None:
        lines[own] = row
    else:
        table = [i for i in range(start, end) if lines[i].startswith("|")]
        lines.insert(table[-1] + 1 if table else end, row)
    JOURNAL_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def matrix_cells(exp: Experiment, closed: str = "", delta: str = "", verdict: str = OPEN, kept: str = "", takeaway: str = "") -> list:
    meta = exp.meta
    base = f"`{meta.get('base_branch')}` @ `{meta.get('base_commit')}`" if meta.get("base_commit") else "empty repo"
    return [f"`{exp.name}`", meta.get("opened") or "", closed, f"`{exp.repo}`", base, meta.get("title") or exp.name,
            delta, f"**{verdict}**", f"`{kept}`" if kept and kept != "none" else kept, takeaway]


# ------------------------------------------------------------------------------------- repos and system pages

def system_page_of(repo: str) -> Path | None:
    systems = CORTEX_DIR / "systems"
    pages = [p for p in sorted(systems.glob("*.md")) if not p.name.startswith("_")] if systems.exists() else []
    header = re.compile(rf"^>\s*Repo:\s*{re.escape(repo)}(\s|\||$)", re.MULTILINE)
    return next((p for p in pages if p.stem == repo or header.search(p.read_text(encoding="utf-8"))), None)


def note_missing_system_page(repo: str) -> None:
    if system_page_of(repo) is None:
        print(f"[NOTE] Experiment repo '{repo}' has no system page yet (cortex/systems/{repo}.md). Write it from "
              "cortex/systems/_TEMPLATE.md before any experiment code; the template says what to do when the repo is new or empty.")


def cmd_init(_args: argparse.Namespace) -> None:
    for folder in (CLONES_DIR, WORKTREES_DIR, EXPS_DIR, *(CORTEX_DIR / layer for layer in ("claims", "topics", "tensions", "systems", "sources/text"))):
        folder.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Lab workspace ready at {LAB_ROOT}")
    print(f"     Clones of experiment repos: {rel(CLONES_DIR)}/   Local worktrees: {rel(WORKTREES_DIR)}/")


def cmd_sync_repos(args: argparse.Namespace) -> None:
    repos = parse_repos_yaml()
    if not repos:
        print("[WARN] No experiment repos in repos.yaml")
        return
    if args.repo and args.repo not in repos:
        fail(f"'{args.repo}' is not in repos.yaml. Repos there: {', '.join(repos)}.")
    CLONES_DIR.mkdir(parents=True, exist_ok=True)
    for name, cfg in repos.items():
        if args.repo and args.repo != name:
            continue
        clone, url = CLONES_DIR / name, cfg.get("url", "")
        if url.startswith(("./", "../")):
            url = str((LAB_ROOT / url).resolve())   # a relative path in repos.yaml is relative to the lab root
        if not SHORT_NAME_RE.match(cfg.get("short_name", "")):
            print(f"[WARN] {name} has no valid `short_name` in repos.yaml (1-12 lowercase letters or digits). `new-exp` needs it.")
        if (clone / ".git").exists():
            current = git_out(clone, "remote", "get-url", "origin")
            if url and "your-org/" not in url and current != url:
                print(f"[SYNC] origin of {name} changed: {current} -> {url}")
                git(clone, "remote", "set-url", "origin", url, check=True)
            print(f"[SYNC] Fetching {name}")
            fetch(clone)
            # The clone is never edited (tries are worked in worktrees), so its default branch only fast-forwards.
            branch = cfg.get("default_branch", "main")
            if ref_exists(clone, f"origin/{branch}"):
                git(clone, "checkout", "-q", branch)
                git(clone, "merge", "--ff-only", "-q", f"origin/{branch}")
        elif not url or "your-org/" in url:
            print(f"[SKIP] {name} has a placeholder url. Set it in repos.yaml.")
            continue
        else:
            print(f"[CLONE] {name} <- {url}")
            subprocess.run(["git", "clone", "-q", url, str(clone)], check=False)
        note_missing_system_page(name)


def cmd_check_drift(_args: argparse.Namespace) -> None:
    """Which system pages describe code that changed since their Fingerprint. Reads headers only."""
    fp_re = re.compile(r"^>\s*Repo:\s*(\S+)\s*\|\s*Fingerprint:\s*git:(\S+)", re.MULTILINE)
    mon_re = re.compile(r"^>\s*Monitored:\s*(.+)$", re.MULTILINE)
    branch_re = re.compile(r"^>\s*Branch:\s*(\S+)", re.MULTILINE)   # the kept try branch the page describes
    checked = drifted = 0
    for page in sorted(CORTEX_DIR.rglob("*.md")):
        if page.name.startswith("_"):
            continue
        text = page.read_text(encoding="utf-8")
        fp = fp_re.search(text)
        if not fp:
            continue
        checked += 1
        repo, sha = fp.group(1), fp.group(2)
        clone = CLONES_DIR / repo
        if not (clone / ".git").exists():
            print(f"  [NOT CLONED] {rel(page)}: experiment repo '{repo}' is not in {rel(CLONES_DIR)}/ (run sync-repos)")
            continue
        if sha == "HEAD":
            print(f"  [UNPINNED]   {rel(page)}: Fingerprint is git:HEAD; pin it to a commit")
            continue
        ref, branch = "HEAD", branch_re.search(text)
        if branch:
            ref = remote_or_local(clone, branch.group(1)) or branch.group(1)
        monitored = [p.strip() for p in mon_re.search(text).group(1).split(",")] if mon_re.search(text) else []
        diff = git(clone, "diff", "--name-only", sha, ref, "--", *monitored)
        changed = [line for line in diff.stdout.splitlines() if line.strip()]
        if diff.returncode != 0:
            print(f"  [WARN]       {rel(page)}: could not compare {sha}..{ref} in {repo}")
        elif changed:
            drifted += 1
            print(f"  [DRIFTED]    {rel(page)}: changed since {sha}: {', '.join(changed)}")
        else:
            print(f"  [FRESH]      {rel(page)}: no change in the monitored paths since {sha}")
    print(f"{checked} system page(s) with a Fingerprint checked, {drifted} drifted.")


# ----------------------------------------------------------------------------------------------- context pack

PACK_LIMITS = {"purpose": 3000, "gap_map": 4000, "journal_section": 6000, "index": 4000}
PACK_CLOSED_ROWS = 12   # most recent closed experiments shown from the matrix; open ones are always shown


def clip(text: str, limit: int, where: str, cuts: list) -> str:
    """`text`, or its first lines up to about `limit` characters and a line that says what was left out and where it is."""
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
    out = []
    for part in re.split(r"(?m)^(?=### )", embed(text)):
        heading = part.splitlines()[0].lstrip("# ") if part.startswith("### ") else ""
        where = f"`JOURNAL.md` → {heading}" if heading else "`JOURNAL.md`"
        if MATRIX_HEADING in heading:
            lines = part.rstrip().splitlines()
            closed = [i for i, l in enumerate(lines) if re.match(r"^\| `[0-9a-f]{2}-", l) and f"**{OPEN}**" not in l]
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
    """Compile cortex/query_pack.md: the purpose, the gap map, the journal and the cortex index in one file."""
    cuts = []
    sections = [f"# Context Pack (`query_pack.md`)\n> Compiled on `{now_iso()}` by `scripts/lab.py context-pack`, for orientation before choosing "
                "a direction. It is a way in, not the knowledge: follow it to the topic pages and the claims. A part that did not fit ends "
                "with a line marked **[CUT]** that names the file to open."]

    def whole_file(title: str, path: Path, limit: int) -> None:
        if path.exists():
            sections.append(f"## {title} (`{rel(path)}`)\n" + clip(embed(path.read_text(encoding="utf-8")), limit, f"`{rel(path)}`", cuts))

    whole_file("1. Purpose", CORTEX_DIR / "purpose.md", PACK_LIMITS["purpose"])
    whole_file("2. The Field: Map of the Cortex", CORTEX_DIR / "index.md", PACK_LIMITS["index"])
    whole_file("3. Gap Map", CORTEX_DIR / "gap_map.md", PACK_LIMITS["gap_map"])
    if JOURNAL_PATH.exists():
        sections.append("## 4. Journal: the Path of the Research (`JOURNAL.md`)\n" + journal_for_pack(JOURNAL_PATH.read_text(encoding="utf-8"), cuts))
    sections.append(
        "## Reminders\n"
        "* **Cross the idea with what the lab knows:** the topic pages and tensions of the cortex (knowledge of the field, from any source), "
        "the open gaps, and the journal (Sparks, open experiments, the Banlist, earlier postmortems).\n"
        "* **Read around the idea, and add what was read** (`cortex add`). The cortex grows at any time, not only from experiments.\n"
        "* **Same Experiment Language:** the idea goes in at an extension point of `EXPERIMENT_LANGUAGE.md` and uses the shared components.\n"
        "* **The loop itself** is in the `experiment-lab-loop` skill."
    )
    out_path = CORTEX_DIR / "query_pack.md"
    out_text = "\n\n".join(sections) + "\n"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"[OK] {rel(out_path)} written ({len(out_text)} characters)")
    if cuts:
        print("[CUT] Not everything fits; each cut is marked in the pack. Left out: " + "; ".join(cuts))


# ------------------------------------------------------------------------------------------------- new-exp

def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def write_lab_kit(worktree: Path, values: dict) -> list:
    """The lab kit on a start branch: the try AGENTS.md from start-branch/, pointers to it, and the lab's skills.

    It replaces what the base holds at the same paths, and returns one note per thing of the repo's own it replaced.
    """
    notes = []
    agents_src, agents_dst = START_BRANCH_DIR / "AGENTS.md", worktree / "AGENTS.md"
    if agents_dst.exists() and "Lab kit of" not in agents_dst.read_text(encoding="utf-8")[:300]:
        notes.append("The base had its own AGENTS.md at the root; the lab kit's AGENTS.md replaced it on this branch. "
                     "If it held rules of the repo, move them into EXPERIMENT_LANGUAGE.md.")
    text = fill(agents_src.read_text(encoding="utf-8"), values)
    if "{{FILL:" in text:
        notes.append(f"{rel(agents_src)} still has {{{{FILL: ...}}}} slots, and they were copied to the start branch as they are. "
                     "Fill them in the lab (and on this start branch before it is pushed).")
    agents_dst.write_text(text, encoding="utf-8")
    for pointer in POINTER_FILES:
        target = worktree / pointer
        if target.exists() and target.read_text(encoding="utf-8").strip() != "@AGENTS.md":
            notes.append(f"The base had its own {pointer}; it now only points to AGENTS.md. Move what it held into EXPERIMENT_LANGUAGE.md.")
        target.write_text("@AGENTS.md\n", encoding="utf-8")
    skills_src, skills_dst, links = LAB_ROOT / ".agents" / "skills", worktree / ".agents" / "skills", worktree / ".claude" / "skills"
    if not skills_src.exists():
        notes.append("The lab has no .agents/skills/, so the start branch carries no skills.")
        return notes
    theirs = sorted(p.name for p in skills_dst.iterdir()) if skills_dst.is_dir() and not skills_dst.is_symlink() else []
    ours = {p.name for p in skills_src.iterdir()}
    if lost := [name for name in theirs if name not in ours]:
        notes.append(f"The base had skills of its own that the lab does not have ({', '.join(lost)}); the lab kit replaced "
                     ".agents/skills/, so they are not on this branch. Add them to the lab if tries need them.")
    for stale in (skills_dst, links):   # the kit is exactly the lab's skills as they are now
        remove_path(stale)
    shutil.copytree(skills_src, skills_dst, symlinks=False, ignore=shutil.ignore_patterns("__pycache__"))
    links.parent.mkdir(parents=True, exist_ok=True)
    links.mkdir()
    for skill in sorted(p for p in skills_dst.iterdir() if p.is_dir()):
        (links / skill.name).symlink_to(Path("../../.agents/skills") / skill.name)
    return notes


def create_start_branch(exp: "Experiment") -> None:
    """The start branch of a recorded experiment, in a local worktree: the experiment template, written this once.

    Called by `new-exp` after the lab's record is published, and by `mount --try main` when the record exists and the
    branch does not (the earlier `new-exp` stopped half way, or its worktree was lost before the branch was pushed).
    """
    meta, clone, name, start_branch = exp.meta, exp.clone, exp.name, exp.start_branch
    base_branch, base_sha = meta.get("base_branch") or "", meta.get("base_commit") or ""
    worktree = exp.worktree(START_TRY)
    worktree.parent.mkdir(parents=True, exist_ok=True)
    if base_sha:
        git(clone, "worktree", "add", "-q", "--no-track", "-b", start_branch, str(worktree), base_sha, check=True)
    else:   # an empty experiment repo: the start branch is its first branch
        git(clone, "worktree", "add", "-q", "--orphan", "-b", start_branch, str(worktree), check=True)
    values = {"<experiment name>": name, "<experiment repo>": exp.repo, "<title>": meta.get("title") or name,
              "<base-branch>": base_branch or "none: the repo was empty", "<base-sha>": base_sha or "no commit",
              "<lab-sha>": git_out(LAB_ROOT, "rev-parse", "--short", "HEAD") or "unknown", "<date>": meta.get("opened") or today()}
    kit_notes = write_lab_kit(worktree, values)
    notes_dir = worktree / NOTES_DIR / name
    notes_dir.parent.mkdir(parents=True, exist_ok=True)
    remove_path(notes_dir)
    shutil.copytree(START_BRANCH_DIR / NOTES_DIR, notes_dir)
    for md in notes_dir.glob("*.md"):
        md.write_text(fill(md.read_text(encoding="utf-8"), values), encoding="utf-8")

    print(f"[START BRANCH] {start_branch}, from " + (f"{base_branch} @ {base_sha}" if base_sha else "nothing (the repo is empty)")
          + f", in {rel(worktree)}/ (nothing committed yet)")
    print(f"               On it: the lab kit (AGENTS.md, .agents/skills/) and {NOTES_DIR}/{name}/ (plan.md, log.md)")
    for note in kit_notes:
        print(f"[NOTE] {note}")
    language, form = worktree / "EXPERIMENT_LANGUAGE.md", START_BRANCH_DIR / "EXPERIMENT_LANGUAGE.md"
    if not language.exists():
        if form.exists():
            language.write_text(fill(form.read_text(encoding="utf-8"), values), encoding="utf-8")
        print("[NOTE] The base has no EXPERIMENT_LANGUAGE.md" + ("; its form is now on the start branch" if form.exists() else "")
              + ". The first job of this experiment is to connect the pipeline and write it.")
    note_missing_system_page(exp.repo)
    print(f"[NEXT] Write the first plan in {rel(notes_dir)}/plan.md (leave `This Try` empty), then commit and push the start branch:")
    print(f"         git -C {rel(worktree)} add -A && git -C {rel(worktree)} commit -m 'Open {name}: lab kit and first plan'")
    print(f"         git -C {rel(worktree)} push -u origin {start_branch}")
    print(f"       After that the start branch is not touched again. Open tries with: new-try --exp {name[:2]} ...")


def cmd_new_exp(args: argparse.Namespace) -> None:
    repos = parse_repos_yaml()
    if args.repo not in repos:
        fail(f"'{args.repo}' is not in repos.yaml. Repos there: {', '.join(repos) or 'none'}.")
    cfg = repos[args.repo]
    short = cfg.get("short_name", "")
    if not SHORT_NAME_RE.match(short):
        fail(f"Repo '{args.repo}' needs a `short_name` in repos.yaml (1-12 lowercase letters or digits, no hyphen).")
    if problem := name_problem(args.name, "The idea"):
        fail(problem)
    for needed in (START_BRANCH_DIR / "AGENTS.md", START_BRANCH_DIR / NOTES_DIR / "plan.md", LAB_FOLDER_TEMPLATE / "results.json"):
        if not needed.exists():
            fail(f"The lab has no {rel(needed)}: the templates an experiment is opened from are missing.")
    clone = CLONES_DIR / args.repo
    if not (clone / ".git").exists():
        fail(f"Experiment repo '{args.repo}' is not cloned here. Run: uv run scripts/lab.py sync-repos --repo {args.repo}")

    begin_record()
    used = {e.name[:2] for e in all_experiments()}
    exp_id = (args.id or "").lower()
    if exp_id and not re.match(r"^[0-9a-f]{2}$", exp_id):
        fail(f"--id takes two hex digits (e.g. 0a), not '{args.id}'.")
    if exp_id in used:
        fail(f"Experiment id '{exp_id}' is taken by {next(e.name for e in all_experiments() if e.name.startswith(exp_id + '-'))}.")
    if not exp_id:
        nxt = max((int(i, 16) for i in used), default=-1) + 1
        if nxt > 0xFF:
            fail("All 256 experiment ids are used.")
        exp_id = f"{nxt:02x}"
    name = f"{exp_id}-{args.name}"

    fetch(clone)
    base_branch = args.base or cfg.get("default_branch", "main")
    base_ref = remote_or_local(clone, base_branch)
    empty_repo = not git_out(clone, "for-each-ref", "--count=1", "refs/heads", "refs/remotes")
    if base_ref is None and not (empty_repo and not args.base):
        fail(f"No branch '{base_branch}' in {args.repo}. A base is the repo's default branch, a start branch or a pushed try branch.")
    start_branch = f"{name}/{START_TRY}"
    if remote_or_local(clone, start_branch):
        fail(f"{args.repo} already has a branch {start_branch}, and the lab has no experiment with id {exp_id}. Pass a free id with --id.")
    base_sha = git_out(clone, "rev-parse", "--short", base_ref) if base_ref else ""
    if not base_ref:
        base_branch = ""
    title = args.title or args.name.replace("-", " ")
    if "|" in title or "\n" in title:
        fail("--title is one cell of the journal's matrix: no '|' and no line break.")

    # 1. The lab's record, published first: it reserves the id and lets any other session find the experiment.
    folder = EXPS_DIR / short / name
    folder.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(LAB_FOLDER_TEMPLATE, folder)
    lab_values = {"<experiment name>": name, "<experiment repo>": args.repo, "<title>": title}
    for md in folder.glob("*.md"):
        md.write_text(fill(md.read_text(encoding="utf-8"), lab_values), encoding="utf-8")
    meta = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    meta.update(experiment_name=name, title=title, experiment_repo=args.repo, repo_short_name=short, base_branch=base_branch,
                base_commit=base_sha, start_branch=start_branch, opened=today(), verdict=OPEN, kept_try=None, closed=None)
    (folder / "results.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    exp = Experiment(folder)
    in_matrix = set_matrix_row(name, matrix_cells(exp))
    log_path = append_cortex_log("new-exp", name, f"Opened on {args.repo}, from " + (f"{base_branch} @ {base_sha}" if base_sha else "an empty repo") + f" ({title})")

    def id_taken() -> str | None:
        twins = [e.name for e in all_experiments() if e.name.startswith(f"{exp_id}-")]
        return f"Id '{exp_id}' was taken meanwhile by {', '.join(t for t in twins if t != name)}. Nothing was created; run new-exp again." if len(twins) > 1 else None

    publish([folder, JOURNAL_PATH if in_matrix else None, log_path], f"Open experiment {name} on {args.repo}", recheck=id_taken)

    print(f"[EXPERIMENT] {name}   (id {exp_id}; lab folder {rel(folder)}/" + (", row OPEN in the journal's matrix)" if in_matrix else ")"))
    if not in_matrix:
        print(f"[WARN] JOURNAL.md has no '{MATRIX_HEADING}' section, so this experiment is not listed there.")
    # 2. The start branch. If this step stops, the record stays: `mount --exp <id> --try main` creates the branch again.
    create_start_branch(exp)


# ------------------------------------------------------------------------------------------------- new-try

def write_brief(plan_path: Path, try_branch: str, base_branch: str, base_sha: str, brief: str) -> None:
    """Put the base and the brief in the plan's `This Try` section, in place of what was there."""
    text = plan_path.read_text(encoding="utf-8")
    section = (f"* **Try:** `{try_branch}`\n* **Base:** `{base_branch}` at `{base_sha}`\n* **Opened:** {today()}\n\n"
               f"**Brief**\n\n{brief.strip()}\n\n"
               "**How this try will do it** (written by whoever works the try: the realisation, and its own open questions)\n")
    match = re.search(r"(?mi)^(## .*This Try.*)$", text)
    if not match:
        text = text.rstrip() + "\n\n## This Try\n" + section
    else:
        following = re.search(r"(?m)^## ", text[match.end():])
        end = match.end() + following.start() if following else len(text)
        text = text[:match.end()] + "\n" + section + ("\n" + text[end:] if following else "")
    plan_path.write_text(text, encoding="utf-8")


def cmd_new_try(args: argparse.Namespace) -> None:
    begin_record()
    exp = find_experiment(args.exp)
    if not exp.is_open():
        fail(f"{exp.name} is closed ({exp.meta.get('verdict')}). A new attempt at a closed experiment is a new experiment.")
    if problem := name_problem(args.name, "The try name"):
        fail(problem)
    if args.name == START_TRY:
        fail(f"'{START_TRY}' is the start branch, not a try.")
    exp.need_clone()
    fetch(exp.clone)
    # A line that is live with no branch anywhere is a `new-try` that stopped half way: this run finishes it.
    repair = (row := exp.try_row(args.name)) is not None and row["status"] == "live" and remote_or_local(exp.clone, exp.branch(args.name)) is None
    if row and not repair:
        fail(f"{exp.name} already has a try '{args.name}' on its map. A try name is used once, also after the try ended.")
    if problem := comment_problem(args.comment):
        fail(problem)
    brief = Path(args.brief_file).read_text(encoding="utf-8") if args.brief_file else args.brief
    if not brief or not brief.strip():
        fail("The brief is empty. Say what to try and what makes this try different, whether it competes or cooperates with "
             "which tries, how far to go, and when to stop and flag.")

    base_branch = args.base or exp.start_branch
    if "/" not in base_branch:
        need_try(exp, base_branch)
        base_branch = exp.branch(base_branch)   # a try name of this experiment
    pushed = has_origin(exp.clone)
    base_ref = f"origin/{base_branch}" if pushed and ref_exists(exp.clone, f"origin/{base_branch}") else None
    if base_ref is None and not pushed and ref_exists(exp.clone, base_branch):
        base_ref = base_branch
    if base_ref is None:
        what = "The start branch" if base_branch == exp.start_branch else f"The base '{base_branch}'"
        fail(f"{what} is not pushed to {exp.repo}. " + ("Write the first plan, commit and push the start branch first "
             f"(it is in {rel(exp.worktree(START_TRY))}/)." if base_branch == exp.start_branch else "A try starts from a pushed branch."))
    plan_at_base = f"{base_ref}:{exp.notes}/plan.md"
    if git(exp.clone, "cat-file", "-e", plan_at_base).returncode != 0:
        fail(f"'{base_branch}' holds no {exp.notes}/plan.md, so it is not a branch of {exp.name}. A try starts from its "
             "experiment's start branch or from another try of the same experiment.")
    try_branch = exp.branch(args.name)
    if remote_or_local(exp.clone, try_branch):
        fail(f"{exp.repo} already has a branch {try_branch} that the map does not know. Choose another try name.")
    base_sha = git_out(exp.clone, "rev-parse", "--short", base_ref)

    # 1. The line in the map, published first: it reserves the try name.
    if repair:
        print(f"[LAB] The map already has `{try_branch}` as live and no such branch exists: creating the branch now.")
    exp.write_try_row(args.name, "live", "", args.comment.strip())

    def name_taken() -> str | None:
        count = sum(1 for row in exp.tries() if row["try"] == args.name)
        return f"Try name '{args.name}' was taken meanwhile. Nothing was created; choose another name." if count > 1 else None

    publish([exp.tries_path], f"Open try {try_branch}: {args.comment.strip()}", recheck=name_taken)

    # 2. The try branch: from the base, with the brief in the plan. The lab kit and the notes come with the base.
    worktree = exp.worktree(args.name)
    worktree.parent.mkdir(parents=True, exist_ok=True)
    git(exp.clone, "worktree", "prune")
    git(exp.clone, "worktree", "add", "-q", "--no-track", "-b", try_branch, str(worktree), base_ref, check=True)
    plan_path = worktree / exp.notes / "plan.md"
    write_brief(plan_path, try_branch, base_branch, base_sha, brief)
    git(worktree, "add", "--", f"{exp.notes}/plan.md", check=True)
    git(worktree, "commit", "-q", "-m", f"Open try {try_branch}: base and brief", check=True)
    if pushed and (push := git(worktree, "push", "-q", "-u", "origin", try_branch)).returncode != 0:
        fail(f"The try is on the map and its branch is in {rel(worktree)}/, but the push to {exp.repo} was refused:\n"
             f"{(push.stderr or push.stdout).strip()}\nWhen pushing works: git -C {rel(worktree)} push -u origin {try_branch}")

    print(f"[TRY] {try_branch}   live on the map ({rel(exp.tries_path)})")
    print(f"      From {base_branch} @ {base_sha}; the brief is in {exp.notes}/plan.md → This Try"
          + ("; pushed." if pushed else "; not pushed: the experiment repo has no remote."))
    print(f"[NEXT] Whoever works it starts on {try_branch} and pushes to it: here in {rel(worktree)}/, "
          "or a try session opened on that branch (the loop skill's references/claude-code-cloud.md).")


# --------------------------------------------------------------------------------- mount, tries, inbox, set-try

def cmd_mount(args: argparse.Namespace) -> None:
    """The local worktree of a try, from its pushed branch. `--try main` mounts the start branch, to write the first plan."""
    exp = find_experiment(args.exp)
    if args.try_name != START_TRY:
        need_try(exp, args.try_name)
    exp.need_clone()
    worktree = exp.worktree(args.try_name)
    if worktree.exists():
        print(f"[OK] Already mounted: {rel(worktree)}/")
        return
    fetch(exp.clone)
    branch = exp.branch(args.try_name)
    git(exp.clone, "worktree", "prune")
    if remote_or_local(exp.clone, branch) is None:
        if args.try_name == START_TRY:
            print(f"[LAB] {exp.name} is recorded and {exp.repo} has no branch {branch}: creating the start branch now.")
            create_start_branch(exp)
            return
        fail(f"The map has the try, but {exp.repo} has no branch {branch}. It was not pushed, or it was deleted. "
             "If `new-try` stopped half way, run the same `new-try` again: it creates the branch.")
    worktree.parent.mkdir(parents=True, exist_ok=True)
    if ref_exists(exp.clone, branch):
        git(exp.clone, "worktree", "add", "-q", str(worktree), branch, check=True)
        if ref_exists(exp.clone, f"origin/{branch}"):
            git(worktree, "branch", "-q", "--set-upstream-to", f"origin/{branch}")
            git(worktree, "merge", "--ff-only", "-q", f"origin/{branch}")
    else:
        git(exp.clone, "worktree", "add", "-q", "--track", "-b", branch, str(worktree), f"origin/{branch}", check=True)
    print(f"[OK] {branch} mounted at {rel(worktree)}/")


def cmd_tries(args: argparse.Namespace) -> None:
    """Print the map of tries. Status comes from the map; signal and last commit are read from each live try's branch."""
    experiments = [find_experiment(args.exp)] if args.exp else [e for e in all_experiments() if e.is_open()]
    if not experiments:
        print("No open experiment.")
        return
    for exp in experiments:
        cloned = (exp.clone / ".git").exists()
        if cloned:
            fetch(exp.clone)
        rows = exp.tries()
        live = [r for r in rows if r["status"] == "live"]
        state = "open" if exp.is_open() else exp.meta.get("verdict")
        print(f"\n{exp.name}  ({exp.repo}, {state})  {len(live)} live of {len(rows)} tries")
        if not cloned:
            print(f"  [NOTE] {exp.repo} is not cloned here, so signals are not read (sync-repos).")
        table = [("TRY", "STATUS", "SIGNAL", "LAST COMMIT", "LAST LAB STEP", "COMMENT")]
        for row in rows if args.all else live:
            status = row["status"] + (f" → {row['into']}" if row["into"] else "")
            signal = commit = "—"
            if row["status"] == "live" and cloned:
                ref = remote_or_local(exp.clone, row["branch"])
                if ref is None:
                    signal, commit = "BRANCH MISSING", "—"
                else:
                    signal = signal_of(read_log(exp, ref))
                    commit = git_out(exp.clone, "log", "-1", "--format=%cs %h", ref)
                    if has_origin(exp.clone) and not ref.startswith("origin/"):
                        commit += " (not pushed)"
            steps = exp.lab_steps(row["try"])
            last = f"#{steps[-1]['n']} {steps[-1]['date']} @{steps[-1]['commit'][:7]}" if steps else "none"
            table.append((row["try"], status, signal, commit, last, row["comment"]))
        if len(table) == 1:
            print("  (no live try)" if not args.all else "  (no try)")
            continue
        widths = [max(len(r[i]) for r in table) for i in range(5)]
        for r in table:
            print("  " + "  ".join(r[i].ljust(widths[i]) for i in range(5)) + "  " + r[5])
        if not args.all and len(rows) > len(live):
            print(f"  ({len(rows) - len(live)} more ended; --all shows them)")


def cmd_inbox(args: argparse.Namespace) -> None:
    """What a try has to tell the lab: its signal, and the notes to the lab added since its last lab step read the log."""
    exp = find_experiment(args.exp)
    need_try(exp, args.try_name)
    exp.need_clone()
    fetch(exp.clone)
    ref = remote_or_local(exp.clone, exp.branch(args.try_name))
    if ref is None:
        fail(f"{exp.repo} has no branch {exp.branch(args.try_name)}.")
    tip = git_out(exp.clone, "rev-parse", "--short", ref)
    log_now = read_log(exp, ref)
    steps = exp.lab_steps(args.try_name)
    seen = set()
    if steps:
        read_up_to = steps[-1]["read_up_to"]
        if not ref_exists(exp.clone, read_up_to):
            print(f"[WARN] The last lab step read up to {read_up_to}, which is not in the clone; showing all notes.")
        else:
            seen = set(log_entries(read_log(exp, read_up_to)))
    print(f"{exp.branch(args.try_name)} @ {tip}   signal: {signal_of(log_now)}")
    print(f"Last lab step: " + (f"#{steps[-1]['n']} on {steps[-1]['date']}, notes read up to {steps[-1]['read_up_to']}" if steps else "none; every entry is new"))
    new = [(heading, body) for heading, body in log_entries(log_now) if (heading, body) not in seen]
    with_notes = [(heading, notes_to_lab(body)) for heading, body in new]
    print(f"{len(new)} new log entr{'y' if len(new) == 1 else 'ies'}, {sum(1 for _, n in with_notes if n)} with notes to the lab.\n")
    for heading, notes in with_notes:
        print(f"## {heading}")
        print(notes if notes else "  (nothing for the lab)")
        print()
    print(f"Record in the lab step record: **Notes read up to:** `{tip}`")


def cmd_set_try(args: argparse.Namespace) -> None:
    begin_record()
    exp = find_experiment(args.exp)
    row = need_try(exp, args.try_name)
    if not exp.is_open() or row["status"] == "closed":
        fail(f"{exp.name} is closed ({exp.meta.get('verdict')}): its map of tries does not change any more.")
    if args.status is None and args.comment is None and args.into is None:
        fail("Nothing to change: give --status, --into or --comment.")
    status = args.status or row["status"]
    into = args.into if args.into is not None else (row["into"] if args.status is None else "")
    comment = args.comment.strip() if args.comment is not None else row["comment"]
    if args.comment is not None and (problem := comment_problem(args.comment)):
        fail(problem)
    if status == "merged" and not into:
        fail("`merged` names the try that took its code: give --into <try name>.")
    if status == "live" and into:
        fail("A live try is not `into` anything.")
    if into:
        if into == args.try_name:
            fail("A try is not reduced into itself.")
        need_try(exp, into)
    exp.write_try_row(args.try_name, status, into, comment)
    cell = status + (f" → {into}" if into else "")
    publish([exp.tries_path], f"Try {exp.branch(args.try_name)}: {cell}")
    print(f"[OK] {exp.branch(args.try_name)} | {cell} | {comment}")


# ----------------------------------------------------------------------------------------- run and evaluate

def run_env(exp: Experiment, step_dir: Path | None = None) -> dict:
    """The lab's .env, plus LAB_ROOT, EXP_DIR (the experiment's lab folder) and, in an evaluation, STEP_DIR."""
    env = load_env_file()
    env["LAB_ROOT"], env["EXP_DIR"] = str(LAB_ROOT), str(exp.folder)
    if step_dir is not None:
        env["STEP_DIR"] = str(step_dir)
    return env


def cmd_run(args: argparse.Namespace) -> None:
    """Run a command in a try's local worktree. Output is shown as it comes; nothing is recorded."""
    exp = find_experiment(args.exp)
    need_try(exp, args.try_name, live=True)
    worktree = exp.worktree(args.try_name)
    if not worktree.exists():
        fail(f"No local worktree for {exp.branch(args.try_name)}. Run: uv run scripts/lab.py mount --exp {exp.name[:2]} --try {args.try_name}")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        fail("Give the command after `--`, e.g. run --exp 02 --try trl-fix-lr -- 'uv run python -m pkg.check'")
    proc = subprocess.run(command[0] if len(command) == 1 else command, shell=len(command) == 1, cwd=str(worktree), env=run_env(exp), check=False)
    sys.exit(proc.returncode)


def cmd_evaluate(args: argparse.Namespace) -> None:
    """The evaluation of one commit of one try, inside a lab step: patch.diff, and metrics when the repo has an evaluate.py."""
    exp = find_experiment(args.exp)
    need_try(exp, args.try_name)
    exp.need_clone()
    fetch(exp.clone)
    branch = exp.branch(args.try_name)
    target = args.commit or remote_or_local(exp.clone, branch)
    if target is None or not ref_exists(exp.clone, target):
        fail(f"Cannot find {'commit ' + args.commit if args.commit else 'branch ' + branch} in {exp.repo}.")
    commit, short_commit = git_out(exp.clone, "rev-parse", target), git_out(exp.clone, "rev-parse", "--short", target)
    if args.commit and git(exp.clone, "merge-base", "--is-ancestor", commit, remote_or_local(exp.clone, branch) or commit).returncode != 0:
        fail(f"Commit {short_commit} is not on {branch}.")

    eval_source = None
    if args.eval_from:
        eval_source = remote_or_local(exp.clone, args.eval_from) or args.eval_from
        if git(exp.clone, "cat-file", "-e", f"{eval_source}:{EVAL_SCRIPT}").returncode != 0:
            fail(f"No {EVAL_SCRIPT} on '{args.eval_from}'.")
    # One folder per evaluation: the try, the commit and, when the evaluation script is borrowed, the commit it came from.
    suffix = f"-eval-{git_out(exp.clone, 'rev-parse', '--short', eval_source)}" if eval_source else ""
    step_dir = exp.folder / "steps" / f"{args.try_name}-{short_commit}{suffix}"
    step_dir.mkdir(parents=True, exist_ok=True)
    for stale in ("evaluate.log", "metrics.json"):   # a run again on the same commit replaces the earlier files, never mixes with them
        (step_dir / stale).unlink(missing_ok=True)
    base = exp.meta.get("base_commit") or EMPTY_TREE   # an experiment opened on an empty repo has no base commit
    if base != EMPTY_TREE and not ref_exists(exp.clone, base):
        fail(f"The experiment's base commit ({base}) is not in the clone, so the code change cannot be computed.")
    # The try's code change against the experiment's base: without the notes folder and without the lab kit.
    excluded = [f":(exclude,top){path}" for path in (exp.notes, *LAB_KIT)]
    diff = git(exp.clone, "diff", base, commit, "--", ".", *excluded).stdout
    (step_dir / "patch.diff").write_text(diff or "# No code change against the experiment's base\n", encoding="utf-8")

    # A temporary worktree at that commit, so the evaluation never touches a working copy someone works in.
    scratch = WORKTREES_DIR / exp.short / exp.name / f".evaluate-{args.try_name}-{short_commit}"
    if scratch.exists():
        git(exp.clone, "worktree", "remove", "--force", str(scratch))
    scratch.parent.mkdir(parents=True, exist_ok=True)
    git(exp.clone, "worktree", "add", "-q", "--detach", str(scratch), commit, check=True)
    try:
        script = scratch / EVAL_SCRIPT
        if eval_source:
            borrowed = subprocess.run(["git", "-C", str(exp.clone), "show", f"{eval_source}:{EVAL_SCRIPT}"], capture_output=True, check=True)
            script.write_bytes(borrowed.stdout)
        if not script.exists():
            append_cortex_log("evaluate", branch, f"No {EVAL_SCRIPT} in {exp.repo}: patch.diff saved at {short_commit}, no metrics")
            print(f"[OK] {rel(step_dir)}/patch.diff saved for {branch} @ {short_commit}.")
            print(f"     No metrics: {exp.repo} has no {EVAL_SCRIPT} yet. The lab step is recorded with its conclusions and no number.")
            return
        version = git_out(scratch, "hash-object", EVAL_SCRIPT)[:12]
        command = f"uv run {EVAL_SCRIPT}"
        print(f"[EVAL] `{command}` on {branch} @ {short_commit} (timeout {args.timeout}s)")
        try:
            proc = subprocess.run(command, shell=True, cwd=str(scratch), timeout=args.timeout, capture_output=True, text=True, check=False, env=run_env(exp, step_dir))
            stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            text = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
            stdout, stderr, code = text(exc.stdout), text(exc.stderr), None
        (step_dir / "evaluate.log").write_text(
            f"$ {command}\ntry: {branch}\ncommit: {commit}\n{EVAL_SCRIPT} from: {args.eval_from or 'the commit itself'}\n"
            f"exit code: {code if code is not None else f'timeout after {args.timeout}s'}\n\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}", encoding="utf-8")

        metrics = None   # the contract: the last line of stdout is one JSON object of metrics
        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        if lines:
            try:
                parsed = json.loads(lines[-1])
                metrics = parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                pass
        problem = (f"timed out after {args.timeout}s" if code is None else f"exit code {code}" if code != 0
                   else "the last line of stdout is not a JSON object" if metrics is None else None)
        if metrics and metrics.get("eval_version"):
            version += f"+{metrics['eval_version']}"
        if problem:
            append_cortex_log("evaluate", branch, f"Evaluation at {short_commit} failed ({problem}; evaluation version {version})")
            sys.exit(f"[FAIL] {EVAL_SCRIPT}: {problem}. Output in {rel(step_dir)}/evaluate.log; no metrics written. "
                     "A technical failure is not a result: say so in the lab step record.")
        (step_dir / "metrics.json").write_text(json.dumps({
            "experiment": exp.name, "try": args.try_name, "commit": commit, "evaluation_version": version,
            "eval_from": args.eval_from, "metrics": metrics, "timestamp": now_iso()}, indent=2) + "\n", encoding="utf-8")
        append_cortex_log("evaluate", branch, f"Evaluated at {short_commit} (evaluation version {version})")
        print(f"[OK] Metrics: {json.dumps(metrics)}")
        print(f"[OK] Evaluation version: {version}   (two numbers are comparable only when this is the same)")
        print(f"[OK] {rel(step_dir)}/: patch.diff, evaluate.log, metrics.json. Copy the result into the lab step record in {rel(exp.steps_path)}.")
    finally:
        git(exp.clone, "worktree", "remove", "--force", str(scratch))


# ------------------------------------------------------------------------------------------- close and clean

def cmd_record_verdict(args: argparse.Namespace) -> None:
    begin_record()
    exp = find_experiment(args.exp)
    if not exp.is_open():
        fail(f"{exp.name} is already closed ({exp.meta.get('verdict')}, on {exp.meta.get('closed')}). A verdict is recorded once.")
    kept = args.kept
    if kept != "none":
        need_try(exp, kept)
    for cell, what in ((args.summary, "--summary"), (args.metric_delta, "--metric-delta")):
        if "|" in cell or "\n" in cell:
            fail(f"{what} is one cell of the journal's matrix: no '|' and no line break.")
    exp.meta.update(verdict=args.verdict, kept_try=None if kept == "none" else kept, closed=today())
    exp.save_meta()
    closed = [row["try"] for row in exp.tries() if row["status"] == "live"]
    for try_name in closed:
        row = exp.try_row(try_name)
        exp.write_try_row(try_name, "closed", "", row["comment"])
    in_matrix = set_matrix_row(exp.name, matrix_cells(exp, closed=today(), delta=args.metric_delta, verdict=args.verdict,
                                                      kept=exp.branch(kept) if kept != "none" else "none", takeaway=args.summary))
    log_path = append_cortex_log("verdict", exp.name, f"{args.verdict}; kept: {kept}; {args.summary} ({args.metric_delta})")
    publish([exp.folder, JOURNAL_PATH if in_matrix else None, log_path], f"Close experiment {exp.name}: {args.verdict}")
    print(f"[OK] {exp.name}: {args.verdict}, kept: {exp.branch(kept) if kept != 'none' else 'none'}.")
    if closed:
        print(f"     Tries that were still live are now `closed` on the map: {', '.join(closed)}")
    if not in_matrix:
        print(f"[WARN] JOURNAL.md has no '{MATRIX_HEADING}' section: the verdict is not in the journal.")
    if not (exp.folder / "postmortem.md").exists() or "[HYPOTHESIS_SUPPORTED |" in (exp.folder / "postmortem.md").read_text(encoding="utf-8"):
        print(f"[NEXT] {rel(exp.folder)}/postmortem.md is still the template: write it.")
    if kept != "none":
        print(f"[NEXT] Name the kept try on the system page: `> Branch: {exp.branch(kept)}` in cortex/systems/{exp.repo}.md.")
    print("[NEXT] By hand: settle this experiment's provisional claims, and update Frontier, Sparks and the Banlist.")


def cmd_cleanup_worktree(args: argparse.Namespace) -> None:
    exp = find_experiment(args.exp)
    worktree = exp.worktree(args.try_name)
    if not worktree.exists():
        print(f"[INFO] No worktree at {rel(worktree)}/")
        return
    dirty = git_out(worktree, "status", "--porcelain")
    unpushed = has_origin(exp.clone) and git_out(worktree, "log", "--oneline", f"origin/{exp.branch(args.try_name)}..HEAD") if ref_exists(exp.clone, f"origin/{exp.branch(args.try_name)}") else ""
    if (dirty or unpushed) and not args.force:
        fail(f"{rel(worktree)}/ holds work that is not pushed ({'uncommitted changes' if dirty else 'commits'}). "
             "Commit and push it, or pass --force to throw it away.")
    git(exp.clone, "worktree", "remove", "--force", str(worktree), check=True)
    parent = worktree.parent
    while parent != WORKTREES_DIR and parent.exists() and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent
    print(f"[OK] Removed {rel(worktree)}/. The branch, the line of the map and the lab folder stay.")


# ------------------------------------------------------------------------------------------------------ main

def main() -> None:
    parser = argparse.ArgumentParser(description="The mechanical steps of a research lab. Run from the lab root, on a checkout of the lab's default branch.")
    parser.add_argument("--no-publish", action="store_true",
                        help="Commit the lab's records but do not pull or push them; publish them by hand afterwards")
    sub = parser.add_subparsers(dest="cmd", required=True)
    exp_help, try_help = "Experiment id or full name (02 or 02-probes)", "Try name (e.g. trl-fix-lr)"

    sub.add_parser("init", help="Create .repos/ and the cortex folders in a fresh lab or clone")
    p = sub.add_parser("sync-repos", help="Clone or fetch the experiment repos of repos.yaml into .repos/clones/")
    p.add_argument("--repo", help="Only this repo")
    p = sub.add_parser("publish", help="Commit every change in experiments/, cortex/ and JOURNAL.md and push it to the lab's default branch (after a lab step, a reduce, a cortex edit)")
    p.add_argument("-m", "--message", required=True, help="One line: what changed in the lab's records")
    sub.add_parser("check-drift", help="Report system pages whose monitored code changed since their Fingerprint")
    sub.add_parser("context-pack", help="Compile cortex/query_pack.md: purpose, map of the field, gap map, journal")

    p = sub.add_parser("new-exp", help="Open an experiment: lab folder and journal row (published), then its start branch with the experiment template")
    p.add_argument("--repo", required=True, help="Experiment repo, by its name in repos.yaml")
    p.add_argument("--name", required=True, help="The idea: one segment of lowercase words joined by hyphens (e.g. probes)")
    p.add_argument("--base", help="Branch the experiment starts from: any pushed try branch or start branch (default: the repo's default branch)")
    p.add_argument("--title", help="A readable title (default: the idea)")
    p.add_argument("--id", help="Two hex digits (default: the next free id)")

    p = sub.add_parser("new-try", help="Open a try: its line in the map of tries (published), then its try branch with the brief in the plan")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--name", required=True, help="Try name: one segment of lowercase words joined by hyphens, never 'main'")
    p.add_argument("--comment", required=True, help=f"What the try tries, at most {MAX_COMMENT} characters: the line of the map")
    brief = p.add_mutually_exclusive_group(required=True)
    brief.add_argument("--brief", help="The brief, as text")
    brief.add_argument("--brief-file", help="The brief, from a file")
    p.add_argument("--base", help="Try name or branch the try starts from (default: the start branch)")

    p = sub.add_parser("mount", help="Create the local worktree of a try from its pushed branch (`--try main`: the start branch)")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--try", dest="try_name", required=True, help=try_help)

    p = sub.add_parser("tries", help="Print the map of tries, with each live try's signal and last commit as read from its branch")
    p.add_argument("--exp", help=exp_help + " (default: every open experiment)")
    p.add_argument("--all", action="store_true", help="Also the tries that ended")

    p = sub.add_parser("inbox", help="A try's signal and its notes to the lab added since its last lab step")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--try", dest="try_name", required=True, help=try_help)

    p = sub.add_parser("set-try", help="Change a try's line in the map of tries, and publish")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--try", dest="try_name", required=True, help=try_help)
    p.add_argument("--status", choices=["live", "merged", "dropped"], help="`closed` is set only by record-verdict")
    p.add_argument("--into", help="The try a reduce took it into")
    p.add_argument("--comment", help=f"At most {MAX_COMMENT} characters: while live what it tries, afterwards how it ended")

    p = sub.add_parser("run", help="Run a command in a try's local worktree, with .env, $LAB_ROOT and $EXP_DIR set")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--try", dest="try_name", required=True, help=try_help)
    p.add_argument("command", nargs=argparse.REMAINDER, help="The command, after `--`")

    p = sub.add_parser("evaluate", help=f"In a lab step: save a try's code change and, when the repo has an {EVAL_SCRIPT}, run it on one commit of the try")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--try", dest="try_name", required=True, help=try_help)
    p.add_argument("--commit", help="The commit to evaluate (default: the tip of the try branch as pushed)")
    p.add_argument("--eval-from", help=f"Run the {EVAL_SCRIPT} of this branch on the try's code (after the evaluation changed)")
    p.add_argument("--timeout", type=int, default=3600, help="Seconds before the evaluation is stopped (default 3600)")

    p = sub.add_parser("record-verdict", help="Close an experiment: verdict and kept try, the journal row, live tries set to closed; published")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--verdict", required=True, choices=VERDICTS)
    p.add_argument("--kept", required=True, help="The try later experiments start from, or `none`")
    p.add_argument("--metric-delta", required=True, help="The metric against the baseline, e.g. '+4.2%% F1', or 'no metric'")
    p.add_argument("--summary", required=True, help="One line for the journal's matrix")

    p = sub.add_parser("cleanup-worktree", help="Remove a local worktree; the branch, the map and the lab folder stay")
    p.add_argument("--exp", required=True, help=exp_help)
    p.add_argument("--try", dest="try_name", required=True, help=try_help)
    p.add_argument("--force", action="store_true", help="Also when it holds work that is not pushed")

    args = parser.parse_args()
    global NO_PUBLISH
    NO_PUBLISH = args.no_publish
    {"init": cmd_init, "publish": cmd_publish, "sync-repos": cmd_sync_repos, "check-drift": cmd_check_drift, "context-pack": cmd_context_pack,
     "new-exp": cmd_new_exp, "new-try": cmd_new_try, "mount": cmd_mount, "tries": cmd_tries, "inbox": cmd_inbox,
     "set-try": cmd_set_try, "run": cmd_run, "evaluate": cmd_evaluate, "record-verdict": cmd_record_verdict,
     "cleanup-worktree": cmd_cleanup_worktree}[args.cmd](args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:   # the output was piped into a command that stopped reading (`| head`)
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
