# rev0310 legal-enforcement coercion, privilege, and memo refactor

Rev0310 addresses the highest-risk remaining family-specific bloat surface: legal-enforcement and penalty routes. These routes govern property seizure, criminal exposure, privilege, summonses, bounty incentives, community-supervision debt, trust-fund personal liability, and wrongful levy. Long local failure and change-trigger sections made the coercive duties harder to see.

## Memo compactness

- Rewrote 4 legal-enforcement `Anti-patterns` sections into cube-axis-backed `Failure-mode capsule` sections.
- Rewrote 4 legal-enforcement `What would change the recommendation` sections into cube-axis-backed `Recalibration trigger capsule` sections.
- Added compact failure and recalibration capsules across all 11 legal-enforcement route memos so the family now has a consistent route shape.
- Hand-compressed the long culpability default-sanction table while preserving the lane distinctions and side screens.

## Cube refactor

- Legal-enforcement `anti_pattern=rent_extraction` records before: 3; after: 0.
- Legal-enforcement public-channel-only delivery records before: 11; after: 0.
- Legal-enforcement `burden_mechanic=legal_risk_transfer` records before: 7; after: 0.
- Legal-enforcement `remedy_type=waiver` records before: 4; after: 0.

Replacement axes now name concrete coercive mechanics: probation-debt extension, forfeiture custody and claim channels, bounty-incentive conflicts, victim-repair shifts, hidden withholding burdens, civil/criminal boundary pressure, penalty cascades, privilege chill, wrongful levy repair, responsible-person review, and no-double-collection credits.

## Metrics

| Metric | Value |
|---|---:|
| Legal-enforcement docs touched | 11 |
| Legal route-memo bytes before | 92237 |
| Legal route-memo bytes after | 87753 |
| Legal route-memo bytes saved | 4484 |
| Legacy legal anti-pattern sections remaining | 0 |
| Legacy legal change-trigger sections remaining | 0 |
| Legal failure-mode capsules | 11 |
| Legal recalibration-trigger capsules | 11 |
| Legal accountability capsules | 11 |

## Rule going forward

Legal-enforcement memos should keep the route-specific ladder, option scan, default table, and evidence packet, but repeated failure modes, reopening conditions, and accountability handoffs should point to cube axes and actor-accountability profiles. Coercive routes should not collapse property seizure, privilege, willfulness, bounty incentives, or contest access into generic rent, public-channel, legal-risk, or waiver labels.
