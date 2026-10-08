# Scenario — dhat scope guard ends before background phase

## Situation

A scoped heap profiler is started for a foreground request path and dropped before a background worker performs the memory-retaining behavior that actually matters.

## Why this fixture exists

This is the canonical warning against profiler runs with unclear phase boundaries.
A memory-observability kit should make it easy to say:

- the backend was valid,
- the scope boundary was too narrow,
- the interesting background phase was excluded,
- and the capture must be re-run or marked `manual_review_required`.

## Artifact expectations

- `capture-scope.policy` should declare whether background phases are in or out.
- `symbolization-fidelity.report` may still be good, but the capture is incomplete.
- `regression-gate.policy` should refuse CI-style confidence when the authoritative phase was not captured.
