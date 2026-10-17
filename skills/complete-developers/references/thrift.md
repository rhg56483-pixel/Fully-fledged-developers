# Thrift: the token economy system

Contents: principle · where tokens leak · the twelve mechanisms · budgets by lane · cheapest sufficient action table · the ledger · session patterns · measuring · what never to economise on

## Principle

Tokens are spent on three things: **reading** (context in), **thinking and writing** (output), and **repeating** (re-reading, re-explaining, re-trying). Quality comes from judgement, checks and good decisions; it does not come from volume. So: spend heavily on decisions and verification, and almost nothing on ceremony, repetition and dumping. The system below cuts the second kind of spend and leaves the first alone. No fixed percentage is promised; savings depend on the task and the habits it replaces. Measure (below).

## Where tokens leak

Opening whole directories to "get a feel" · re-reading unchanged files · pasting full logs, lockfiles, bundles or JSON · reprinting a whole file to change one line · long plans and recaps nobody uses · explaining the method instead of showing the work · retrying the same failing approach · loading every reference "just in case" · fictional specialist panels and self-ratings · essays in the final answer.

## The twelve mechanisms

1. **Lane routing.** Spark / Craft / Atelier chosen from the task. Most work is Spark or Craft; Atelier only when visual quality or scale justifies it.
2. **Progressive loading.** Metadata always; core `SKILL.md` on trigger; references only when the step is reached, at most two at once; scripts run without being read. Unread files cost nothing.
3. **Map before read.** `python scripts/repomap.py <dir>` (tree, line counts, symbols) tells you *which* file and *which* function matter. Then read a range around the symbol (for example 60 lines), widening only if needed. Prefer search for an identifier over opening a file to look for it.
4. **Price before reading.** `python scripts/tokencount.py <paths> --top 10` shows what is expensive. Skip or sample generated, minified, lock and data files; read their schema, not their contents.
5. **No re-reads.** Record paths already read and their conclusion in the ledger; re-read a file only if it may have changed (you or a tool edited it, or time passed).
6. **Telegraphic cards.** The Prompt Card is fragments, not prose: about 120 words for medium work. Plans are numbered one-liners. State the decision and a short reason, not the deliberation.
7. **Edit by diff.** Targeted replace/patch for existing files. A whole file is written once, when it is new, and not echoed back in chat.
8. **Trim tool output.** Pipe long commands through `logtrim.py`; use `--quiet`, `-q`, `head`, `tail`, `grep -n`, `git diff --stat` first and the full diff only for files you must inspect. Keep the decisive error and its context, drop the repetition.
9. **Batch independent work.** Independent reads and searches in one step; dependent edits and checks in order. Do not run the full suite after a one-line text change; run the check that covers the change.
10. **Ledger, not diary.** Keep resumable state to ≤40 lines of *current* facts and the next action; replace stale lines, do not append history. Put detail in the project files (README, tests), not in chat.
11. **Short replies, code in files.** Final answer about 12 lines: result, how to run, verified, limits, next step. No recap of what the user just read, no restating the card, no apology paragraphs.
12. **Stop rules.** Stop at acceptance. Cap elective polish at two passes after acceptance. After two failed attempts change the strategy. Never loop without a completion check and a maximum.

## Budgets by lane (heuristics, adjust with evidence)

| Lane | Reads | Output | Checks |
|---|---|---|---|
| Spark | 1–3 targeted ranges | diff + 3-line reply | the one check that covers the edit |
| Craft | map + ≤10 ranges; ≤2 references | card ≈120 words, plan ≤7 lines, code in files, ≈12-line reply | per-slice check + final journey check |
| Atelier | map + ≤15 ranges; ≤3 references | + 3 thumbnails, charter, critique | + visual QA and the design checklist |

If a budget is tight (small context, cost limit), shrink the *slice size*, not the checks: do a thinner vertical slice that still passes its check, then continue.

## Cheapest sufficient action

| You need to know | Do this, not that |
|---|---|
| What is in this repo | `repomap.py`, not opening folders |
| Where something is defined | search for the identifier, then read ±30 lines |
| Whether a file is worth opening | `tokencount.py` |
| Why the build failed | `cmd 2>&1 \| python scripts/logtrim.py`, not the full log |
| What changed | `git diff --stat`, then diff of only the relevant files |
| Whether a colour pair passes | `contrast.py`, not reasoning about luminance |
| Which design tokens to use | `charter.py`, not hand-picking and re-checking |
| What an external API accepts | the installed package's types or docs for that call, not the whole docs site |
| What was decided earlier | the ledger, not re-deriving |

## The ledger (`.cd/ledger.md`)

```
GOAL      one line
CARD      path or 3-line digest of the Prompt Card
DONE      slices finished, each with evidence pointer (cmd/file/observation)
NOW       the slice in progress and its check
NEXT      the single next action
READ      paths already read → one-line conclusion
DECISIONS irreversible or surprising choices, one line each
BLOCKERS  what is missing and what it needs
```

Rewrite it at milestones and before the context gets tight. On resume, trust it as a lead, re-check anything that may have changed, then continue from NEXT. Keep it out of version control unless the user wants it there.

## Session patterns

- **Long session:** after each milestone, rewrite the ledger and drop details that live in files. If context is about to roll over, persist goal, constraints, assumptions, done, evidence, blockers, next action and key paths first.
- **Small-context model:** Spark or thin Craft slices; one acceptance check at a time; no references beyond one; explicit input/output for each step; repomap output capped with `--budget 1500`.
- **Parallel agents:** only when the host supports them, tasks are independent and the speed-up outweighs duplicated context. Give each a compact assignment and merge evidence; never fake agents in a monologue.
- **Repeated corrections:** when the user corrects the same thing twice, write it as a one-line rule in `.cd/profile.md` so it is never paid for again.

## Measuring honestly

When the host exposes usage, record input, output and cached tokens, tool calls, time and passed checks for a task with and without these habits. Compare like with like (same task, same model). Estimates from `tokencount.py` are ±25% and guide decisions, not billing. Do not report savings you did not measure.

## What never to economise on

Requirements from the card · the check that proves the central journey · security gate on risky code · accessibility floor (contrast, focus, keyboard, labels) · honest labelling of demo data · the user's explicit constraints. If a cut would remove one of these, spend the tokens.
