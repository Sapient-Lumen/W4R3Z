---
status: audit_report
claim_kind: release_report
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
revision_current: rev0355
---

# Rev0348 — large-load tariff incidence and proof-debt closeout

Rev0348 is a substance-first case pass. It adds six sources and no cases or schema fields, all aimed at the riskiest unfinished piece of the AI/data-center public-backstop case: project/jurisdiction-level tariff and service-agreement instruments.

Current counts after this release: **95 case memos / 95 scoreboards**, **501 sources**, **367 registered field keys**, **50 registered_unused fields**. Evidence-edge count is regenerated during finalization.

## What changed

- Added **S496-S501**: Ohio PUCO/AEP tariff evidence, Virginia SCC/Dominion GS-5 safeguards, Pennsylvania PUC model-tariff proceeding, Wisconsin We Energies tariff decision, and Wisconsin Alliant/Beaver Dam service-agreement decision.
- Upgraded the AI/data-center case from “localized load incidence exists” to “specific tariff/service-agreement safeguards are visible and testable.”
- Rewrote the AI scoreboard’s cost-shift, utility-affordability, public-balance-sheet, and seniority-waterfall notes so the unresolved debt is no longer generic doctrine.

## Concrete incidence extracted

- **Ohio / AEP:** 25 MW Schedule DCT perimeter, study fees, ramp commitments, ramp-plus-eight-year term, 50% collateral for lower-credit customers, minimum-demand charges capped at 85% of contract capacity, reassignment rules, BTM generation controls, and exit-fee mechanics. [S496] [S497]
- **Virginia / Dominion:** GS-5 large-load class, 14-year contract obligation, 85% T&D minimum charge, generation-demand minimum charge, collateral, and future interconnection-process review. [S498]
- **Pennsylvania:** tentative statewide model tariff emphasizing cost causation, CIAC, tiered collateral, minimum contract terms, low-income contributions, flexible-service options, transparency, and public feedback before final order. [S499]
- **Wisconsin:** We Energies and Alliant/Beaver Dam decisions add 15-year term, lower tariff threshold, transmission-cost-shift revisions, full-cost resource treatment, termination-charge safeguards, reporting, transparency, and a move away from ad hoc confidential agreements toward stand-alone future large-load tariffs. [S500] [S501]

## Audit/refactor

Rev0348 refactors the AI case’s proof-debt register and seniority waterfall: tariff/source facts are now bound to specific obligations instead of being repeated as abstract “collateral/minimum-bill needed” language. The validator was also updated so rev0347 remains a historical receipt while rev0348 owns the current front-door count and changelog invariants.

## Remaining proof debt

- Final orders/service agreements, not just press releases or utility summary pages.
- Class-cost studies and actual residential/small-business rate incidence.
- Project-level water permits, wastewater capacity, drought/basin stress, and mitigation terms.
- Abatement contracts, local public-finance agreements, community-benefit clauses, clawbacks, and no-stranded-cost language.
