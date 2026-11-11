#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a research lab repository from this skill's scaffold (assets/lab).

    uv run scripts/new_lab.py <destination> --name "<lab name>"

Copies the scaffold, puts the files that need a dot name or a symlink in place, and lists the
`{{FILL: ...}}` slots that only the user can answer. It never overwrites an existing file, so it
is safe to run again on a lab that is partly built. Standard library only.
"""

import argparse
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
    "review-wiki-skill.md": ".agents/skills/review-wiki/SKILL.md",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("destination", type=Path, help="Folder of the new lab (created if missing)")
    parser.add_argument("--name", required=True, help="Lab name as it appears in AGENTS.md, e.g. 'Retrieval'")
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


if __name__ == "__main__":
    main()
