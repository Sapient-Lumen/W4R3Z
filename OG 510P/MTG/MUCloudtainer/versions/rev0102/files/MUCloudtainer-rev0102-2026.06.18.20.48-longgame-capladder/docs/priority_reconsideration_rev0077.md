# rev0077 priority reconsideration

The riskiest unfinished issue was not more rollout volume. It was sampling provenance.

Recent revisions correctly showed no promotion under exact maximin, raw-lineage, stratum, boolean, context-normalization, and score-orientation checks. But rev0075 was deliberately adaptive: it selected high-point underpowered cells and then challenged them with more seed-disjoint games. That evidence should not be used to improve a global pooled estimate.

Priority change made in rev0077:

```text
Before: population rows were mostly separated by convention.
After: rows carry an explicit sampling-frame guard before broad pooled gates.
```

The naive contamination comparison shows the concern was real: adding targeted challenge rows would raise the broad conservative LCB by about 0.136. It still does not promote, but a smaller future margin could have become a false confidence path.

Next highest-value work:

1. Add a preregistered full-panel rev0078/79 expansion if runtime allows.
2. Keep targeted challenge evidence separate from full-panel evidence unless inverse-probability/design weights are explicitly modeled.
3. Continue replacing filename/revision conventions with semantic source metadata only where it blocks a concrete failure mode.
