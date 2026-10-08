# Non-authority edit posture page — rights, local-change fate, and continuity mode interface spec

## Purpose

This page answers one ordinary question:

> this seat is not authoritative for this subject, so can I edit locally at all, what happens if I do, and do future updates keep flowing or stop per path?

The page exists because `read only`, `observer`, `backup`, and `mirror` are not enough.
The operator needs one direct statement of local-edit fate.

## Core decision

Every non-authority subject must render one first-class **Non-authority edit posture** page.
The page owns:

- authority grade on this seat
- whether local edits are blocked, tolerated, auto-healed, or allowed only outside the managed lane
- change-class fate for add / edit / rename / delete
- future-update continuity rule
- hardwired posture limits

## Primary layout

The page always renders the same regions in the same order:

1. posture strip
2. authority and lane card
3. local-change fate matrix
4. continuity mode card
5. hardwired limits card
6. receipts

### 1) Posture strip

Show:

- subject label
- seat label
- authority grade: `owner`, `writer`, `non-authority`, `opaque-backup`, `unknown`
- local-edit mode: `blocked`, `freeze-on-change`, `auto-heal`, `divert-locally`, `mixed`
- one honest next action

### 2) Authority and lane card

This card publishes:

- whether this seat may publish changes upstream
- whether this seat may only receive
- whether local edits are within the managed lane or must be redirected elsewhere
- whether this posture was chosen intentionally, inherited, or hardwired

The operator must be able to answer: **am I not allowed to write upstream, or am I not even allowed to change the local managed copy?**

### 3) Local-change fate matrix

Render one row for each change class:

- add local file
- edit existing file
- rename existing file
- delete existing file
- mutate metadata only

Columns:

- `local edit permitted?`
- `upstream propagation?`
- `future remote updates continue?`
- `auto-heal / revert risk?`
- `local-only residue possible?`
- `receipt language`

The product must not compress these rows into one generic `read only` sentence.

### 4) Continuity mode card

This card publishes:

- whether future updates stop per changed path, whole subject, or not at all
- whether auto-heal replaces local edits with remote state
- whether some local additions remain outside sync while other path classes revert
- what must happen to restore full continuity for frozen paths

The operator must be able to answer: **if I touch this here, what later updates do I stop getting?**

### 5) Hardwired limits card

This card publishes:

- posture-imposed limits such as `overwrite forced`, `selective materialization unavailable`, or `path-local freeze only`
- whether the current surface can change these limits
- whether the limit belongs to identity design, peer type, encryption posture, or current surface only

### 6) Receipts

Receipts show:

- authority grade
- local-edit mode
- continuity mode
- hardwired limits acknowledged
- strongest safe sentence after review

## Public object

### `non_authority_edit_posture`

Fields:

- `non_authority_edit_posture_id`
- `subject_ref`
- `seat_ref`
- `authority_grade`
- `local_edit_mode`
- `change_class_rules[]`
- `continuity_mode`
- `hardwired_limits[]`
- `policy_origin`
- `generated_at`

## Non-negotiable rules

### Rule 1 — permission and local-edit fate must stay separate

`Cannot publish upstream` is not the same truth as `cannot safely edit local managed bytes`.

### Rule 2 — per-change-class outcomes must stay visible

Add, edit, rename, delete, and metadata-only mutations may differ.
The page must publish those differences directly.

### Rule 3 — forced policy must look forced

If the posture hardwires overwrite, disables selective materialization, or forbids a safer alternative, the page must say so explicitly.

## Honest outputs

The page may conclude:

- `This seat is non-authoritative. Editing an existing managed file freezes future updates for that path until continuity is repaired.`
- `This seat is non-authoritative with auto-heal enabled. Local edits may be reverted by upstream state and should be treated as disposable unless preserved elsewhere first.`
- `This posture forces auto-heal and does not offer selective materialization on this seat.`

It may not collapse those outcomes into one `read only` badge.
