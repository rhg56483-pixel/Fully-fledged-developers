# Hosts and models: adapting without pretending

Contents: what a skill can and cannot do · capability check · scaffolding by model strength · host notes · installing · limits

## What a skill can and cannot do

A skill is instructions plus helper files that load on demand. It improves *consistency*: decomposing, sketching, slicing, verifying and economising happen reliably instead of occasionally. It does not add knowledge or reasoning power the model lacks, it cannot make every model perform alike, and it does not override the host's permissions. Never claim zero errors, equal results across models, or fixed token savings.

## Capability check (once, quietly)

Before promising any step, find out what exists: read/write files, run commands, browser or screenshot, web search, image input, persistent memory, question tool, sub-agents. Plan with what is there:

| Missing | Do instead |
|---|---|
| Cannot run code | Provide code and run instructions marked **unexecuted**; report checks as *not run* |
| No browser/vision | Verify structure and contrast by script; report visual QA as *not run* |
| No file access | Output files in labelled blocks; keep each complete and copy-ready |
| No Python | Skip helper scripts; do the same job with built-in search and ranges |
| No question tool | Put the ≤3 grouped questions in the reply with recommended defaults, and continue with them if unanswered |
| No network | Use installed packages and local docs; do not guess URLs or versions |

## Scaffolding by model strength

Choose by observed reliability on *this* task, not by brand name.

- **Strong model, clear task:** Spark/Craft with minimal narration; bigger slices; the checks do the arguing.
- **Mid-range or new task:** Craft with explicit slices of one acceptance criterion each; write input/output contracts before code; re-check after each slice.
- **Small or unreliable model:** thin slices (one function or one component), one reference loaded, concrete examples copied from the project, checks after every edit, the ledger every few steps, and no multi-file refactors without a plan. Tell the user the limits instead of promising polish.

Increase slice size only while checks stay green; shrink it when errors accumulate.

## Host notes

- **Claude.ai / Claude apps:** inline visuals and artifacts are good for sketches and single-file pages; keep long code in an artifact or file rather than chat. Ask grouped questions through the question tool when available.
- **Claude Code, OpenCode, Codex CLI and similar agents:** read project instruction files first; use real file edits and the project's test commands; helper scripts run from the skill folder (use the path the host reports for the skill's base directory). Skills are re-scanned at session start; restart after installing.
- **Chat-only assistants without skills support:** paste `SKILL.md` as a system or project instruction, and paste a reference only when its step arrives; use the Prompt Card format manually.

## Installing

`python scripts/install.py --host claude` (or `opencode`, `agents`, `codex`, `gemini`, `all`) copies the skill into the user or project skills folder, keeping a timestamped backup of any previous install; `--mode link` symlinks it, `--dest <dir>` targets any folder, `--uninstall` removes it, `--dry-run` previews. Folder conventions differ between tools and change over time, so if a tool does not pick the skill up, check its documentation for the current skills path and use `--dest`.

Manual install: copy the `complete-developers/` folder (the one containing `SKILL.md`) into the tool's skills directory, then start a new session and mention the skill by name once to confirm it loaded.

## Limits worth stating

Automatic triggering depends on the host and the model; naming the skill the first time removes doubt. The numeric budgets here are starting heuristics, not measured optima. Design taste cannot be fully automated: the charter and critique make results consistent, but a person's eye is the final reviewer.
