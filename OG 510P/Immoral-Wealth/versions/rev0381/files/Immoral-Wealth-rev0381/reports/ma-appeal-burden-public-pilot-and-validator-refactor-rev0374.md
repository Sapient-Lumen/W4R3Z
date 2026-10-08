---
revision: rev0374
base_revision: rev0373
generated_at: 2026-06-18T18:42:00Z
codename: ma-appeal-burden-public-pilot-and-validator-refactor
status: active_release_report
---

# ma-appeal-burden-public-pilot-and-validator-refactor — rev0374

Rev0374 deliberately adds **no new source routes**. It spends the turn on substance: using the existing Medicare Advantage sources to create a quantified public pilot for denial, appeal, overturn, and reporting-scope risk.

## What changed

- Added 7 locator-bound evidence records: `VCEDGE-rev0374-0187` through `VCEDGE-rev0374-0193`.
- Added `cases/social-security-medicare-claim-security-rev0318-ma-appeal-burden-public-pilot-rev0374.json` and `.md`.
- Added 8 explicit mechanical public-pilot route rows for the Social Security/Medicare case.
- Added `tools/audit_ma_appeal_burden_pilot.py` and refactored the row-contract audit script so it no longer fails merely because the current revision advanced past the rev0373 workbench filename.
- Updated the live-surface contract to make the public pilot, semantic audit, and validation report the current operator surface.

## Substantive finding

The public pilot changes the inference rule. A high overturn rate is **not** a self-correction pass when most denials are not appealed. It is an alarm that forces the cube to require unappealed-denial, delay, harm, and remedy rows.

## Certification boundary

Still **not certified current**. The next decisive work is one joined contract-year/service-category row with denominator, denial, appeal, overturn, reopenings, criteria/delegation, notice, time-to-relief, service furnished, beneficiary/provider financial restoration, quality/network context, and RADV/payment-integrity recovery.
