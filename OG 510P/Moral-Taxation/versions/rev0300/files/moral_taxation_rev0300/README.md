# Moral Taxation Archive — rev0300

Rev0300 is the cross-border-reporting accountability and cube-axis refactor. The priority change is practical: international coordination, customs/CBAM border charges, remittance corridors, immigration/asylum/status fees, withholding/treaty/MAP relief, and global-minimum-tax/GIR claim-split routes now identify who controls the rule table, rail, registry, corridor, portal, reclaim queue, exchange, formula, evidence, repair, and fallback duty.

## What rev0300 changed

- Rewrote all 6 `cross_border_reporting` actor-accountability profiles.
- Reduced cross-border beneficiary placeholders from 6 to 0 and generic benefit-trace evidence from 6 to 0.
- Refactored generic cross-border cube axes, especially in `international_coordination_claim_split` and `un_inclusive_international_tax`, replacing inherited generic values with route-specific participation, source-state fiscal agency, customs/CBAM registry, remittance corridor, immigration status gate, withholding reclaim, GIR exchange, capacity, and claim-split records.
- Corrected market/channel/remedy axes across the cross-border family so treaty relief, customs entries, CBAM certificates, remittance rails, KYC gates, status portals, MAP queues, and GIR exchange are visible.
- Added `docs/00-meta/cross-border-reporting-accountability-refactor-rev0300.md` as the focused refactor memo.
- Added Rev0300 accountability-map sections to six cross-border framework/calibration documents.
- Hardened `tools/audit_actor_accountability_profiles.py` so cross-border placeholder regression is fatal.

## Start path

Use `START_HERE.md` first. For the current focused pass, read `docs/00-meta/cross-border-reporting-accountability-refactor-rev0300.md`, then inspect `docs/00-meta/actor-accountability-profiles.json` and the `cross_border_reporting` records in `cube-index.json`.

## Validation

Run `make package`. It renders the scorecard, rebuilds the manifest, runs all audits and archive checks, and writes the named release zip.
