# 461 — Repair ladders, restored-record uncertainty, and recovery-proof boundaries

## One-line thesis

When consequential public-AI records, logs, indexes, or service state are damaged, institutions should publish a least-destructive repair ladder and label restored artifacts with continuity and uncertainty classes instead of letting recovery masquerade as untouched truth.

## Why this matters

Consequential public-AI systems depend on more than model outputs. They depend on dossiers, logs, indexes, retrieval corpora, case packets, published disclosures, access records, routing state, and other artifacts that preserve what happened and what can still be reviewed. Those supporting surfaces fail in practice.

A log store can lose a shard. A public card can be regenerated from partial source. A case packet can be rebuilt from surviving traces. A damaged index can be recreated while preserving some bytes but not the original ordering or timestamps. A disclosure page can be restored from backup while its surrounding metadata lags behind. Recovery is necessary. Recovery also creates a temptation to overclaim.

The archive already governs records retention, contemporaneous witnesses, canonical public heads, and external-evidence integrity. What it still lacked was one direct rule for the repair moment itself: classify what broke, show the safest repair ladder, preserve blast-radius honesty, and keep restored artifacts visibly distinct from untouched originals when that distinction matters.

## Pattern pack

### 1. Classify the damaged layer before proposing repair

Repair should start by naming what appears damaged, such as:

- local index or search structure,
- log segment or audit trail,
- public disclosure surface,
- source-native governing record,
- case packet or derivative summary,
- identity or routing state,
- or underlying bytes themselves.

Different layers justify different repairs. A generic “rebuild” button is too blunt for consequential governance artifacts.

### 2. Publish a least-destructive repair ladder

The archive should prefer an ordered ladder such as:

- verify and remount,
- rescan or reindex,
- restore from preserved source,
- reconstruct from logs or witnesses,
- regenerate derivative surfaces,
- or retire the damaged artifact and issue a replacement record.

Each stronger step should say why the weaker step is insufficient.

### 3. Declare blast radius, evidence loss, and continuity effect before repair

Before a repair is applied, reviewers should be able to see:

- what scope is in blast radius,
- what evidence may be lost or degraded,
- what continuity is preserved,
- whether identifiers, timestamps, ordering, or signatures change,
- and whether the repair creates a new record instance rather than restoring the old one.

A repair that silently changes the review object is a governance event, not mere maintenance.

### 4. Distinguish restore for inspection from live reintroduction

A recovered artifact may be used in at least three different ways:

- inspection-only recovery,
- authoritative replacement of a damaged live artifact,
- or side-by-side fork for comparison and dispute review.

Those paths should not be collapsed. Inspecting an old packet is not the same as restoring it to current authority.

### 5. Label restored artifacts with continuity and uncertainty classes

Where a record or derivative surface is repaired, the archive should mark whether it is:

- original and unmodified,
- restored from preserved source,
- reconstructed from logs or witnesses,
- regenerated from derivative inputs,
- partially recovered,
- or completeness-unknown.

The point is not to scare people away from using restored records. It is to preserve the review truth about what kind of artifact now exists.

### 6. Preserve a recovery ledger

The archive should keep a durable ledger for consequential repair actions showing:

- who initiated the repair,
- what diagnosis justified it,
- what ladder step was chosen,
- what evidence sources were used,
- what uncertainty remains,
- and what later validation was performed.

That ledger helps later reviewers understand whether the repaired artifact can support operational use, public disclosure, appeals, or only limited internal study.

### 7. Keep replay and recovery proof within their boundary

A successful replay or restoration can prove that recovery steps worked as intended. It does not automatically prove that the live public service, live routing state, or full historical record is now complete. The archive should keep recovery proof and live-operational proof separate.

## Guardrails

- Do not let “restored” silently imply “identical in all material respects.”
- Do not escalate immediately to destructive repair when a narrower step may preserve more evidence.
- Do not overwrite the damaged artifact without preserving what can still be studied safely.
- Do not present reconstructed summaries or recompiled packets as original governing records.
- Do not hide remaining uncertainty once a service looks operational again.

## Failure modes

- **repair laundering**: recovery is reported as if nothing materially changed.
- **destructive impatience**: teams jump to wide rebuilds that needlessly erase evidence.
- **replacement without notice**: a new artifact quietly inherits the authority of the damaged one.
- **uncertainty erasure**: restored completeness limits disappear from the record.
- **recovery/live collapse**: repair validation is mistaken for full operational proof.

## Practical tests

A repair-honest archive passes when it can answer yes to all of the following:

1. Is the damaged layer classified before repair begins?
2. Is there an ordered least-destructive repair ladder rather than one blunt rebuild action?
3. Can reviewers see blast radius, evidence loss, and continuity effect before a stronger repair step is taken?
4. Are restored or reconstructed artifacts labeled with continuity and uncertainty classes?
5. Does the archive preserve a durable ledger of consequential repair actions and later validation?

## Compression rule for the archive

If a recovered governance artifact cannot say **what was repaired, what continuity was preserved, and what uncertainty remains**, then the archive is still letting **recovery impersonate originality**.
