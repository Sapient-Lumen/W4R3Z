# 991 — Cloudtainer fieldwork execution controls, incident clocks, audit logs, retention/release, and no outcome by operating log

## One-line thesis

Rev0792 established that fieldwork cannot begin from a design control, consent checklist, or authorization packet alone; rev0793 adds the missing execution layer so even authorized UI or housing fieldwork would need pause clocks, incident reporting, audit-log review, breach response, retention/disposition authority, and disclosure-reviewed release before any result can be trusted.

## Why this matters

The cube had reached a dangerous threshold. It was no longer merely saying “affected-person proof is missing.” It had begun to define how UI claimant and housing household evidence might be sampled, screened, authorized, and held outside the archive. That is useful, but it creates a new failure mode: once a future owner authorizes collection outside the cube, the archive could treat operating paperwork as if it were outcome proof.

That would be a new form of administrative theater. A fieldwork log can prove that contact was attempted. It does not prove that a benefit was paid, a hold was lifted, an overpayment was waived, an appeal was corrected, possession was retained, a household stayed housed, a screening record stopped harming someone, or a person experienced less coercion.

The new `metadata/fieldwork_execution_controls.json` sits after `metadata/fieldwork_authorization_gates.json`. It is not a permission slip and it is not a data store. It says what must be true if fieldwork is later approved elsewhere: contact attempts, refusals, withdrawals, incidents, audit failures, suspected breaches, retention decisions, destruction holds, and publication releases must be logged, paused, escalated, and reviewed outside the cube. The cube may carry only redacted status and aggregate-safe findings.

The governing rule is **no outcome by operating log**.

## Pattern pack

1. **Authorization is not execution.** An approved protocol still needs a start/stop register, approved-channel ledger, operator roles, and custody-aware operating logs.
2. **Execution is not outcome.** Contact attempts, surveys, interviews, extracts, and audit logs are evidence of process, not proof of payment, possession, waiver, appeal, re-housing, debt relief, or durable stability.
3. **Withdrawal defeats momentum.** Refusal or withdrawal must pause contact and cannot affect benefits, representation, shelter, rental assistance, adjudication, payment, waiver, appeal, identity review, or fraud-control posture.
4. **Incident clocks must be separate from publication clocks.** Unanticipated problems, adverse events, protocol deviations, serious or continuing noncompliance, and safety concerns are reviewed before outputs are summarized.
5. **PII breach suspicion pauses the lane.** Contact, linkage, extraction, and publication stop while the owner, privacy officer, security owner, and custodian assess risk and response outside the cube.
6. **Audit failure is a stop condition.** Missing or failed logs make the fieldwork result unfit for archive reliance until the custodian/security owner resolves the failure.
7. **Retention is a legal control, not a cleanup habit.** No outside fieldwork record is destroyed or transferred without disposition authority, hold clearance, and custodian-controlled evidence.
8. **Disclosure review comes last.** No quote, local office, building, provider, shelter, docket, employer, rare cohort, or geographic detail becomes public merely because the raw fieldwork exists.

## What changed

### Fieldwork execution controls

Rev0793 adds two non-closing controls.

`FEC-UI-001` covers unemployment-insurance claimant fieldwork after any future authorization. It requires a date-bounded execution ledger, aggregate-safe contact counts, consent/refusal/withdrawal tracking outside the cube, incident and unanticipated-problem triage, PII breach response, audit-log review, retention/disposition authority, and disclosure review before any public output.

`FEC-HC-001` covers housing household fieldwork after any future authorization. It adds the same operating controls, with housing-specific safety triggers for retaliation, lockout, domestic safety, immigration sensitivity, landlord/adverse-party exposure, shelter/provider risk, rare geographies, and household narrative detail.

Both controls link back to the authorization gates, field-intake controls, sampling gates, and outcome-tail plans. Both block `GAP-029`, `GAP-031`, `GAP-032`, and `GAP-033`. Neither can close them.

### Execution ledger boundaries

The execution ledger is deliberately split. Outside-cube owners or custodians may need full operating evidence: who was contacted, what channel was used, whether consent was given or withdrawn, whether an incident occurred, what audit logs show, whether a breach was suspected, what records schedule applies, and whether disclosure review cleared an output. The cube must not hold that private operating evidence.

Inside the cube, only redacted execution status, aggregate-safe contact counts, disclosure-reviewed findings, and non-identifying protocol metadata may appear later. Names, addresses, claim numbers, docket numbers, contact rosters, linkage keys, raw transcripts, raw audio/video, private screenshots, partner case records, incident details, breach details, audit logs, and secure-environment raw outputs remain prohibited.

### Incident, audit, breach, and retention receipts

Rev0793 adds locator-level source receipts for OHRP unanticipated-problem guidance, OHRP incident reporting, OHRP continuing review, 45 CFR 46.109, OMB M-17-12 breach response, NIST SP 800-53 audit/accountability posture, and NARA records scheduling. These receipts do not authorize fieldwork. They force operating questions:

- What counts as an incident, adverse event, unanticipated problem, or protocol deviation?
- Who receives the initial and follow-up reports?
- What changes require continuing review or amendment?
- What happens if a participant withdraws or refusal is not honored?
- What happens if audit logging fails?
- What happens if PII may have been exposed?
- What retention schedule, destruction authority, and litigation-hold rule applies?
- What disclosure review must pass before any output leaves the secure environment?

### Audit/refactor

The bounded refactor is a fieldwork-control lint helper. The new helper centralizes the repeated check that a fieldwork surface links to the correct authorization gate, intake control, sampling gate, outcome-tail plan, live gaps, and source-claim receipts before bespoke checks run. This reduces the risk that each new surface adds a slightly different chain of cross-reference checks.

The Makefile target chain is also extended: `fieldwork_execution_controls` now depends on `fieldwork_authorization_gates` before common test matrices and case-matrix generation. This keeps individual targets aligned with `build_all.py` rather than relying on full-build luck.

## What this still does not do

It does not approve fieldwork.

It does not execute fieldwork.

It does not contact claimants or households.

It does not create consent, refusal, withdrawal, incident, breach, audit, retention, destruction, or publication records.

It does not access claim records, court records, provider records, shelter records, screening records, recordings, screenshots, contact rosters, linkage keys, or secure-environment outputs.

It does not prove payment, waiver, debt relief, appeal success, possession retention, re-housing, screening correction, durable stability, coercion reduction, or material redistribution.

It does not close any live gap.

## Anti-theater tests

1. Pick `FEC-UI-001`. Does it say fieldwork is still `not_executed`?
2. Pick `FEC-HC-001`. Does it pause for retaliation, lockout, safety, or disclosure risk rather than turning household contact into reader value?
3. Pick either control. Does it prohibit incident details, breach details, audit logs, raw transcripts, linkage keys, and secure-environment raw output from entering the cube?
4. Pick either control. Does audit-log failure pause fieldwork and output release?
5. Pick either control. Does suspected PII breach pause contact, linkage, extraction, and publication?
6. Pick either control. Does retention/destruction require outside authority rather than a maintainer cleanup choice?
7. Pick `generated/FIELDWORK_EXECUTION_CONTROLS.md`. Does it show blockers and stop conditions rather than field results?
8. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the new execution layer?

## Source posture

Use OHRP unanticipated-problem and incident-reporting guidance as incident-clock and corrective-action triggers, not as a substitute for local IRB or institutional reporting. Use OHRP continuing-review guidance and 45 CFR 46.109 to keep approved fieldwork reviewable after changes, not to imply that review has occurred. Use OMB M-17-12 for PII breach preparedness and risk response, not as a cube breach plan. Use NIST SP 800-53 for audit/accountability and privacy-control selection, not as system certification. Use NARA records scheduling guidance to require retention/disposition authority, not to decide what the archive may destroy.

The practical rule is: **the cube can preserve execution boundaries, but it must not become the fieldwork operator, incident file, audit log, breach record, retention authority, or outcome proof.**
