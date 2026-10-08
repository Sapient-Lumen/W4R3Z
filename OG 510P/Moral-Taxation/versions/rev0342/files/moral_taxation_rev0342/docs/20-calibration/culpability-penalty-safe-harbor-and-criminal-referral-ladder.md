# Culpability, penalty, safe-harbor, and criminal-referral ladder

## Question in one sentence

Given the archive's closed rules that tax enforcement should be **proportionate, floor-protecting, explainable, and strongest against strategic evasion rather than easy debtors**, **what is the smallest workable ladder for deciding when non-compliance warrants correction only, when it warrants compensating interest, when low automatic civil additions are justified, when stronger culpability-scaled penalties or enabler penalties should apply, when bounded disclosure / self-correction lanes may soften the response, and when criminal referral is justified at all?**[S27][S39][S98][S99][S100][S321][S322][S323][S324][S325][S326][S327][S328][S329][S172][S173][S208][S312][S313][S315][S317][S318][S319][S320]

## Companion routes

Use this memo with:

- [`../10-framework/enforcement-proportionality-and-recovery-routing.md`](../10-framework/enforcement-proportionality-and-recovery-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/timing-and-liquidity-routing.md`](../10-framework/timing-and-liquidity-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/standing-representation-and-remedy-routing.md`](../10-framework/standing-representation-and-remedy-routing.md)
- [`../10-framework/classification-arbitrage-and-substance-over-form-routing.md`](../10-framework/classification-arbitrage-and-substance-over-form-routing.md)

Route: separate inability from bad faith, separate time-value recovery from punishment, keep ordinary correction easier than coercive escalation, push the harshest sanctions upstream toward strategic evasion and professional enabling, and reserve criminal treatment for serious tax crime rather than using it as the ordinary face of collection.[S27][S39][S98][S99][S100][S321][S322][S323][S324][S325][S326][S327][S328][S329]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — tax due only, almost no sanctions | assess the underlying tax and avoid most interest and penalties except in rare fraud cases.[S98] | Reject: under-protects compliant taxpayers and makes late payment or concealment a cheap source of finance. |
| B — broad automatic penalties for most failures | rely on strong automatic additions for late filing, late payment, deposit failures, accuracy disputes, and reporting mistakes with limited distinction among hardship, reasonable cause, negligence, repeated carelessness, and intentional evasion.[S39][S98][S312][S313][S318][S319] | Reject: blurs inability and bad faith and punishes easy debtors more than strategic evaders. |
| C — differentiated sanction ladder | sort cases into correction-only, interest-only, low automatic civil additions, culpability-scaled penalties, upstream enabler penalties, or criminal referral.[S27][S39][S98][S99][S100][S321][S322][S323][S324][S325][S326][S327][S328][S329] | Adopt. |
| D — wide criminal backdrop plus periodic amnesties | keep ordinary non-compliance under a threatening criminal shadow while periodically using disclosure or amnesty rounds to clear hidden liabilities.[S99][S100] | Reject: too punitive in routine administration and too permissive toward strategic waiting. |

## Six-rung ladder

1. **correction-only lane** — use when no tax loss or no culpable non-compliance is shown because the failure is de minimis, administration-caused, promptly self-corrected, or within a clearly signaled safe harbor,[S27][S39][S98]
2. **interest-only lane** — use when tax was paid late or underpaid without evidence of concealment, so the state restores time value without pretending every delay is punishable misconduct,[S98]
3. **low automatic civil-addition lane** — use for routine late filing or late payment failures only where deterrence is justified and hardship, waiver, and cure pathways remain real,[S39][S98]
4. **culpability-scaled civil-penalty lane** — use for negligence, recklessness, repeated non-co-operation, false statements, obstruction, or strategic threshold / entity games, with stronger treatment for repeated and better-resourced actors,[S39][S98][S99]
5. **enabler / controller / platform lane** — use when the violation is materially designed, multiplied, or industrialised by preparers, payroll agents, platform operators, shell-service providers, controller groups, or similar upstream actors,[S99]
6. **criminal-referral lane** — use only for serious intentional evasion, falsification, concealment, organised fraud, or repeated high-value offending where civil measures no longer describe the conduct accurately and suspects' rights remain fully protected.[S99][S100]

## Provisional recommendation

Adopt **Option C — the differentiated sanction ladder** as the archive's default calibration for live penalty disputes.[S27][S39][S98][S99][S100][S321][S322][S323][S324][S325][S326][S327][S328][S329]

Presumption:

- use the **correction-only lane** when the administration caused the defect, the error is trivial, the taxpayer disclosed quickly, or the safe-harbor purpose would be defeated by punishment,
- use the **interest-only lane** when the state's real claim is the value of delayed payment rather than a punitive moral judgment,
- use the **low automatic civil-addition lane** for routine late failures only if hardship, waiver, and cure paths remain open,
- move to the **culpability-scaled civil-penalty lane** when conduct becomes negligent, reckless, obstructive, repeated, or strategically evasive,
- move sanctions to the **enabler / controller / platform lane** whenever upstream actors materially designed, enabled, or multiplied the misconduct,
- and reserve the **criminal-referral lane** for serious intentional tax crime rather than ordinary debt management.

That is the narrowest workable setting because it protects compliance norms without collapsing the difference between delay, incapacity, carelessness, strategic evasion, and criminal fraud.

For current AI systems, the implication is direct: **present LLMs are not direct sanction subjects. Where model-generated filings, agentic bookkeeping tools, or platform automation contribute to violations, liability and sanction should still route through controllers, deployers, preparers, firms, and other rights-bearing human or organisational actors unless and until person-threshold conditions are actually crossed.**[S27][S39][S99]

## Default sanction table

| Context | Default lane | Guardrail |
|---|---|---|
| trivial, administration-caused, or quickly corrected mismatch | correction-only or interest-only | no fraud language for explainable worker-side mismatches. |
| late filing/payment with visible principal and relief facts | interest-only or low automatic addition | public abatement/recomputation; no paid abatement maze. |
| payroll, platform, or remitter deposit failure | remitter/enabler lane | do not shift remitter control failures to workers.[S41] |
| proposed trust-fund personal recovery | TFRP side ladder | require authority, knowledge, willfulness, Letter 1153/Form 4180, and payment-credit proof. |
| repeated negligent, reckless, or obstructive conduct | culpability-scaled civil penalty | tie escalation to blameworthy repeated conduct, not administrative irritation. |
| falsified books, shell-chain concealment, organised fraud, or serious intentional evasion | criminal-referral lane | require rights-protecting proof, counsel, and no civil-collection proxy. |

## Failure-mode capsule

Axes: `duplicate_penalty_stack`, `liability_misassignment`, `trapdoor_or_cliff`, `penalty_farming`. Watch for penalty cascades, safe-harbor erasure, paid abatement mazes, or downstream punishment of upstream-enabled failures.

## Recalibration trigger capsule

Axes: `coercive_escalation_or_criminal_boundary`, `ability_or_floor_sanction_failure`, `classification_or_boundary_drift`. Reopen when automatic additions, erased reasonable cause, enabler patterns, or criminal-referral escalation appear.

## Accountability capsule
Authoritative assignment: route `culpability_penalty_safe_harbor_and_criminal_referral` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `penalty_decisionmaker_or_enforcement_program_owner_controlling_culpability_safe_harbor_and_escalation_thresholds`.
- Rent/benefit trace: `penalty_program_or_enabler_avoiding_upstream_accountability_while_downstream_taxpayer_bears_automatic_additions`.
- Bottleneck/evidence: `penalty_notice_and_computation_system; reasonable_cause_or_first_time_abatement_channel +3 more`; evidence starts with `penalty_notice_computation_base_and_statutory_authority_record; control_notice_fault_reasonable_cause_and_willfulness_evidence_record +3 more`.
- Fallback duty: `public_body_must_preserve_fallback_notice_abatement_reasonable_cause_safe_harbor_appeal_and_nonforfeiture_channel_for_penalty_cases`.


## Source IDs only

[S27][S39][S98][S99][S100][S321][S322][S323][S324][S325][S326][S327][S328][S329]


## Rev0270 criminal-referral boundary refinement

The sixth rung in this ladder now points to a dedicated criminal-tax boundary memo. Use [`criminal-tax-referral-civil-criminal-boundary-voluntary-disclosure-and-restitution-ladder.md`](criminal-tax-referral-civil-criminal-boundary-voluntary-disclosure-and-restitution-ladder.md) before recommending criminal posture. The threshold is not "serious tax due" or "hard case"; it is evidence-weighted willfulness plus affirmative deceptive acts, documented through fraud development and a referral theory that can identify actor, period, scheme, taxpayer explanation, estimated criminal tax liability, and proof method.[S353][S354][S355][S363][S364][S365]

Voluntary disclosure should remain a side lane for willful exposure, not a general amnesty market or paid confession gate. Restitution and civil re-entry must be no-double-recovery and credit-visible.[S357][S359][S360][S362]


## Rev0271 informant-source firewall

A whistleblower tip may start the culpability screen but cannot finish it. Before a case moves from correction to penalty, fraud development, or criminal referral, the claim must be corroborated, translated into contestable facts, and separated from award incentives, source conflict, or retaliatory motive.[S366][S373][S374][S376]

Use [`whistleblower-tip-classification-confidentiality-award-and-accused-taxpayer-protection-ladder.md`](whistleblower-tip-classification-confidentiality-award-and-accused-taxpayer-protection-ladder.md) as the side screen whenever a penalty theory begins with an informant claim.

### Offshore information-return side screen

Before an international information-return case enters the ordinary penalty ladder, run the offshore ladder. The key questions are: which foreign object and which reporting regime are at issue; whether there is tax loss or only visibility failure; whether nonwillful FBAR treatment is per-report; whether duplicate Form 8938 / FBAR facts exist; whether Form 3520 / 3520-A trustee or gift context limits culpability; whether Form 5471 / 5472 / 8865 / 8858 facts show control or merely mapping; and whether streamlined, delinquent, reasonable-cause, abatement, or Appeals routes should resolve the case before harsher sanctions.[S407][S408][S409][S414][S415][S416][S419][S420][S423][S425][S426][S427][S428][S429][S430][S173][S432][S433]

Use [`international-information-return-fbar-fatca-and-offshore-correction-ladder.md`](international-information-return-fbar-fatca-and-offshore-correction-ladder.md) whenever a sanction theory begins with foreign accounts, FATCA data, FBAR, foreign trust, foreign gift, foreign entity, foreign branch, or offshore correction facts.

[S353]: ../../SOURCES.md#S353
[S354]: ../../SOURCES.md#S354
[S355]: ../../SOURCES.md#S355
[S357]: ../../SOURCES.md#S357
[S359]: ../../SOURCES.md#S359
[S360]: ../../SOURCES.md#S360
[S362]: ../../SOURCES.md#S362
[S363]: ../../SOURCES.md#S363
[S364]: ../../SOURCES.md#S364
[S365]: ../../SOURCES.md#S365

[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S98]: ../../SOURCES.md#S98
[S99]: ../../SOURCES.md#S99
[S100]: ../../SOURCES.md#S100
[S172]: ../../SOURCES.md#S172
[S173]: ../../SOURCES.md#S173
[S208]: ../../SOURCES.md#S208
[S312]: ../../SOURCES.md#S312
[S313]: ../../SOURCES.md#S313
[S315]: ../../SOURCES.md#S315
[S317]: ../../SOURCES.md#S317
[S318]: ../../SOURCES.md#S318
[S319]: ../../SOURCES.md#S319
[S320]: ../../SOURCES.md#S320
[S41]: ../../SOURCES.md#S41

[S321]: ../../SOURCES.md#S321
[S322]: ../../SOURCES.md#S322
[S323]: ../../SOURCES.md#S323
[S324]: ../../SOURCES.md#S324
[S325]: ../../SOURCES.md#S325
[S326]: ../../SOURCES.md#S326
[S327]: ../../SOURCES.md#S327
[S328]: ../../SOURCES.md#S328
[S329]: ../../SOURCES.md#S329
[S366]: ../../SOURCES.md#S366
[S373]: ../../SOURCES.md#S373
[S374]: ../../SOURCES.md#S374
[S376]: ../../SOURCES.md#S376
[S407]: ../../SOURCES.md#S407
[S408]: ../../SOURCES.md#S408
[S409]: ../../SOURCES.md#S409
[S414]: ../../SOURCES.md#S414
[S415]: ../../SOURCES.md#S415
[S416]: ../../SOURCES.md#S416
[S419]: ../../SOURCES.md#S419
[S420]: ../../SOURCES.md#S420
[S423]: ../../SOURCES.md#S423
[S425]: ../../SOURCES.md#S425
[S426]: ../../SOURCES.md#S426
[S427]: ../../SOURCES.md#S427
[S428]: ../../SOURCES.md#S428
[S429]: ../../SOURCES.md#S429
[S430]: ../../SOURCES.md#S430
[S432]: ../../SOURCES.md#S432
[S433]: ../../SOURCES.md#S433
