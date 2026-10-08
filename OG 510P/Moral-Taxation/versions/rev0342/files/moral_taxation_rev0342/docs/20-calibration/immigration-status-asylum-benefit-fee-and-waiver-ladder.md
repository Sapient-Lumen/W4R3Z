# Immigration status, asylum, benefit-fee, and waiver ladder

## Question in one sentence

What ladder should decide when immigration filing and status fees are permissible cost recovery and when they become status ransom, protection tolls, or agency-delay rents?[S523][S524][S525]

## Companion routes

Use this memo with:

- [`../10-framework/immigration-status-asylum-and-benefit-fee-floor-routing.md`](../10-framework/immigration-status-asylum-and-benefit-fee-floor-routing.md)
- [`../10-framework/migration-remittance-transfer-tax-and-diaspora-family-routing.md`](../10-framework/migration-remittance-transfer-tax-and-diaspora-family-routing.md)
- [`../10-framework/channel-pluralism-and-access-independence-routing.md`](../10-framework/channel-pluralism-and-access-independence-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — cost-recovery filing fee | applicant pays adjudication cost. | Conditional on floor and waiver. |
| B — humanitarian exemption | no fee for protection category. | Required where safety or status floor is at stake. |
| C — employer-side fee | beneficiary employer pays. | Preferred for labor-market petitions. |
| D — recurring pending-case fee | annual fee while case remains pending. | High risk; requires delay and waiver review. |
| E — online-only payment | electronic collection only. | Reject absent assisted fallback. |

## Ten-gate ladder

1. **benefit gate** — identify asylum, work authorization, naturalization, family unity, parole, appeal, replacement document, or employer petition.
2. **floor gate** — classify protection, subsistence work, family unity, legal identity, or discretionary convenience.
3. **payer gate** — assign cost to employer, sponsor, agency, or general fund where applicant capacity is weak.
4. **waiver gate** — test availability, evidence burden, language access, and processing reliability.[S523][S524]
5. **channel gate** — require non-digital, assisted, or low-cost payment options.
6. **delay gate** — prevent recurring fees caused mainly by agency backlog.[S525]
7. **rejection gate** — provide cure for wrong amount, form edition, or payment failure.
8. **nonrefundability gate** — limit loss where rejection or agency error occurs.
9. **proceeds gate** — disclose cross-subsidy among humanitarian, family, and employment categories.
10. **review gate** — recalibrate when fee rejection, waiver denial, abandonment, or pro se failure rises.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| humanitarian protection | exemption / waiver | no protection toll. |
| employer petition | employer fee | no worker pass-through. |
| wrong fee | cure period | preserve priority. |
| pending-case annual fee | waiver and delay offset | no agency-delay rent. |
| online-only fee | fallback channel | no digital exclusion. |

## Accountability capsule

Authoritative assignment: route `immigration_status_asylum_benefit_fee_floor` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `immigration_fee_authority_application_portal_owner_or_status_benefit_decisionmaker_with_fee_waiver_receipt_and_work_authorization_control`.
- Rent/benefit trace: `immigration_agency_budget_portal_vendor_employer_intermediary_or_status_gatekeeper_capturing_application_fee_delay_rejection_or_status_access_rent`.
- Bottleneck/evidence: `fee_schedule_and_waiver_channel; application_portal_and_receipt_gate +3 more`; evidence starts with `fee_schedule_cost_recovery_budget_dependency_and_waiver_rule_record; application_portal_rejection_receipt_biometric_appointment_and_queue_log +4 more`.
- Fallback duty: `immigration_and_benefit_authorities_must_preserve_fallback_fee_waiver_humanitarian_access_offline_filing_language_access_receipt_cure_status_continuity_and_no_forfeiture_when fee_or_portal_failure_blocks protected applicants`.


## Source IDs only

[S523][S524][S525]

[S523]: ../../SOURCES.md#S523
[S524]: ../../SOURCES.md#S524
[S525]: ../../SOURCES.md#S525
