#!/usr/bin/env python3
"""Map a codebase in tens of lines instead of reading it in thousands.

  python repomap.py .                      # tree + line counts + top symbols
  python repomap.py src --max-files 80 --symbols 6
  python repomap.py . --budget 1500        # keep output under ~1500 tokens

Read-only: lists file names, line counts and declared symbols (functions,
classes, exports). It never runs project code, installs anything or opens
secret-like files (.env, keys, credentials). Use it to choose WHICH files and
line ranges to read, then read only those.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__", "target",
             ".next", ".nuxt", ".cache", "vendor", ".idea", ".vscode", "coverage", "Pods", "bin",
             "obj", ".gradle", ".dart_tool", ".cd"}
SECRET_RE = re.compile(r"(^\.env|\.pem$|\.key$|\.p12$|\.pfx$|id_rsa|id_ed25519|credentials|secrets?\.)",
                       re.I)
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".lua", ".luau", ".go", ".rs",
            ".java", ".kt", ".cs", ".php", ".rb", ".swift", ".c", ".h", ".cpp", ".hpp", ".sh",
            ".html", ".css", ".scss", ".vue", ".svelte", ".json", ".yaml", ".yml", ".toml", ".md"}
ENTRY_NAMES = {"main.py", "app.py", "index.js", "index.ts", "main.ts", "main.js", "server.js",
               "main.go", "main.rs", "Program.cs", "main.lua", "init.server.lua", "init.client.lua",
               "index.html", "manifest.json", "package.json", "pyproject.toml", "go.mod", "Cargo.toml"}

PATTERNS = {
    "js": [re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)"),
           re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)"),
           re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>")],
    "lua": [re.compile(r"^\s*(?:local\s+)?function\s+([A-Za-z_][\w.:]*)"),
            re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=\s*function\s*\(")],
    "go": [re.compile(r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)"), re.compile(r"^type\s+([A-Za-z_]\w*)\s+(?:struct|interface)")],
    "rs": [re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)"),
           re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+([A-Za-z_]\w*)")],
    "jvm": [re.compile(r"^\s*(?:public|private|protected|internal|static|final|open|abstract|override|\s)*"
                       r"(?:class|interface|object|enum|record)\s+([A-Za-z_]\w*)"),
            re.compile(r"^\s*(?:public|private|protected|internal|static|override|suspend|\s)+"
                       r"[\w<>\[\],.? ]+\s+([a-z_]\w*)\s*\([^;]*\)\s*(?:\{|:|=)")],
    "php": [re.compile(r"^\s*(?:abstract\s+|final\s+)?class\s+([A-Za-z_]\w*)"),
            re.compile(r"^\s*(?:public|private|protected|static|\s)*function\s+([A-Za-z_]\w*)")],
    "rb": [re.compile(r"^\s*(?:def|class|module)\s+([A-Za-z_][\w.:?!]*)")],
    "sh": [re.compile(r"^\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\)\s*\{")],
    "vue": [re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)")],
}
EXT_LANG = {".js": "js", ".jsx": "js", ".ts": "js", ".tsx": "js", ".mjs": "js", ".cjs": "js",
            ".vue": "vue", ".svelte": "vue", ".lua": "lua", ".luau": "lua", ".go": "go", ".rs": "rs",
            ".java": "jvm", ".kt": "jvm", ".cs": "jvm", ".php": "php", ".rb": "rb", ".sh": "sh",
            ".swift": "jvm"}


def py_symbols(src: str) -> list[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and not n.name.startswith("_")]
            out.append(f"class {node.name}" + (f"({','.join(methods[:4])}{'…' if len(methods) > 4 else ''})" if methods else ""))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(f"def {node.name}")
    return out


def regex_symbols(src: str, lang: str) -> list[str]:
    pats, out = PATTERNS.get(lang, []), []
    for line in src.splitlines():
        if len(line) > 300:
            continue
        for p in pats:
            m = p.match(line)
            if m:
                out.append(m.group(1))
                break
    return out


def file_symbols(path: str, text: str) -> list[str]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        return py_symbols(text)
    if ext == ".json" and os.path.basename(path) == "package.json":
        try:
            d = json.loads(text)
            bits = [f"name={d.get('name')}"] if d.get("name") else []
            if d.get("scripts"):
                bits.append("scripts=" + ",".join(list(d["scripts"])[:8]))
            return bits
        except ValueError:
            return []
    if ext == ".html":
        m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
        scripts = len(re.findall(r"<script", text, re.I))
        return ([f"title={m.group(1).strip()[:40]}"] if m else []) + ([f"{scripts} script tag(s)"] if scripts else [])
    lang = EXT_LANG.get(ext)
    return regex_symbols(text, lang) if lang else []


def iter_files(root: str):
    for cur, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".") or d in {".github"})
        for f in sorted(files):
            p = os.path.join(cur, f)
            if os.path.islink(p):
                continue
            yield p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--max-files", type=int, default=150)
    ap.add_argument("--symbols", type=int, default=8, help="max symbols shown per file")
    ap.add_argument("--budget", type=int, default=0, help="approximate token cap for the output")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        print(f"error: not a directory: {a.root}", file=sys.stderr)
        return 2

    rows, withheld, skipped_ext, entries = [], 0, 0, []
    for p in iter_files(root):
        rel = os.path.relpath(p, root)
        name = os.path.basename(p)
        if SECRET_RE.search(name):
            withheld += 1
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in CODE_EXT:
            skipped_ext += 1
            continue
        try:
            if os.path.getsize(p) > 1_500_000:
                rows.append((rel, -1, ["(large file, not parsed)"]))
                continue
            with open(p, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        n = text.count("\n") + 1
        syms = file_symbols(p, text) if ext not in {".md", ".css", ".scss", ".yaml", ".yml", ".toml"} else []
        rows.append((rel, n, syms))
        if name in ENTRY_NAMES:
            entries.append(rel)

    total_files = len(rows)
    rows.sort(key=lambda r: (0 if os.path.basename(r[0]) in ENTRY_NAMES else 1, r[0]))
    shown = rows[: a.max_files]
    lines = [f"# repomap: {os.path.basename(root)}  ({total_files} text/code files)"]
    if entries:
        lines.append("entry/config: " + ", ".join(entries[:10]))
    for rel, n, syms in shown:
        head = f"{rel} [{n}L]" if n >= 0 else rel
        if syms:
            more = f" +{len(syms) - a.symbols}" if len(syms) > a.symbols else ""
            head += "  " + ", ".join(syms[: a.symbols]) + more
        lines.append(head)
    if total_files > len(shown):
        lines.append(f"... {total_files - len(shown)} more files (raise --max-files or map a subfolder)")
    if withheld:
        lines.append(f"[{withheld} secret-like file(s) withheld by name]")
    out = "\n".join(lines)
    if a.budget:
        cap = a.budget * 4
        if len(out) > cap:
            out = out[:cap].rsplit("\n", 1)[0] + "\n... [truncated to budget; map a subfolder]"
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
