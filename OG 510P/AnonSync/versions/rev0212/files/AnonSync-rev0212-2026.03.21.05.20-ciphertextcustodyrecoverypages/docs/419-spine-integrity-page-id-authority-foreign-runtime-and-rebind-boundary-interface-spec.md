# Spine integrity page — ID authority, foreign runtime, and rebind boundary interface spec

## Purpose

The archive already had repair ladders, seat-lineage work, and service-material integrity language.
What it still lacked was one ordinary page for the narrower question:

> is the continuity-bearing hidden spine for this subject actually healthy, or am I looking at missing identity, duplicate runtime ownership, foreign-managed state, or a repair that recreates a new epoch?

Current official Resilio docs make this seam concrete.
They still say deleting or corrupting `.sync` / the ID file suspends synchronization, that two Sync instances touching the same folder can corrupt internal state, that one repair path is remove/re-add after checking Archive and deleting `.sync`, and that cloning a Sync instance by raw copy is unsupported.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Spine integrity** page for every degraded or repair-reviewed subject.

The page exists to answer five things in one place:

1. whether continuity-bearing hidden state is healthy, damaged, foreign, duplicated, or recreated
2. which component currently acts as the authoritative spine witness
3. whether the likely cause is loss, corruption, duplicate runtime, foreign ownership, or unsupported copy
4. which repair paths preserve the current epoch and which create a successor epoch
5. what evidence or history must be exported before any destructive repair

## Fixed page order

1. **Integrity verdict**
2. **Authoritative spine witnesses**
3. **Likely damage or conflict origin**
4. **Preserve vs recreate repair ladder**
5. **Evidence and receipts**

### 1) Integrity verdict

Show:

- `spine_integrity_page_id`
- subject scope
- current `integrity_verdict` (`healthy`, `missing-id`, `corrupted-spine`, `duplicate-runtime`, `foreign-owned`, `recreated`, `unknown`)
- strongest honest summary
- last materially integrity-shaping event time

The operator must be able to answer:

> does this subject still have the same continuity spine or not?

### 2) Authoritative spine witnesses

Show rows for components such as:

- subject identity witness
- preserved history witness
- current runtime owner witness
- imported or recreated spine witness

Each row must show:

- witness strength
- whether it proves preserved continuity or only recreated capability
- whether another seat corroborates it
- whether the witness is stale, conflicting, or absent

### 3) Likely damage or conflict origin

Show candidate causes such as:

- accidental deletion or movement of continuity spine
- duplicate runtimes touching one subject
- external-drive reuse across runtimes
- unsupported disk or machine clone
- abrupt interruption / corruption
- operator-accepted clean rebind

Each row shows confidence, evidence used, and whether it threatens payload bytes, continuity, or both.

### 4) Preserve vs recreate repair ladder

Actions may include:

- `Reattach preserved spine`
- `Quarantine foreign runtime ownership`
- `Export history before rebind`
- `Create reviewed successor epoch`
- `Force clean rebind`
- `Abort destructive repair`

Each action must preview continuity result, archive/history risk, and reversibility.

### 5) Evidence and receipts

Show:

- recent integrity receipts
- exported history / archive witnesses
- repair drafts awaiting approval
- whether a successor-epoch receipt would be issued

## Public object

### Spine integrity page

Fields:

- `spine_integrity_page_id`
- `subject_ref`
- `integrity_verdict`
- `authoritative_witness_rows[]`
- `candidate_origin_rows[]`
- `preserve_vs_recreate_actions[]`
- `history_export_requirements[]`
- `successor_epoch_preview`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. integrity verdict
3. dominant origin hypothesis
4. preserve/recreate boundary
5. next least-widening action

Example:

```text
Project Alpha     duplicate-runtime     shared external path conflict     preserve possible if foreign owner quarantined     Open spine integrity
```

## Non-goals

This page does **not** replace sidecar editing, ordinary browse, or residue cleanup.
It proves only the current **continuity-spine integrity** and the repair boundary around it.
