# Narrow-seat mutation review page — suspension, auto-heal, local-only additions, and Selective Sync ceiling

## Purpose

When a user says `I changed something here and it did something weird`, this page determines the exact fate of the local divergence.
It exists because narrow-seat edits do not all fail the same way.
Rename, delete, content edit, and local add can diverge differently.

## Situations that must open this page

- a read-only or otherwise narrowed seat edited content and publication stopped;
- a renamed file reappeared under the old name;
- a deleted file came back unexpectedly;
- a newly added file stayed local instead of propagating;
- `Overwrite any changed files` is being proposed or was already active;
- Selective Sync is involved and the operator assumes auto-heal remains available.

## Inputs the page must collect

### Seat facts

- current grant label
- effective posture class
- whether `Overwrite any changed files` is enabled, disabled, or unavailable
- whether Selective Sync is ON for this seat
- whether the seat is direct, linked-family derived, local-share derived, or encrypted hard-wired

### Mutation facts

- action family (`rename`, `delete`, `content_edit`, `local_add`, `mixed`)
- whether the object was already known to peers
- whether the object existed only locally before the action
- whether continuity for this file is already suspended
- whether source bytes remain available from an authoritative writer

## Decision ladder

### Branch 1 — ordinary allowed mutation

Use this branch when the seat has actual writeback authority.
The page should show:

- that the mutation is expected to publish;
- archive or chronology caveats if relevant;
- no narrow-seat repair path needed.

### Branch 2 — suspension on known file

Use this branch when a narrow seat edited a known synced file and continuity for that file is now suspended.
The page should show:

- the exact action that triggered suspension;
- whether the suspension is per-file or wider;
- what evidence proves that peers are now waiting on authoritative source state.

### Branch 3 — auto-heal / revert from source

Use this branch when overwrite-heal is active and the product will restore source state.
The page should show:

- whether the local action was rename, delete, or content edit;
- the exact expected heal result;
- destructive-loss risk for local-only changes;
- whether source bytes are still online and authoritative.

### Branch 4 — local-only addition survivor

Use this branch when a local add on a narrow seat will remain present locally but will not be propagated.
The page should show:

- that the new object is not publishing outward;
- whether the object now creates silent local divergence;
- whether later promotion or copy-out is required to keep it.

### Branch 5 — repair option unavailable because posture ceilings changed

Use this branch when the operator expects auto-heal but the seat's current combination blocks it, including Selective Sync ON for a RO seat.
The page should show:

- why overwrite-heal is unavailable;
- the next admissible repair rung;
- whether posture change, manual copy-out, or alternate writer seat is required.

## Required warnings

- `sync stopped` is weaker than `all mutation classes behaved the same`.
- `overwrite changed files` is weaker than `safe`; it is a destructive repair path.
- `file came back` is weaker than `undo is complete`; chronology and archive truth may still matter.
- `added here` is weaker than `shared with peers`; it may be local-only residue.
- `read-only + selective sync` is weaker than `same repair menu`; available repair options may narrow.

## Review outputs

- `action_family`
- `fate_class`
- `continuity_status`
- `heal_availability`
- `source_authority_needed`
- `strongest_safe_sentence`
