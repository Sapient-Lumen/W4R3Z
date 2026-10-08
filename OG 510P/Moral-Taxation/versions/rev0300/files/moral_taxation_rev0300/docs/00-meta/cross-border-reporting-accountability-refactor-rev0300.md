# Cross-border reporting accountability refactor — rev0300

## Why this pass mattered

After rev0299, the largest remaining family with both beneficiary placeholders and generic benefit-trace evidence was `cross_border_reporting`. The risk was not cosmetic. These routes decide who controls treaty relief, withholding, customs/CBAM border charges, remittance corridors, asylum/status fees, international information exchange, and global claim splitting. Generic accountability can quietly blame the foreign taxpayer, migrant, claimant, source state, or visible remitter while the real gatekeeper controls the rail, record, formula, queue, or dispute path.

## What was specialized

Rev0300 rewrites all 6 cross-border-reporting actor-accountability profiles:

- `un_inclusive_international_tax`
- `customs_tariff_carbon_border`
- `migration_remittance_transfer_tax_diaspora_family`
- `immigration_status_asylum_benefit_fee_floor`
- `withholding_treaty_relief_map_double_tax_protection`
- `international_coordination_claim_split`

Each profile now names the accountable actor, benefit or rent recipient, bottleneck or channel actor, protected burden bearers, non-responsible actors, default liability/remedy move, fallback public duty, route-specific evidence, and review triggers.

## Accountability clusters

### 1. International coordination and source-state fiscal agency

Coordination is not legitimate merely because it is technical or multilateral. Responsibility follows agenda-setting, drafting, model-rule control, exchange rails, dispute access, implementation capacity, and the ability to preserve source, market, services, withholding, and host-burden claims. Weaker source states and ordinary public-service users are protected burden bearers, not the actors who made the bargain.

### 2. Customs, CBAM, tariffs, and hidden border pass-through

A border charge must separate the customs collector, importer/declarant, verifier, certificate registry, protected industry, consumer, exporter, and source-state worker. Rev0300 requires customs value, HS/origin, embedded-emissions, certificate, registry, pass-through, rebate, and retaliation records before a border charge is treated as ordinary incidence.

### 3. Remittances, migration fees, and family-floor transfers

Remittance responsibility follows the corridor: money-transfer operator, correspondent bank, FX spread, agent network, KYC/name-match gate, mobile or cash-out channel, and transfer-release record. Migrants and diaspora families are not the default revenue base for rails they cannot control.

### 4. Immigration, asylum, status, and fee-waiver gates

Status access is not ordinary service pricing. Fee-setting authorities, immigration agencies, portal vendors, asylum offices, benefit agencies, and employers can control the gate. Rev0300 requires fee, waiver, portal, receipt, biometric, appointment, language-access, work-authorization, refund, and status-continuity evidence.

### 5. Withholding, treaty relief, MAP, and double-tax protection

The visible claimant is not responsible for payment-chain overwithholding or treaty-relief paywalls. Responsibility follows the withholding agent, custodian/payor, source agency, residence agency, competent authority, MAP channel, refund/reclaim queue, foreign-tax-credit record, and reclaim intermediary.

### 6. GIR exchange, global minimum tax, and claim splitting

Global coordination has become implementation-sensitive. Rev0300 treats central filing/exchange readiness, safe harbors, top-up allocation, apportionment factors, host-burden carveouts, source-state capacity, and dispute outcomes as accountability evidence, not background doctrine.

## Cube-axis refactor

Several cross-border records still used inherited generic values such as `not_market_specific`, `not_channel_specific`, `legal_risk_transfer`, `not_remedy_specific`, and `classification_integrity`. Rev0300 replaces those with route-visible values including `cross_border_coordination_forum`, `customs_border_gate`, `remittance_corridor`, `immigration_status_gate`, `cross_border_payment_chain`, `global_tax_coordination_floor`, `customs_entry_or_cbam_registry`, `money_transfer_rail`, `immigration_application_portal`, `withholding_reclaim_portal`, `gir_exchange_and_competent_authority_rail`, `source_state_fiscal_agency`, `status_access_ransom`, `financial_exclusion`, and `base_erasure_or_overlap`.

The deepest axis corrections are `international_coordination_claim_split`, which now exposes GIR exchange, top-up allocation, source/host/market/residence claim splitting, capacity, and direct host-burden erasure, and `un_inclusive_international_tax`, which now distinguishes participation, fiscal agency, source-state revenue loss, and capacity support from generic foreign-record risk.

## Regression rule

`tools/audit_actor_accountability_profiles.py` now rejects any cross-border-reporting profile that keeps generic beneficiaries, generic benefit-trace evidence, unidentified bottlenecks, too-thin responsibility bases, or missing route-specific evidence for source-state participation/capacity, customs/emissions/pass-through, remittance/KYC/corridor, fee/waiver/status, withholding/treaty/MAP, or GIR/claim/source records.
