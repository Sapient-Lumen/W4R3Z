# Trust-fund recovery responsible-person and willfulness ladder

Use this calibration memo when payroll trust-fund taxes have not been collected, accounted for, deposited, or paid, and the live frontier question is **how much evidence is enough before a business-side withholding failure becomes personal trust-fund recovery against a named person**.

## Companion routes

- [`../10-framework/sanctions-culpability-and-disclosure-routing.md`](../10-framework/sanctions-culpability-and-disclosure-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/record-asymmetry-burden-shifting-and-adverse-inference-routing.md`](../10-framework/record-asymmetry-burden-shifting-and-adverse-inference-routing.md)
- [`../10-framework/private-ordering-non-waiver-and-anti-indemnification-routing.md`](../10-framework/private-ordering-non-waiver-and-anti-indemnification-routing.md)
- [`../../archive/192-trust-fund-recovery-penalty-responsible-person-payroll-withholding-and-third-party-payer-rules-should-not-be-turned-into-responsible-person-rents-or-payroll-collapse-scapegoat-traps.md`](../../archive/192-trust-fund-recovery-penalty-responsible-person-payroll-withholding-and-third-party-payer-rules-should-not-be-turned-into-responsible-person-rents-or-payroll-collapse-scapegoat-traps.md)

## Option scan

| Option | Description | Default judgment |
|---|---|---|
| A — business-account only | never assess personal trust-fund recovery; pursue the employer or bankruptcy estate only.[S321][S323][S324] | Reject: fails where withheld worker money was knowingly diverted by real controllers. |
| B — title / signer sweep | assess officers, signers, bookkeepers, owners, and payroll-console users whenever the business account cannot pay.[S322][S323][S325] | Reject: turns visibility into scapegoating and ignores independent judgment. |
| C — evidence-weighted control-and-willfulness ladder | require period-specific proof of trust amount, real authority, independent judgment, knowledge or disregard, and usable pre-assessment protest before personal recovery hardens.[S322][S323][S324][S325][S326][S327] | Adopt. |
| D — fraud-style escalation first | treat most unpaid withholding as intentional evasion or criminal shadow unless the target proves innocence.[S39][S99][S324] | Reject: collapses cash distress, outsourced payroll failure, and willful diversion. |

## Adopted ladder

1. **No personal TFRP lane** — use when the target was a worker, payee, directed bill-payer, ministerial clerk, nominal signer, or outside preparer without independent creditor-choice authority.[S21][S39][S322][S325]
2. **Record-development lane** — use when title, bank access, check-signing, payroll software, board role, or ownership creates a concrete question but the authority, knowledge, or payment-choice record is incomplete.[S322][S323][S325]
3. **Provider-failure / payroll-fraud lane** — use when a payroll service provider, reporting agent, section 3504 agent, PEO, CPEO, bank, or platform materially controlled deposits, account visibility, or misdirection; evaluate employer oversight separately from provider fault.[S318][S323][S328][S329]
4. **Business-collection / arrangement lane** — use when a responsible actor exists but prompt business payment, short-term full payment, current filing compliance, instalment treatment, or account correction can resolve the trust amount without unnecessary person-level multiplication.[S39][S318][S325]
5. **Civil TFRP lane** — use when the target had independent judgment, knew or recklessly disregarded unpaid trust taxes, and chose not to collect, account for, or pay them while other payments or decisions continued.[S322][S323][S324]
6. **Upstream-enabler / professional discipline lane** — use when provider fraud, payroll-agent design, preparer misconduct, platform withholding architecture, or shell-service behavior multiplied the failure beyond one firm.[S21][S39][S99][S328][S329]
7. **Criminal-referral lane** — reserve for serious falsification, concealment, organized diversion, or repeated high-value evasion after civil proof and rights-protecting thresholds are met.[S39][S99]

## Evidence packet before personal assessment

A personal trust-fund recovery packet should show:

- the employer, EIN, periods, forms, and trust-fund portion;
- payments, credits, deposits, offsets, refunds, provider recoveries, and open ledger disputes;
- the target person's formal title, actual duties, bank authority, signing authority, payroll access, tax-deposit access, and creditor-choice authority;
- facts showing knowledge, notice, participation in nonpayment, creditor preference, reckless disregard, or obstruction;
- third-party payer structure, authorization scope, EFTPS visibility, provider failure or fraud, and who controlled deposit timing;
- interview / Form 4180 status, proposed-assessment explanation, Letter 1153 delivery date, deadline, protest path, and appeal status.[S322][S323][S324][S325][S326][S327][S328][S329]

## Defaults

- **Directed ministerial worker:** no personal TFRP; shift records to the employer, officer, provider, or controller who actually chose payment priorities.[S21][S322][S325]
- **Nominal officer with ambiguous authority:** record-development lane; do not assess until independent judgment, knowledge, and period facts are shown.[S322][S323][S325]
- **Owner-manager with creditor-choice power and notice:** civil TFRP lane if willful failure is shown, with credit symmetry for all payments and recoveries.[S322][S323][S324][S326]
- **Payroll-service fraud victim:** provider-failure lane plus penalty-relief / proof-shift review; do not ignore outsourcing facts when judging willfulness.[S328][S329]
- **Multiple responsible persons:** maintain shared credit memory; do not let separate account surfaces produce duplicate pressure.[S39][S41][S175][S326][S327]

## Red flags requiring supervisory review

- assessment mainly because the person is easiest to locate, employed, solvent, family-connected, or listed on forms;
- Form 4180 or equivalent interview was unavailable, incomplete, or used only as a confession device;
- Letter 1153 or protest cues do not identify periods, amounts, duties, appeal route, and payment disputes;
- payroll-provider default or fraud appears in the facts but not in responsibility / willfulness analysis;
- business payments or provider recoveries are not mirrored across person-level accounts;
- collection pressure starts before pre-assessment protest and bounded record correction can matter.[S322][S325][S326][S327][S328][S329]

## Failure-mode capsule

Axes: `classification_or_label_arbitrage`, `custody_blind_penalty`, `liability_misassignment`. Watch for title/check-access shortcuts substituting for authority, knowledge, willfulness, notice, and payment-credit accounting.

## Recalibration trigger capsule

Axes: `willfulness_or_personal_liability_dispute`, `record_or_measurement_staleness`, `property_or_proceeds_contest_failure`. Reopen when Form 4180, Letter 1153, protest, willfulness, provider-failure, or no-double-collection records are thin.

## Accountability capsule

Authoritative assignment: route `trust_fund_recovery_responsible_person_and_willfulness` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `person_with_actual_payroll_tax_collection_payment_authority_and_willful_trust_fund_nonpayment_control`.
- Rent/benefit trace: `business_or_creditor_benefiting_from_using_withheld_trust_fund_taxes_as_working_capital_or_preferring_other_payments`.
- Bottleneck/evidence: `payroll_withholding_and_deposit_rail; bank_account_and_check_signing_control +3 more`; evidence starts with `withholding_liability_deposit_failure_and_trust_fund_amount_record; actual_payment_authority_bank_signature_role_and payroll_control_record +3 more`.
- Fallback duty: `public_body_must_preserve_fallback_Form_4180_interview_Letter_1153_notice_protest_appeal_payment_credit_and_no_double_collection_channel`.


## Source IDs only

[S21][S39][S41][S99][S175][S318][S321][S322][S323][S324][S325][S326][S327][S328][S329]

[S21]: ../../SOURCES.md#S21
[S39]: ../../SOURCES.md#S39
[S41]: ../../SOURCES.md#S41
[S99]: ../../SOURCES.md#S99
[S175]: ../../SOURCES.md#S175
[S318]: ../../SOURCES.md#S318
[S321]: ../../SOURCES.md#S321
[S322]: ../../SOURCES.md#S322
[S323]: ../../SOURCES.md#S323
[S324]: ../../SOURCES.md#S324
[S325]: ../../SOURCES.md#S325
[S326]: ../../SOURCES.md#S326
[S327]: ../../SOURCES.md#S327
[S328]: ../../SOURCES.md#S328
[S329]: ../../SOURCES.md#S329
