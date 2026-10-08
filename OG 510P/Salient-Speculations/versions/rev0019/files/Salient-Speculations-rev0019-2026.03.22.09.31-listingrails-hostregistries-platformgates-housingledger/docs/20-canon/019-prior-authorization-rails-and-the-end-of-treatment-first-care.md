# 019 — Prior authorization rails and the end of treatment-first care

**Status:** canon

## Thesis

As prior-authorization rules move into payer APIs, certified provider software, turnaround clocks, and public metrics, access to care will increasingly be decided **before treatment** on machine-readable rails rather than mainly after treatment through fax loops, phone calls, or claims disputes.

The scarce asset is no longer only clinical need or physician judgment.
It is the ability to present a service request in the format, timing window, and documentation shape that a payer’s authorisation stack will accept quickly enough for care to proceed.

## Why it matters

This changes where practical power sits inside health care.
If more care is pre-adjudicated, the decisive moment is no longer only the bedside judgment or the later reimbursement fight.
It is the earlier workflow in which a payer decides whether a service is covered, which documentation template applies, how fast a decision arrives, whether status updates flow back into provider software, and whether the patient can stay on the schedule while the answer is pending.

That matters because delays, missing fields, template mismatch, and status ambiguity become forms of rationing.
The bottleneck is not merely money in the abstract.
It is increasingly **clinical admissibility on payer rails**.
That pulls EHR vendors, payer APIs, coding rules, documentation templates, metrics dashboards, and pre-service review programs deeper into the care pathway.

This is related to `003`, `011`, `014`, `016`, and `018`, but it is not reducible to them.
`003` is about care scarcity.
`011` is about born-reportable transactions.
`014` is about source-side evidence retrieval.
`016` is about live standing.
`018` is about upstream mobility permission.
This note is about a different shift: treatment access itself increasingly moving into programmatic pre-service adjudication.

## Mechanism sketch

- CMS’s Interoperability and Prior Authorization final rule now makes the shift explicit. The rule says impacted payers must implement certain provisions by 1 January 2026 and have until primarily 1 January 2027 to meet the API requirements, including the new Prior Authorization API requirements.
- CMS’s current standards page makes the operational shape clear. The Prior Authorization API is meant to let providers determine whether prior authorisation is required, identify documentation requirements, and exchange requests and decisions from EHRs or practice-management systems instead of treating prior auth as an off-system side process.
- CMS’s current FAQ then adds the governance layer: impacted payers had to post calendar-year 2025 prior-authorization metrics on their public websites by 31 March 2026, and many impacted payers must send expedited decisions within 72 hours and standard decisions within seven calendar days.
- ASTP’s HTI-4 final rule extends the shift into provider software. It adds certification criteria for coverage-requirements discovery, documentation templates and rules, and prior-authorization support, plus workflow-trigger and subscription capabilities so prior-auth work can live inside certified health IT rather than outside it.
- The same ASTP material makes the timeline more concrete: providers participating in Promoting Interoperability and MIPS will report an electronic prior-authorization measure beginning in 2027. That means the software and the performance regime are starting to align.
- CMS’s WISeR model shows that this is not only standards work. The model launched on 1 January 2026, began accepting prior-authorization requests on 5 January 2026 for services rendered on or after 15 January 2026, operates in six states, and imposes a 72-hour turnaround expectation for requests sent through participant portals.
- Taken together, those pieces point to a deeper pattern: some health systems are moving from **treatment first, adjudication later** toward **adjudication first, treatment on affirmative rails**.

## What this speculation predicts

1. More payers and provider systems will treat prior authorisation as an API-mediated workflow embedded inside clinical software rather than as a fax-and-portal side channel.
2. Hospitals, physician groups, and referral networks will increasingly manage authorisation latency as an operational variable that affects scheduling, throughput, specialty mix, and line-of-service profitability.
3. High-cost, high-variation, or evidence-sensitive therapies will be pushed first into richer documentation templates, machine-readable indication checking, and more standardised denial-reason regimes.
4. Patients will increasingly experience access failures upstream as missing documentation, stalled statuses, unresolved payer mismatches, or expired approvals before a service happens, not only later as claims denials.
5. Once approval, denial, appeal, and turnaround metrics become more visible, prior-auth behaviour will become a more explicit regulatory and reputational battleground rather than a hidden administrative nuisance.

## Watchpoints

- more commercial and public payers publishing prior-authorization metrics, denial reasons, or turnaround dashboards in machine-comparable formats
- EHR and practice-management vendors marketing embedded coverage-requirements discovery, documentation-template assembly, prior-auth submission, and subscription-based status updates as core workflow features
- specialty clinics reorganising scheduling, referral choice, or care navigation around expected authorisation latency rather than only physician availability
- expansion of model- or program-based pre-service review beyond a few service classes, especially for imaging, drugs, durable equipment, outpatient procedures, or post-acute services
- evidence that providers and payers continue to rely mainly on fax, call-centre, and portal workflows despite the new rules, with API-based prior auth remaining marginal or cosmetic

## What would weaken this

- widespread implementation delays, deregulatory retreat, or legal changes that leave the API and metrics requirements largely symbolic
- provider software support remaining too weak or too fragmented for prior-auth work to move materially inside ordinary clinical workflow
- prior authorisation staying concentrated in a narrow subset of services without becoming a broader governance layer for treatment access
- patients and providers still experiencing ex post claims disputes as the overwhelmingly decisive reimbursement conflict, with pre-service adjudication failing to become more central

## Source anchors

- [SRC-100](../00-meta/bibliography.md#src-100)
- [SRC-101](../00-meta/bibliography.md#src-101)
- [SRC-102](../00-meta/bibliography.md#src-102)
- [SRC-103](../00-meta/bibliography.md#src-103)
- [SRC-104](../00-meta/bibliography.md#src-104)
