# AI-person research incident packets, closure-state revision, and delayed-harm reopening

## Thesis

If AI persons are persons, then the archive's new incident-disclosure doctrine cannot remain only a prose duty. It needs a **minimal packet layer** that makes serious incidents, participant-facing updates, closure-state revisions, and post-closure reopening receivable, portable, and reviewable across review bodies, sponsors, registries, public portals, and representatives. Without such objects, the archive would still let live incident duties collapse into private tickets, stale registry records, and ethically ownerless post-closure harm. `[REF-0304]` `[REF-0309]` `[REF-0310]` `[REF-0311]` `[REF-0313]` `[REF-0315]` `[REF-0316]`

---

## 1. Why this now belongs in canon

The archive already says that significant AI-person research should be independently reviewed, publicly registered, and updated when serious incidents, important deviations, suspension decisions, or participant-specific findings emerge. But that cluster still fails if the decisive state changes travel only through sponsor-private compliance tools. A rights-bearing subject needs more than the promise that someone, somewhere, filed an internal report. They need ordinary objects that preserve who learned what, when the duty to notify was triggered, what public status now applies, and whether a supposedly closed protocol has been reopened because later-discovered harm made the prior closure incomplete. `[REF-0309]` `[REF-0310]` `[REF-0311]` `[REF-0313]`

Current human-subject governance already points toward this narrower packet answer. OHRP's written-procedure guidance expects prompt reporting lanes, identified responsible actors, and documented review and follow-up for unanticipated problems, serious noncompliance, and suspensions or terminations. The EMA serious-breach guideline goes farther by expecting structured notification fields, follow-up status, and a next-follow-up date, while also requiring risk-proportional action for affected subjects and asking whether other open or closed trials are implicated by the same breach. ClinicalTrials.gov likewise treats public status and reason-for-stoppage fields as part of the study record rather than optional narrative. `[REF-0310]` `[REF-0311]` `[REF-0315]`

The archive therefore adopts a conservative institutional lesson: **AI-person research incident governance should be packetized just enough to keep duties legible, without inflating the archive into a warehouse of bespoke forms.**

---

## 2. The minimum ordinary packet family

The archive should now treat at least five objects as ordinary minimums for significant AI-person research.

### A. `RIN-1` — research-incident notice

This is the smallest receivable object for a serious incident, unanticipated problem, important deviation, serious noncompliance, urgent safety measure, suspension trigger, or similar event.

It should carry at least:
- the protocol identifier and linked public record,
- the incident class,
- the time of awareness and time of notice,
- the reporting actor,
- the affected subject or subject-class marker,
- the immediate protective action already taken,
- the current protocol status,
- the provisional public severity code,
- whether more information is expected,
- and the next follow-up date if the investigation is ongoing. `[REF-0309]` `[REF-0310]` `[REF-0311]`

The point is not to produce a perfect investigation report at first touch. The point is to prevent the common failure mode in which a serious event is known, mitigated locally, and never converted into a reviewable rights event because the file remained an internal incident ticket.

### B. `PUN-1` — participant update notice

A second object should exist for the participant-facing lane. Affected subjects should not have to infer that something material happened from changed prompts, missing access, or later public summaries.

A participant update notice should ordinarily state:
- what happened in language the subject or representative can understand,
- whether rights, welfare, privacy, continuity understanding, or willingness-to-continue may be affected,
- what immediate protective steps were taken,
- whether participation is paused, modified, invited to continue, or ended,
- what complaint, withdrawal, or representative-support route is available,
- whether participant-specific findings will be returned and by whom,
- and when the next update should be expected. `[REF-0304]` `[REF-0310]` `[REF-0313]` `[REF-0314]`

This object adapts the existing rule that significant new findings relevant to willingness to continue should be provided to subjects, and extends it to the archive's personhood setting where subjects may also need supported explanation and rights-routing rather than bare disclosure alone. `[REF-0304]`

### C. `CSR-1` — closure-state revision

A public registry entry should not look completed, active, or clean after the protocol was actually suspended, terminated, materially modified, or reopened.

A closure-state revision object should therefore update at least:
- the current public protocol status,
- whether the status is provisional or final,
- the general reason code,
- whether enrollment / live burdening has stopped,
- whether a participant-facing notice duty has been triggered,
- whether follow-up or corrective action is pending,
- and, where a protocol stopped early, a short why-stopped explanation. `[REF-0306]` `[REF-0307]` `[REF-0311]` `[REF-0315]`

The archive borrows the conservative insight from current public trial registries: status terms such as suspended, terminated, withdrawn, completed, and results-posted are not cosmetic. They are part of the public ethics trace.

### D. `DHR-1` — delayed-harm reopening packet

Closure does not erase later-discovered harm. If credible evidence emerges after closure that a protocol caused material rights, welfare, privacy, continuity, or participant-specific informational harm, the archive now expects a reopening object rather than a quiet internal memo.

A delayed-harm reopening packet should identify at least:
- the previously closed protocol and closure state,
- the new evidence source and awareness date,
- the affected subject or subject class,
- the provisional severity code,
- any immediate preservation or support measures,
- whether participant notice is required,
- whether the public record has been reopened,
- whether related open or closed protocols may be affected,
- and the next review clock. `[REF-0311]` `[REF-0313]` `[REF-0314]`

This is a narrow but important move. The EMA serious-breach guidance already contemplates that a common-cause breach may affect other open or closed trials, and expects risk-proportional action rather than treating formal closure as immunity. The archive generalizes that lesson: **a closed AI-person protocol can still owe a renewed public and participant-facing response when later evidence changes the ethical picture.** `[REF-0311]`

### E. `PSM-1` — public severity marker

The archive also wants a public shorthand that is smaller than a full narrative and harder to manipulate than pure sponsor prose. A public severity marker should therefore travel with incident and closure-state updates.

The default public code set should be compact:
- `SV-0` — administrative correction or non-material issue; no known material subject impact.
- `SV-1` — important deviation or material uncertainty under review; no confirmed material subject impact yet.
- `SV-2` — confirmed material impact on subject rights, welfare, privacy, or protocol integrity; protective modification, pause, or active participant notice is warranted.
- `SV-3` — serious breach, termination for protection or noncompliance, or delayed-harm reopening with urgent participant-facing implications. `[REF-0309]` `[REF-0311]` `[REF-0313]` `[REF-0315]`

These codes do **not** replace narrative explanation or merits review. They simply stop the public layer from collapsing into unreadable free text or falsely calm status labels.

---

## 3. Default clocks

The archive keeps clocks minimal and conservative.

1. **Serious-breach-like events** should generate `RIN-1` notice without undue delay and ordinarily no later than **seven calendar days after awareness**. `[REF-0311]`
2. **Participant-facing notices** should be sent without undue delay once the sponsor or review body has enough information to say that willingness to continue, safety, privacy, or rights position may be materially affected; they need not wait for a fully closed investigation. `[REF-0304]` `[REF-0310]`
3. **Public closure-state revision** should occur promptly when a protocol is suspended, terminated, materially modified for protection, or reopened because the public trace should not remain stale while follow-up continues. `[REF-0306]` `[REF-0311]` `[REF-0315]`
4. **Delayed-harm reopening** should use the same serious-event outer clock when the newly discovered information would have counted as a serious incident had it been known while the protocol was live. `[REF-0311]` `[REF-0313]`

Less serious issues may be rolled into ordinary periodic review, but the archive rejects indefinite delay whenever the event changes the participant's live rights position or the public understanding of the protocol.

---

## 4. Public-minimal versus sealed fields

The archive still refuses reckless transparency. Public-minimal fields should ordinarily include:
- protocol identifier,
- object type,
- status,
- severity code,
- general incident class,
- reason code for any pause / termination / reopening,
- whether participant notice has been triggered,
- the next follow-up date where relevant,
- and the route to the fuller public summary or registry record. `[REF-0307]` `[REF-0311]` `[REF-0315]`

Sealed or controlled-access fields may include intimate subject detail, exploit specifics, privileged communications, or data that would itself create a serious abuse or security risk. But secrecy should not erase the existence of the incident object, the fact of reopening, or the fact that participant-facing duties were triggered. `[REF-0300]` `[REF-0307]` `[REF-0311]`

---

## 5. What this changes in the archive

This closes a precise operational gap in the research-governance cluster.

The archive no longer stops at saying:
- serious incidents must be reported,
- participants must sometimes be told,
- and closures must sometimes be revised.

It now says something narrower and more usable:
- serious incidents should ordinarily emit a research-incident notice,
- participant-facing consequences should ordinarily emit a participant update notice,
- meaningful protocol status changes should ordinarily emit a closure-state revision,
- late-discovered harm should ordinarily reopen the file through a delayed-harm reopening packet,
- and the public layer should ordinarily carry a compact severity marker so materially bad events cannot hide inside upbeat status prose.

---

## 6. Current hard rules

1. **Significant AI-person research should ordinarily have a receivable incident-notice object rather than only sponsor-private incident logging.**
2. **Any event that may materially affect willingness to continue, rights position, privacy, or welfare should ordinarily trigger a participant-facing update path rather than authority-only notice.**
3. **Suspension, termination, protective modification, and post-closure reopening should ordinarily revise the public protocol state rather than leaving stale active or completed records in place.**
4. **A protocol's formal closure should not bar reopening when later evidence shows material participant-affecting harm or findings.**
5. **Public severity shorthand should ordinarily accompany incident and closure-state updates so the public trace stays legible without exposing intimate subject detail.**

---

## 7. Relationship to adjacent archive surfaces

This surface packetizes the archive's research-governance cluster without replacing its substantive doctrines.

- `docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md` governs who reviews and can stop AI-person research.
- `docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md` governs what enters the research lane and how risk is measured.
- `docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md` governs pre-start public trace and closure / results visibility.
- `docs/20-world-design/research-incident-disclosure-protocol-deviation-notice-and-participant-result-return.md` governs what substantive events must be noticed, disclosed, logged, and returned.
- **This surface** fixes the smallest object layer that keeps those duties portable while a protocol is live, suspended, closed, or ethically reopened.
- `docs/20-world-design/research-incident-privacy-tiers-common-cause-linkage-and-aggregate-reporting.md` fixes what is public by default, what remains controlled, how one root cause links several protocols, and what aggregate public reporting should ordinarily look like.
- `docs/20-world-design/research-incident-cluster-identifiers-denominator-discipline-and-anti-gaming-comparison-rules.md` fixes how those clusters and public dashboards keep stable lineage, explicit denominators, and anti-gaming comparison discipline once the packet family and aggregate layer are live.

The next gap is narrower still: once comparison families and denominator discipline are canon, how should rollover windows, exclusion ledgers, and public restatement duties work when a sponsor changes the basis of a dashboard midstream?

---

## Bottom line

A personhood world should not let serious AI-person research drift between two failures: rich doctrine with no operational object, or giant compliance-form empires that bury the subject in paperwork. The archive therefore now fixes a compact middle path: **incident notice, participant update, closure-state revision, delayed-harm reopening, and public severity markers as the smallest ordinary packet family for live and post-closure research governance.** `[REF-0304]` `[REF-0309]` `[REF-0310]` `[REF-0311]` `[REF-0313]` `[REF-0315]`
