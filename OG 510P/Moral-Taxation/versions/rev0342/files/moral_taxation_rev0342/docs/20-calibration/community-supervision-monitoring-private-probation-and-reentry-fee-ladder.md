# Community supervision, monitoring, private probation, and reentry-fee ladder

## Question in one sentence

What ladder should distinguish lawful supervision conditions from fee-funded reentry rents, private-probation tolls, and poverty-based revocation?[S516][S517][S518][S537]

## Companion routes

Use this memo with:

- [`../10-framework/community-supervision-private-probation-and-monitoring-fee-routing.md`](../10-framework/community-supervision-private-probation-and-monitoring-fee-routing.md)
- [`../10-framework/court-fines-fees-ability-to-pay-and-civil-access-routing.md`](../10-framework/court-fines-fees-ability-to-pay-and-civil-access-routing.md)
- [`../10-framework/private-ordering-non-waiver-and-anti-indemnification-routing.md`](../10-framework/private-ordering-non-waiver-and-anti-indemnification-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — no supervision fee | public funding of public safety. | Preferred default. |
| B — capped fee | small charge with waiver. | Only if no floor burden. |
| C — private vendor billing | vendor collects from supervisee. | Presumptively suspect. |
| D — mandatory monitoring/testing | required compliance service. | Cost-controlled and waivable. |
| E — revocation for nonpayment | incarceration or extension. | Reject absent willful refusal. |

## Ten-gate ladder

1. **condition gate** — identify whether the charge is tied to supervision, treatment, testing, monitoring, room/board, or collection.
2. **public-function gate** — decide whether the service is core public safety and should be appropriated, not user-funded.
3. **conflict gate** — test whether agency or vendor revenue rises with supervision length or violation.[S537]
4. **ability gate** — assess income, employment, dependents, restitution, housing, and health costs.[S516]
5. **reentry gate** — prioritize work, housing, transportation, treatment, and family stability.[S518]
6. **vendor gate** — ban captive markup, pay-to-report, or private collection of court coercion.
7. **duration gate** — prohibit extending supervision solely for debt.
8. **willfulness gate** — no revocation, jail, warrant, or reincarceration without willful nonpayment.[S517]
9. **cancellation gate** — forgive old or uncollectible administrative debt where collection undermines reentry.
10. **review gate** — recalibrate when fees correlate with violation, extension, or reincarceration.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| low-income supervisee | waiver / cancellation | no reentry charge. |
| mandatory device/testing | public procurement price | no vendor toll. |
| nonpayment | ability hearing | no automatic violation. |
| private probation | public alternative | conflict ban. |
| old debt | amnesty | reentry first. |

## Failure-mode capsule

Axes: `private_probation_subsidy_lock_in`, `trapdoor_or_cliff`, `supervision_debt_extension`. Watch for fee-funded supervision, monitoring, and nonpayment sanctions that extend debt or block reentry.

## Recalibration trigger capsule

Axes: `ability_or_floor_sanction_failure`, `capacity_or_control_shift`, `remedy_or_contest_failure`. Reopen when ability hearing is missing, vendor incentives reward violations, or nonpayment extends supervision.

## Accountability capsule

Authoritative assignment: route `community_supervision_private_probation_monitoring_fees` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `sentencing_court_supervision_agency_or_vendor_contract_owner_controlling_fee_and_nonpayment_sanction`.
- Rent/benefit trace: `private_probation_monitoring_or_collection_vendor_and_fee_funded_supervision_budget_benefiting_from_captive_supervisee_payments`.
- Bottleneck/evidence: `supervision_order; vendor_contract +3 more`; evidence starts with `supervision_order_condition_and_fee_authority_record; vendor_contract_markup_commission_and_collection_terms_record +3 more`.
- Fallback duty: `public_body_must_preserve_no_rent_fallback_supervision_payment_waiver_notice_cure_ability_hearing_and_nonrevocation_channel_with_fallback_channel`.


## Source IDs only

[S516][S517][S518][S537]

[S516]: ../../SOURCES.md#S516
[S517]: ../../SOURCES.md#S517
[S518]: ../../SOURCES.md#S518
[S537]: ../../SOURCES.md#S537
