# rev0309 tax-administration access memo, contest, and fallback refactor

Rev0309 addresses the highest-risk remaining bloat surface after rev0308: tax-administration route memos. These routes govern filing channels, refund rails, information-reporting penalties, contest windows, official-error reliance, third-party records, remittance chains, and cashflow timing. Repeated local failure taxonomies made those operational duties harder to see.

## Memo compactness

- Rewrote 11 tax-administration `Anti-patterns` sections into cube-axis-backed `Failure-mode capsule` sections.
- Rewrote 11 tax-administration `What would change the recommendation` sections into cube-axis-backed `Recalibration trigger capsule` sections.
- Added compact accountability capsules to 15 additional tax-administration route memos so every tax-administration route now points to its actor-accountability profile.

## Cube refactor

- Tax-administration route records using `anti_pattern=rent_extraction` before: 16.
- Tax-administration route records using `anti_pattern=rent_extraction` after: 0.
- Tax-administration route records with specialized anti-pattern axes touched: 16.

The replacement values name concrete failures such as refund-rail capture, public-option erasure, vendor lock-in, review desert, settlement hostage, record lock-in, official-looking hallucination, one-way loss recognition, and freeze-by-default. The generic rent frame remains available elsewhere in the cube, but it no longer explains tax-administration access/fallback routes by itself.

## Metrics

| Metric | Value |
|---|---:|
| Tax-administration docs touched | 15 |
| Tax route-memo bytes before | 145987 |
| Tax route-memo bytes after | 143748 |
| Tax route-memo bytes saved | 2239 |
| Legacy tax anti-pattern sections remaining | 0 |
| Legacy tax change-trigger sections remaining | 0 |
| Tax failure-mode capsules | 11 |
| Tax recalibration-trigger capsules | 11 |
| Tax accountability capsules | 17 |

## Rule going forward

Tax-administration access memos should keep the route-specific ladder, option scan, default table, and provisional recommendation, but repeated failure modes, reopening conditions, and accountability handoffs should point to the cube axes and actor-accountability profiles. Tax-administration route records should not collapse access, refund, contest, record, and fallback failures into generic `rent_extraction`.
