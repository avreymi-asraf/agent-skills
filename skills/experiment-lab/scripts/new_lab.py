#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a research lab repository from this skill's scaffold (assets/lab).

    uv run scripts/new_lab.py <destination> --name "<lab name>" [--target <https-url> [--short-name <x>]]

Copies the scaffold, puts the files that need a dot name or a symlink in place, gives the lab its own
copy of the companion skills found next to this one, and lists the `{{FILL: ...}}` slots that only the
user can answer. With --target it also registers the target repo in repos.yaml, runs `lab.py init` and
`sync-repos`, and starts the target's system page from the template. It never overwrites an existing file,
so it is safe to run again on a lab that is partly built (run it again with --target when the target is
named later). Standard library only.
"""

import argparse
import re
import shutil
import subprocess
from pathlib import Path

SCAFFOLD = Path(__file__).resolve().parent.parent / "assets" / "lab"
# Scaffold path -> path in the lab, for files that cannot keep their real name inside a skill.
RENAMED = {
    "gitignore": ".gitignore",
    "env.example": ".env.example",
    "rejects.md": ".grow-autonomy/rejects.md",
    # Stored under other names so no agent tool mistakes the scaffold for live instructions or a skill.
    "lab-AGENTS.md": "AGENTS.md",
    "loop-skill.md": ".agents/skills/experiment-lab-loop/SKILL.md",
}
# Every skill the lab's own content names (AGENTS.md, the loop skill). A lab must be whole wherever it
# is cloned, so it gets its own copy of each one that is installed next to this skill. When the scaffold
# starts naming another skill, add it here.
COMPANIONS = ("cortex", "grow-autonomy", "code-as-tools", "iterative-deep-researcher")


def register_target(lab: Path, url: str, short_name: str | None) -> str:
    """Put the target in repos.yaml, clone it, and start its system page. Returns the repo's folder name."""
    name = url.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    short = short_name or name.replace("-", "")[:4].lower()
    repos = lab / "repos.yaml"
    text = repos.read_text(encoding="utf-8")
    entry = (f"  - name: {name}\n    url: {url}\n    short_name: {short}\n    default_branch: main\n")
    if url in text:
        print(f"[OK] {name} is already in repos.yaml.")
    else:
        # The scaffold's placeholder entry is replaced; a real entry is kept and this one is added after it.
        text = re.sub(r"  - name: your-repo[^\n]*\n(?:    .*\n)+", "", text)
        repos.write_text(text.rstrip("\n") + "\n\n" + entry, encoding="utf-8")
        print(f"[OK] Registered {name} (short name '{short}') in repos.yaml. Check default_branch there.")
    for command in ("init", "sync-repos"):
        subprocess.run(["uv", "run", "scripts/lab.py", command], cwd=lab, check=False)
    page = lab / "cortex" / "systems" / f"{name}.md"
    clone = lab / ".targets" / "repos" / name
    if not page.exists() and (clone / ".git").exists():
        sha = subprocess.run(["git", "-C", str(clone), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=False).stdout.strip() or "<sha>"
        template = (lab / "cortex" / "systems" / "_TEMPLATE.md").read_text(encoding="utf-8")
        page.write_text(template.replace("<target-repo>", name).replace("git:<sha>", f"git:{sha}"), encoding="utf-8")
        print(f"[OK] Started cortex/systems/{name}.md from the template.")
    return name


def print_remaining(lab: Path, target: str | None) -> None:
    """What is still open after this run. A list, not a gate: the lab is ready when none of it is left."""
    open_items = []
    if target is None and "your-repo" in (lab / "repos.yaml").read_text(encoding="utf-8"):
        open_items.append("No target repo registered. Ask the user for one (a session may not be able to create a "
                          "repository), then run this script again with --target <https-url>.")
    if target:
        open_items.append(f"Read the code of {target} and write its system page (cortex/systems/{target}.md): the "
                          "Experiment Language, or 'Not written yet' for a new or empty target. Add a line for it to cortex/index.md. "
                          "In a cloud session the target must also be attached to the session (add_repo).")
    open_items.append("Fill the slots above from the user's answers; one the user has not answered stays visibly open.")
    open_items.append("Run the check in the skill (Check-a-lab), then commit and push the lab.")
    print("\nStill open before this lab is ready for its first experiment (agent's work unless it says the user's):")
    for item in open_items:
        print(f"  - {item}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("destination", type=Path, help="Folder of the new lab (created if missing)")
    parser.add_argument("--name", required=True, help="Lab name as it appears in AGENTS.md, e.g. 'Retrieval'")
    parser.add_argument("--target", help="HTTPS url of a target repo to register (repos.yaml), clone and give a system page")
    parser.add_argument("--short-name", help="Short name for experiment names (default: first 4 letters of the repo name)")
    args = parser.parse_args()
    lab = args.destination.resolve()

    written, kept = [], []
    for src in sorted(p for p in SCAFFOLD.rglob("*") if p.is_file()):
        rel = src.relative_to(SCAFFOLD).as_posix()
        dst = lab / RENAMED.get(rel, rel)
        if dst.exists():
            kept.append(dst)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if dst.suffix == ".md":
            dst.write_text(dst.read_text(encoding="utf-8").replace("{{FILL: lab name}}", args.name), encoding="utf-8")
        written.append(dst)

    skills_home = SCAFFOLD.parent.parent.parent  # the folder this skill is installed in
    missing = []
    for name in COMPANIONS:
        src, dst = skills_home / name, lab / ".agents" / "skills" / name
        if dst.exists():
            continue
        if (src / "SKILL.md").exists():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            missing.append(name)

    for pointer in ("CLAUDE.md", "GEMINI.md"):  # tools that do not read AGENTS.md by themselves
        if not (lab / pointer).exists():
            (lab / pointer).write_text("@AGENTS.md\n", encoding="utf-8")

    # Claude Code reads .claude/skills/; other agents read .agents/skills/. One copy, one relative link.
    for skill in sorted(p for p in (lab / ".agents" / "skills").iterdir() if p.is_dir()):
        link = lab / ".claude" / "skills" / skill.name
        if not link.exists() and not link.is_symlink():
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(Path("../../.agents/skills") / skill.name)

    if not (lab / ".git").exists():
        subprocess.run(["git", "init", "-q", str(lab)], check=False)

    print(f"[OK] Lab at {lab}: {len(written)} file(s) written, {len(kept)} existing file(s) left as they were.")
    if missing:
        print(f"[TODO] Not found next to this skill: {', '.join(missing)}. The lab's content relies on them: "
              "install them into the lab's .agents/skills/ and commit.")
    target_name = register_target(lab, args.target, args.short_name) if args.target else None

    slots = []
    for path in sorted(lab.rglob("*.md")):
        if {".targets", ".venv"} & set(path.parts):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "{{FILL:" in line:
                slots.append(f"  {path.relative_to(lab)}:{number}  {line.strip()[:110]}")
    if slots:
        print("Slots only the user can answer (ask, then write the answer in their terms):")
        print("\n".join(slots))
    print_remaining(lab, target_name)


if __name__ == "__main__":
    main()
