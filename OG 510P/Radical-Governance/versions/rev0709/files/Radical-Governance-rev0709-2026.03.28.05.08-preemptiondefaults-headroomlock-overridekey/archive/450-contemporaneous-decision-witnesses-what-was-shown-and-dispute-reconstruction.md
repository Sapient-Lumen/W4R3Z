# 450 — Contemporaneous decision witnesses, what-was-shown records, and dispute reconstruction

## One-line thesis

Consequential public AI should preserve a compact contemporaneous witness of what the system showed, decided, and relied on at the moment of action so later appeals, incidents, and audits do not have to reconstruct governing state from overwritten traces and memory.

## Why this matters

Many public-AI failures become hardest to govern only after something goes wrong. By then the live interface has changed, thresholds have moved, the system card was refreshed, the output was recomputed, and the surviving logs answer only technical questions. The institution can often prove that *a* system existed, but not exactly what this person saw, what basis was active, what route the case took, or what explanation, score band, warning, source set, and override posture were actually in force when the consequential step happened.

That gap weakens appeals, incident review, external oversight, and institutional self-knowledge. The archive should therefore require a compact witness at consequential moments: not every keystroke, but enough frozen state to answer the later accountability question without imaginative reconstruction.

## Pattern pack

### 1. Create a compact witness at consequential state changes

A witness should be created whenever the system:

- makes or materially informs a consequential decision,
- changes a person's case state,
- triggers a warning or adverse route,
- enters or exits human review,
- uses an override, hold, or rollback path,
- or generates a decision-ready explanation or appeal packet.

The witness is not a full replay movie. It is a minimal, reviewable state capture.

### 2. Preserve the exact governing basis in force at that moment

A contemporaneous witness should point to the active basis, such as:

- model or rule version,
- threshold or score band,
- source set or retrieval context where relevant,
- notice/explanation text version,
- human-review posture,
- operator mode,
- and release or approval state.

This prevents later systems from backfilling a cleaner story onto an older event.

### 3. Preserve what was shown or communicated

Where relevant, the witness should capture the exact outward-facing state, such as:

- decision or recommendation text,
- reason codes or explanation snippet,
- warning or caution label,
- confidence band or threshold category if used,
- next-step or remedy route offered,
- and the visible case-state label shown to the user or operator.

The point is to preserve the governing communication surface, not only the hidden computation.

### 4. Keep the witness compact but portable

A useful witness is small enough to retain and export. It can often be a structured packet naming:

- event identifier,
- actor and channel,
- timestamps,
- case or transaction reference,
- basis identifiers,
- visible outputs,
- key inputs or source references,
- and whether a human accepted, overrode, or deferred the system state.

A witness that is too heavy to preserve will usually not survive the moment it is most needed.

### 5. Record unresolved or ambiguous states honestly

If the system abstained, routed to fallback, flagged uncertainty, awaited human confirmation, or displayed a provisional outcome, the witness should say so. It should not later narrate a clean decision that had not yet been made. Appropriate fields include:

- provisional / final,
- abstained,
- override requested,
- human confirmation pending,
- fallback route used,
- evidence incomplete.

### 6. Bind witnesses to appeal, incident, and review packets

A witness should be easy to pull into:

- appeal packets,
- incident files,
- second-look review samples,
- public-case logs where appropriate,
- and internal after-action analysis.

This keeps downstream review grounded in frozen contemporaneous state rather than summaries written long after the event.

### 7. Preserve enough context to challenge the system fairly

A witness should help an affected person or reviewer ask meaningful questions such as:

- what version was active,
- what notice or explanation was shown,
- what evidence or source family was relied on,
- whether a human reviewed or merely received the output,
- whether a safeguard or threshold actually fired,
- and what recourse route was offered at the time.

The archive should prefer challenge-ready witnesses over technically rich but procedurally useless log fragments.

## Guardrails

- Do not rely on overwritten live systems to explain past consequential events.
- Do not preserve only hidden computation while losing the outward-facing message.
- Do not replace contemporaneous witnesses with later narrative summaries.
- Do not pretend provisional or fallback states were final decisions.
- Do not make witnesses so heavy that they become impractical to retain or export.

## Failure modes

- **after-the-fact reconstruction theater**: reviewers rebuild the event from memory and scattered logs.
- **output amnesia**: the institution saved telemetry but not what the person or operator actually saw.
- **basis drift overwrite**: later versions silently replace the basis active at event time.
- **false finality**: provisional, abstained, or fallback states are retold as settled outcomes.
- **non-portable evidence**: the record exists only in dashboards or brittle internal traces.

## Practical tests

A contemporaneous-witness discipline passes when it can answer yes to all of the following:

1. Are consequential moments defined so the system knows when to create a witness?
2. Does each witness point to the exact governing basis active at that moment?
3. Does it preserve what was shown, said, or routed outward, not only internal telemetry?
4. Can the witness be exported into appeals, incidents, and review packets without heroic reconstruction?
5. Does it preserve uncertainty, fallback, and provisional status honestly where they existed?

## Compression rule for the archive

If a later reviewer cannot tell **what this system showed, relied on, and decided at the moment it mattered**, then the archive is still missing a **contemporaneous witness**.
