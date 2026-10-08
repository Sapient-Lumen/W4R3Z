---
status: active
claim_kind: revision_report
route_role: jurisdictional_mobility_core
route_refs:
- jurisdictional_mobility_core
- measurement_uncertainty_core
- tax_rail_core
- source_governance_core
- certification_core
revision_current: rev0355
source_refresh_due: 2026-12-31
---

# rev0336 jurisdictional-mobility current-law hardening and source-fit burndown

Generated: `2026-06-13T05:49:57Z`  
Codename: `jurisdictional-mobility-current-law-hardening-and-sourcefit-burndown`

## Why this was next

After rev0335, fifteen active scoreboards still carried seed calibration labels. Gate 13 was the next priority because jurisdictional mobility can invalidate the cube in two opposite ways: mobile wealth can overclaim exit threat and weaken public claims, while migrant workers and transnational families can be excluded from the wealth they help produce.

## Cases hardened

- `eu-investor-citizenship-residence-rev0311`
- `united-kingdom-non-dom-transition-rev0311`
- `global-high-wealth-migration-exit-threat-rev0311`
- `gulf-migrant-public-wealth-perimeter-rev0311`
- `remittance-dependence-transnational-family-burden-rev0311`

## Substantive changes

The investor citizenship/residence case now blocks comfort scoring until scheme-level approvals, refusals, revocations, source-of-funds failures, physical-presence evidence, CRS/tax-residence verification, and visa/infringement follow-through are visible.[S203][S204][S206][S470]

The UK non-dom case now treats residence-tax repair as a watch case rather than a solved case. FIG relief, transfer-of-assets/trust/IHT restructuring, revenue uncertainty, and actual taxpayer/asset movement must be proven with HMRC/OBR evidence.[S207][S208][S209][S469]

The high-wealth exit-threat case now demotes market/NGO/academic claims into a data-trigger rather than a veto. The proof burden is linked taxpayer migration, asset location, destination residence, CRS/AEOI, exit-tax valuation, and counterfactual migration.[S180][S181][S210][S211][S212]

The Gulf migrant-worker case now treats public wealth as failed when migrant workers are inside the productive economy but outside durable social-protection, portability, appeal, family, and survivor claims.[S216][S217][S218][S471]

The remittance case now treats remittances as household-support conversion rails. Scale is not enough; corridor fees, exchange spreads, recruitment debt, wage theft, recipient control, public-service substitution, and payment-rail remedies determine whether transfers build wealth.[S218][S219][S471]

## Source-fit refactor

- S205 is official European Commission context, not dispositive operative law.
- S206 is official judicial/direct evidence.
- S208 is official/direct HMRC operational guidance.
- S211 is nonprofit-research context, not official authority.
- S212 is academic-research context, not official authority.
- S216 is multilateral-research context.
- S217 is official statistical/report evidence for migrant-worker scale.

Remaining active seed-calibration labels after this pass: 10.

<!-- current_revision: rev0336; codename: jurisdictional-mobility-current-law-hardening-and-sourcefit-burndown -->
