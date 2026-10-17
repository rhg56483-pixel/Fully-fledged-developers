# Prove: evidence instead of confident guesses

Contents: evidence ladder · what to check per change · status words · high-signal review · security gate · patch mode (vulnerabilities) · recovery loop · bounded iteration · visual QA · honesty rules

## Evidence ladder

Prefer, in order: runtime observation (you ran it and saw the result) → current source code → primary documentation for external contracts → the user's statement of intent → memory or search snippets (leads, not proof). For a consequential claim keep one pointer: file and symbol, command and result, UI observation, or URL with date. Vendor benchmarks are vendor reports. Resolve conflicting evidence before building on it.

## What to check, per kind of change

| Change | A useful check | Not enough alone |
|---|---|---|
| Content or style | Render it and inspect | Tests that mirror the CSS |
| Calculation or state | Normal and boundary examples | "It parses" |
| Bug fix | Failing reproduction before, passing after | A different-looking diff |
| API or storage | Integration run including a failure path | A mock that always succeeds |
| UI journey | Real interaction (click, type, resize) | "The build passed" |
| Security boundary | Threat-specific check or review | A quiet scanner |
| Performance | Measured before/after in a stated environment | "Feels faster" |
| Game or mod | Play the loop; test join/leave; test with bad input | Reading the code |

## Status words (use exactly these)

**passed** observed and met · **failed** observed and not met · **not run** possible but skipped, say why · **blocked** cannot run here, say what is needed. Do not write "tested", "secure", "accessible", "deployed" or "saved" unless you observed it at that scope. Mark demo data and simulated services in the product and in the report.

## High-signal review of your own diff

Before delivery, read the diff once for problems that *will* matter:

- Code that cannot compile, parse or import; missing or misnamed references.
- Logic that produces wrong results regardless of input.
- Unsafe handling of input, secrets, files, shells, queries, HTML.
- Violations of a rule stated by the user or the repository, which you can quote.
- A requirement from the Prompt Card with no implementation or no check.

Do **not** report style preferences, hypothetical issues that depend on unlikely state, or improvements nobody asked for. If you are not sure an issue is real, verify it or leave it out; false alarms cost trust and tokens.

## Security gate

Run when code touches any row below; fix before delivery or report as a limitation.

| Pattern | Risk | Do instead |
|---|---|---|
| String-built SQL, shell, or path | Injection, traversal | Parameterised queries; argument arrays, no shell; resolve and confine paths |
| `innerHTML`, `eval`, `new Function`, `document.write` with dynamic data | XSS, code execution | `textContent`, templating with escaping, no dynamic code |
| Secrets, tokens or keys in source, client code, logs, URLs | Disclosure | Environment/secret store; rotate anything already leaked |
| Client-supplied prices, roles, damage, ids | Tampering | Recompute and authorise on the trusted side |
| Missing authorisation on an endpoint or remote | Broken access control | Check identity and ownership at the data |
| Unbounded input, uploads, loops, retries | DoS, cost | Limits, timeouts, rate limits, caps |
| Deserialising untrusted data, `pickle`, unsafe YAML | Code execution | Safe parsers with schemas |
| Weak or home-made crypto, `Math.random` for tokens | Predictability | Platform crypto APIs |
| Permissive CORS, disabled TLS checks, `--no-verify` | Exposure | Specific origins; keep verification on |
| Unpinned or unverified dependency | Supply chain | Verify name, version, lockfile |

A clean scan is not proof of safety; say what was reviewed and what was not.

## Patch mode (fixing a reported vulnerability or bug)

Work from this structure; it outperforms a bare "fix this" because it forces the right questions. Give the model (or yourself):

1. **Task:** smallest appropriate fix that preserves intended behaviour.
2. **Finding:** the report, location, and the vulnerable code.
3. **Context:** the callers, the data flow into the sink, existing helpers or validators to reuse (find these with `repomap` + targeted reads or AST/grep, not by pasting the repo).
4. **Rules:** explain the root cause; change as little as possible; keep public interfaces; no unrelated refactors or new dependencies; do not invent functions or APIs; state assumptions; if context is missing, say exactly what.
5. **Output:** root cause → diff → why it works → compatibility risk → regression tests.
6. **Claims:** never say "secure" or "tested" unless you ran the check. A patch candidate is a proposal until its tests pass and the exploit path is shown closed.

## Recovery loop

On failure: capture the *relevant* error (use `logtrim.py`), form one hypothesis with a discriminating check, apply a targeted fix, re-run. After **two** changed attempts at the same failure, change strategy: shrink the reproduction, inspect a different signal, bisect, read the docs for the exact version, or record the blocker and continue unaffected work. Intermittent failures need controlled reruns and their results kept, not a lucky pass.

## Bounded iteration

Loops that retry until "done" are only safe with a defined stop: an observable completion check (tests pass, screenshot matches the card), a maximum number of iterations, and a rule for what to report when the cap is hit. State them before starting. Do not build self-restarting loops without host support and an explicit user request.

## Visual QA (design work)

Run the critique protocol in `atelier.md`. Then verify: no horizontal scroll at 360 px; text pairs pass `contrast.py`; visible focus ring on every control; keyboard path through the main journey; reduced-motion respected; images have alternatives; long content and empty states handled; dark and RTL re-checked if offered. If you cannot render, report visual QA as **not run**.

## Honesty rules

Never invent logs, screenshots, coverage numbers, citations, saved files or URLs. Never weaken a check to get green. If credentials or permissions block an integration, finish the independent work and state exactly what the user must activate. If you cannot do something in this environment (no browser, no network, no execution), say so and mark the output unexecuted.
