---
status: audit_report
claim_kind: release_report
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
revision_current: rev0355
---

# Rev0347 — DFA share extraction and grid-load incidence

Rev0347 is a substance-first currentness release. It adds three sources and no cases or schema fields.

Current counts: **95 case memos / 95 scoreboards**, **495 sources**, **367 registered field keys**, **50 registered_unused fields**, and **5478 evidence edges**.

## What changed

- Added **S493**, the FRED/Federal Reserve DFA release table, and replaced vague U.S. share language with exact 2025:Q4 total-net-worth shares: bottom 50 = **2.5%**, 50-90 = **29.2%**, 90-99 = **36.4%**, top 1 = **31.9%**, and top 0.1 = **14.5%**.
- Added **S494** and **S495** to move the AI/data-center case from national electricity-demand projection into localized PJM/EIA grid-incidence evidence.
- Updated the macro-consistent wealth-accounts case to distinguish **S490** as a live Z.1 aggregate-balance-sheet release from **S493** as a DFA distributional-share table.

## Audit/refactor

The brittle rev0346 validator check was refactored so historical rev0346 invariants no longer demand that current front-door files preserve rev0346 counts and CHANGELOG order. Rev0347 now owns current front-door facts, while rev0346 remains a historical receipt check.

## Remaining proof debt

- U.S.: reconcile the extracted DFA shares against Z.1 totals, WID/DINA perimeter choices, liquidity/usable-wealth cuts, and trust/private-vehicle/control-layer opacity.
- AI/data-center: attach project-level tariff orders, class-cost studies, minimum bills, collateral, exit fees, water permits, abatement contracts, and no-stranded-cost clauses.
