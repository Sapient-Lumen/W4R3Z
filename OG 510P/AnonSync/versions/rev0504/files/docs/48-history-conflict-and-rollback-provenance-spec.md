# History, conflict, and rollback provenance spec

## Problem this spec resolves

The archive already had pieces of this territory:

- file-intent scope
- preservation reports and preservation sets
- file history listing and restore commands
- conflict objects and conflict-resolution commands
- settlement barriers for high-signal share-wide actions

What it still lacked was one dedicated answer to the operator question:

> what exact earlier state can I still recover, who or what produced it, what confidence and retention horizon does that answer have, and what durable receipt proves how I resolved or rolled back the situation?

A further Resilio pass makes that gap much sharper.
Current official docs still spread rollback truth across several distinct surfaces:

- `History` in the desktop main view shows general syncing activity for the last 30 days
- Archive restore is manual, desktop-UI or hidden-path oriented, and the docs warn that Sync should already be running or an older restored file may simply be archived again on rescan
- Archive itself does not record which peer changed a file; the docs send operators to History for that
- an offline peer that later returns can override later online edits, with overwritten versions then landing in Archive
- conflict handling still depends on `.Conflict` artifacts and safe-removal ritual, and a power-user preference can suppress conflict-file creation while leaving syncing unpredictable

Those are not trivial UX nits.
They are evidence that rollback provenance, restore scope, and conflict resolution are still not one public operator model.

AnonSync should not clone that shape.

## Core rule

Rollback, restore, and conflict resolution must share one public timeline model.

That means:

1. history entries are durable objects, not just event text
2. restore candidates are typed and scope-bearing, not implicit in hidden on-disk layout
3. conflict cases link to the relevant history entries when possible
4. completed restore or conflict-resolution actions emit rollback receipts
5. audit can later answer not only that something changed, but which prior state won, what lost, and what proof or settlement posture was attached

If any ordinary operator workflow still depends on opening hidden archive directories, interpreting suffix-heavy filenames, or remembering that one short-lived activity view contains the missing provenance, the public model is not explicit enough.

## Vocabulary

### History entry

A durable timeline record describing one prior file state or rollback-relevant capture.
Examples:

- remote file replaced
- remote file deleted
- conflict candidate preserved
- deviation artifact copied aside
- operator restore applied
- conflict resolution applied

### Restore candidate

A typed proposal derived from one or more history entries, current path state, and scope rules.
This is the public object that answers “what would it mean to restore this here?”

### Conflict case

A durable record for content concurrency, delete-vs-modify, or path/capability mapping ambiguity.
Conflict cases are first-class public objects, not a filename convention.

### Rollback receipt

A durable explanation record proving how a restore or conflict-resolution action actually completed, what source it used, and what loser-handling or scope was applied.

## Non-negotiable design rules

1. **No hidden-path dependency for ordinary rollback.**  
   Hidden storage may exist, but ordinary restore and conflict review must not require filesystem spelunking.

2. **No magic filename API.**  
   Suffixed artifacts may exist as compatibility outputs, but the public control model may not require operators to edit or delete them directly.

3. **Provenance must be explicit.**  
   Where known, a history entry should expose source peer, capture cause, capture time, and retention horizon.

4. **Gaps must be surfaced, not implied.**  
   If history is peer-only, TTL-limited, size-capped, or confidence-limited, the model must say so directly.

5. **Scope must stay explicit at rollback time.**  
   Restoring locally, restoring on one device, and writing an old version back into replicated share state are separate actions with separate proof requirements.

6. **Conflict resolution must publish loser handling.**  
   It is not enough to say which candidate won; the product must say what happened to the loser: copied aside, quarantined, left intact locally, or deleted share-wide.

7. **High-signal rollback may still need settlement.**  
   A share-wide restore or destructive conflict resolution may depend on settlement policy and should say so directly before apply.

## Object-model additions

### History entry

Fields:

- `history_entry_id`
- `share_ref`
- `mount_ref` nullable
- `path`
- `entry_kind` (`remote-replaced`, `remote-deleted`, `conflict-candidate`, `deviation-artifact`, `restored`, `resolved-conflict`)
- `capture_reason` (`remote-update`, `remote-delete`, `conflict-detected`, `deviation-preserved`, `operator-restore`, `operator-resolution`)
- `captured_from_peer_ref` nullable
- `captured_at`
- `retention_horizon` nullable
- `storage_class` (`history-store`, `preservation-copy`, `derived-remote`, `mixed`)
- `scope_allowances[]` (`mount-local`, `device-local`, `share-plan`)
- `confidence` (`high`, `guarded`, `low`)
- `linked_conflict_refs[]`
- `linked_receipt_refs[]`
- `provenance_ref` nullable

### Restore candidate

Fields:

- `restore_candidate_id`
- `history_entry_ref`
- `share_ref`
- `mount_ref` nullable
- `path`
- `target_scope` (`mount-local`, `device-local`, `share-plan`)
- `overwrite_risk` (`none`, `guarded`, `high`, `blocked`)
- `current_path_state` (`missing`, `present`, `placeholder`, `conflicted`, `blocked-by-policy`)
- `requires_settlement` (`true`, `false`)
- `preservation_report_ref` nullable
- `settlement_policy_ref` nullable
- `recommended_next_action`
- `generated_at`

### Conflict case (refined)

Required refinements above the older conflict object:

- `kind` expands to include `capability` for filesystem or platform-specific mapping collisions
- `candidates[]` should include source peer, path rendering, content fingerprint summary, and whether the candidate already has a history entry
- `suggested_winner_policy` may be present, but must never hide loser handling
- `loser_handling_options[]` should be explicit (`copy-aside`, `quarantine`, `leave-local`, `delete-sharewide`)
- `history_refs[]` should link any relevant preserved or inferred earlier states

### Rollback receipt

Fields:

- `rollback_receipt_id`
- `share_ref`
- `mount_ref` nullable
- `path`
- `source_type` (`history-entry`, `conflict-case`, `deviation-artifact`, `manual-import`)
- `source_ref`
- `action_kind` (`restore-local`, `restore-share`, `resolve-conflict`, `copy-aside-and-restore`, `quarantine-and-continue`)
- `scope` (`mount-local`, `device-local`, `share-plan`)
- `winner_ref` nullable
- `loser_refs[]`
- `loser_handling` (`left-intact`, `copied-aside`, `quarantined`, `deleted-sharewide`, `deleted-local`, `unknown`)
- `settlement_receipt_ref` nullable
- `file_intent_receipt_ref` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `blocked`, `cancelled`, `reverted`)
- `provenance_ref` nullable

## Report implications

The report language should support a dedicated `rollback-conflict` family.

It should answer:

- what prior state exists for this path
- what confidence and retention horizon those states have
- whether a conflict is content, delete-vs-modify, case, unicode/path-mapping, or capability-class
- what the safest next move is
- what follow-up remains after apply
- whether an apply will emit a rollback receipt and whether settlement/preservation proof is still required

## CLI implications

A minimum public surface should include:

```text
anonsync file history <share> <path>
anonsync file history <share> <path> --show-provenance
anonsync file restore <share> <path> --entry <history_entry_id> --scope local
anonsync file restore <share> <path> --entry <history_entry_id> --scope share --plan
anonsync conflict list --share <share>
anonsync conflict show <conflict_id> --history
anonsync conflict resolve <conflict_id> --winner <candidate_id> --loser-handling copy-aside --plan
anonsync rollback receipt list --path <path>
anonsync rollback receipt show <rollback_receipt_id>
```

Semantics:

- `history` is provenance-first, not just timestamp-first
- `restore` must state scope explicitly
- `conflict show --history` should join the conflict case to relevant preserved earlier states where possible
- `rollback receipt show` should answer what source was used, what lost, what scope changed, and what proof/settlement standard backed the apply

## Daemon API implications

A minimum public surface should include:

```text
GET  /v1/files/history?share_id=...&path=...
GET  /v1/files/history/{history_entry_id}
POST /v1/files/history/query
POST /v1/files/restore
GET  /v1/conflicts/{conflict_id}/history
GET  /v1/rollback-receipts
GET  /v1/rollback-receipts/{rollback_receipt_id}
```

The API should not assume that a caller can or should reconstruct rollback provenance from raw audit text, filesystem layout, or transport logs.

## Workbench implications

The share detail page should expose one combined **History, conflicts, and rollback** card.

It should answer:

- what prior states exist for the selected path or subtree
- who produced them and when
- whether any relevant conflict case is still open
- whether restore is local-only, device-local, or share-plan scope
- what evidence or settlement barrier still blocks apply
- which rollback receipt last touched this path

The point is not to add another tab.
The point is to stop file history, conflict resolution, and rollback proof from becoming three separate mini-products.

## Canonical operator questions this spec should make easy

- “Which peer produced the recoverable version I am about to use?”
- “Is this restore local-only, or will it rewrite the replicated share?”
- “Do I still have enough retention/provenance to trust this rollback?”
- “What exactly conflicted here: bytes, delete-vs-modify, or path mapping?”
- “What happened to the losing version after I resolved the conflict?”
- “Can I prove later what source and proof standard backed this restore?”

## Why this is a real non-clone requirement

Resilio's current docs are candid and useful.
But they still leave rollback meaning spread across:

- a generic 30-day History surface
- hidden/manual Archive restore
- offline-wins overwrite behavior
- `.Conflict` filename ritual and safe-removal choreography
- power-user toggles that can change conflict behavior below the main product story

That is workable support knowledge.
It is not the right public contract for AnonSync.

AnonSync should instead make rollback provenance and conflict resolution first-class state from day one.
