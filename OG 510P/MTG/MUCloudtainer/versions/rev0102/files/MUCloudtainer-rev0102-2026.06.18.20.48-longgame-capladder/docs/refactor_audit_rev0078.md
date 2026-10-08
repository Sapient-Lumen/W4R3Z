# rev0078 refactor audit

## What moved into shared code

Familywise interval construction is now a shared population-frontier helper rather than ad-hoc analysis code. The helpers are:

```text
population_familywise_interval_rows
population_familywise_gate_rows
```

This keeps interval recomputation, alpha splitting, gate metadata, and fail-closed behavior in one place.

## Concrete failure prevented

A near-threshold 2×2 test case now shows the intended failure mode: an ordinary per-cell gate can pass while the familywise matrix gate fails on low conservative floor. This means the cube has an executable guard against a future borderline promotion riding on unadjusted multiple comparisons.

## Kept out of scope

No new bulky games or transition traces were generated. rev0078 is a statistical/refactor hardening pass over existing compact population summaries.
