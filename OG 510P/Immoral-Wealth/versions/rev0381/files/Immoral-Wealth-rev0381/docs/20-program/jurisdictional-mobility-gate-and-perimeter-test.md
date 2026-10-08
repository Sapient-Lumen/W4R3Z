---
status: active_doctrine
claim_kind: verdict_protocol
route_role: jurisdictional_mobility_core
canonical_anchor: false
route_refs:
- jurisdictional_mobility_core
- certification_core
supersedes: null
depends_on:
- scoreboard-schema.json
- verdict-engine-and-certification-gates.md
source_refresh_due: 2026-12-31
case_pressure: rev0311_jurisdictional_mobility
---

# Jurisdictional mobility gate and claimant-perimeter test

## Gate 13 — jurisdictional mobility, exit blackmail, and claimant perimeter

A case cannot pass when wealth can escape the order while ordinary claimants remain bound by it. Gate 13 asks whether tax residence, legal status, capital mobility, property ownership, public claims, and remedies are aligned across borders.

## Pass conditions

A case can pass or watch-pass Gate 13 only when it can show:

- high-wealth exit threats are evidence-calibrated, not treated as automatic vetoes;
- residence and tax-residence rules are enforceable;
- exit-tax, deemed-disposal, source-tax, or trailing-residence rails exist where necessary;
- CRS/AEOI, beneficial ownership, and trust/legal-arrangement rails cover relevant asset channels;
- citizenship/residence-by-investment schemes do not create secrecy, impunity, tax-residence, housing, or political-access breaches;
- resident workers and long-term migrants have a clear claimant perimeter for labor, social protection, injury, wage, pension, housing, and remedy claims;
- remittance channels are low-cost and do not substitute for failed public floors;
- capital-flow management is transparent, targeted, lawful, and stability-oriented when used.[S203][S204][S213][S214][S216][S217][S218][S219]

## Gate statuses

| Status | Meaning |
|---|---|
| passed | cross-border rails are strong enough for the package being certified |
| watch | rails exist but rely on monitoring, treaty cooperation, or uncertain behavioural evidence |
| blocked | elite exit/status/asset mobility can defeat domestic reform or claimant rights |
| missing | no credible cross-border evidence exists |

## Hard blocks

Gate 13 blocks comfort certification when:

- a country relies on public/common wealth while excluding a large worker-resident population from ordinary claims;
- CBI/RBI or special tax regimes undercut tax transparency, solidarity, or housing access;
- reform is watered down because of unverified wealth-flight claims without a data plan;
- offshore or cross-border ownership makes top-tail compression unenforceable;
- migrant remittances are counted as household security without scoring recruitment debt, transfer cost, wage theft, deportation risk, and family control.

## Data fields

Use the rev0311 fields in [`scoreboard-schema.json`](scoreboard-schema.json): `jurisdictional_mobility_gate`, `high_wealth_exit_threat`, `residence_citizenship_by_investment_risk`, `tax_residency_enforcement`, `exit_tax_and_deemed_disposal_rails`, `capital_flow_or_asset_flight_risk`, `crs_aeoi_information_exchange_coverage`, `migrant_claimant_perimeter_exclusion`, `portable_social_rights_for_migrants`, `remittance_or_transnational_support_burden`, and `remittance_fee_leakage`.
