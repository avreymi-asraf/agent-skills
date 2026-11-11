#!/usr/bin/env python3
"""Check that a Claude Code session in this repo loads context only from the repo.

Starts `claude -p` in the repo with stream-json output, reads the documented
`system/init` event (skills, plugins, MCP servers, agents) and the
InstructionsLoaded hook (every CLAUDE.md and rule file), then stops before any
model call. Everything that does not come from the repo is reported.

What counts as the repo:
  skills    .claude/skills/<name>/ and .claude/commands/<name>.md
  agents    .claude/agents/<name>.md, plus Claude Code's built-in agents
  MCP       servers named in .mcp.json
  memory    CLAUDE.md / rules files whose path is inside the repo

Usage:
  check_isolation.py [--repo DIR] [--allow NAME ...] [--json]

Exit code 0 = nothing external loaded, 1 = something external loaded,
2 = the check itself could not run. Standard library only.

Limit: a cloud session's claude.ai connectors are passed in by the cloud host,
so a `claude -p` started inside the container does not see them. Check those in
the session itself (see references/isolating-agent-context.md).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Agents that ship with Claude Code. They are part of the tool, not outside context.
BUILTIN_AGENTS = {"general-purpose", "Explore", "Plan", "statusline-setup", "claude-code-guide", "claude"}


def repo_root(start: str) -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=start,
                             capture_output=True, text=True, check=True).stdout.strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path(start).resolve()


def frontmatter_name(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if m:
        n = re.search(r"^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", m.group(1), re.M)
        if n:
            return n.group(1).strip()
    return None


def repo_context(root: Path) -> dict:
    claude = root / ".claude"
    skills = set()
    for skill_md in (claude / "skills").glob("*/SKILL.md"):
        skills.add(frontmatter_name(skill_md) or skill_md.parent.name)
    for cmd in (claude / "commands").rglob("*.md"):
        skills.add(cmd.relative_to(claude / "commands").with_suffix("").as_posix().replace("/", ":"))
    agents = set()
    for agent in (claude / "agents").rglob("*.md"):
        agents.add(frontmatter_name(agent) or agent.stem)
    mcp = set()
    try:
        mcp = set(json.loads((root / ".mcp.json").read_text()).get("mcpServers", {}))
    except (OSError, ValueError):
        pass
    return {"skills": skills, "agents": agents, "mcp": mcp}


def run_probe(root: Path):
    """Start claude -p, collect InstructionsLoaded payloads and the init event, stop before the model call."""
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "instructions.jsonl"
        hook = {"type": "command", "command": f"cat >> '{log}'; echo >> '{log}'"}
        settings = json.dumps({"hooks": {"InstructionsLoaded": [{"hooks": [hook]}]}})
        cmd = ["claude", "-p", "ok", "--output-format", "stream-json", "--verbose", "--settings", settings]
        try:
            proc = subprocess.Popen(cmd, cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            sys.exit("check_isolation: `claude` is not on PATH")
        init = None
        for line in proc.stdout:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "system" and event.get("subtype") == "init":
                init = event
                break
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        if init is None:
            print("check_isolation: no init event from claude:\n" + proc.stderr.read()[-2000:], file=sys.stderr)
            sys.exit(2)
        loaded = []
        if log.exists():
            for line in log.read_text().splitlines():
                try:
                    loaded.append(json.loads(line))
                except ValueError:
                    pass
        return init, loaded


def tracked(path: str, root: Path) -> bool:
    """True if git tracks the file, so everyone who clones the repo gets it."""
    r = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=root, capture_output=True)
    return r.returncode == 0


def inside(path: str, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def compare(root: Path, init: dict, loaded: list, allow: set) -> dict:
    repo = repo_context(root)
    plugins = init.get("plugins", [])
    plugin_names = {p.get("name") for p in plugins}
    external = {"instructions": [], "skills": [], "plugins": [], "mcp": [], "agents": []}
    untracked, builtin_plugins = [], []

    for item in loaded:
        path = item.get("file_path", "")
        if not inside(path, root):
            external["instructions"].append(f"{path} ({item.get('memory_type')}, {item.get('load_reason')})")
        elif not tracked(path, root):
            untracked.append(path)

    for skill in init.get("skills", []):
        if skill in repo["skills"] or skill in allow:
            continue
        prefix = skill.split(":", 1)[0] if ":" in skill else None
        if prefix == "anthropic-skills":
            origin = "claude.ai account"
        elif prefix in plugin_names:
            origin = f"plugin {prefix}"
        else:
            origin = "bundled with Claude Code or user-level"
        external["skills"].append(f"{skill} ({origin})")

    for p in plugins:
        source = p.get("source") or p.get("path", "")
        if source.endswith("@builtin"):
            builtin_plugins.append(p.get("name"))  # part of Claude Code itself
        elif p.get("name") not in allow:
            external["plugins"].append(f"{p.get('name')} ({source})")

    for server in init.get("mcp_servers", []):
        name = server.get("name")
        if name in repo["mcp"] or name in allow:
            continue
        external["mcp"].append(f"{name} (source: {server.get('source', '?')}, {server.get('status')})")

    for agent in init.get("agents", []):
        if agent not in repo["agents"] and agent not in BUILTIN_AGENTS and agent not in allow:
            external["agents"].append(agent)

    return {
        "repo": str(root),
        "cloud_session": os.environ.get("CLAUDE_CODE_REMOTE") == "true",
        "claude_code_version": init.get("claude_code_version"),
        "loaded_from_repo": {
            "instructions": [i.get("file_path") for i in loaded if inside(i.get("file_path", ""), root)],
            "skills": sorted(set(init.get("skills", [])) & repo["skills"]),
            "mcp": sorted({s.get("name") for s in init.get("mcp_servers", [])} & repo["mcp"]),
            "agents": sorted(set(init.get("agents", [])) & repo["agents"]),
        },
        "untracked_in_repo": untracked,
        "builtin_plugins": builtin_plugins,
        "external": external,
    }


def print_report(r: dict) -> None:
    print(f"# Context isolation check: {r['repo']}")
    print(f"Claude Code {r['claude_code_version']}, {'cloud session' if r['cloud_session'] else 'local'}\n")
    print("## Loaded from the repo")
    for kind, items in r["loaded_from_repo"].items():
        print(f"- {kind}: {', '.join(items) if items else '(none)'}")
    if r["untracked_in_repo"]:
        print("- not committed, so only this machine has them: " + ", ".join(r["untracked_in_repo"]))
    if r["builtin_plugins"]:
        print(f"\nBuilt into Claude Code (not reported as external): {', '.join(r['builtin_plugins'])}")
    print("\n## Loaded from outside the repo")
    leaks = {k: v for k, v in r["external"].items() if v}
    if not leaks:
        print("- nothing")
    for kind, items in leaks.items():
        print(f"- {kind}:")
        for item in items:
            print(f"  - {item}")
    if r["cloud_session"]:
        print("\nNot covered here: claude.ai connectors the cloud host passes to the session. "
              "Check them in the session itself (/mcp, or the MCP servers in the agent's own context).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=".", help="repository to check (default: current directory)")
    ap.add_argument("--allow", nargs="*", default=[], help="names to accept although they are not in the repo")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    args = ap.parse_args()

    root = repo_root(args.repo)
    init, loaded = run_probe(root)
    result = compare(root, init, loaded, set(args.allow))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)
    sys.exit(1 if any(result["external"].values()) else 0)


if __name__ == "__main__":
    main()
