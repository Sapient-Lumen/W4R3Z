# Memory Observability Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0084 Memory Observability Kit**.

## Core schemas

- `capture-scope.policy.schema.json`
- `symbolization-fidelity.report.schema.json`
- `regression-gate.policy.schema.json`

## Scenario families

- `alloc_count_flat_but_peak_rss_regresses/` — allocation-count stability hides retained-memory or RSS growth.
- `dhat_scope_guard_ends_before_background_phase/` — scoped profiling misses the interesting background phase unless boundaries are explicit.
- `jemalloc_stats_present_but_callsite_attribution_missing/` — allocator stats exist, but they do not imply callsite-level attribution.

The point of this fixture pack is to stop future passes from flattening:

- scope boundaries,
- backend capabilities,
- symbolization quality,
- and release-gating decisions

into one fake “we profiled memory” story.
