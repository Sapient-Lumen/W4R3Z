# Sanctions, de-risking, financial-access, and humanitarian-channel ladder

## Question in one sentence

What ladder should distinguish targeted sanctions/AML enforcement from indiscriminate financial exclusion, corridor closure, and humanitarian access failure?[S507][S508][S509][S510][S511]

## Companion routes

Use this memo with:

- [`../10-framework/sanctions-aml-cft-de-risking-and-financial-access-routing.md`](../10-framework/sanctions-aml-cft-de-risking-and-financial-access-routing.md)
- [`../10-framework/migration-remittance-transfer-tax-and-diaspora-family-routing.md`](../10-framework/migration-remittance-transfer-tax-and-diaspora-family-routing.md)
- [`../10-framework/channel-pluralism-and-access-independence-routing.md`](../10-framework/channel-pluralism-and-access-independence-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — strict blocking | freeze or reject named sanctioned transactions. | Legitimate with specific basis, notice where lawful, and correction. |
| B — broad de-risking | exit categories of customers or corridors. | Suspect by default; often shifts public risk onto protected people. |
| C — tiered KYC | simplified due diligence for low-risk accounts. | Preferred where exclusion is the main risk. |
| D — humanitarian licenses/safe harbors | clarify permitted aid and payments. | Required where protected beneficiaries are harmed by uncertainty. |
| E — civil penalties | punish culpable sanctions/AML failures. | Must distinguish willfulness, recklessness, voluntary disclosure, and remediation. |

## Ten-gate ladder

1. **legal-basis gate** — identify statute, sanctions program, AML/CFT duty, tax-reporting rule, or internal risk appetite.
2. **specificity gate** — distinguish named party, beneficial owner, vessel, geography, product, payment purpose, name match, or vague category risk.
3. **floor gate** — identify migrants, refugees, humanitarian beneficiaries, low-balance accounts, small transmitters, or charity beneficiaries.
4. **risk-based gate** — apply simplified, standard, or enhanced due diligence instead of one-size-fits-all exclusion.[S507][S511]
5. **corridor gate** — test correspondent-banking and remittance access impacts, especially small or fragile corridors.[S508][S509]
6. **humanitarian gate** — require license clarity, safe-harbor guidance, and public fallback channels for protected aid.
7. **notice/correction gate** — give actionable reason and identity-resolution path unless secrecy is legally required.
8. **penalty gate** — evaluate culpability, voluntary disclosure, compliance program, harm, remediation, and aggravating factors.[S510]
9. **data gate** — collect only the facts needed to clear or block the transaction; do not build general surveillance by default.
10. **review gate** — revisit when account closures, delayed aid, remittance cost, false positives, or corridor exits rise.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| exact sanctioned party | block/report | targeted and documented. |
| weak name match | bounded hold | identity correction before closure. |
| low-risk inclusion case | tiered KYC | transaction caps and monitoring. |
| humanitarian payment | license/safe harbor | no avoidable toll. |
| bank category exit | supervisory review | inclusion remedy and corridor plan. |

## Failure-mode capsule

Axes: `screening_or_custody_lockout`, `access_exclusion`, `opacity_or_erasure`.

## Recalibration trigger capsule

Triggers: `cbr_loss`, `humanitarian_channel_blocked`, `sanctions_false_positive`, `blocked_account_delay`.


## Accountability capsule

Authoritative assignment: route `sanctions_aml_cft_derisking_financial_access` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `bank_compliance_officer_sanctions_authority_or_correspondent_bank_with_name_match_blocked_account_and_humanitarian_channel_control`.
- Rent/benefit trace: `bank_compliance_vendor_correspondent_bank_or_low_risk_portfolio_manager_capturing_de_risking_cost_savings_blocked_float_or_compliance_fee_rent`.
- Bottleneck/evidence: `sanctions_screening_and_name_match_queue; blocked_account_freeze_and_license_channel +3 more`; evidence starts with `sanctions_list_name_match_hit_and_false_positive_review_record; blocked_account_freeze_release_license_and_notice_file +4 more`.
- Fallback duty: `public_body_must_preserve_fallback_humanitarian_payment_channel_false_positive_cure_tiered_kyc_and_financial_access_nonforfeiture_when de_risking blocks lawful users`.


## Source IDs only

[S507][S508][S509][S510][S511]

[S507]: ../../SOURCES.md#S507
[S508]: ../../SOURCES.md#S508
[S509]: ../../SOURCES.md#S509
[S510]: ../../SOURCES.md#S510
[S511]: ../../SOURCES.md#S511
