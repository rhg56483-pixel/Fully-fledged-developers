#!/usr/bin/env python3
"""Validate this skill's own structure (used by CI and before publishing).

  python scripts/selfcheck.py            # run from the skill folder or anywhere

Checks: frontmatter (name matches folder, description length), SKILL.md size,
every relative link and every reference named in SKILL.md resolves, scripts
compile, the archetype table in atelier.md is in sync with charter.py, and no
leftover TODO/FIXME markers. Exit code 1 on any failure.
"""
import py_compile
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
errors: list[str] = []


def err(msg):
    errors.append(msg)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data, key, buf = {}, None, []
    for line in m.group(1).splitlines():
        km = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if km and not line.startswith(" "):
            if key:
                data[key] = " ".join(buf).strip()
            key, buf = km.group(1), [km.group(2).lstrip(">-| ").strip()]
        else:
            buf.append(line.strip())
    if key:
        data[key] = " ".join(buf).strip()
    return data


def main():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        err("SKILL.md: missing frontmatter")
    else:
        if fm.get("name") != SKILL.name:
            err(f"name {fm.get('name')!r} != folder {SKILL.name!r}")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm.get("name", "")):
            err("name must be lowercase letters, digits, hyphens")
        d = fm.get("description", "")
        if not 50 <= len(d) <= 1024:
            err(f"description length {len(d)} outside 50..1024")
        if "<" in d or ">" in d:
            err("description must not contain angle brackets")
    lines = text.count("\n")
    if lines > 300:
        err(f"SKILL.md has {lines} lines (>300); move detail into references/")
    for path in SKILL.rglob("*.md"):
        body = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body):
            if re.match(r"^(https?:|mailto:)", target):
                continue
            if not (path.parent / target).resolve().exists():
                err(f"{path.relative_to(SKILL)}: broken link {target}")
        for ref in re.findall(r"`((?:references|scripts|assets)/[\w./-]+)`", body):
            if "<" in ref or "*" in ref:
                continue
            if not (SKILL / ref).exists():
                err(f"{path.relative_to(SKILL)}: missing file {ref}")
        if re.search(r"\b(TODO|FIXME|XXX)\b", body):
            err(f"{path.relative_to(SKILL)}: leftover TODO/FIXME")
    for py in (SKILL / "scripts").glob("*.py"):
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            err(f"{py.name}: {exc.msg}")
    try:
        import charter
        table = charter.archetype_table()
        atel = (SKILL / "references" / "atelier.md").read_text(encoding="utf-8")
        m = re.search(r"<!-- archetypes:start -->\n(.*?)\n<!-- archetypes:end -->", atel, re.S)
        if not m or m.group(1).strip() != table.strip():
            err("atelier.md archetype table out of sync: run scripts/sync_docs.py")
    except Exception as exc:  # noqa: BLE001
        err(f"charter import failed: {exc}")
    for e in errors:
        print("FAIL", e)
    print("selfcheck:", "FAILED" if errors else "ok", f"({lines} lines in SKILL.md)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
