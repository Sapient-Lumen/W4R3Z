# 441 — Record schedules, hold-safe deletion, and discovery-ready AI logs

## One-line thesis

Prompts, retrieved sources, outputs, feedback, and operational logs from public AI should be treated as **scheduled records with clear deletion rules, hold behavior, access controls, and export paths**, not as disposable exhaust.

## Why this matters

A public AI system can look well governed right up until someone asks for the evidence. Then the team discovers that prompts were never classified, retrieval traces were kept arbitrarily, deletion jobs ran during an investigation, or audit logs exist but cannot be exported in a way that supports oversight, appeal, litigation, or public-record obligations. In practice, many public systems still treat interaction data as mere telemetry even when it documents consequential service activity.

Current official materials support a tighter model. Canada’s 2026 privacy and security guidance for AI help applications says teams should establish default retention periods for all collected data, delete data when the period ends, and work with information-management branches on retention and disposition schedules. The same guidance says audit logs should maintain detailed records of all access and activity and should use role-based access controls. NARA’s federal records guidance says records schedules are approved by NARA and are mandatory, and that staff must follow disposition instructions. NARA’s freeze guidance says that when a litigation hold is issued, the records officer suspends the normal disposition cycle of the records in scope to prevent premature disposal. The UK ATRS guidance now explicitly treats real-world operational data as including user inputs, retrieved documents, system-generated logs, and other data generated during use.

The archive should therefore make a sharper move: **before launch, decide what the system creates, how long each class is kept, when deletion pauses, who can see it, and how it can be exported for review**.

## Pattern pack

### 1. Classify AI-generated and AI-mediated records before launch

Create a records matrix covering at least:

- user inputs,
- retrieved source lists,
- model outputs,
- moderation or redaction events,
- operator overrides,
- appeal packets and complaint references,
- system-generated logs,
- evaluation samples,
- and incident-response artifacts.

Each class should have an owner and a retention rule.

### 2. Separate retention classes instead of keeping or deleting everything together

Different artifacts often justify different schedules. For example:

- raw conversation text may need shorter retention,
- decision-support packets may need longer retention,
- incident and override logs may need to persist through investigation windows,
- and anonymised evaluation sets may have separate retention and access rules.

A single blanket retention window usually hides risk rather than reducing it.

### 3. Build hold-safe deletion into the system

Deletion should be pausable when:

- litigation holds apply,
- appeals or complaints remain open,
- a serious incident investigation is underway,
- a public-record or audit request is active,
- or an internal review has frozen the relevant corpus.

The system should be able to stop normal disposition for the affected record classes without freezing everything else unnecessarily.

### 4. Keep audit logs reviewable, not only immutable

Audit logs should capture enough detail to reconstruct:

- who accessed or changed data,
- what prompt or retrieval event occurred,
- what source set was used,
- whether moderation or redaction fired,
- and whether a human overrode or affirmed the output.

But they should also be exportable into review packets rather than remaining trapped in vendor dashboards.

### 5. Use role-based access controls for sensitive log data

Prompt and log access should be granted by role and review purpose. Not every engineer, vendor, or product manager should be able to inspect live public interactions just because the data is technically available.

### 6. Align deletion, minimisation, and public-accountability needs

The answer to overcollection is not permanent storage, but neither is it unreviewable deletion. Teams should minimize what is collected while still preserving the classes of evidence needed for complaints, incident analysis, legal compliance, and oversight.

### 7. Test export and hold procedures like operational drills

Before launch, run a drill that asks:

- can we place a hold on a subset of records,
- can we export the relevant logs and interaction history,
- can we prove the applicable retention schedule,
- and can we show what was deleted, what was preserved, and why?

A records schedule that has never been exercised is still partly theoretical.

## Guardrails

- No launch without a record-class matrix and retention schedule.
- Deletion should be scheduled, not ad hoc.
- Hold events should suspend normal disposition for affected records.
- Audit logs should be role-restricted and exportable.
- Evidence needed for appeal, incident review, or public accountability should not depend on vendor goodwill.

## Failure modes

- **telemetry amnesia**: consequential interaction data is treated as throwaway analytics.
- **blanket retention**: everything is kept indefinitely because no record classes were defined.
- **premature deletion**: data is destroyed while an appeal, investigation, or hold should have preserved it.
- **dashboard captivity**: logs exist but cannot be exported into a durable review packet.
- **overbroad access**: sensitive prompt and interaction data becomes casually visible to staff or suppliers who do not need it.

## Practical tests

A records-ready AI service passes when it can answer yes to all of the following:

1. Are prompts, outputs, retrieval traces, logs, and review artifacts assigned explicit record classes?
2. Does each class have a documented retention and deletion rule?
3. Can the service pause normal deletion for records under hold, appeal, or investigation?
4. Are audit logs detailed enough and exportable enough to support oversight and discovery?
5. Are access rights to logs and interaction data constrained by role and review purpose?

## Compression rule for the archive

If a public AI system cannot say **what evidence it keeps, when it deletes it, and how deletion stops under hold**, it is not yet ready for real public accountability.
