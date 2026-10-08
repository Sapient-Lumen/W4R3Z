# Kernel slice 0: Debug Acceptance Matrix

## Identity
- candidate: **Feedback / Debug Acceptance Commons**
- governing kernel: `kernels/top-band-v0/debug-acceptance-matrix.v0.md`
- current verdict context: `deepen`
- slice codename: `debug-acceptance-matrix/slice0`

## Why this slice first
This slice should prove that the repo can turn debugging complaints into **replayable tuple truth**.
That is a better first milestone than ranking debuggers or building integrations because the public gap is still acceptance across debugger × OS × capability tuples.

## Exact deliverables
Ship only:
1. `fixtures/core/` with a tiny sync corpus
2. `fixtures/async/` with one small async/state-machine corpus
3. `schemas/debug-session-pack-v0.schema.json`
4. `tuples/` with at least three tuple cards
5. `replays/` with one stored regression replay
6. `docs/unsupported-states.md`

## Acceptance checks
The slice counts as done when it can:
- collect one normalised session pack for each starter fixture family;
- render tuple cards that make visualizer, async, and expression-evaluation posture explicit;
- mark at least one tuple as yellow or red with a concrete unsupported-state receipt;
- and replay one changed result across versions or tools without hand-written narrative as the only proof.

## Proving grounds
Start with:
- two Linux tuples using different debuggers,
- one Windows tuple where capabilities differ materially,
- one async fixture that exercises task/stack visibility.

## Imports and dependencies
Allowed imports:
- debugger-native transcripts or structured exports
- Cargo build receipts for fixtures
- explicit debugger/runtime/version metadata

## Postponed work
Do **not** include yet:
- debugger rankings or “best tool” claims
- automated issue filing
- large UI layers or hosted comparison portals
- broad coverage claims across many languages or IDEs

## Failure receipts
Ship unsupported-state receipts for:
- missing or lossy debugger exports
- tuple-specific visualizer breakage
- async stepping behavior that cannot yet be replayed confidently

## Next-slice trigger
Take slice 1 only after the corpus survives at least one real regression and reviewers can make a tuple-specific decision without falling back to anecdotes.
