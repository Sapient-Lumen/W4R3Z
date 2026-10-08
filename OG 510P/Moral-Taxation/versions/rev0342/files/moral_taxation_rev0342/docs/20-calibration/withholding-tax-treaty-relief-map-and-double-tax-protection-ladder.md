# Withholding tax, treaty relief, MAP, and double-tax protection ladder

## Question in one sentence

What ladder should decide whether a cross-border withholding or double-tax system provides enough relief, credit, and competent-authority access to remain morally legitimate?[S548][S549][S550][S551]

## Companion routes

Use this memo with:

- [`../10-framework/withholding-tax-treaty-relief-map-and-double-tax-protection-routing.md`](../10-framework/withholding-tax-treaty-relief-map-and-double-tax-protection-routing.md)
- [`../10-framework/international-coordination-and-apportionment-routing.md`](../10-framework/international-coordination-and-apportionment-routing.md)
- [`international-coordination-claim-split-ladder.md`](international-coordination-claim-split-ladder.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — relief at source | treaty rate applied before payment. | Preferred where eligibility is verifiable. |
| B — fast refund/reclaim | overwithholding returned promptly. | Required fallback. |
| C — credit/exemption | residence relief for source tax. | Required where withholding persists. |
| D — MAP/competent authority | bilateral correction. | Required for double-tax disputes. |
| E — paper-only reclaim | slow, costly, uncertain. | Reject if durable. |

## Ten-gate ladder

1. **claim gate** — identify source tax, residence tax, treaty article, domestic relief, and beneficial-owner eligibility.
2. **withholding-agent gate** — assign documentation, rate application, and error-correction duties to the best remittance node.[S548]
3. **relief-at-source gate** — use standardized documentation when eligibility is readily verifiable.
4. **reclaim gate** — when overwithholding occurs, provide refund, interest where appropriate, status tracking, and low-cost submission.
5. **credit gate** — coordinate foreign tax credit or exemption so relief is not lost to timing or form mismatch.
6. **double-tax gate** — route actual or likely double taxation to competent authority or MAP.[S550][S551]
7. **settlement-warning gate** — warn before domestic closing agreements impair correlative relief.
8. **queue gate** — monitor MAP inventories, average time, denials, and unresolved outcomes.[S549]
9. **small-claim gate** — simplify relief for retail investors, pension savers, migrants, and small firms.
10. **repair gate** — convert persistent overwithholding into relief-at-source reform, intermediary discipline, or treaty renegotiation.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| portfolio payment | relief at source | standardized proof. |
| overwithheld dividend | refund/reclaim | fee and delay control. |
| TP adjustment | MAP | collection coordination. |
| treaty mismatch | competent authority | timely access. |
| persistent queue | review trigger | resource and process reform. |

## Accountability capsule

Authoritative assignment: route `withholding_treaty_relief_map_double_tax_protection` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `withholding_agent_revenue_agency_or_competent_authority_with_payment_treaty_reclaim_credit_and_map_control`.
- Rent/benefit trace: `source_state_treasury_custodian_reclaim_vendor_or_intermediary_capturing_overwithheld_cash_delay_float_fee_or_settlement_leverage`.
- Bottleneck/evidence: `withholding_agent_payment_and_rate_application_record; treaty_residence_beneficial_owner_and_documentation_channel +3 more`; evidence starts with `withholding_certificate_payment_rate_deposit_and_information_return_record; treaty_residence_beneficial_owner_limitation_on_benefits_and_documentation_file +4 more`.
- Fallback duty: `source_and_residence_tax_authorities_must_preserve_fallback_relief_at_source_low_cost_reclaim_credit_exemption_map_access_status_tracking_interest_where_appropriate_and_no_treaty_relief_paywall_for_small_claimants`.


## Source IDs only

[S548][S549][S550][S551]

[S548]: ../../SOURCES.md#S548
[S549]: ../../SOURCES.md#S549
[S550]: ../../SOURCES.md#S550
[S551]: ../../SOURCES.md#S551
