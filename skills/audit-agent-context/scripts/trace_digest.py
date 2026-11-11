#!/usr/bin/env python3
"""Slim Claude Code session transcripts down to what an audit needs.

Claude Code writes one JSONL file per session under
~/.claude/projects/<cwd-slug>/<session-id>.jsonl, and one per subagent under
<session-id>/subagents/agent-<id>.jsonl. Raw transcripts are huge (full tool
results, signatures, bookkeeping entries). This tool lists the sessions of a
repo and prints a short markdown digest of one: the prompts, the thinking,
every tool call, and a truncated view of each result.

Usage:
  trace_digest.py list   [--repo DIR] [--limit N]
  trace_digest.py digest TRANSCRIPT.jsonl [--out FILE] [--max-chars N] [--no-subagents]

Never modifies transcripts. Standard library only. Prints to stdout unless --out is given.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def projects_root() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(Path.home(), ".claude")
    return Path(base) / "projects"


def project_dir(repo: str) -> Path:
    """Claude Code names the folder after the cwd, with non-alphanumerics as '-'."""
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(repo))
    return projects_root() / slug


def read_entries(path: Path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue  # a session still being written can end mid-line


def clip(text, limit: int) -> str:
    text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]} … [+{len(text) - limit} chars]"


def result_text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict):
            parts.append(block.get("text") or f"[{block.get('type', 'block')}]")
    return "\n".join(parts)


def first_prompt(path: Path) -> str:
    for entry in read_entries(path):
        if entry.get("type") != "user":
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        for block in content or []:
            if block.get("type") == "text":
                return block.get("text", "")
    return ""


def cmd_list(args) -> int:
    folder = project_dir(args.repo)
    if not folder.is_dir():
        print(f"No Claude Code sessions found for this repo (looked in {folder}).")
        return 0
    files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    print(f"# Sessions in {folder} ({len(files)} total, newest first)")
    for path in files[: args.limit]:
        stat = path.stat()
        when = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        subs = len(list((folder / path.stem / "subagents").glob("agent-*.jsonl")))
        prompt = " ".join(first_prompt(path).split())
        print(f"- {when}  {stat.st_size // 1024:>6} KB  {subs} subagents  {path}")
        print(f"    first prompt: {clip(prompt, 160)}")
    return 0


def digest(path: Path, limit: int, out) -> None:
    tool_names = {}
    counts = {}
    for entry in read_entries(path):
        kind = entry.get("type")
        if kind == "attachment":
            # Records what the harness injected (CLAUDE.md, skills, reminders).
            att = entry.get("attachment") or {}
            label = att.get("type", "attachment")
            detail = att.get("path") or att.get("filename") or att.get("name") or ""
            out.write(f"- _context injected:_ {label} {detail}\n")
            continue
        if kind not in ("user", "assistant"):
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for block in content or []:
            btype = block.get("type")
            if btype == "text":
                who = "USER" if kind == "user" else "AGENT"
                out.write(f"\n**{who}:** {clip(block.get('text', ''), limit * 2)}\n")
            elif btype == "thinking":
                thought = block.get("thinking") or ""
                if thought.strip():
                    out.write(f"- _thinking:_ {clip(thought, limit * 2)}\n")
                else:
                    out.write("- _thinking:_ [not stored in transcript]\n")
            elif btype == "tool_use":
                name = block.get("name", "?")
                tool_names[block.get("id")] = name
                counts[name] = counts.get(name, 0) + 1
                out.write(f"- **{name}** {clip(block.get('input', {}), limit)}\n")
            elif btype == "tool_result":
                name = tool_names.get(block.get("tool_use_id"), "?")
                flag = " ERROR" if block.get("is_error") else ""
                text = " ".join(result_text(block.get("content")).split())
                out.write(f"  - result{flag} ({name}): {clip(text, limit)}\n")
    if counts:
        summary = ", ".join(f"{n}×{c}" for n, c in sorted(counts.items(), key=lambda x: -x[1]))
        out.write(f"\n_Tool calls:_ {summary}\n")


def cmd_digest(args) -> int:
    path = Path(args.transcript)
    if not path.is_file():
        print(f"Transcript not found: {path}", file=sys.stderr)
        return 1
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as out:
            write_digest(path, args, out)
        print(f"{args.out} ({os.path.getsize(args.out) // 1024} KB)")
    else:
        write_digest(path, args, sys.stdout)
    return 0


def write_digest(path: Path, args, out) -> None:
    out.write(f"# Session {path.stem}\n")
    digest(path, args.max_chars, out)
    if args.no_subagents:
        return
    for sub in sorted((path.parent / path.stem / "subagents").glob("agent-*.jsonl")):
        meta = {}
        meta_path = sub.with_suffix("").with_suffix(".meta.json")
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                meta = {}
        title = meta.get("description") or sub.stem
        out.write(f"\n## Subagent: {title} ({meta.get('agentType', 'unknown type')})\n")
        digest(sub, args.max_chars, out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list this repo's sessions, newest first")
    p_list.add_argument("--repo", default=".", help="repo directory (default: cwd)")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_digest = sub.add_parser("digest", help="print a slim markdown digest of one session")
    p_digest.add_argument("transcript")
    p_digest.add_argument("--out", help="write the digest to this file instead of stdout")
    p_digest.add_argument("--max-chars", type=int, default=300,
                          help="max characters kept per tool input/result (default 300)")
    p_digest.add_argument("--no-subagents", action="store_true")
    p_digest.set_defaults(func=cmd_digest)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
