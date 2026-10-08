
# Destructive review shell page — endpoint, seat, loss, and salvage interface spec

## Purpose

The archive already has overwrite-plan, overwrite-review, overwrite-ledger, and overwrite-receipt pages.
What this tranche still lacked was the higher shell that makes those pages feel like one reviewed danger workflow rather than several related documents.
This page exists to answer:

> before any destructive action is approved, what endpoint am I controlling, with what authority, against what loss surface, and with what remaining rescue ladder?

## Core decision

AnonSync must expose one first-class **Destructive review shell** whenever any serious action can:

- overwrite local work
- discard divergence
- reset encrypted/local custody
- replace an existing bind with a source-authoritative winner
- strand existing bytes outside the restored line

This shell is the stable container for all narrower overwrite/review/receipt pages.
No projection may skip it.

## Fixed shell anatomy

1. **Endpoint and trust strip**
2. **Action-under-review banner**
3. **Loss-class matrix pane**
4. **Salvage ladder pane**
5. **Proof drawer**
6. **Action tray and barrier link**
7. **Receipt continuity rail**

### 1) Endpoint and trust strip

Must show:

- endpoint label and stable handle
- listener scope (`local-only`, `lan-exposed`, `reverse-tunneled`, `publicly-routable`, `unknown`)
- auth posture (`unauthenticated`, `session-authenticated`, `device-bound`, `delegated`, `unknown`)
- transport trust grade (`managed`, `pinned`, `self-issued-reviewed`, `bootstrap-exception`, `unknown`)
- acting seat
- seat capability relevant to the current action

This is the answer to:

> what am I actually controlling, from where, and under what trust claim?

### 2) Action-under-review banner

Show:

- current destructive action name
- scope slice
- source-authority basis
- current readiness (`preview only`, `reviewable`, `blocked`, `ready for barrier`, `stale basis`)
- strongest honest sentence
- stronger unsupported sentence

This is the answer to:

> what dangerous act is on the table right now?

### 3) Loss-class matrix pane

This pane must embed the shared loss-matrix component family.
It must remain visible without opening a separate page on ordinary desktop/local-web widths.
At minimum it must summarize:

- edited files
- renames
- deletes
- local additions
- archive-bearing prior versions
- non-bearing residue
- successor-only survivors

### 4) Salvage ladder pane

This pane must embed the shared salvage-ladder component family.
It must remain visible before any approval barrier opens.
At minimum it must summarize:

- local rescue rungs
- remote rescue dependencies
- expiry pressure
- same-line restoration versus side survival
- already-spent or unavailable rungs

### 5) Proof drawer

The proof drawer must explain:

- why the action is destructive
- how each row got its loss classification
- which peer/locality bears old versions
- what assumptions remain unresolved

The drawer must be adjacent to the matrix and ladder, not buried in a help link.

### 6) Action tray and barrier link

The action tray must separate:

**safe-adjacent actions**

- export residue
- open salvage ledger
- promote successor instead
- refresh proof
- narrow scope

from

**destructive actions**

- open destructive approval barrier
- execute previously approved destructive action

No direct destructive commit may appear in the shell without the barrier object.

### 7) Receipt continuity rail

Show latest related objects:

- current overwrite plan
- current overwrite review
- current salvage ledger
- current destructive receipt
- superseding recovery/rejoin receipt if any

This is the answer to:

> what reviewed history already exists here, and what would this action supersede?

## Projection rule

A narrow-width or compact projection may stack these regions.
It may not hide endpoint/trust, loss matrix, or salvage ladder behind advanced settings before approval.

## Public object

### Destructive review shell page

Fields:

- `destructive_review_shell_page_id`
- `endpoint_ref`
- `listener_scope`
- `auth_posture`
- `transport_trust_grade`
- `acting_seat_ref`
- `seat_capability_rows[]`
- `destructive_action_ref`
- `loss_matrix_ref`
- `salvage_ladder_ref`
- `proof_rows[]`
- `latest_receipt_refs[]`
- `readiness_state`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `generated_at`
