#!/usr/bin/env python3
"""Regenerate the archetype table inside references/atelier.md from charter.py."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import charter  # noqa: E402

p = HERE.parent / "references" / "atelier.md"
s = p.read_text(encoding="utf-8")
new = "<!-- archetypes:start -->\n" + charter.archetype_table() + "\n<!-- archetypes:end -->"
s2 = re.sub(r"<!-- archetypes:start -->.*?<!-- archetypes:end -->", lambda _: new, s, flags=re.S)
p.write_text(s2, encoding="utf-8")
print("atelier.md table", "updated" if s2 != s else "already in sync")
