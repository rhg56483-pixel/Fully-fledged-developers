#!/usr/bin/env python3
"""Install, update or remove this skill for one or more agent hosts.

  python install.py --host claude                 # ~/.claude/skills/complete-developers
  python install.py --host claude --scope project # ./.claude/skills/...
  python install.py --host all --mode link        # symlink instead of copy (edits stay live)
  python install.py --dest /custom/skills         # any folder your tool reads
  python install.py --host claude --uninstall
  python install.py --host all --dry-run          # show what would happen

Safe by design: an existing install is moved to <name>.bak-<timestamp> first,
nothing outside the target folders is touched, and no network is used.
Paths follow each tool's documented convention at the time of writing; if your
tool differs, use --dest. Restart the tool afterwards so it re-scans skills.
"""
import argparse
import os
import shutil
import sys
import time
from pathlib import Path

NAME = "complete-developers"
HERE = Path(__file__).resolve().parent
SKILL_SRC = HERE.parent  # .../skills/complete-developers (this script lives in scripts/)

HOSTS = {  # host: (user dir, project dir)
    "claude": ("~/.claude/skills", ".claude/skills"),
    "opencode": ("~/.config/opencode/skills", ".opencode/skills"),
    "agents": ("~/.agents/skills", ".agents/skills"),  # open standard; read by Codex in repos
    "codex": ("~/.codex/skills", ".codex/skills"),  # legacy/CODEX_HOME location
    "gemini": ("~/.gemini/skills", ".gemini/skills"),  # community convention; verify in your tool
}
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "tests")


def targets(args):
    if args.dest:
        return [Path(args.dest).expanduser() / NAME]
    names = list(HOSTS) if args.host == "all" else [args.host]
    out = []
    for h in names:
        user, proj = HOSTS[h]
        base = Path(user).expanduser() if args.scope == "user" else Path.cwd() / proj
        out.append(base / NAME)
    return out


def remove(path: Path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", choices=[*HOSTS, "all"], default="claude")
    ap.add_argument("--scope", choices=("user", "project"), default="user")
    ap.add_argument("--mode", choices=("copy", "link"), default="copy")
    ap.add_argument("--dest")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    if not (SKILL_SRC / "SKILL.md").is_file():
        print(f"error: SKILL.md not found next to {SKILL_SRC}", file=sys.stderr)
        return 2
    for t in targets(a):
        if a.uninstall:
            print(f"{'would remove' if a.dry_run else 'removing'}: {t}")
            if not a.dry_run and (t.exists() or t.is_symlink()):
                remove(t)
            continue
        print(f"{'would install' if a.dry_run else 'installing'} ({a.mode}): {t}")
        if a.dry_run:
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        if t.exists() or t.is_symlink():
            bak = t.with_name(f"{t.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            t.rename(bak)
            print(f"  previous install kept at {bak}")
        if a.mode == "link":
            os.symlink(SKILL_SRC, t, target_is_directory=True)
        else:
            shutil.copytree(SKILL_SRC, t, ignore=IGNORE)
    print("done. Restart your tool so it re-scans skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
