#!/usr/bin/env python3
"""Shrink a long log or command output to what a debugger needs.

  npm run build 2>&1 | python logtrim.py
  python logtrim.py build.log --max-lines 60 --context 2

Keeps: the first lines, the last lines, every line that looks like an error,
failure or warning (with context), and folds consecutive repeats ("x37").
Never hides that it trimmed: it prints how many lines were dropped.
"""
import argparse
import re
import sys

PAT = re.compile(r"(error|exception|traceback|fatal|panic|fail(ed|ure)?|assert|denied|"
                 r"cannot|can't|unable|undefined|not found|warn(ing)?|✗|✘|ERR!|"
                 r"segfault|timeout|timed out|خطأ|فشل)", re.I)


def fold(lines):
    out, prev, n = [], None, 0
    for ln in lines:
        if ln == prev:
            n += 1
            continue
        if n:
            out[-1] = f"{out[-1]}  (x{n + 1})"
        out.append(ln)
        prev, n = ln, 0
    if n:
        out[-1] = f"{out[-1]}  (x{n + 1})"
    return out


def trim(lines, head=8, tail=15, context=2, max_lines=80):
    n = len(lines)
    keep = set(range(min(head, n))) | set(range(max(0, n - tail), n))
    hits = [i for i, ln in enumerate(lines) if PAT.search(ln)]
    for i in hits:
        keep.update(range(max(0, i - context), min(n, i + context + 1)))
    idx = sorted(keep)
    if len(idx) > max_lines:  # prefer error hits over filler when over budget
        core = set(range(min(head, n))) | set(range(max(0, n - tail), n))
        extra = [i for i in idx if i not in core]
        room = max(0, max_lines - len(core))
        idx = sorted(core | set(extra[:room]))
    out, last = [], -1
    for i in idx:
        if last != -1 and i != last + 1:
            out.append(f"... [{i - last - 1} lines omitted]")
        out.append(lines[i])
        last = i
    return fold(out), n - len(idx)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="log file (default: stdin)")
    ap.add_argument("--head", type=int, default=8)
    ap.add_argument("--tail", type=int, default=15)
    ap.add_argument("--context", type=int, default=2)
    ap.add_argument("--max-lines", type=int, default=80)
    a = ap.parse_args(argv)
    src = open(a.file, encoding="utf-8", errors="replace") if a.file else sys.stdin
    lines = [ln.rstrip("\n") for ln in src]
    out, dropped = trim(lines, a.head, a.tail, a.context, a.max_lines)
    print("\n".join(out))
    print(f"[logtrim: {len(lines)} lines in, {len(out)} out, {dropped} dropped]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
