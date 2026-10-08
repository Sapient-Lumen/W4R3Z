# Remittance-transfer tax, migration fee, and diaspora-family ladder

## Question in one sentence

What ladder should decide whether a remittance tax, migration-related charge, provider fee, or transfer-rail rule is legitimate revenue, financial-inclusion policy, or a toll on family survival?[S505][S506][S508][S509]

## Companion routes

Use this memo with:

- [`../10-framework/migration-remittance-transfer-tax-and-diaspora-family-routing.md`](../10-framework/migration-remittance-transfer-tax-and-diaspora-family-routing.md)
- [`../10-framework/sanctions-aml-cft-de-risking-and-financial-access-routing.md`](../10-framework/sanctions-aml-cft-de-risking-and-financial-access-routing.md)
- [`../10-framework/channel-pluralism-and-access-independence-routing.md`](../10-framework/channel-pluralism-and-access-independence-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — no remittance tax | leave household-support flows untaxed beyond ordinary income rules. | Default where floor or access risk is material. |
| B — low visible remittance tax | levy collected by provider. | Only with exemptions, caps, cost review, and proceeds repair. |
| C — provider/FX spread regulation | reduce private transfer costs. | Often better than taxing the flow. |
| D — financial-inclusion subsidy | support low-cost public or postal rails. | Strong candidate where corridors are fragile. |
| E — AML/sanctions screening surcharge | provider recovers compliance cost. | Must be bounded and not close humanitarian corridors. |

## Ten-gate ladder

1. **flow gate** — classify family support, wages sent home, humanitarian transfer, business payment, investment, evasion, or high-net-worth capital movement.
2. **total-cost gate** — combine tax, provider fee, FX spread, cash-out cost, delay, ID cost, and bank-account cost against corridor benchmarks.[S505]
3. **floor gate** — identify migrant worker, unbanked sender, cash recipient, disaster recipient, refugee family, or remittance-dependent household.
4. **purpose gate** — state whether the levy funds administration, migration services, development, enforcement, or general revenue.[S506]
5. **access gate** — preserve cash, agent, postal, public, mobile, and low-cost alternatives; do not force one private rail.
6. **de-risking gate** — test whether banks or correspondents will exit a corridor, especially small-island and fragile corridors.[S508][S509]
7. **exemption gate** — exempt or rebate humanitarian, low-value, family-support, and floor-sensitive transfers where feasible.
8. **collection gate** — assign collection only to record-capable providers and keep the tax visible rather than embedded in spread.
9. **proceeds gate** — route proceeds to cost reduction, inclusion, corridor stability, or migrant services before general revenue.
10. **review gate** — revisit if total cost exceeds target, volume shifts underground, providers exit, delays rise, or recipient hardship increases.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| family remittance | no extra tax by default | ordinary income rules remain separate. |
| high-cost corridor | fee/FX-cost reduction | do not add levy first. |
| statutory remittance tax | visible collection | cap, exemption, and review. |
| fragile correspondent banking | public/international support | prevent corridor closure. |
| suspected evasion/capital flight | targeted enforcement | do not generalize to all remittances. |

## Accountability capsule

Authoritative assignment: route `migration_remittance_transfer_tax_diaspora_family` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `remittance_tax_authority_money_transfer_operator_or_correspondent_bank_with_fee_kyc_corridor_and_family_floor_control`.
- Rent/benefit trace: `tax_authority_bank_correspondent_money_transfer_provider_fx_spread_recipient_or_compliance_vendor_capturing_remittance_tax_fee_spread_or_derisking_rent`.
- Bottleneck/evidence: `money_transfer_operator_and_agent_network; correspondent_banking_and_cbr_channel +3 more`; evidence starts with `corridor_fee_fx_spread_tax_and_total_cost_record; kyc_identity_name_match_sanctions_screen_and_rejection_file +4 more`.
- Fallback duty: `public_body_and_financial_regulator_must_preserve_fallback_low_cost_remittance_tiered_kyc_cash_mobile_offline_cure_transfer_release_and_nonforfeiture_when migrant_or_family_floor_support_depends_on_the_channel`.


## Source IDs only

[S505][S506][S508][S509]

[S505]: ../../SOURCES.md#S505
[S506]: ../../SOURCES.md#S506
[S508]: ../../SOURCES.md#S508
[S509]: ../../SOURCES.md#S509
