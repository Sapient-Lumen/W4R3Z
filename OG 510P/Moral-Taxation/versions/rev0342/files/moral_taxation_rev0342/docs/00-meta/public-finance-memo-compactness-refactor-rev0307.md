# rev0307 public-finance memo compactness refactor

Rev0307 addresses the next bloat surface after accountability capsules: public-finance-core route memos were still carrying local anti-pattern lists and change-trigger lists even though the cube now has compressed `anti_pattern` and `review_trigger` axes.

## Change

- Rewrote legacy public-finance `Anti-patterns` sections into `Failure-mode capsule` sections backed by each route record's cube `anti_pattern` axes.
- Rewrote legacy public-finance `What would change the recommendation` sections into `Recalibration trigger capsule` sections backed by each route record's cube `review_trigger` axes.
- Preserved source continuity in the new capsules so footnote definitions remain live and source orientation is not lost.
- Left substantive ladders, option scans, default tables, and provisional recommendations intact.

## Metrics

| Metric | Value |
|---|---:|
| Public-finance docs touched | 26 |
| Legacy anti-pattern sections before | 24 |
| Legacy change-trigger sections before | 26 |
| Legacy anti-pattern sections remaining | 0 |
| Legacy change-trigger sections remaining | 0 |
| Public-finance route-memo bytes before | 338257 |
| Public-finance route-memo bytes after | 314599 |
| Public-finance route-memo bytes saved | 23658 |
| Trigger/failure section bytes before | 40668 |
| Trigger/failure capsule bytes after | 17010 |
| Trigger/failure section bytes saved | 23658 |

## Rule going forward

When the cube already holds the controlled failure-mode and review-trigger vocabulary, public-finance route memos should keep only a compact capsule and any truly route-specific exception. They should not rebuild a local taxonomy of anti-patterns or reopening conditions.
