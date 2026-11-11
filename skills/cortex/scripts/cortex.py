#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""cortex.py - the mechanical checks of a cortex, standard library only.

    uv run cortex.py check  [--cortex cortex] [--sources DIR] [--also DIR] [--strict]
    uv run cortex.py claims [--status S] [--anchor K] [--from TEXT] [--grep TEXT]
    uv run cortex.py links <node>

It reads the files and decides nothing about content: whether a claim is worth writing, whether a
page explains well and whether a tension is settled are judgments, and stay with the agent.
Run it from the folder that contains the cortex. Files whose name starts with "_" are templates.
"""

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ANCHORS = ("quote", "experiment", "stated")
CLAIM_STATUS = ("provisional", "confirmed", "withdrawn", "superseded")
VERIFIED = ("pass", "partial", "fail", "unchecked")
DEAD = ("withdrawn", "superseded")

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
ITEM_RE = re.compile(r"^\s*[-*]\s*([a-z_]+)::\s*(.*)$")
QUOTE_LINE_RE = re.compile(r"^\s*>\s?(.*)$")
OMISSION_RE = re.compile(r"\[\s*(?:\.\.\.|…)\s*\]|…")
TYPOGRAPHY = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "‐": "-", "‑": "-"})


@dataclass
class Evidence:
    kind: str
    rest: str
    quotes: list = field(default_factory=list)  # one string per blockquote under the item


@dataclass
class Node:
    path: Path
    rel: str                       # path inside the cortex, without ".md"
    meta: dict
    title: str
    text: str                      # body with code spans and blocks removed (for links)
    lines: list                    # raw body lines
    evidence: list = field(default_factory=list)
    relations: list = field(default_factory=list)  # (relation name, rest of the line)

    @property
    def kind(self) -> str:
        return self.meta.get("type", "")


def read_node(path: Path, root: Path) -> Node:
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---\n") and "\n---" in raw[4:]:
        head, body = raw[4:].split("\n---", 1)
        for line in head.splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                key, value = line.split(":", 1)
                meta[key.strip()] = value.split(" #", 1)[0].strip().strip("\"'")
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)  # template hints left in a node are not content
    lines = body.splitlines()
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "")
    text = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    node = Node(path, path.relative_to(root).with_suffix("").as_posix(), meta, title, text, lines)

    current, in_code, in_quote = None, False, False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        item = ITEM_RE.match(line)
        if item:
            name, rest = item.group(1), item.group(2).strip()
            if name in ANCHORS:
                current = Evidence(name, rest)
                node.evidence.append(current)
            else:
                node.relations.append((name, rest))
                current = None
            in_quote = False
            continue
        quoted = QUOTE_LINE_RE.match(line)
        if quoted and current is not None and current.kind == "quote":
            if not in_quote:
                current.quotes.append("")  # each blockquote under the item is checked as one quote
            current.quotes[-1] += " " + quoted.group(1)
        in_quote = bool(quoted)
    for ev in node.evidence:
        ev.quotes = [q.strip() for q in ev.quotes if q.strip()]
    return node


class Cortex:
    def __init__(self, cortex: Path, sources: Path | None, also: list):
        self.root = cortex.resolve()
        if not self.root.is_dir():
            sys.exit(f"[ERROR] No cortex folder at {cortex}. Run from the folder that contains it, or pass --cortex.")
        inside, beside = self.root / "sources", self.root.parent / "sources"
        self.sources = sources.resolve() if sources else (inside if inside.is_dir() else beside)
        self.also = [Path(a).resolve() for a in also]
        files = sorted(p for p in self.root.rglob("*.md")
                       if not any(part.startswith(("_", ".")) for part in p.relative_to(self.root).parts))
        self.nodes = [read_node(p, self.root) for p in files]
        self.by_path = {n.path: n for n in self.nodes}

    def claims(self) -> list:
        return [n for n in self.nodes if n.kind == "claim"]

    def resolve(self, target: str) -> Path | None:
        """Where a [[target]] leads: a file or folder in the cortex, beside it, or in an --also folder."""
        target = target.strip().removesuffix(".md")
        for base in (self.root, self.root.parent, self.sources.parent, *self.also):
            for candidate in (base / f"{target}.md", base / target):
                if candidate.exists():
                    return candidate.resolve()
        matches = [n.path for n in self.nodes if n.rel == target or n.rel.endswith("/" + target)]
        return matches[0] if len(matches) == 1 else None

    def links_of(self, node: Node) -> list:
        """(target text, resolved path or None) for every link in a node, placeholders skipped."""
        found = []
        for target in LINK_RE.findall(node.text):
            if any(mark in target for mark in ("<", ">", "...")):
                continue
            found.append((target.strip(), self.resolve(target)))
        return found

    def source_text(self, target: str) -> str | None:
        """The stored text of a source: its note plus anything in sources/text/ with the same name."""
        note = self.resolve(target)
        parts = []
        if note and note.is_file():
            parts.append(note.read_text(encoding="utf-8", errors="replace"))
        stem = Path(target.strip()).name
        text_dir = self.sources / "text"
        if text_dir.is_dir():
            parts += [p.read_text(encoding="utf-8", errors="replace")
                      for p in sorted(text_dir.iterdir()) if p.is_file() and p.stem == stem]
        return "\n".join(parts) if parts else None


def squash(text: str) -> str:
    """Text reduced to what must match: no whitespace, hyphens, emphasis marks, case or typography."""
    text = unicodedata.normalize("NFKC", text).translate(TYPOGRAPHY).lower()
    return re.sub(r"[\s\-*_`]+", "", text)


def quote_found(quote: str, source: str) -> bool:
    haystack, position = squash(source), 0
    for segment in OMISSION_RE.split(quote):
        needle = squash(segment)
        if not needle:
            continue
        position = haystack.find(needle, position)
        if position < 0:
            return False
        position += len(needle)
    return True


def check_claim(cx: Cortex, node: Node, errors: list, review: list) -> None:
    status = node.meta.get("status", "")
    if status not in CLAIM_STATUS:
        errors.append(f"{node.rel}: status '{status}' is not one of {', '.join(CLAIM_STATUS)}")
    verified = node.meta.get("verified")
    if verified is not None and verified not in VERIFIED:
        errors.append(f"{node.rel}: verified '{verified}' is not one of {', '.join(VERIFIED)}")
    if not node.title:
        errors.append(f"{node.rel}: no '# ' title; the title is the claim's sentence")
    if not node.evidence:
        errors.append(f"{node.rel}: no evidence item (expected one of: {', '.join(a + '::' for a in ANCHORS)})")

    for ev in node.evidence:
        if ev.kind == "quote":
            target = LINK_RE.search(ev.rest)
            if not target:
                errors.append(f"{node.rel}: quote:: names no [[source]]")
                continue
            source = cx.source_text(target.group(1))
            if source is None:
                errors.append(f"{node.rel}: source [[{target.group(1)}]] has no stored note or text")
            elif not ev.quotes:
                errors.append(f"{node.rel}: quote:: from [[{target.group(1)}]] has no quoted words under it")
            else:
                for quote in ev.quotes:
                    if not quote_found(quote, source):
                        errors.append(f"{node.rel}: quoted words are not in [[{target.group(1)}]]: \"{quote[:70]}...\"")
        elif ev.kind == "experiment":
            if not re.search(r"\bround\s+\d+", ev.rest) or not re.search(r"@\s*`?[0-9a-f]{7,40}\b", ev.rest):
                errors.append(f"{node.rel}: experiment:: needs a round and a commit (`<name>` round <n> @ `<sha>`)")
            name = re.match(r"`([^`]+)`|(\S+)", ev.rest)
            name = (name.group(1) or name.group(2)) if name else ""
            if cx.also and name and not any((base / name).exists() for base in cx.also):
                review.append(f"{node.rel}: experiment '{name}' is not in {', '.join(a.name for a in cx.also)}")
        elif ev.kind == "stated":
            if not re.search(r"\d{4}-\d{2}-\d{2}", ev.rest):
                errors.append(f"{node.rel}: stated:: needs who said it and a date (YYYY-MM-DD)")

    relation_names = {name for name, _ in node.relations}
    if status == "superseded" and not any(n == "superseded_by" and LINK_RE.search(r) for n, r in node.relations):
        errors.append(f"{node.rel}: superseded, with no 'superseded_by::[[claims/...]]' line")
    if status == "withdrawn" and not any(n == "withdrawn" and r for n, r in node.relations):
        errors.append(f"{node.rel}: withdrawn, with no 'withdrawn::<why, and after what>' line")
    if status not in DEAD and relation_names & {"superseded_by", "withdrawn"}:
        errors.append(f"{node.rel}: has a superseded_by:: or withdrawn:: line but status is '{status}'")


def cmd_check(cx: Cortex, args: argparse.Namespace) -> None:
    errors, review = [], []
    claim_paths = {n.path: n for n in cx.claims()}
    index = next((n for n in cx.nodes if n.rel == "index"), None)
    indexed = {path for _, path in cx.links_of(index)} if index else set()

    for node in cx.nodes:
        links = cx.links_of(node)
        for target, path in links:
            if path is None:
                errors.append(f"{node.rel}: [[{target}]] leads nowhere")
        if node.kind == "claim":
            check_claim(cx, node, errors, review)
            continue
        if not node.kind or node.kind == "source":
            continue  # routing pages (index, profile, log) and source notes carry no claims of their own

        cited = [claim_paths[p] for _, p in links if p in claim_paths]
        settled = node.meta.get("status") in ("resolved", "answered")
        for claim in cited:
            if claim.meta.get("status") in DEAD and not settled:
                review.append(f"{node.rel}: cites {claim.meta['status']} claim {claim.rel}")
        if not cited and "anchor" not in node.meta:
            review.append(f"{node.rel}: {node.kind} page cites no claim")
        if node.kind == "tension" and len({c.path for c in cited}) < 2:
            review.append(f"{node.rel}: a tension names fewer than two claims")
        if index and node.path not in indexed:
            review.append(f"{node.rel}: not in index.md")

    for line in errors:
        print(f"ERROR   {line}")
    for line in review:
        print(f"REVIEW  {line}")
    counts = {}
    for claim in cx.claims():
        counts[claim.meta.get("status", "?")] = counts.get(claim.meta.get("status", "?"), 0) + 1
    by_status = ", ".join(f"{n} {s}" for s, n in sorted(counts.items())) or "none"
    pages = sum(1 for n in cx.nodes if n.kind and n.kind not in ("claim", "source"))
    print(f"{len(cx.claims())} claim(s) ({by_status}), {pages} typed page(s): {len(errors)} error(s), {len(review)} to review.")
    if errors or (args.strict and review):
        sys.exit(1)


def cmd_claims(cx: Cortex, args: argparse.Namespace) -> None:
    rows = []
    for claim in sorted(cx.claims(), key=lambda n: (n.meta.get("created", ""), n.rel)):
        kinds = sorted({ev.kind for ev in claim.evidence})
        origin = "; ".join(ev.rest for ev in claim.evidence)
        if args.status and claim.meta.get("status") != args.status:
            continue
        if args.anchor and args.anchor not in kinds:
            continue
        if args.origin and args.origin.lower() not in origin.lower():
            continue
        haystack = f"{claim.title} {claim.meta.get('description', '')} {claim.rel}".lower()
        if args.grep and args.grep.lower() not in haystack:
            continue
        rows.append((claim.meta.get("status", "?"), claim.meta.get("verified", "-"), ",".join(kinds) or "-",
                     claim.meta.get("created", "-"), claim.rel, claim.title))
    if not rows:
        print("No claims match.")
        return
    print("| status | verified | anchor | created | file | claim |")
    print("|---|---|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print(f"\n{len(rows)} claim(s).")


def cmd_links(cx: Cortex, args: argparse.Namespace) -> None:
    path = cx.resolve(args.node)
    node = cx.by_path.get(path) if path else None
    if node is None:
        sys.exit(f"[ERROR] '{args.node}' is not a node of this cortex.")
    status = f" [{node.meta['status']}]" if node.meta.get("status") else ""
    print(f"{node.rel}{status}: {node.title}\n\nPoints to:")
    for target, resolved in cx.links_of(node):
        other = cx.by_path.get(resolved)
        note = f" [{other.meta['status']}]" if other is not None and other.meta.get("status") else ""
        print(f"  [[{target}]]{note}" + ("" if resolved else "  (leads nowhere)"))
    print("\nPointed to by:")
    for other in cx.nodes:
        if other is node:
            continue
        for line in other.lines:
            if any(cx.resolve(t) == node.path for t in LINK_RE.findall(line)):
                print(f"  {other.rel}: {line.strip()[:140]}")


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cortex", type=Path, default=Path("cortex"), help="The cortex folder (default: ./cortex)")
    common.add_argument("--sources", type=Path, help="The sources folder (default: <cortex>/sources, else beside the cortex)")
    common.add_argument("--also", action="append", default=[], metavar="DIR",
                        help="Another folder that links may point into, e.g. a lab's experiments/ (repeatable)")
    parser = argparse.ArgumentParser(description="Mechanical checks of a cortex (stdlib only)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", parents=[common], help="Validate claims, anchors and links; list what a review should look at")
    p_check.add_argument("--strict", action="store_true", help="Fail on the review items too")

    p_claims = sub.add_parser("claims", parents=[common], help="List claims, filtered")
    p_claims.add_argument("--status", choices=CLAIM_STATUS)
    p_claims.add_argument("--anchor", choices=ANCHORS)
    p_claims.add_argument("--from", dest="origin", metavar="TEXT", help="A source id or an experiment name in the evidence")
    p_claims.add_argument("--grep", metavar="TEXT", help="A word in the claim, its description or its file name")

    p_links = sub.add_parser("links", parents=[common], help="What a node points to and what points to it")
    p_links.add_argument("node", help="A node, as in a link: claims/<name>, pages/<name>, or just <name>")

    args = parser.parse_args()
    cx = Cortex(args.cortex, args.sources, args.also)
    {"check": cmd_check, "claims": cmd_claims, "links": cmd_links}[args.cmd](cx, args)


if __name__ == "__main__":
    main()
