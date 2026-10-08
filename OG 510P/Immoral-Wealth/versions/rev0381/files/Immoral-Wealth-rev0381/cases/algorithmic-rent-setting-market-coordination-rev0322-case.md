---
status: active_case
claim_kind: case_memo
route_role: anti_monopoly_core
canonical_anchor: false
route_refs:
- anti_monopoly_core
- housing_land_core
- household_market_extraction_core
- measurement_uncertainty_core
- case_calibration_core
supersedes: null
depends_on:
- algorithmic-rent-setting-market-coordination-rev0322-scoreboard.json
source_refresh_due: 2026-09-30
case_pressure: rev0322_rental_market_power
case_pressure_rev0332: seed_backlog_closure
---

# Algorithmic rent setting, competitor data, and market coordination — rev0355 case memo

## Why this case belongs in the cube

rev0322 adds a rental-market-power layer because the cube had strong housing, tenant-screening, eviction, and public-backstop surfaces, but still under-instrumented the **private market power inside ordinary rent and nominal homeownership**. This case asks whether the claimant can actually accumulate wealth when shelter access is mediated by pricing software, corporate-landlord systems, land-lease control, fee stacks, repair delays, or mobility lock-in. [S414][S415][S416][S426]

The governing rule is: **housing is not a foothold if the resident's apparent tenure is subordinated to a landlord, platform, park owner, data vendor, or fee/remedy system that can extract the savings before they become durable assets.**

## Unit of analysis

- **Jurisdiction:** United States
- **Subsystem:** rental_market_power_case
- **Dominant breach:** rental pricing software can convert dispersed landlords into a coordinated data-and-recommendation system that raises rents or suppresses independent price competition while renters lack usable visibility into the coordination channel
- **Fastest washout:** nonpublic competitor data, rent-recommendation adoption pressure, algorithmic sameness, lease-renewal timing, and high moving costs wash out household bargaining before antitrust remedies arrive
- **Verdict:** `correction_required` with `medium` confidence.

## Rev0332 active hardening

The companion scoreboard blocks ordinary comfort certification until the case can prove all-in housing cost, local market power, remedy access, and resident/tenant incidence. The case is a bounded active stress case rather than a full jurisdictional certification.

## What would change the verdict

A softer verdict would require direct local evidence that residents or renters retain exit power, cost transparency, price competition, timely repair or refund remedies, and durable ownership or tenure claims. A harder verdict would be justified if new evidence shows systematic price alignment, fee/deposit extraction, lot-rent escalation, forced moves, asset abandonment, or subgroup-skewed lock-in that persists after enforcement or preservation interventions.


## Rev0332 active hardening note

This memo is active after rev0332 because RealPage litigation/settlement posture makes rental-pricing algorithms a live currentness and remedy problem. Certification requires data-flow restrictions, pricing-independence monitoring, tenant incidence evidence, and restoration where rent was inflated.

<!-- current_revision: rev0332; codename: seed-backlog-closure-and-gate-inventory-source-refactor -->

<!-- current_revision: rev0341; codename: case-memo-status-drift-and-stale-seed-language-repair; repaired stale seed-status language -->


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S10]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.
