"""8-word overlap check: repo docs vs. a source text file.

Usage:
    python3 scripts/check_overlap.py /path/to/source.txt

The source document itself is never committed to this repo. The script
normalises both sides (lowercase, punctuation stripped, whitespace
collapsed), builds every 8-word window, and reports any shared window.
Exit 0 and "0 hits" is the required result; anything else fails loudly
with the offending windows printed.

Scanned: README.md, docs/, knowledge/, and bank_in_a_box/ docstrings
(via the .py files themselves — code identifiers rarely form 8-word
prose windows, but checking costs nothing).
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent.parent
WINDOW = 8


def normalise(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def windows(text):
    words = normalise(text).split()
    return {" ".join(words[i : i + WINDOW]) for i in range(len(words) - WINDOW + 1)}


def main():
    if len(sys.argv) != 2:
        print("usage: python3 scripts/check_overlap.py /path/to/source.txt")
        return 2
    source_windows = windows(pathlib.Path(sys.argv[1]).read_text(errors="ignore"))
    hits = {}
    targets = [ROOT / "README.md"]
    targets += sorted((ROOT / "docs").glob("*.md"))
    targets += sorted((ROOT / "knowledge").glob("*.md"))
    targets += sorted((ROOT / "bank_in_a_box").glob("*.py"))
    for target in targets:
        shared = windows(target.read_text(errors="ignore")) & source_windows
        if shared:
            hits[str(target.relative_to(ROOT))] = sorted(shared)
    if hits:
        for path, shared in hits.items():
            print(f"{path}: {len(shared)} shared 8-word window(s)")
            for window in shared:
                print(f"  {window!r}")
        print(f"TOTAL: {sum(len(v) for v in hits.values())} hits — FAILED")
        return 1
    print("0 hits — overlap check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
