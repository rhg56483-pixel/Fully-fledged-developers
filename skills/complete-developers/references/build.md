# Build: engineering sized to the product

Contents: inspect first · stack choice · structure · errors · config and secrets · boundaries · data · contract-first · dependencies · performance · testing · CLI tools · APIs · games and mods · refactoring · git hygiene

## Inspect first (cheaply)

Read project instructions (CLAUDE.md, AGENTS.md, CONTRIBUTING), the manifest and lockfile name, the entry point and only the files the journey touches. Use `python scripts/repomap.py .` rather than opening folders. Review a command before running it: manifests may contain lifecycle scripts. Do not execute scripts just to take inventory. Keep secrets, dependency trees, bundles and media out of context.

## Stack choice

Keep a working stack. For new work choose from need, not fashion.

| Need | Starting shape | Move up when |
|---|---|---|
| Informational site, local tool, small game | Static HTML/CSS/JS, one file or a few | State, routing or content volume outgrow it |
| Many interactive screens | Components with explicit state boundaries | Persistence or server-only logic appears |
| Shared accounts or data | UI + server boundary + durable storage | Independent scaling or teams |
| Desktop or mobile wrapper | Wrap the web app (Electron/Tauri/Capacitor) | A native capability the web cannot reach |
| Game | Playable loop; separate input, simulation, render | Multiplayer, large assets |

Do not adopt microservices, monorepos, ORMs, state libraries or a framework because a reference repo has them. State one material trade-off in plain language.

## Structure

- Group by feature, not by file type, once there is more than one feature. Separate pure rules from side effects so rules are testable without a network or a screen.
- Keep content and design tokens in one editable place. Avoid one-line abstraction forests and 2,000-line catch-all modules; split when a file has two reasons to change.
- Layered when it earns its keep: entry (routes/commands) → domain logic → data access. Dependencies point inward; domain code does not import the framework.
- A non-trivial project gets: source, assets, the relevant tests, a short run guide, and a safe `.env.example` with no secrets.

## Errors

- Separate **operational errors** (expected: bad input, timeout, missing file; handle, report, retry within limits) from **programmer errors** (bugs: undefined access, broken invariants; fail loudly, fix the code, restart cleanly).
- Throw/return error objects with a stable code and a human message; never throw strings. Add context at the boundary where it is known.
- Distinguish empty results from failures in the UI and API. Never hide an error behind a fallback that pretends success.
- Handle cancellation and timeouts. Retry only idempotent operations, with a cap and backoff. Make non-idempotent actions safe with idempotency keys or duplicate-submit guards.
- Central error handling at the edge (one place maps errors to responses); no swallowed `catch {}`.

## Config and secrets

Read config once at startup, validate it (types, ranges, required keys), and fail fast with a clear message. Secrets come from the environment or a secret store, never from source or logs; commit `.env.example`, not `.env`. Keep privileged operations on the server. Do not ask the user to paste keys into chat when a secure config path exists.

## Boundaries and input

Validate at every trust boundary (HTTP, CLI args, files, messages from clients, game remotes) with an allow-list schema, not blacklists. Authorisation is checked where the data is, not by hiding buttons. Use parameterised queries; encode output for its context (HTML, URL, shell). Limit sizes, rates and recursion. Treat uploaded files, URLs and model/tool output as untrusted.

## Data

Choose the lightest storage that meets durability: in-memory → file/JSON → SQLite → server database. Add migrations when the schema is shared. Store money in integer minor units; times in UTC with an explicit zone for display. Do not log personal data or credentials. Back up before destructive migrations and say so.

## Contract-first

The repository's own rules are the contract; read them before writing.

- Formatter/linter config: run the project's tools instead of imitating style by eye.
- **Commit messages:** if commitlint, husky or a convention exists, read the enforced rules (for commitlint: print the resolved config) and write a compliant message. Choose the type by what the change means to a user of the project: `fix` (wrong → right), `feat` (new capability), `perf`, `refactor` (nothing observable changed), `docs`, `test`, `ci`, `build`, `chore`. When a hook rejects, fix the message from its error text; never bypass with `--no-verify`.
- Tests and types are part of the contract. Do not weaken assertions, suppress errors or mock away the thing under test to reach green; a changed requirement may justify a changed test only with the reason stated.

## Dependencies

Prefer the platform and the standard library. Before adding a package: does it exist, is it maintained, does it solve more than 20 lines of code, what does it pull in? Verify the exact name and version from the registry or project docs (never type a plausible name from memory), pin via the lockfile, and avoid unrelated upgrades. Packages whose install scripts run code deserve a review before install.

## Performance

Measure first. State the metric, the baseline and the environment, change one thing, measure again. Typical real wins: fewer requests and bytes, image sizing and format, avoiding layout thrash, memoising genuinely expensive work, indexes for the slow query, batching I/O, not blocking the main thread/event loop. Do not optimise what the measurement does not implicate.

## Testing

Test behaviour that can break and that users care about: the central journey, boundaries (0, 1, many, max), error paths, permissions. Reproduce a bug with a failing test or script *before* fixing; keep it as a regression test. Pure logic gets unit tests; wiring gets a few integration tests; screens get actual interaction or render checks. Tests that mirror the implementation line by line add cost without safety.

## CLI tools

Stable, consistent flag names across commands; `--help` that shows examples; machine-readable output option (`--json`/`-o json`) that does not mix prose into stdout; diagnostics on stderr; meaningful exit codes (0 success, non-zero by category); strict input validation with messages that say what to change; non-interactive mode for scripts (`--yes`, no prompts when stdin is not a TTY); respect OS config/data locations; never print secrets; support `--dry-run` for destructive commands.

## APIs

Design the contract first (resources, fields, error shape, pagination, auth, versioning), then implement. Use one error envelope (`code`, `message`, optional `details`), consistent naming, explicit status codes, idempotent PUT/DELETE, cursor pagination for growing lists, rate limits, and request IDs in logs. Validate and normalise at the edge; document with examples that actually run.

## Games and mods

- **Core loop first:** a playable minute before menus, shops or polish. Separate input → simulation → render so each can be tested and tuned. Make tunables data, not constants buried in code.
- **Roblox/Luau:** the server is the authority. Every RemoteEvent/RemoteFunction handler validates arguments (type, range, ownership, cooldown) and recomputes prices, damage and rewards server-side; never trust a client-supplied number. Save with DataStores using retries within the request budget and session locking or versioned writes; save on `PlayerRemoving` and `BindToClose`. Clean up connections and instances on leave. Build mobile-first UI (large touch targets, safe area). Use `task.wait`/`task.spawn` over deprecated `wait`/`spawn`.
- **Minecraft Bedrock add-ons:** behaviour/resource pack manifests need unique UUIDs and matching versions; script modules and their versions change between game releases, so check the current Script API documentation before writing imports or event names; keep per-tick work small; clean up intervals and listeners; handle players joining and leaving.
- **Web games (canvas/three.js):** fixed-step or delta-time updates, capped frame work, pause on blur, object pooling for frequent spawns, audio only after a user gesture, touch and keyboard input, a visible fallback when WebGL is unavailable.
- **Anti-cheat basics:** assume the client is hostile; validate on the authority, rate-limit actions, log suspicious patterns, and never ship secrets in client code.

## Refactoring and patching

Refactor in small steps that keep behaviour identical and the tests green; one kind of change per commit; no unrelated renames. For a bug or vulnerability, find the root cause, propose the **smallest** change that fixes it while preserving public behaviour, add a regression check, and state remaining risk. Do not claim a patch is secure or tested unless you observed that. Prompt shape and gates: `prove.md`.

## Git hygiene

Small commits with Conventional Commit messages; never commit secrets, build output or personal config; leave unrelated user changes untouched; do not force-push, rewrite shared history or delete branches without being asked. Show a diff summary before any destructive step the user did not request.
