# V0 kernel brief: Debug Acceptance Matrix

## Identity
- candidate: **Feedback / Debug Acceptance Commons**
- macro-program: **Feedback / Debug Acceptance Commons**
- current verdict context: `deepen`
- kernel codename: `debug-acceptance-matrix/v0`

## Why this kernel and not a bigger build
The first honest build is not a new debugger and not a winner-table.
It is a **fixture + replay + tuple-status corpus** that makes debugger support legible across debugger × OS × capability tuples.
That is justified because the public capability bar is already explicit: multi-debugger, multi-OS, visualizers, async support, and Rust-expression evaluation. The missing work is acceptance truth, not more abstract complaint aggregation.
Relevant sources:
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Repo shape
Suggested first repo tree:
- `fixtures/core/` — tiny sync/non-async fixtures exercising common Rust data types
- `fixtures/async/` — async state-machine and task-ownership fixtures
- `fixtures/visualizers/` — collections / enums / strings / smart-pointer inspection fixtures
- `tuples/` — debugger × OS × runtime tuple cards in markdown or JSON front matter
- `replays/` — saved session packs and reproduction scripts
- `crates/debugpack-cli/` — optional CLI for collecting and validating session packs
- `schemas/debug-session-pack-v0.schema.json` — machine-readable export format
- `docs/unsupported-states.md` — canonical yellow/red posture notes

## User surfaces
The first user surfaces should be:
1. `collect` — record a bounded debugging session against a known fixture
2. `validate` — check the session pack against required fields
3. `status` — render tuple cards as `green` / `yellow` / `red` with explicit caveats

Each tuple card should answer:
- debugger name and version
- OS and architecture
- fixture family
- visualizer quality
- async visibility quality
- expression-evaluation posture
- regressions / unsupported states / caveats

## Import seams
The kernel should import:
- debugger-native session transcripts or structured exports where available
- fixture build receipts from Cargo builds
- explicit runtime / target metadata

Avoid assuming one debugger's export format becomes the canon for all.
The matrix should normalize outcomes, not force one tool's internal representation onto the others.

## Proof assets
The kernel should emit:
- one session pack per fixture run
- one tuple card summarizing current posture
- one unsupported-state receipt when something is partial or broken
- one diff when a tuple changes over time

## Proving grounds
Start with:
1. a small Linux tuple set with at least two debuggers
2. one Windows tuple where expression-evaluation or visualizer behavior differs materially
3. one async fixture family where stepping and task identity are visible pain points
4. one regression replay where a toolchain or debugger-version change alters results

## Owner shape / upkeep
Best first owner:
- cross-tool steward group or small coalition of debugger-adjacent maintainers

Immediate upkeep tax:
- debugger-version churn
- OS-version churn
- fixture drift as Rust internals evolve
- session-pack normalization work

## Refused expansions
Do not let v0 become:
- a “best debugger” portal
- a synthetic score that hides unsupported tuples
- a rewrite of debugger internals
- or a claim that anecdotal success on one tuple equals ecosystem acceptance

## Exit criteria
This kernel has earned a stronger next stage when it can show:
- a replayable corpus across multiple tuples
- explicit unsupported-state receipts for the yellow/red space
- at least one meaningful regression-detection loop
- and enough maintained tuple cards that future decisions are based on corpus, not memory

