# 984 — Cloudtainer affected-person evidence pilot, UI and housing receipt tests, source-receipt spine, build-registry refactor, and no proof by official surface

## One-line thesis

The riskiest unfinished work is not another doctrine family; it is proving that official records, generated rows, portal states, and dashboards can be joined to affected-person outcomes without storing private lives in the cube or pretending field validation has already happened.

## Why this matters

Rev0785 correctly named the mission kernel: evidence continuity from authority through delivery, affected-person outcome, contestability, repair, continuity, and source posture. The next dangerous failure is to answer that diagnosis with more archive scaffolding. That would repeat the cube's vice: generating disciplined surfaces that feel like progress while the public outcome remains untested.

This note therefore does three narrower things. First, it turns the affected-person gap into two operational pilots: unemployment insurance and housing continuity. Second, it creates a receipt spine that records what an official source can prove and what it cannot prove. Third, it refactors build orchestration just enough to reduce private registries inside the tooling, without spending the revision on registry ceremony.

The governing rule is **no proof by official surface**. A survey framework, claim-status page, modernization report, court-filing dataset, right-to-counsel report, or tenant-screening page can justify a test. It cannot by itself prove that a person was paid, housed, heard, protected, or repaired.

## Pattern pack

1. **Affected-person proof starts with a boundary, not a claim of access.** The pilot records official-source posture first so the archive can say what is still missing without inventing lived evidence.
2. **Unemployment insurance must follow a claimant, not a queue.** A held claim needs issue state, notice, cure path, channel burden, appeal or waiver, and payment-after-cure receipt.
3. **Housing continuity must follow a household and unit, not a docket.** A filing, award, counsel statute, payment, or screening correction must be joined to possession, displacement, shelter, re-housing, and durable stability.
4. **Non-users are part of the denominator.** People who never complete the portal, never reach counsel, abandon an application, miss a hearing, cannot verify identity, or are screened out after a stale record are not allowed to disappear from the evidence frame.
5. **Remedy completion is separate from remedy availability.** A waiver form, appeal route, correction right, rental-assistance award, or representation mandate does not prove repair until the consequence changed.
6. **The receipt spine is deliberately privacy-bounded.** It stores claim-to-source posture and missing proof classes, not names, addresses, claim numbers, case numbers, screenshots, or private records.
7. **A build refactor is useful only when it lowers risk.** Centralizing `build_all.py` steps prevents another hidden orchestration list from drifting, but it is secondary to the affected-person proof work.
8. **Do not close the gap because a pilot exists.** The correct status is in progress until external evidence, field observation, user-side records, or independently collected outcome data can validate the packet.

## Pilot 1 — unemployment-insurance claimant receipt

The UI packet now needs two additional tests. `UI-11` asks whether the packet measures claimant burden, non-users, abandonment, assisted-digital sufficiency, and subgroup experience rather than treating a portal, claim count, or survey as complete access evidence. `UI-12` asks whether a delayed, held, overpaid, waived, appealed, or identity-theft-related claim can be followed through actual payment, debt removal, refund, certification restoration, notice correction, or other completed remedy.

The minimum claimant receipt should include: claim issue state; channel attempted; notice actually received; steps demanded; records gathered; staff or representative contact; delay; out-of-pocket cost; lost certifications; appeal or waiver action; cure acceptance; payment after cure; debt or recovery status; and remaining harm. The pilot does not require the cube to store personal data. It requires the cube to stop treating official status as outcome proof.

## Pilot 2 — housing-continuity household receipt

The housing packet now needs two additional tests. `HC-11` asks whether the packet can distinguish a filing, portal state, counsel law, payment record, or screening page from household outcome and non-user evidence. `HC-12` asks whether a housing remedy can be followed through durable stability: payment posted to the right ledger, court posture changed, possession protected or safe relocation achieved, screening record corrected, application re-tried, shelter/re-housing tail tracked, and recurrence measured.

The minimum household receipt should include: household/unit identity; arrears and assistance state; court posture; representation at the event; payment posting; possession or lockout status; informal move-out; shelter or temporary placement; screening adverse action or correction; reapplication effect; durable housing at follow-up; and remaining debt or instability.

## Evidence-receipt spine

This revision adds `metadata/evidence_receipts.json` and generated `EVIDENCE_RECEIPTS.*`. The first rows are not an evidence archive. They are a map of claim-to-source posture and missing proof. Each row records the claim, case family, linked notes, source keys, locator, proof status, affected-person gap, minimum next receipts, and risk if the source is mistaken for outcome proof.

The first seven receipt rows cover public-benefit burden measurement, UI claim-status visibility, UI claimant-experience surveys and user testing, UI identity/overpayment/remedy safety, eviction filing limits, right-to-counsel implementation, and tenant-screening / rental-assistance tails. The repeated conclusion is intentional: official sources support tests and boundaries, not completed field validation.

## Audit/refactor

The cube had a small but real build-risk smell: `tools/build_all.py` owned a private ordered list of build scripts. This made the all-build order another registry that could drift from the Makefile, lint, and generated surfaces. Rev0786 moves that list into `tools/build_steps.py` and has `build_all.py` import it. The refactor is intentionally modest because the session priority is substantive proof, not build-system redesign.

The new receipt builder uses the same generated-output conventions as the test matrices: stable release timestamp, JSON and Markdown output, one source metadata file, and linted source-key/note references.

## What remains deliberately open

This pass does not validate real claimants or households. It does not collect interviews. It does not preserve private screenshots. It does not prove non-user rates. It does not retire a route. It does not solve licensing or archive stewardship. It does not supply a complete theory of power and distribution. It moves two critical gaps from undifferentiated open status to executable pilot status without calling them repaired.

## Failure modes

- **Survey substitution:** feedback mechanics are treated as proof that an eligible person received the benefit or remedy.
- **Claim-status substitution:** a clear status page hides unresolved staff action, employer delay, identity false positives, or payment-after-cure failure.
- **Docket substitution:** an eviction filing count becomes an eviction outcome despite missing possession, informal eviction, shelter, and re-housing evidence.
- **Counsel-statute substitution:** a right to counsel is treated as representation at the hearing despite provider-capacity failure.
- **Payment-award substitution:** a rental-assistance or UI payment record is treated as repair despite missing posting, retroactive eligibility, debt removal, or court effect.
- **Screening-correction substitution:** a corrected record is treated as housing access despite lost unit, repeated fees, adverse action, or no reapplication effect.
- **Receipt laundering:** the new evidence receipt row itself becomes a proof object rather than a statement of remaining proof need.

## Anti-theater tests

1. Pick a held UI claim. Can the packet show notice, burden, cure path, non-digital route, appeal or waiver, and payment-after-cure?
2. Pick a claimant survey or user-test result. Does the packet say who is outside the sample and what outcome the survey cannot prove?
3. Pick an overpayment or identity-theft remediation. Can the packet show debt classification, waiver/appeal state, recovery pause, correction, and money actually returned or protected?
4. Pick an eviction filing. Can the packet show whether the household stayed, moved informally, was locked out, entered shelter, or re-housed?
5. Pick a right-to-counsel jurisdiction. Can the packet show counsel at the operative event, not merely statutory eligibility?
6. Pick a tenant-screening correction. Can the packet show whether a subsequent housing application succeeded or whether the harm persisted?
7. Pick any generated receipt row. Does its proof status avoid claiming field validation?
8. Pick the build. Is the step order declared in one registry instead of being silently duplicated inside `build_all.py`?

## Source posture

Use OMB customer-experience and public-benefits burden guidance to justify feedback, burden, and beginning-to-end experience tests. Use DOL UI claims-status and modernization materials to justify issue visibility, actionable notices, assisted-digital support, survey, and user-testing pilots. Use GAO and Eviction Lab to bound what filing records can and cannot prove. Use NYC right-to-counsel reporting to distinguish representation law, representation rate, and stable-housing outcome. Use CFPB tenant-screening material to preserve screening-error tails. None of these sources closes the affected-person gap by itself.
