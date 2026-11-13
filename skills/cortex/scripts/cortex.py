#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""cortex.py - the mechanical checks of a cortex, standard library only.

    uv run cortex.py store  <source-id> [--file PATH] [--part NAME]   # text from the file, or from stdin
    uv run cortex.py store  <source-id> --compare [--file PATH]       # a second copy: which stored passages it lacks
    uv run cortex.py check  [--cortex cortex] [--sources DIR] [--also DIR] [--strict]
    uv run cortex.py claims [--status S] [--anchor K] [--from TEXT] [--grep TEXT]
    uv run cortex.py links <node>
    uv run cortex.py similar <text file>
    uv run cortex.py pairs [--all]

It reads the files and decides nothing about content: whether a claim is worth writing, whether a
page explains well and whether a tension is settled are judgments, and stay with the agent.
Run it from the folder that contains the cortex. Files whose name starts with "_" are templates.
"""

import argparse
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ANCHORS = ("quote", "experiment", "stated")
CLAIM_STATUS = ("provisional", "confirmed", "withdrawn", "superseded")
VERIFIED = ("pass", "partial", "fail", "unchecked")
DEAD = ("withdrawn", "superseded")

SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
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
        stored = (self.sources / "raw", self.sources / "text")  # what a source says, not something the cortex wrote
        files = sorted(p for p in self.root.rglob("*.md")
                       if not any(part.startswith(("_", ".")) for part in p.relative_to(self.root).parts)
                       and not any(p.is_relative_to(d) for d in stored))
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

    def source_files(self, target: str) -> list:
        """A source's stored text: the files `store` wrote to sources/text/ under its id (<id>.md, <id>--<part>.md).
        The note is not one of them: it is the agent's description of the source, not the source's words."""
        stem = Path(target.strip().removesuffix(".md")).name
        text_dir = self.sources / "text"
        if not text_dir.is_dir():
            return []
        return [p for p in sorted(text_dir.iterdir())
                if p.is_file() and (p.stem == stem or p.stem.startswith(stem + "--"))]

    def note_meta(self, target: str) -> dict:
        note = self.resolve(target)
        return read_node(note, note.parent).meta if note and note.is_file() else {}

    def source_text(self, target: str) -> str | None:
        files = self.source_files(target)
        return "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files) if files else None


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


def quote_lines(quote: str, text: str) -> tuple | None:
    """First and last line (0-based) of the text that the quote covers, or None when it is not there."""
    lines, starts, haystack = text.splitlines(), [], ""
    for line in lines:
        starts.append(len(haystack))
        haystack += squash(line)
    line_at = lambda pos: max(i for i, start in enumerate(starts) if start <= pos)
    first, position = None, 0
    for segment in OMISSION_RE.split(quote):
        needle = squash(segment)
        if not needle:
            continue
        position = haystack.find(needle, position)
        if position < 0:
            return None
        first = line_at(position) if first is None else first
        position += len(needle)
    return None if first is None else (first, line_at(position - 1))


def not_obtained(meta: dict) -> bool:
    return meta.get("read", "").startswith("not obtained")


def waiting(claim: Node) -> bool:
    """A live quoted claim that no blind verifier has judged yet: what `pairs` shows and `check` counts."""
    return (claim.meta.get("status") not in DEAD and claim.meta.get("verified", "unchecked") == "unchecked"
            and any(ev.kind == "quote" and ev.quotes for ev in claim.evidence))


def check_claim(cx: Cortex, node: Node, errors: list, review: list) -> None:
    status = node.meta.get("status", "")
    if status not in CLAIM_STATUS:
        errors.append(f"{node.rel}: status '{status}' is not one of {', '.join(CLAIM_STATUS)}")
    verified = node.meta.get("verified")
    if verified is not None and verified not in VERIFIED:
        errors.append(f"{node.rel}: verified '{verified}' is not one of {', '.join(VERIFIED)}")
    if verified == "fail" and status not in DEAD:
        errors.append(f"{node.rel}: verified: fail, so the evidence does not carry the sentence; "
                      "delete it if it never passed verification, withdraw it if it did")
    if verified == "partial" and status not in DEAD:
        review.append(f"{node.rel}: verified: partial, so the sentence says more than its evidence; "
                      "narrow it in place, set it back to unchecked and verify again")
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
            if not_obtained(cx.note_meta(target.group(1))):
                errors.append(f"{node.rel}: quotes [[{target.group(1)}]], whose text was not obtained; a lead yields no claims")
            elif source is None:
                errors.append(f"{node.rel}: [[{target.group(1)}]] has no stored text in sources/text/ "
                              "(store what was fetched with `cortex.py store`)")
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

    # Sources: a stored original or its extracted text never changes once committed, and a source
    # that no claim quotes is the backlog of `add`.
    if cx.sources.is_dir():
        changed = subprocess.run(["git", "diff", "--name-only", "--relative", "--diff-filter=MDR", "HEAD", "--", "raw", "text"],
                                 cwd=cx.sources, capture_output=True, text=True, check=False)
        if changed.returncode == 0:
            errors += [f"sources/{name}: changed or removed after it was committed; sources are never edited"
                       for name in changed.stdout.splitlines() if name.strip()]
        quoted = {Path(target.group(1).strip().removesuffix(".md")).name
                  for claim in cx.claims() for ev in claim.evidence
                  if ev.kind == "quote" and (target := LINK_RE.search(ev.rest))}
        for note in sorted(cx.sources.glob("*.md")):
            if note.name.startswith("_") or note.stem in quoted:
                continue
            if not_obtained(read_node(note, note.parent).meta):
                review.append(f"sources/{note.stem}: text not obtained; a lead, to `add` when a route to its text works")
            elif not cx.source_files(note.stem):
                review.append(f"sources/{note.stem}: no stored text in sources/text/ and no claim quotes it")
            else:
                review.append(f"sources/{note.stem}: no claim quotes it yet")

    for line in errors:
        print(f"ERROR   {line}")
    for line in review:
        print(f"REVIEW  {line}")
    counts = {}
    for claim in cx.claims():
        counts[claim.meta.get("status", "?")] = counts.get(claim.meta.get("status", "?"), 0) + 1
    by_status = ", ".join(f"{n} {s}" for s, n in sorted(counts.items())) or "none"
    pages = sum(1 for n in cx.nodes if n.kind and n.kind not in ("claim", "source"))
    pending = sum(1 for claim in cx.claims() if waiting(claim))
    print(f"{len(cx.claims())} claim(s) ({by_status}), {pages} typed page(s): {len(errors)} error(s), {len(review)} to review.")
    print(f"{pending} quoted claim(s) wait for blind verification"
          + (": a fresh agent judges them from `cortex.py pairs` alone (cortex skill, Verify)." if pending else "."))
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


STOPWORDS = set("""about above after again also another because been before being between both cannot could does doing
down during each from further have having here into itself more most only other over same should some such than that
their them then there these they this those through under until very were what when where which while will with would
your using used based show shows shown figure table section paper results result model models""".split())


def cmd_similar(cx: Cortex, args: argparse.Namespace) -> None:
    """Claims and pages that share the most frequent words of a text: what to read before writing from it."""
    words = re.findall(r"[a-z][a-z0-9]{3,}", args.file.read_text(encoding="utf-8", errors="replace").lower())
    counts = {}
    for word in words:
        if word not in STOPWORDS:
            counts[word] = counts.get(word, 0) + 1
    top = sorted(counts, key=lambda w: (-counts[w], w))[:40]
    scored = []
    for node in cx.nodes:
        if not node.kind or node.kind == "source":
            continue
        text = f"{node.title} {node.meta.get('description', '')}".lower()
        shared = [w for w in top if re.search(rf"\b{re.escape(w)}", text)]
        if len(shared) >= 2:
            scored.append((len(shared), node, shared))
    if not scored:
        print("Nothing in the cortex shares this text's main words.")
        return
    for count, node, shared in sorted(scored, key=lambda item: (-item[0], item[1].rel))[:args.top]:
        print(f"{count:>2}  {node.rel} [{node.meta.get('status', '-')}]  {node.title}\n      shares: {', '.join(shared[:8])}")


def cmd_pairs(cx: Cortex, args: argparse.Namespace) -> None:
    """For a blind verifier: each claim's sentence, its quoted words and the source text around them. Nothing else."""
    shown = 0
    for claim in cx.claims():
        quotes = [ev for ev in claim.evidence if ev.kind == "quote" and ev.quotes]
        if not quotes or not (args.all or waiting(claim)):
            continue
        shown += 1
        print(f"=== {claim.rel}\nSTATEMENT: {claim.title}")
        for ev in quotes:
            target = LINK_RE.search(ev.rest)
            for quote in ev.quotes:
                print(f"QUOTE: {quote}")
                for path in (cx.source_files(target.group(1)) if target else []):
                    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
                    span = quote_lines(quote, "\n".join(lines))
                    if span:
                        a, b = max(0, span[0] - args.context), min(len(lines), span[1] + 1 + args.context)
                        print(f"SOURCE CONTEXT ({path.name}, lines {a + 1}-{b}):")
                        print("\n".join("    " + line for line in lines[a:b]))
                        break
                else:
                    print("SOURCE CONTEXT: the quoted words were not found in the stored text")
        print()
    if not shown:
        print("No quoted claims are waiting for verification.")
        return
    print("Judge each claim from what is printed here and nothing else:\n"
          "  pass     the text states or clearly entails the sentence\n"
          "  partial  the sentence says more, or is surer, than the text\n"
          "  fail     the text does not support the sentence\n"
          "Answer one line per claim: file, verdict, a short reason.")


def read_input(path: Path | None) -> str:
    text = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    return text.replace("\r\n", "\n").replace("\r", "\n")


def passages(text: str) -> list:
    """The stored text in passages: blank-line separated blocks, each heading a passage of its own, omissions dropped."""
    found, block = [], []
    for line in text.splitlines() + [""]:
        heading = re.match(r"^\s*#+\s*(.*)$", line)
        if heading or not line.strip():
            if block:
                found.append(" ".join(block))
            block = []
            if heading and heading.group(1).strip():
                found.append(heading.group(1).strip())
        else:
            block.append(line.strip())
    return [p for p in found if not OMISSION_RE.fullmatch(p)]


def cmd_store(cx: Cortex, args: argparse.Namespace) -> None:
    """Store a source's text exactly as a route delivered it, or compare the stored text with a second copy."""
    if not SOURCE_ID_RE.match(args.source_id) or "--" in args.source_id:
        sys.exit(f"[ERROR] '{args.source_id}' is not a source id: lowercase kebab-case, as in [[sources/<source-id>]].")
    if args.compare:
        stored = cx.source_files(args.source_id)
        if not stored:
            sys.exit(f"[ERROR] Nothing is stored for {args.source_id} in {cx.sources / 'text'}.")
        second = read_input(args.file)
        missing = [(path.name, passage) for path in stored
                   for passage in passages(path.read_text(encoding="utf-8")) if not quote_found(passage, second)]
        for name, passage in missing:
            print(f"NOT IN THE SECOND COPY  {name}: \"{passage[:90]}...\"")
        total = sum(len(passages(path.read_text(encoding="utf-8"))) for path in stored)
        print(f"{total - len(missing)} of {total} stored passage(s) found in the second copy.")
        if missing:
            sys.exit(1)
        return
    if args.part and not SOURCE_ID_RE.match(args.part):
        sys.exit(f"[ERROR] '{args.part}' is not a part name: lowercase kebab-case.")
    text = read_input(args.file)
    if not text.strip():
        sys.exit("[ERROR] No text came in. Give --file, or pipe the text on standard input.")
    name = args.source_id + (f"--{args.part}" if args.part else "")
    target = cx.sources / "text" / f"{name}.md"
    if target.exists():
        sys.exit(f"[ERROR] {target} exists, and stored text is never edited. "
                 "Store more of the same source with --part <name>.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    print(f"Stored {len(text)} characters in {os.path.relpath(target)} ({len(passages(text))} passage(s)). "
          "Record how it arrived in the source note's `route:`.")


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cortex", type=Path, default=Path("cortex"), help="The cortex folder (default: ./cortex)")
    common.add_argument("--sources", type=Path, help="The sources folder (default: <cortex>/sources, else beside the cortex)")
    common.add_argument("--also", action="append", default=[], metavar="DIR",
                        help="Another folder that links may point into, e.g. a lab's experiments/ (repeatable)")
    parser = argparse.ArgumentParser(description="Mechanical checks of a cortex (stdlib only)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_store = sub.add_parser("store", parents=[common], help="Store a source's fetched text unchanged (from --file or stdin)")
    p_store.add_argument("source_id", help="The source id, as in [[sources/<source-id>]]")
    p_store.add_argument("--file", type=Path, help="Read the text from this file instead of standard input")
    p_store.add_argument("--part", metavar="NAME", help="Store more text of an already stored source as <source-id>--<NAME>.md")
    p_store.add_argument("--compare", action="store_true",
                         help="Read a second copy instead, and list the stored passages it does not contain")

    p_check = sub.add_parser("check", parents=[common], help="Validate claims, anchors and links; list what a review should look at")
    p_check.add_argument("--strict", action="store_true", help="Fail on the review items too")

    p_claims = sub.add_parser("claims", parents=[common], help="List claims, filtered")
    p_claims.add_argument("--status", choices=CLAIM_STATUS)
    p_claims.add_argument("--anchor", choices=ANCHORS)
    p_claims.add_argument("--from", dest="origin", metavar="TEXT", help="A source id or an experiment name in the evidence")
    p_claims.add_argument("--grep", metavar="TEXT", help="A word in the claim, its description or its file name")

    p_links = sub.add_parser("links", parents=[common], help="What a node points to and what points to it")
    p_links.add_argument("node", help="A node, as in a link: claims/<name>, pages/<name>, or just <name>")

    p_similar = sub.add_parser("similar", parents=[common], help="Claims and pages closest to a text file: read them before writing from it")
    p_similar.add_argument("file", type=Path, help="The extracted text of a source")
    p_similar.add_argument("--top", type=int, default=15)

    p_pairs = sub.add_parser("pairs", parents=[common], help="Sentence, quote and source context of each unverified claim, for a blind verifier")
    p_pairs.add_argument("--all", action="store_true", help="Every quoted claim, not only those still unchecked")
    p_pairs.add_argument("--context", type=int, default=8, help="Lines of source shown before and after the quote (default 8)")

    args = parser.parse_args()
    cx = Cortex(args.cortex, args.sources, args.also)
    {"store": cmd_store, "check": cmd_check, "claims": cmd_claims, "links": cmd_links, "similar": cmd_similar, "pairs": cmd_pairs}[args.cmd](cx, args)


if __name__ == "__main__":
    main()
