# 885 — Platform sampling historical CSV compaction and size-budget refactor

**Track:** Shared / Source maintenance / Release size
**Status:** v858 audit/refactor companion

rev0858 removes repeated historical platform-source sampling CSVs from rev0846 through rev0857. Those CSVs duplicated bounded platform/UI/vendor sample rows across many releases, were not linked from docs, and consumed release-size budget without improving current source maintenance.

Kept surfaces:

```text
artifacts/reports/platform-source-sampling-plan-rev0845.csv
artifacts/reports/platform-source-sampling-plan-rev0858.csv
artifacts/reports/platform-source-sampling-plan-rev0858.json
artifacts/reports/platform-sampling-historical-csv-compaction-rev0858.json
```

The rev0845 CSV remains because it is the design-anchor report referenced by `docs/850-platform-source-maintenance-sampling-plan-and-no-linear-review.md`. The current rev0858 CSV remains because it is the actionable queue for this release. The intervening JSON summaries preserve release-level counts without carrying repeated row-level CSV bodies.

Boundary: this compaction does not validate platform/vendor sources, does not alter source-review dates, does not create current voter instruction, and does not change the synthetic-only release posture.
