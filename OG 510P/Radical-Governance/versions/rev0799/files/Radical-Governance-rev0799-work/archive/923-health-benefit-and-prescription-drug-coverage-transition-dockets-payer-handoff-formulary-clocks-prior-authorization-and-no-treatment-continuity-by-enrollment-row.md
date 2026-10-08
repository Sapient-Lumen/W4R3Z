# 923 — Health-benefit and prescription-drug coverage-transition dockets, payer handoff, formulary clocks, prior authorization, and no treatment continuity by enrollment row

## One-line thesis

Health-coverage and prescription-drug transitions are not safe because an enrollment row, plan card, formulary row, renewal status, special-enrollment period, or payment option exists; continuity requires a treatment-level docket that proves payer handoff, medication access, utilization-management cure, cost-sharing feasibility, notice reach, assisted navigation, and appeal / retroactive repair before a person experiences a gap.

## Why this matters

The archive already has an entitlement-continuity docket (`894`) and a Medicaid / CHIP unwinding case (`895`). Those notes correctly separate legal eligibility from paperwork failure. They do not yet force the next question: did the person keep receiving treatment, medication, and clinical support when coverage moved from one payer, plan, pharmacy benefit, account, formulary, or cost-sharing state to another?

Health transitions are uniquely dangerous because administrative status and clinical continuity diverge. A person can be technically enrolled but unable to fill a drug because the plan changed formularies, prior authorization is missing, step therapy reset, a pharmacy sees conflicting eligibility, premium payment has not posted, low-income subsidy status has shifted, the transition fill was temporary, or the exception / appeal route requires a prescriber statement the person cannot obtain in time. Conversely, a person can be administratively terminated but still eligible for retroactive coverage, fair-hearing protection, or Marketplace special enrollment if the handoff is completed.

The anti-theater rule is therefore **no treatment continuity by enrollment row**. Enrollment, plan selection, and public dashboards are only first-order statuses. They must be joined to the specific treatment, prescription, provider, pharmacy, cost, notice, and remedy states that determine whether care actually continues.

## Pattern pack

### 1. Split coverage continuity from treatment continuity

| State | Proof question |
| --- | --- |
| legal eligibility | Which coverage category, payer, subsidy, or benefit rule applies? |
| administrative enrollment | Is the person open, renewed, terminated, transferred, pending, plan-selected, premium-paid, or retroactively reinstated? |
| plan / product state | Which managed-care plan, Marketplace QHP, Medicare plan, Part D sponsor, PBM, formulary, and network apply on the service date? |
| treatment baseline | Which active diagnoses, prescriptions, therapies, devices, home services, specialists, and care plans existed before transition? |
| medication access | Can the drug be filled now, at the pharmacy, in the right quantity, with the right cost-sharing, without unsafe interruption? |
| utilization-management state | Are prior authorization, step therapy, quantity limit, non-formulary, exception, appeal, expedited review, and prescriber-statement states visible? |
| cost state | Are premium, deductible, copay, coinsurance, out-of-pocket cap, payment-plan, Extra Help / LIS, dual-eligible, and arrears states visible? |
| remedy state | Can the person obtain temporary supply, emergency fill, retroactive coverage, exception, appeal, fair hearing, reinstatement, or repayment? |

If the packet cannot join these states, the archive should not say coverage was continuous.

### 2. Payer handoff is a controlled transition, not a referral

A coverage handoff should leave a receipt trail:

- old payer / program status, end date, and reason;
- new payer / program eligibility result, plan selected, effective date, premium state, and first usable date;
- account transfer, application, attestation, and document state;
- prescription / treatment continuity list at the handoff date;
- provider, pharmacy, plan, PBM, and prescriber contact path;
- temporary-fill, emergency-fill, bridge supply, or clinical override route;
- retroactive correction and payment reconciliation route;
- denominator metrics for people who completed, failed, delayed, or reversed the handoff.

A warm transfer that cannot produce a coverage and treatment receipt is not yet a handoff.

### 3. Formularies are annual rule changes with clinical consequences

Medicare Part D, Marketplace plans, Medicaid managed-care plans, pharmacy benefit managers, state preferred drug lists, and specialty-drug policies all change over time. A plan card says almost nothing about whether a specific drug will be available. The packet must preserve:

1. drug name, dosage, quantity, route, prescriber, and condition;
2. old coverage rule and new coverage rule;
3. formulary tier, non-formulary status, selected-drug / redesign rule where relevant;
4. prior authorization, step therapy, quantity limit, network, specialty-pharmacy, and refill-too-soon flags;
5. transition fill, emergency fill, exception, appeal, and expedited decision route;
6. notice that the transition fill is temporary and what must happen next;
7. evidence that the prescriber and patient can complete the cure route before medication runs out.

A temporary transition supply is a bridge. It is not proof that the bridge reaches the other side.

### 4. Cost-sharing can be denial by another name

A drug may be covered and still inaccessible. The continuity docket should map:

- premium due and grace-period state;
- deductible and initial cost-sharing state;
- out-of-pocket cap and whether the drug counts toward it;
- Medicare Prescription Payment Plan election / likely-to-benefit notice / monthly billing state;
- Extra Help / LIS, Medicare Savings Program, Medicaid dual-eligible, or state assistance status;
- coupon / manufacturer assistance exclusion or coordination issue;
- pharmacy point-of-sale price and abandonment risk;
- retroactive premium, cost-sharing, or reimbursement correction.

A cost-reduction policy is not a continuity policy until people can use it before abandonment.

### 5. Clinical risk should set the clock

Ordinary administrative clocks are too slow for some treatments. The packet should label clinical-risk classes:

- insulin, HIV, transplant, cancer, seizure, serious mental illness, anticoagulation, medication-assisted treatment for opioid use disorder, dialysis / renal, pregnancy, complex pediatric care, home- and community-based services, durable medical equipment, and other high-interruption-risk therapies;
- whether interruption causes immediate danger, rebound, withdrawal, hospitalization, infection, disease progression, or loss of function;
- the maximum safe gap before expedited review or bridge supply is mandatory.

When clinical-risk evidence is high, the question is not whether the appeal clock is legal. The question is whether the person can keep treatment while the record is corrected.

### 6. Notice and assistance must be treatment-aware

Coverage notices often say how to renew, pick a plan, submit documents, or appeal. Treatment-aware notices must also say:

- which active prescriptions / services may need attention;
- how to check a formulary, network, prior authorization, and cost-sharing rule;
- how to request transition fill, exception, expedited decision, or clinical bridge;
- how to involve a prescriber, representative, navigator, SHIP counselor, broker, MCO, pharmacy, or caseworker;
- what to do if the app, account, document upload, language, disability, phone, address, or representative route fails.

A notice that preserves plan-choice rights but not medication continuity is incomplete.

### 7. Metrics must count gaps, not just enrollment

Minimum public metrics:

- people due for renewal / transition / plan change;
- renewed automatically, renewed by form, terminated for ineligibility, and procedurally terminated;
- transferred to Marketplace, selected plan, paid premium, and effectuated coverage;
- active high-risk-treatment cohort at transition;
- transition fills, emergency fills, exceptions, denials, appeals, reversals, expedited requests, and late prescriber statements;
- pharmacy rejection / abandonment where available;
- reinstatement, retroactive coverage, and reimbursement tail;
- treatment interruption, medication possession, and service-gap metrics where legally and technically feasible.

If a dashboard cannot show treatment gaps, it should not be used as evidence of treatment continuity.

### 8. Relationship to existing notes

Use this note with:

- `894` when coverage, benefit, or eligibility continuity is in question;
- `895` for Medicaid / CHIP unwinding and renewal-specific proof;
- `897` when reimbursements, cost-sharing corrections, or payment tails arise;
- `901` when identity, account, login, document upload, or credential access gates coverage;
- `905` when representatives, caregivers, payees, appointees, navigators, or appeal representatives preserve health rights;
- `913` when employment, UI, or income changes interact with coverage or subsidy loss;
- `917` and `919` when dashboards, state registers, local pilots, or public AI / automation records are cited as proof of health-service governance;
- `921` when non-English source, translation, or source-language risk affects health-benefit interpretation.

## Failure modes

- **No treatment continuity by enrollment row**: plan enrollment is treated as proof that medication and care continued.
- **No medication continuity by plan card**: possession of a card hides formulary, network, prior authorization, and cost-sharing failure.
- **No bridge by temporary fill**: a transition fill is counted as cure even though exception, prescriber, or plan change work remains unfinished.
- **No affordability by cap announcement**: out-of-pocket caps, payment plans, or subsidy programs are cited without pharmacy, billing, premium, or awareness evidence.
- **No handoff by referral**: a Medicaid-to-Marketplace, Marketplace-to-Medicare, plan-to-plan, or fee-for-service-to-managed-care referral lacks receipt, plan selection, premium, and first-use proof.
- **No appeal by form availability**: exception and appeal forms exist but clinical urgency, prescriber statement, representative authority, and interim supply are missing.
- **No safety by dashboard**: state or federal enrollment metrics hide medication interruption and treatment-abandonment tails.
- **No clinical cure by administrative deadline**: legal timelines are followed but treatment gaps occur before review.

## Anti-theater tests

1. Which payer, plan, PBM, formulary, pharmacy, and provider states apply before and after transition?
2. Which active medications and treatments are at risk, and what is the maximum safe gap?
3. Has the handoff produced an effective-date, premium, plan-selection, document, and first-use receipt?
4. Does the packet separate eligibility, enrollment, plan, formulary, utilization-management, cost, and remedy states?
5. Is a temporary or emergency fill available, and does it preserve time to complete the permanent cure?
6. Are prior authorization, step therapy, exception, appeal, expedited review, and prescriber-statement routes usable before harm?
7. Are Extra Help / LIS, Medicaid dual status, payment-plan election, premium, deductible, and cost-sharing states visible?
8. Does notice reach the person, representative, prescriber, pharmacy, and assister in time?
9. Can retroactive reinstatement, reimbursement, or payment correction repair harm if the handoff fails?
10. Do public metrics count medication / treatment gaps, not only enrollment, renewal, or disenrollment?

## Reconstruction instruction

Use this note before treating a health-coverage renewal, Medicaid / CHIP termination, Marketplace transfer, Medicare enrollment, Part D plan change, formulary change, payer migration, managed-care transition, pharmacy-benefit redesign, payment-plan option, prior authorization process, or drug exception route as evidence of continuity. Then route to `924` for the applied U.S. Medicaid / CHIP / Marketplace / Medicare Part D packet, `894` for entitlement-continuity doctrine, `897` for payment and reimbursement tails, `901` for credential and account gates, and `905` for representative / prescriber / assister authority.

## Sources

Source anchors are registered in `sources/source_keys.json` and attached to this note in `sources/source_catalog.json`, including CMS Medicaid / CHIP streamlining and access rules, HealthCare.gov Medicaid-to-Marketplace transition pages, Medicare Part D model materials, CMS Part D redesign and Medicare Prescription Payment Plan guidance, Medicare.gov Part D appeals guidance, KFF unwinding trackers, and recent medication-access research.
