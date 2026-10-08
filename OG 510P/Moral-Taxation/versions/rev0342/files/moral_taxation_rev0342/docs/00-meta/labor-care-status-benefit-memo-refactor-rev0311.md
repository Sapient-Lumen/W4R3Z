# rev0311 labor/care status, benefit, and memo refactor

Rev0311 addresses the next high-risk family after legal-enforcement: labor, care, and benefits. These routes govern worker status, social-insurance credits, student debt, care-load attribution, child and long-term-care access, platform-worker benefits, data minimization, pension pass-through, and worker/member-share repair. Long local failure and change-trigger sections made status and care duties harder to see.

## Memo compactness

- Rewrote 2 labor/care `Anti-patterns` sections into cube-axis-backed `Failure-mode capsule` sections.
- Rewrote 1 labor/care `Anti-pattern definitions` section into a cube-axis-backed `Failure-mode capsule`.
- Rewrote 4 labor/care `What would change the recommendation` sections into cube-axis-backed `Recalibration trigger capsule` sections.
- Added compact failure and recalibration capsules across all 11 labor/care route memos.

## Cube refactor

- Labor/care `anti_pattern=rent_extraction` records before: 6; after: 0.
- Labor/care `burden_mechanic=legal_risk_transfer` records before: 3; after: 0.
- Labor/care public-channel-only delivery records before: 1; after: 0.

Replacement axes now name concrete status and benefit mechanics: misclassification risk shift, social-insurance credit gap, credential gatekeeping, unpaid care load, second-earner penalty, childcare price capture, spenddown burden, portable-benefit ledger lock-in, sensitive-attribute reuse, pension fee capture, and member-distribution erasure.

## Metrics

| Metric | Value |
|---|---:|
| Labor/care docs touched | 11 |
| Labor/care route-memo bytes before | 78885 |
| Labor/care route-memo bytes after | 78075 |
| Labor/care route-memo bytes saved | 810 |
| Legacy labor/care anti-pattern sections remaining | 0 |
| Legacy labor/care anti-pattern-definition sections remaining | 0 |
| Legacy labor/care change-trigger sections remaining | 0 |
| Labor/care failure-mode capsules | 11 |
| Labor/care recalibration-trigger capsules | 11 |
| Labor/care accountability capsules | 11 |

## Rule going forward

Labor/care memos should keep the route-specific ladder, option scan, default table, and evidence packet, but repeated failure modes, reopening conditions, and accountability handoffs should point to cube axes and actor-accountability profiles. Labor/care routes should not collapse status, care, credential, pension, childcare, or worker-benefit mechanics into generic rent, public-channel, or legal-risk labels.
