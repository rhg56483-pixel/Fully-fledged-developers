# Ship: hand off so the user can run it, trust it and continue

Contents: the delivery reply · project README · ledger and charter files · release notes · commits · when blocked

## The delivery reply (about 12 lines)

1. **What exists:** the artifact or changed project, in one or two sentences.
2. **Run it:** the exact command or file to open (one path, no tour).
3. **Verified:** each acceptance check with passed / failed / not run / blocked.
4. **Simulated or missing:** demo data, mock payments, placeholder content, unconfigured keys; what the user must supply.
5. **Assumptions you made** that they may want to reverse.
6. **Next step:** the single best one.

Write in the user's language. Tables only when they carry real comparison. Do not repeat code the user can open, do not narrate the method, do not thank or apologise at length. If you published or copied files, point to them; if nothing could be executed, say so first.

## Project README (when the project is large enough to hand over)

Keep it to what a stranger needs in five minutes: what it is, how to run it, how to configure it (with `.env.example` and the meaning of each key), how to test it, folder map in 5–10 lines, known limits. No marketing copy, no badges that point nowhere, no invented screenshots.

## Files this skill creates

- `.cd/profile.md`: standing preferences. Short bullets, each one the user's own words or a rule they repeated.
- `.cd/charter.md`: the design charter from `charter.py`, edited as the design evolves; page exceptions at the bottom.
- `.cd/ledger.md`: resumable state (`thrift.md`). Replace, do not append.

Ask before adding `.cd/` to a repository that is not clearly the user's own, and mention it in the delivery reply when you create it.

## Release notes

When the user asks for notes or a changelog, run `python scripts/changelog.py [--since <tag>] [--version X.Y.Z]` and edit the draft: lead with what users can now do, group by Breaking changes, Features, Fixes, Performance; credit issues or PRs if known; keep internal chores out. If commits are not conventional, the script puts them under Other; rewrite those lines by hand from the diff rather than guessing. The draft reports what commit messages claim, not what was tested.

Versioning: breaking change → major; new capability → minor; fixes → patch. Say which and why. Tag only when the user asks for a release; never publish, push or create releases on your own.

## Commits and pull requests

If the repository enforces a convention, follow it exactly (see `build.md`, contract-first). Otherwise use Conventional Commits: `type(scope): imperative summary` under about 72 characters, body explains *why*, footer for `BREAKING CHANGE:` or issue links. One logical change per commit. A PR description lists what changed, how it was verified, and risk. When two types fit, say which you chose and why.

## When blocked

Deliver the independent work as partial work and label it partial. Name the smallest next action for the user ("add your API key to `.env`", "run `npm install` and tell me the first error"), preserve everything finished, and do not pretend completion to look done.
