# Customs, tariff, carbon-border, and retaliation ladder

## Question in one sentence

What ladder should decide whether a border measure should be a customs duty, VAT/GST collection rule, carbon border adjustment, anti-evasion rule, retaliation measure, industrial-policy instrument, or non-tax rule?[S462][S463][S464][S465][S466]

## Companion routes

Use this memo with:

- [`../10-framework/customs-tariff-carbon-border-and-trade-retaliation-routing.md`](../10-framework/customs-tariff-carbon-border-and-trade-retaliation-routing.md)
- [`../10-framework/incidence-and-protected-burden-routing.md`](../10-framework/incidence-and-protected-burden-routing.md)
- [`../10-framework/regressivity-correction-and-floor-protection-routing.md`](../10-framework/regressivity-correction-and-floor-protection-routing.md)
- [`../10-framework/international-coordination-and-apportionment-routing.md`](../10-framework/international-coordination-and-apportionment-routing.md)
- [`../10-framework/tax-morale-state-capacity-and-political-economy-routing.md`](../10-framework/tax-morale-state-capacity-and-political-economy-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — ordinary tariff | duty on imported goods. | Use only with honest incidence and purpose. |
| B — carbon border adjustment | charge embedded emissions net of domestic/foreign carbon pricing. | Adopt when proof and equivalence are real. |
| C — platform/VAT collection | require platforms/intermediaries to collect VAT/GST on low-value trade. | Prefer to consumer-side traps where administrable. |
| D — retaliation tariff | countermeasure against another state. | Use narrowly, visibly, and with sunset/review. |
| E — direct industrial support | on-budget subsidy, procurement, or transition aid. | Prefer when tariff would hide protection rents. |

## Ten-gate ladder

1. **purpose gate** — classify the measure as revenue, carbon leakage, anti-evasion, safety/security, retaliation, industrial policy, or transition support.
2. **base gate** — define product, origin, value, embedded emissions, platform role, de minimis threshold, and importer/declarant duty.[S464][S465]
3. **domestic-equivalence gate** — for CBAM-like rules, test whether the border charge mirrors a real domestic carbon cost and phaseout of domestic free allowances.[S462]
4. **proof gate** — specify customs value, origin, emissions, small-importer thresholds, default values, and correction paths.[S463]
5. **incidence gate** — estimate pass-through to consumers, SMEs, input users, workers, and protected households.
6. **capacity gate** — assess whether low-capacity exporters or small importers can comply; use safe harbors or technical assistance when proof burdens would exclude them.
7. **collection gate** — choose importer, platform, carrier, vendor, intermediary, withholding, or customs collection; avoid making consumers reconstruct complex records.[S466]
8. **retaliation gate** — test dispute risk, countermeasure exposure, supply-chain effects, and whether a non-tax instrument is cleaner.
9. **proceeds gate** — route revenue to rebates, climate transition, customs capacity, affected workers, or international equalization where the measure imposes cross-border burden.
10. **review gate** — sunset or recalibrate when domestic carbon price, foreign rules, emissions data, trade retaliation, or low-value import patterns change.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| carbon cost mismatch | CBAM-like charge | credit foreign carbon price and protect low-capacity proof paths. |
| low-value VAT/GST leakage | platform/intermediary collection | do not trap consumers with impossible declarations. |
| protection claim without honest purpose | direct subsidy or reject | no hidden consumer tax. |
| retaliation | narrow countermeasure | sunset and incidence disclosure. |
| regressive import burden | rebate or exemption | protect floor before revenue. |

## Accountability capsule

Authoritative assignment: route `customs_tariff_carbon_border` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `customs_authority_importer_or_cbam_declarant_with_tariff_value_embedded_emissions_certificate_and_rebate_control`.
- Rent/benefit trace: `importer_protected_industry_general_fund_certificate_intermediary_or_upstream_exporter_capturing_hidden_tariff_carbon_premium_free_allowance_or_trade_rent`.
- Bottleneck/evidence: `customs_entry_and_hs_classification_channel; origin_and_customs_value_record +3 more`; evidence starts with `hs_classification_origin_customs_value_and_invoice_record; embedded_emissions_supplier_default_factor_and_verification_record +4 more`.
- Fallback duty: `customs_and_climate_authorities_must_preserve_fallback_small_importer_assistance_low_income_rebate_transparent_pass_through_disclosure_contest_window_and_climate_repair_channel_when border charges hit protected consumers_or_source_state_burdens`.


## Source IDs only

[S462][S463][S464][S465][S466]

[S462]: ../../SOURCES.md#S462
[S463]: ../../SOURCES.md#S463
[S464]: ../../SOURCES.md#S464
[S465]: ../../SOURCES.md#S465
[S466]: ../../SOURCES.md#S466
