# rev0079 refactor audit

## What moved into shared code

The population-frontier module now owns two risk-reduction paths that were previously either absent or only implicit:

```text
exact_support_enumeration_maximin
population_hierarchical_familywise_gate_rows
summarize_population_hierarchical_gate
```

`zero_sum_maximin` now uses exact support enumeration for small games with more than two row policies, while still keeping the explicit fictitious-play fallback available when exact enumeration is disabled or a matrix is too large.

## Concrete failure prevented

Two executable tests now cover failure modes that would be easy to miss in registry-only work:

1. A synthetic aggregate-only promotion can pass globally while failing in a bad size stratum. The hierarchical gate marks the overall mandatory decision as not passed.
2. A 3×3 empirical game now takes the exact small-game path by default, with a separate test proving that the fictitious-play fallback still exists when exact enumeration is disabled.

## Artifact discipline

No new raw games, transition traces, or replay JSONL were generated. The revision works from existing compact summaries and writes only gate/audit CSVs plus one small solver diagnostic.
