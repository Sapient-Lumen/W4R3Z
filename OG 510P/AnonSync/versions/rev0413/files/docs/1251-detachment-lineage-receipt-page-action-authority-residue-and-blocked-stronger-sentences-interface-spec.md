# Detachment lineage receipt page: action, authority, residue, and blocked stronger sentences interface spec

This receipt exists so a later operator can open one object and answer five questions without re-reading several prose articles:

1. **what detachment or revocation action happened**
2. **who had authority to do it**
3. **what future channels were cut off**
4. **what residue survived in bytes, rosters, or storage**
5. **what stronger sentence the product refused to make**

## Required receipt fields

- `receipt_id`
- `issued_at`
- `actor_handle`
- `action_class`
- `scope_class`
- `authority_basis`
- `target_subject_refs`
- `target_peer_refs`
- `future_update_boundary`
- `byte_survivor_scope`
- `roster_residue_scope`
- `storage_residue_scope`
- `reappearance_triggers`
- `blocked_stronger_sentence`
- `followup_review_refs`

## Example safe sentences

- `Offline roster row was hidden only; standing relationship evidence may still survive.`
- `Selected peer was cut off from future updates, but already synchronized bytes remained outside the action boundary.`
- `Program uninstall removed the runtime while leaving filesystem and archive residue for separate review.`

## Example blocked stronger sentences

- `This seat is gone everywhere.`
- `No one can reattach without new approval.`
- `All data and records were removed.`

## Why this receipt matters

Detachment actions are easy to overclaim because the UI often gets cleaner before the world gets smaller.
AnonSync must therefore leave a durable receipt that preserves the difference between:

- decluttering and severance
- future-update cutoff and byte retraction
- linked-family removal and ecosystem-wide disappearance
- uninstalling software and clearing all state
