#!/usr/bin/env python3
"""WCAG contrast for opaque sRGB colours.

  python contrast.py "#1A1A1A" "#FAF8F3"
  python contrast.py "#fff" "#0F6B5C" "#777" "#fff"     # several fg bg pairs

Exit code 1 if any pair is below AA for normal text (4.5:1).
Not a validator for gradients, alpha, glass or images: check those visually.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _color import contrast, rate  # noqa: E402


def main(argv):
    if len(argv) < 2 or len(argv) % 2:
        print(__doc__.strip())
        return 2
    worst = 99.0
    for i in range(0, len(argv), 2):
        try:
            ratio = contrast(argv[i], argv[i + 1])
        except ValueError as exc:
            print(f"error: {exc}")
            return 2
        worst = min(worst, ratio)
        flags = " ".join(f"{k}:{'pass' if v else 'FAIL'}" for k, v in rate(ratio).items())
        print(f"{argv[i]} on {argv[i + 1]}  {ratio:.2f}:1  {flags}")
    return 0 if worst >= 4.5 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
