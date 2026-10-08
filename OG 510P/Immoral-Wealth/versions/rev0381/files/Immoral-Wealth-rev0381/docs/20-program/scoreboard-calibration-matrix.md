---
status: active_bridge
claim_kind: program_rule
route_role: certification_core
canonical_anchor: false
route_refs:
- certification_core
- case_calibration_core
supersedes: null
depends_on: []
source_refresh_due: 2026-12-31
case_pressure: rev0304_portfolio_calibration
---

# Scoreboard calibration matrix

## Purpose

This matrix is the working bridge between [`scoreboard-spec.md`](scoreboard-spec.md), [`scoreboard-schema.json`](scoreboard-schema.json), and live cases. It gives operators a field-by-field decision rule: what counts as pass, watch, fail, what source order to prefer, and what a missing field does to certification.

The matrix is not a weighted index. A single decisive fail can veto comfort.

## Field matrix

| Field | Pass signal | Warning signal | Fail / veto signal | Preferred source order | Missing-data consequence | Route moved |
|---|---|---|---|---|---|---|
| `bottom_50_private_wealth_share` | 15–25% and usable | 5–15% or fragile | under 5%, negative, or mostly unusable | national distributional accounts, WID/OECD, household survey | no near-ideal/acceptable certification | target / floor |
| `middle_40_private_wealth_share` | 45–55% and diversified enough | 35–45% or concentrated in fragile housing | under 35% or debt-fragile | national distributional accounts, OECD, survey | no thick-middle comfort | target / washout |
| `next_9_private_wealth_share` | stable buffer without exclusion | too dominant relative to middle/lower | upper-middle capture of entry assets | national accounts, survey | watch only | target / circulation |
| `top_1_private_wealth_share` | 8–15% without rule signs | 15–25% | above 25% or rule signs | WID/OECD/national accounts/tax data | no soft top-tail pass | top-tail |
| `top_0_1_private_wealth_share` | at/below 3% and legible | 3–7% or unclear control | above 7%, dynastic/control signs | tax data, rich lists as proxy, registry, WID | opacity penalty | top-tail / rails |
| `public_social_counterweight` | positive, broad, rule-bound | thin, underfunded, complex | negative, patronage-routed, privatized | national balance sheets, budgets, program data | no public-substitution credit | public/common |
| `lower_half_real_floor` | claimable, keepable, shock-survivable | paper or delayed | spend-down-trapped, cliff-punished, seizure-exposed | admin data, surveys, benefit rules | no real-floor pass | floor |
| `early_foothold_open_access` | early, person-level, non-family | late, uneven, group-limited | parent-backed, household-gated, place-closed | cohort panels, transfer data, housing/education data | no open-circulation pass | early footholds |
| `parent_backed_threshold_dependency` | family help not decisive | material but not central | deposits, guarantees, inherited place normally decisive | panel data, surveys, housing transaction data | family-gate watch becomes active | early footholds |
| `group_person_closure` | no central subgroup veto | material subgroup gaps | racial/caste/Indigenous/gender/migrant closure | subgroup wealth/title/control data | no anti-averaging pass | anti-averaging |
| `housing_land_washout` | low burden, open entry, stable tenure | local/subgroup overburden | rents, land prices, scarcity, local concentration, lease decay | housing costs, supply, registry, local market data | package durability unproven | washout |
| `debt_fee_washout` | low stress, good insolvency restart | moderate stress | predatory credit, fee drag, collection/seizure, negative equity | credit data, insolvency data, household survey | no protected-foothold comfort | washout / floor |
| `wealth_to_rule_risk` | low concentration/influence | watch channels | political finance, media, procurement, rescue, monopoly capture | integrity data, lobbying, ownership, procurement | no prevention-mode comfort | anti-oligarchy |
| `ownership_legibility` | verified enough to govern | partial registries | opacity-blocked, private entities untraceable | beneficial ownership, land/company/trust registers | hard-instrument proof debt | rails |
| `climate_insurance_drag` | affordable, available, reliable coverage | rising premiums/deductibles | nonrenewal, uninsurable, self-eroding | insurance data, hazard data, mortgage/claims data | no housing pass in exposed markets | floor / housing |
| `digital_intangible_concentration` | broad access/competition | concentration watch | compute/data/IP/platform rents harden top tail | firm data, investment, labor share, market concentration | top-tail watch in frontier economies | formation / top-tail |
| `dynastic_infrastructure_pressure` | transparent and bounded | growing vehicles | trusts/family offices/DAFs/foundations preserve control | tax/registry/philanthropy/family-office data | no dynasty pass | top-tail / rails |
| `monetary_asset_price_channel` | stabilization plus repair | distributional watch | repeated asset-holder rescue without repair | central bank, asset prices, ownership data | washout/top-tail proof debt | macro/washout |

## Calibration class labels

Use the following labels inside scoreboard instances:

- `case_portfolio_seed`: enough evidence to route, not enough to certify.
- `stress_surface_seed`: a single surface that can block a broader case.
- `direct_case_read`: current direct evidence for most required fields.
- `cross_case_pattern`: not a country case; used to support pattern extraction.
- `stale_case`: evidence older than the case's refresh rule.

## Proof-debt priority order

When several fields are missing, collect them in this order:

1. Fields that can change the **verdict**.
2. Fields that can change the **opening lane**.
3. Fields that can reveal a **constitutional veto**.
4. Fields that can change **instrument feasibility**.
5. Fields that only improve description.

## Case pressure from rev0304

The portfolio adds a practical rule: a field should not be made more complex unless at least one live case changes because of it. The climate-insurance field, parent-backed threshold field, public/social substitution field, and ownership-legibility field all survived this test in rev0304. Several finer-grained fields remain parked.

# rev0305 comparative calibration rows

| Calibration class | Cases | Main false pass | Required extra check |
|---|---|---|---|
| Pension/housing/age-hidden wealth | UK, Canada, Netherlands, Norway | household wealth looks broad because older owners/pension claimants hold claims | liquidity, renter entry, parental transfers, age/tenure split |
| Top-tail undermeasurement | Canada, India, Brazil, United States | survey data undercount concentrated ownership | corrected top-tail, beneficial ownership, top 0.1 |
| Public counterweight | Norway, Alaska, Singapore, Vienna | public asset exists but claimant access is assumed | citizenship/residency, portability, rule-bound claim |
| Group/person veto | South Africa, India, Brazil, United States, Canada | national average hides subordinated group closure | race/caste/gender/Indigenous/migrant/person-title data |
| Housing as asset substitute | Vienna, Singapore | housing stability is assumed to equal wealth security | access, maintenance, climate retrofit, exit/portability |
| Legibility-first state capacity | India, Brazil, South Africa | ambitious redistributive instrument outruns rails | cadastre, tax admin, subgroup statistics, courts, registry |
