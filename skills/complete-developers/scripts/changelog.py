#!/usr/bin/env python3
"""Draft release notes from Conventional Commit messages (read-only, uses `git log`).

  python changelog.py                      # since the latest tag (or all history)
  python changelog.py --since v1.2.0 --version 1.3.0
  python changelog.py --repo ../project

Groups: Breaking changes, Features, Fixes, Performance, Refactoring, Docs, Other.
Commits that do not follow the convention land in Other, so nothing is lost.
Review the draft: it reports what the commit messages say, not what was tested.
"""
import argparse
import re
import subprocess
import sys
from datetime import date

HEADER = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<subject>.+)$")
GROUPS = [("feat", "Features"), ("fix", "Fixes"), ("perf", "Performance"),
          ("refactor", "Refactoring"), ("docs", "Docs")]
QUIET = {"chore", "ci", "build", "test", "style"}


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def parse(log: str):
    commits = []
    for chunk in log.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        sha, _, rest = chunk.partition("\x1f")
        subject, _, body = rest.partition("\n")
        commits.append((sha[:7], subject.strip(), body))
    return commits


def build(commits, version=None):
    buckets = {k: [] for k, _ in GROUPS}
    other, breaking = [], []
    for sha, subject, body in commits:
        m = HEADER.match(subject)
        is_break = "BREAKING CHANGE" in body or (m and m.group("bang"))
        if m and m.group("type") in buckets:
            scope = f"**{m.group('scope')}:** " if m.group("scope") else ""
            buckets[m.group("type")].append(f"- {scope}{m.group('subject')} ({sha})")
        elif m and m.group("type") in QUIET:
            continue
        else:
            other.append(f"- {subject} ({sha})")
        if is_break:
            breaking.append(f"- {subject} ({sha})")
    title = f"## {version or 'Unreleased'} · {date.today().isoformat()}"
    out = [title, ""]
    if breaking:
        out += ["### Breaking changes", *breaking, ""]
    for key, name in GROUPS:
        if buckets[key]:
            out += [f"### {name}", *buckets[key], ""]
    if other:
        out += ["### Other", *other, ""]
    if len(out) == 2:
        out.append("_No user-facing changes found._")
    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--since", help="tag/ref to start after (default: latest tag)")
    ap.add_argument("--version")
    a = ap.parse_args(argv)
    since = a.since
    if not since:
        r = subprocess.run(["git", "-C", a.repo, "describe", "--tags", "--abbrev=0"],
                           capture_output=True, text=True)
        since = r.stdout.strip() if r.returncode == 0 else None
    rng = f"{since}..HEAD" if since else "HEAD"
    log = git(a.repo, "log", rng, "--no-merges", "--format=%H%x1f%s%n%b%x1e")
    sys.stdout.write(build(parse(log), a.version))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
