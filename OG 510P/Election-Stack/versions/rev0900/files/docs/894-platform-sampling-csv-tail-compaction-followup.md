# 894 — Platform-sampling CSV tail compaction follow-up

**Track:** Shared / Source maintenance / Release gate

rev0861 removes duplicated historical platform-source sampling CSV bodies for rev0859 and rev0860 while preserving JSON summaries, the rev0858 compaction anchor, and the current rev0861 CSV.

The source-review meaning does not change: expired review windows remain zero, current-authority rows due within 30 days remain zero, and the remaining near-term pressure is mostly platform/UI/vendor source sprawl.

Audit: `artifacts/reports/platform-sampling-csv-tail-compaction-rev0861.json`.

Boundary: this is size-budget hygiene, not a source refresh or authority review.
