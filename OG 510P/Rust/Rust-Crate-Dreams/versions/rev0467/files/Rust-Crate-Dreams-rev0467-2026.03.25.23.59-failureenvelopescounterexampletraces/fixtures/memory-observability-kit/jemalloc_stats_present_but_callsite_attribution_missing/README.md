# Scenario — jemalloc stats present but callsite attribution missing

## Situation

A service can retrieve allocator statistics or dumps, but cannot provide trustworthy callsite-level attribution for the release under review.

## Why this fixture exists

This is the canonical warning against treating backend power as uniform.
A memory-observability kit should make it easy to say:

- allocator stats are present,
- the backend can support high-level memory totals,
- callsite attribution is absent or partial,
- and summary conclusions must stay at the appropriate evidence level.

## Artifact expectations

- `symbolization-fidelity.report` should classify the run as `allocator_stats_only`, `partial_symbols`, or `manual_review_required`.
- `regression-gate.policy` can still gate on `peak_rss_bytes` or dump-growth factors.
- Human summaries should avoid overclaiming root-cause attribution.
