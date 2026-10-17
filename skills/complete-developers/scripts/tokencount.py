#!/usr/bin/env python3
"""Estimate how many tokens files would cost to read, before reading them.

  python tokencount.py src/ docs/README.md --top 15 --budget 8000

The estimate is heuristic (about 3.7 chars/token for Latin text and code,
about 2.2 chars/token for Arabic script) and typically within +/-25%.
Use it to decide what NOT to open, not as a billing figure.
"""
import argparse
import os
import sys

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__", "target",
             ".next", ".cache", "vendor", ".idea", ".vscode", "coverage"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tar",
              ".mp3", ".mp4", ".wav", ".ogg", ".woff", ".woff2", ".ttf", ".otf", ".exe", ".dll",
              ".so", ".class", ".jar", ".rbxl", ".rbxm", ".mcworld", ".mcpack", ".lock"}


def estimate(text: str) -> int:
    arabic = sum(1 for c in text if "\u0600" <= c <= "\u06ff" or "\u0750" <= c <= "\u077f")
    other = len(text) - arabic
    return int(arabic / 2.2 + other / 3.7) + 1


def walk(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p, followlinks=False):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in files:
                    yield os.path.join(root, f)
        else:
            print(f"skip (not found): {p}", file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--top", type=int, default=20, help="show the N most expensive files")
    ap.add_argument("--budget", type=int, default=0, help="flag when the total exceeds this many tokens")
    a = ap.parse_args(argv)
    rows, total = [], 0
    for f in walk(a.paths):
        if os.path.splitext(f)[1].lower() in BINARY_EXT or os.path.islink(f):
            continue
        try:
            if os.path.getsize(f) > 3_000_000:
                rows.append((f, -1))
                continue
            with open(f, "r", encoding="utf-8", errors="strict") as fh:
                t = estimate(fh.read())
        except (UnicodeDecodeError, OSError):
            continue
        rows.append((f, t))
        total += t
    rows.sort(key=lambda r: -r[1])
    for f, t in rows[: a.top]:
        print(f"{'>3MB skipped' if t < 0 else f'{t:>8}'}  {f}")
    print(f"{total:>8}  TOTAL (~tokens, {len(rows)} files)")
    if a.budget and total > a.budget:
        print(f"over budget by ~{total - a.budget}: read symbols/ranges, not whole files")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
