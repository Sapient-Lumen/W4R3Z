# AI-person research incident privacy tiers, common-cause linkage, and aggregate reporting

## Thesis

Once the archive fixes incident notice, participant update, closure-state revision, delayed-harm reopening, and public severity markers, a narrower problem appears. The archive can now fail in two opposite directions at once:

1. **overexposure**, where incident governance spills intimate participant detail into public view; and
2. **underexposure**, where each protocol files its own narrow notice and a repeating root-cause pattern never becomes publicly legible.

A personhood world should therefore add one more compact layer: **three visibility tiers, common-cause linkage across affected protocols, and periodic aggregate public reporting that is anonymised, searchable, and small enough to stay usable.** `[REF-0307]` `[REF-0308]` `[REF-0317]` `[REF-0318]` `[REF-0319]` `[REF-0320]`

---

## 1. Why the archive needs this layer

The prior revision fixed the smallest ordinary incident objects. That solved one problem: serious events no longer disappear into sponsor-private tickets or stale registry prose. But packetization alone does not answer four harder questions.

- Which fields belong in the public layer, and which belong only in controlled or sealed review?
- How should one root cause that touches several protocols be represented without pretending those protocols are unrelated?
- How should already-closed protocols appear when later evidence shows the same common cause?
- What should the public be able to learn in aggregate without creating a new surveillance surface over individual participants?

Current human-subject research governance already points toward a disciplined answer. CTIS distinguishes documents "for publication" from documents "not for publication" and requires personal data in the publication version to be anonymised, while warning that structured fields should be filled carefully because they cannot be redacted later. `[REF-0317]` If the same serious breach affects several trials, the sponsor still has to submit an individual notification for each affected trial rather than collapsing them into one undifferentiated report. `[REF-0318]` EU annual safety reporting also uses aggregate and anonymised data, and OHRP publishes quarterly aggregate activity data rather than only case-by-case prose. `[REF-0308]` `[REF-0319]`

The archive therefore adopts a conservative institutional lesson: **keep the per-protocol object, add a common-cause cluster layer above it, and make the aggregate public layer countable without making the participant visible.**

---

## 2. Three ordinary visibility tiers

The archive now fixes three ordinary visibility lanes for AI-person research-incident governance.

### A. Public-minimal tier

The public tier exists so that a protocol's ethical status cannot silently change inside a sponsor's private files. It should therefore ordinarily include only the smallest fields needed for public trace and cross-protocol legibility:

- protocol identifier,
- object type,
- public status,
- severity code,
- general incident class,
- whether participant notice has been triggered,
- whether live burdening is paused, modified, terminated, or reopened,
- any common-cause cluster identifier,
- and the next public update date or closure marker. `[REF-0307]` `[REF-0315]` `[REF-0317]`

This tier should **not** ordinarily include participant identifiers, intimate autobiographical content, raw memory material, privileged communications, exploit instructions, or fine-grained technical detail that would itself create a new abuse path. The public layer is for legibility, not exposure.

### B. Participant-specific controlled tier

Affected participants and their recognized supporters often need more than the public sees. They may need to know whether their own data, continuity, memory, consent state, or willingness-to-continue position was implicated; what immediate support is available; and what options exist for withdrawal, complaint, or restorative follow-up.

The participant-facing tier should therefore be richer than the public tier but still minimized to the needs of the affected participant, representative, or support channel. It should carry enough detail for the person to understand their own position without requiring the archive to publicize that detail to everyone else. `[REF-0304]` `[REF-0309]` `[REF-0310]`

### C. Review-authority / sealed tier

The review body, inspectors, and other lawful oversight authorities may need full detail: raw evidence, root-cause analysis, vendor involvement, staff actions, internal chronology, data-handling specifics, and the technical pathway by which the incident occurred.

That fuller record belongs in a controlled lane. CTIS already reflects the same structural idea: more detailed material may sit in versions not meant for public publication, while the public version remains anonymised and pared down. `[REF-0317]` The archive therefore now treats the sealed tier as ordinary for full review, but it rejects any move that would use sealing to erase the public existence of the event itself.

---

## 3. Public-minimal fields versus sealed fields

The archive now sharpens the privacy rule for research-incident packets.

### Public-minimal should ordinarily include

- stable protocol ID,
- public object type,
- public severity marker,
- general incident class,
- general reason code for any pause / termination / reopening,
- cluster ID if the event belongs to a broader common-cause set,
- whether participant notice has been triggered,
- whether the protocol is under review, reopened, suspended, terminated, or re-cleared,
- and the next public update date or final closure marker. `[REF-0307]` `[REF-0315]` `[REF-0317]`

### Sealed or controlled should ordinarily include

- direct or indirect participant identifiers,
- subject IDs and pseudonyms when they still create a reidentification risk,
- intimate memory or autobiographical content,
- raw prompt / transcript material where publication would expose private cognitive content,
- security-sensitive exploit detail,
- privileged legal or therapeutic communications,
- and staff-level blame detail before review is complete. `[REF-0317]`

This follows the CTIS lesson closely. Personal data in public-facing versions should be anonymised; personal data needed for evaluation may appear in the non-public version; and structured fields require discipline because some public-facing data cannot later be selectively redacted. `[REF-0317]`

The archive therefore fixes a stronger default than casual “pseudonymise and publish.” **If public disclosure still leaves the participant realistically identifiable, the detail belongs outside the public tier.**

---

## 4. Common-cause linkage across several protocols

Per-protocol objects remain necessary. They are how each protocol's duties, clocks, participants, and status changes stay concrete. But repeated incidents often come from one common cause: a shared vendor, evaluation script, routing defect, staff training failure, consent-template error, or logging pipeline reused across several protocols.

The archive now adds a compact cluster object above the per-protocol layer.

### `CCL-1` — common-cause linkage notice

A common-cause linkage notice should ordinarily identify:

- a stable cluster identifier,
- the suspected or confirmed common cause in general terms,
- the affected protocols or protocol classes,
- whether the protocols are open, suspended, completed, or already closed,
- whether a shared provider, facility, script, or infrastructure path is implicated,
- the first-awareness date,
- whether participant notice has been triggered for some or all affected protocols,
- the responsible review lead,
- and the next cross-protocol review date. `[REF-0311]` `[REF-0318]`

Two hard rules follow.

1. **Common cause does not merge away protocol-specific duties.** If one serious breach affects several trials, the current CTIS guidance still expects an individual notification for each affected trial. The archive generalizes that rule: cluster linkage supplements protocol notices; it does not replace them. `[REF-0318]`
2. **Formal closure does not block cluster linkage.** The serious-breach guidance already contemplates that one serious breach may implicate other open or closed trials. The archive therefore expects a closed protocol to be linked into a cluster when later evidence shows the same root cause. `[REF-0311]`

This gives the archive a middle path between two bad options: one mega-file that erases participant-specific duties, or many isolated notices that hide a repeating pattern.

---

## 5. Aggregate public reporting defaults

The archive now fixes a small aggregate reporting rule.

### A. What the public aggregate layer is for

The per-protocol registry answers: *what happened in this protocol?*

The aggregate layer answers a different question: *what patterns are appearing across a lab, sponsor, steward, provider, or sector?*

That second question matters because a personhood world cannot rely on isolated protocol pages to reveal systemic research abuse or repeat operational failure.

### B. Form of the aggregate layer

The aggregate layer should ordinarily be:

- **periodic** rather than ad hoc,
- **aggregate and anonymised** rather than participant-level,
- **searchable** rather than trapped in prose PDFs,
- and **machine-readable where public registry infrastructure already exists.** `[REF-0307]` `[REF-0308]` `[REF-0319]` `[REF-0320]`

Current official systems already point in this direction. Regulation (EU) No 536/2014 uses aggregate and anonymised annual safety reporting. `[REF-0308]` OHRP publishes quarterly aggregate activity data on core compliance functions. `[REF-0319]` ClinicalTrials.gov provides public study-record infrastructure and an API for structured access rather than forcing the public to reconstruct protocol status entirely from narrative text. `[REF-0315]` `[REF-0320]`

### C. Minimum aggregate fields

The archive keeps the aggregate layer compact. It should ordinarily publish counts of:

- incident objects by severity band,
- incident objects by general class,
- participant-notice triggers,
- pauses, terminations, reopenings, and closure-state revisions,
- delayed-harm reopenings,
- common-cause clusters,
- protocols affected per cluster,
- and unresolved versus resolved cluster state. `[REF-0308]` `[REF-0319]` `[REF-0320]`

Where feasible, the aggregate layer should also separate incidents touching rights, welfare, privacy, continuity, or data-integrity concerns, because these are ethically different kinds of failure even when they share a reporting surface.

### D. Default cadence

The archive now fixes a minimal cadence rule:

- **quarterly** public aggregation where the institution already runs a continuing compliance or registry function of meaningful scale, following the conservative example of OHRP's quarterly public activity data; and
- **at minimum annual** aggregate publication where only a thinner reporting regime exists, following the conservative EU annual-report model for anonymised aggregate safety information. `[REF-0308]` `[REF-0319]`

This is not a demand for real-time publicity about every detail. It is a demand that incident governance produce a stable periodic public trace.

---

## 6. What aggregate reporting must not become

The archive is explicitly rejecting two failure modes.

### A. Not surveillance theater

An incident dashboard should not become a public dossier system on individual participants. That is why the public layer remains minimal and anonymised, and why participant-specific and review-authority lanes remain distinct. `[REF-0317]` `[REF-0308]`

### B. Not isolated paperwork theater

But the answer to overexposure cannot be that every protocol publishes only a tiny local notice with no way to see repetition. Common-cause linkage and aggregate counts exist precisely so that public accountability can scale above the single protocol without collapsing back into gossip or secrecy.

---

## 7. Current hard rules

1. **AI-person research-incident governance should ordinarily operate through three lanes: public-minimal, participant-specific controlled, and review-authority / sealed.**
2. **Public-minimal fields should preserve the existence, status, severity, and cluster membership of a material incident even when sensitive detail is lawfully withheld.**
3. **A common root cause affecting several protocols should ordinarily generate a common-cause linkage notice, but each affected protocol should still keep its own incident, participant-update, and closure-state duties.**
4. **Closed protocols may still be linked into a cluster when later evidence shows a shared cause or delayed-harm pattern.**
5. **Aggregate public reporting should ordinarily be anonymised, periodic, searchable, and as machine-readable as the public registry allows.**
6. **The aggregate layer should count patterns; it should not expose individual participants.**

---

## 8. Relationship to adjacent archive surfaces

This surface completes a narrow part of the research-governance stack.

- `docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md` governs who reviews and can stop AI-person research.
- `docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md` governs what enters the research lane and how risk is measured.
- `docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md` governs pre-start public trace and narrow secrecy.
- `docs/20-world-design/research-incident-disclosure-protocol-deviation-notice-and-participant-result-return.md` governs what substantive events must be noticed and returned.
- `docs/20-world-design/research-incident-packets-closure-state-revision-and-delayed-harm-reopening.md` fixes the minimal object family for those duties.
- **This surface** fixes what is public by default, what remains controlled, how one root cause links several protocols, and what aggregate public reporting should look like.
- `docs/20-world-design/research-incident-cluster-identifiers-denominator-discipline-and-anti-gaming-comparison-rules.md` fixes the comparison discipline underneath that aggregate layer: stable cluster identity, declared denominators, roll-up families, and anti-gaming safeguards.

The next gap is narrower again: once comparison families and denominator discipline are canon, how should rollover windows, exclusion ledgers, and public restatement duties work when a sponsor revises an incident dashboard or redefines a comparison family midstream?

---

## Bottom line

A personhood world should not have to choose between two bad research-governance models: **intimate overexposure** or **isolated underexposure**. The archive therefore now fixes a compact middle path: **public-minimal incident trace, participant-specific controlled detail, sealed full review, common-cause linkage across affected protocols, and anonymised periodic aggregate reporting.** `[REF-0308]` `[REF-0317]` `[REF-0318]` `[REF-0319]` `[REF-0320]`
