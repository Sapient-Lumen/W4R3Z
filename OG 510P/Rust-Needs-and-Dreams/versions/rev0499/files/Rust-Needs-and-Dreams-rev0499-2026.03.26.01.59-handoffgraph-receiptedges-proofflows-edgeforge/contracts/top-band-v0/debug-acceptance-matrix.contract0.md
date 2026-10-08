# Kernel interface contract 0: Debug Acceptance Matrix

## Identity
- candidate: **Feedback / Debug Acceptance Commons**
- governing kernel: `kernels/top-band-v0/debug-acceptance-matrix.v0.md`
- governing slice: `slices/top-band-v0/debug-acceptance-matrix.slice0.md`
- current verdict context: `deepen`
- contract codename: `debug-acceptance-matrix/contract0`

## Contract scope
Fix the first explicit surface for collecting debugger results into **session packs, tuple cards, replay results, and matrix summaries**.
This contract is for acceptance truth, not for selecting a universal “best debugger”.

## Public surfaces
### Commands
1. `debug-accept collect --fixture <id> --tuple <tuple-id> --out <session.json>`
2. `debug-accept tuple-card --session <session.json> --out <tuple-card.md|json>`
3. `debug-accept replay --baseline <session.json> --candidate <session.json> --out <replay.json>`
4. `debug-accept matrix --tuples <glob> --out <matrix.md|json>`

### Rendered/operator surfaces
- one normalized debug session pack per run
- one tuple card with explicit capability posture
- one replay result artifact for regressions or improvements
- one unsupported-state receipt when evidence is partial

## Required inputs
- fixture identity
- debugger identity and version
- OS / target environment identity
- Rust toolchain identity
- runtime identity when relevant (for async fixtures)
- debugger-native transcript or exported evidence
- optional visualizer evidence or screenshots/transcripts references

## Emitted artifact families
- `debug-session-pack/v0`
- `debug-tuple-card/v0`
- `debug-replay-result/v0`
- `unsupported-state-receipt/v0`

Minimum tuple-card fields should include:
- tuple id
- fixture family
- debugger / OS / runtime versions
- stepping posture
- visualizer posture
- async/task visibility posture
- Rust expression evaluation posture
- known caveats
- verdict color / status with receipt links

## Stable imports
Allowed stable imports:
- Cargo build receipts for fixtures
- debugger/runtime/version metadata
- text transcripts or debugger-provided exports

## Optional experimental imports
Allowed but caveated imports:
- IDE-specific metadata exports
- screenshots or structured visualizer snapshots
- auxiliary runtime traces for async fixtures

Rule: tuple cards must say when a result depends on a non-portable export format or manual observation.

## Versioning and compatibility posture
- `contract0` is tuple-additive.
- Unknown tuple capability fields must not break readers.
- A missing capability field must not be silently interpreted as “green”.
- Manual-observation-only results must remain labeled as such.

## Negative states / receipts
The contract must preserve receipts for:
- missing or lossy debugger exports
- visualizer failures
- async stepping or task-visibility gaps
- expression-evaluation unsupported states
- replay mismatches that cannot yet be normalized confidently
- tuple runs where evidence exists only as partial transcripts

## Proving-ground invocation
A valid proving-ground run should include:
1. two Linux tuples using different debuggers;
2. one Windows tuple with materially different capability posture;
3. one async fixture that generates at least one yellow or red receipt;
4. one replay comparing baseline versus changed behavior.

## Refused expansions
Do **not** treat `contract0` as permission for:
- debugger rankings,
- auto-filed upstream issues,
- hosted comparison portals,
- or coverage claims across the whole ecosystem.

## Exit criteria
This contract may widen only after:
- at least one real regression or improvement is replayed successfully,
- reviewers can make tuple-specific decisions without anecdotal prose doing all the work,
- and unsupported-state receipts remain intact across tools and operating systems.
