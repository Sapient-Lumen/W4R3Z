# Scenario — alloc count flat but peak RSS regresses

## Situation

Two releases show nearly identical allocation counts during a representative workload, but the newer release retains more memory and ends with materially higher peak RSS.

## Why this fixture exists

This is the canonical warning against treating allocator event counts as the whole memory story.
A memory-observability kit should make it easy to say:

- `alloc_count` remained stable,
- `peak_rss_bytes` regressed,
- live-memory or retention evidence is incomplete or present,
- and the regression gate should key off RSS or post-phase live bytes instead of raw count totals.

## Artifact expectations

- `capture-scope.policy` should pin the representative workload window.
- `regression-gate.policy` should name `peak_rss_bytes` or `live_bytes_after_phase` as authoritative.
- `symbolization-fidelity.report` may still be partial; a useful gate does not require perfect callsite attribution.
