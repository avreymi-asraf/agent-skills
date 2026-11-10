#!/usr/bin/env bash
# Inventory for the audit-consistency skill.
# Prints a bounded overview of the repo, split into the semantic layer
# (instruction/documentation files) and code & config.
# Must always exit 0: a failing injected command aborts the whole skill.

set -u

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root" 2>/dev/null || true

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  all_files() { git ls-files --cached --others --exclude-standard 2>/dev/null; }
else
  all_files() {
    find . -type f \
      -not -path '*/.git/*' -not -path '*/node_modules/*' \
      -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' \
      2>/dev/null | sed 's|^\./||'
  }
fi

# Skip previous audit output and obvious binaries / data blobs.
binary_re='\.(png|jpe?g|gif|webp|ico|svg|pdf|zip|gz|tgz|bz2|xz|7z|tar|whl|jar|so|dylib|dll|exe|bin|pt|pth|ckpt|safetensors|onnx|h5|pkl|pickle|npy|npz|parquet|arrow|feather|db|sqlite|mp3|mp4|wav|mov|ttf|woff2?|lock)$'

# Semantic layer: agent instruction files, Claude config, prose docs.
semantic_re='(^|/)(CLAUDE|CLAUDE\.local|AGENTS)\.md$|(^|/)\.claude/|(^|/)\.cursor/rules/|(^|/)\.cursorrules$|(^|/)\.github/copilot-instructions\.md$|(^|/)\.windsurfrules$|(^|/)\.clinerules|\.(md|mdx|rst|adoc)$'

files="$(all_files | grep -v '^\.audit/' | grep -Eiv "$binary_re" | sort -u)"
semantic="$(printf '%s\n' "$files" | grep -E "$semantic_re" || true)"
code="$(printf '%s\n' "$files" | grep -Ev "$semantic_re" | grep -v '^$' || true)"

count_lines() { # stdin: file list -> "lines<TAB>path"
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    printf '%s\t%s\n' "$(wc -l < "$f" 2>/dev/null | tr -d ' ')" "$f"
  done
}

n_sem=$(printf '%s\n' "$semantic" | grep -c . || true)
n_code=$(printf '%s\n' "$code" | grep -c . || true)

echo "### Repo"
echo "- root: $root"
echo "- semantic-layer files: $n_sem"
echo "- code & config files: $n_code"
echo

echo "### Semantic layer (lines, path)"
if [ "$n_sem" -gt 0 ]; then
  printf '%s\n' "$semantic" | count_lines | head -n 400
  [ "$n_sem" -gt 400 ] && echo "... ($((n_sem - 400)) more; list them with git ls-files)"
fi
echo

echo "### Code & config by directory (files, lines, directory — depth 2)"
if [ "$n_code" -gt 0 ]; then
  printf '%s\n' "$code" | count_lines | awk -F'\t' '
    { n = split($2, p, "/");
      d = (n == 1) ? "." : (n == 2 ? p[1] : p[1] "/" p[2]);
      files[d]++; lines[d] += $1 }
    END { for (d in files) printf "%6d files %8d lines  %s\n", files[d], lines[d], d }' \
    | sort -k5 | head -n 200
fi
echo

echo "### Largest code & config files (lines, path)"
if [ "$n_code" -gt 0 ]; then
  printf '%s\n' "$code" | count_lines | sort -t$'\t' -k1,1nr | head -n 25
fi
echo

exit 0
