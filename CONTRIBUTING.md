# Contributing

Thanks for helping. The skill is deliberately small at the top and deep underneath, so contributions follow a few rules.

1. **Keep `SKILL.md` lean** (≤300 lines; the self-check enforces it). Put detail in `references/`, and route to it from the table in `SKILL.md`.
2. **Explain why**, not just what. Instructions that carry a reason generalise better than bare commands.
3. **Original wording only.** Ideas from other projects are welcome; copied text, data or code is not. State the idea and its source in the PR.
4. **No unmeasured claims.** Do not add token-saving percentages or "works equally on every model" statements without a reproducible measurement attached.
5. **Scripts** use only the Python standard library, are read-only by default, and need tests in `tests/`.
6. **Archetypes** live in `scripts/charter.py`; run `python skills/complete-developers/scripts/sync_docs.py` to refresh the table in `references/atelier.md`.
7. **Commits** follow Conventional Commits (`feat:`, `fix:`, `docs:` …).

Before opening a PR:

```bash
python -m unittest discover -s tests -v
python skills/complete-developers/scripts/selfcheck.py
```

Bug reports are most useful with: host and model, the prompt you gave, what the skill did, and what you expected.
