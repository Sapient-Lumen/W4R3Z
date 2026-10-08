# Mount binding, repair, and preservation spec

## Purpose

This document makes one more operator seam first-class:

> where is this share actually bound locally, what survives if that path drifts or breaks, and how can the operator detach, repair, relocate, or restore without remove/re-add folklore?

This matters because a deeper Resilio pass reveals the same coupling from several directions:

- linked-device convenience prefers a default folder unless the device is switched into `Disconnected` mode and each folder is manually connected to a chosen path
- reconnect can propose a different default path and create a duplicate-index directory if the expected name already exists
- moving a syncing folder is only supported inside fairly narrow path boundaries; otherwise the user lands in `Folder not found`
- `Service files missing` remediation still tells the operator to remove the share, make sure nothing important remains in archive, delete `.sync`, and add the folder back
- archive restore is manual and depends on a hidden directory or desktop-only affordance, with extra timing caveats if the daemon is not already running

AnonSync should not inherit that seam as “advanced behavior”.
Bound path, visible-share state, and preservation posture should be ordinary supported state.

## Core rule

Share identity, incoming visibility, local path binding, and preservation posture are separate first-class objects.

That means:

- a share can remain visible even when no local path is currently bound
- a broken or missing local binding should not force share re-creation
- preservation coverage should be inspectable even when the active path is degraded
- repair should produce a reviewed plan and a durable receipt
- detach, relocate, restore, and repair should reuse one coherent grammar instead of scattering across warnings, hidden folders, and per-platform ritual

## Vocabulary

### Bound path

The concrete local filesystem path currently attached to a mount.

### Desired path

The path the operator intends this mount to live at, even if the current path is missing or degraded.
Keeping this distinct avoids turning “path drift” into “share disappeared”.

### Binding health

A compact summary of whether the mount's local attachment is still trustworthy.
Examples:

- `ok`
- `missing-path`
- `marker-drift`
- `needs-compare`
- `repair-required`

### Binding receipt

A durable audit record for one successful or attempted bind-oriented action such as adopt, relocate, detach, reconnect, or repair.

### Preservation set

A summary of what rollback or recovery material is currently available for a share or mount.
It should not depend on the operator already knowing where hidden history or service data happens to live on disk.

## Non-negotiable design rules

1. **Repair is not remove/re-add.**  
   If the product can still prove share identity and compare candidate paths, the primary action should be repair or rebind, not “start over”.

2. **Detach is not forget.**  
   Releasing one local path should not automatically erase incoming visibility, authority records, or recovery context.

3. **Binding identity is not path string equality.**  
   A path move, rename, or reconnect prompt should not silently create a second local universe when the operator intended continuity.

4. **Preservation must be visible before local surgery.**  
   If a repair or destructive cleanup would strand history, local-only changes, or the easiest rollback path, that must be shown before apply.

5. **Repair plans must carry comparison, compatibility, and preservation evidence together.**  
   Path repair is exactly the sort of action that becomes dangerous when proof is split across multiple hidden places.

6. **Hidden service directories are never part of the ordinary operator contract.**  
   Internal markers, version stores, and service metadata may exist, but the supported workflow must not depend on manually editing or deleting them.

## Object-model refinements

### Mount refinements

The existing `mount` object should additionally expose:

- `desired_path` nullable
- `binding_health` (`ok`, `missing-path`, `marker-drift`, `needs-compare`, `repair-required`, `blocked`)
- `last_path_probe_at` nullable
- `last_binding_receipt_ref` nullable
- `preservation_set_ref` nullable
- `visible_if_detached` boolean

`binding_status` may still summarize coarse lifecycle such as `bound`, `relocating`, `drifted`, or `blocked`.
`binding_health` exists to answer the narrower question “what is wrong with the current local attachment right now?”

### Binding receipt

A durable record for bind-oriented actions.

Fields:

- `binding_receipt_id`
- `share_ref`
- `mount_ref` nullable
- `action` (`adopt`, `relocate`, `repair`, `detach`, `reconnect`)
- `old_path` nullable
- `new_path` nullable
- `visibility_after_action` (`incoming`, `mounted`, `hidden-by-policy`)
- `comparison_report_ref` nullable
- `fs_compat_report_ref` nullable
- `preservation_report_ref` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `cancelled`, `blocked`, `reverted`)
- `provenance_ref` nullable

### Preservation set

A compact summary of the currently usable rollback surface for one share or mount.

Fields:

- `preservation_set_id`
- `share_ref`
- `mount_ref` nullable
- `current_binding_path` nullable
- `history_backend` (`local-store`, `replica-derived`, `mixed`, `none`)
- `retention_summary`
- `captures_local_changes` (`yes`, `no`, `peer-only`, `mixed`)
- `max_capture_size` nullable
- `known_plaintext_replicas`
- `known_encrypted_replicas`
- `coverage_confidence` (`high`, `guarded`, `low`)
- `last_verified_at`
- `provenance_ref` nullable

This object does not replace `preservation_report`.
It provides a reusable baseline so the workbench can answer “what survives here at all?” before a specific delete, detach, or restore is proposed.

## Workbench implications

The share-detail page should expose a dedicated **Binding & Preservation** card or tab.

It should answer:

- current bound path
- desired path, if different
- binding health and most recent probe time
- whether the share would remain visible if detached
- what preservation set currently exists
- what the last binding receipt changed
- which next-safe actions exist right now

### Required actions

The card should be able to surface:

- `Compare target`
- `Prepare repair`
- `Relocate`
- `Detach but keep visible`
- `Preview preservation`
- `Browse history`
- `Restore locally`
- `Restore to share` (guarded)

### Repair drawer

When the operator chooses repair, the workbench should not jump straight to an apply button.
It should show, in order:

1. what binding is currently degraded
2. what candidate target path is being compared
3. whether filesystem semantics remain acceptable there
4. what preservation posture exists if the repair goes wrong
5. whether the result will keep the same visible share / mount lineage
6. what receipt will be emitted after apply

## CLI surface

Suggested commands:

```text
anonsync mount doctor mnt_01J...
anonsync mount detach mnt_01J... --keep-visible
anonsync mount compare mnt_01J... --path /srv/workdocs
anonsync mount repair mnt_01J... --path /srv/workdocs --plan
anonsync preserve show mnt_01J...
anonsync preserve show workdocs --path Reports/Q1.xlsx
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
```

Expected semantics:

- `mount doctor` explains current binding health, expected path, marker state, last receipt, and whether repair is possible
- `mount detach --keep-visible` releases the local binding without pretending the share was forgotten or revoked
- `mount repair` is for continuity of an existing mount whose path drifted, moved, or lost markers; it is not shorthand for remove/re-add
- `preserve show` renders the baseline preservation set and should make history gaps or peer-only capture explicit
- a repair plan should normally reference a fresh comparison report, filesystem-compatibility report, and preservation report together

## API surface

A daemon API should expose at least:

```text
GET    /v1/mounts/{mount_id}/doctor
POST   /v1/mounts/{mount_id}/detach
POST   /v1/mounts/{mount_id}/repair
GET    /v1/mounts/{mount_id}/preservation
GET    /v1/preservation-sets
GET    /v1/preservation-sets/{preservation_set_id}
POST   /v1/preservation-sets/{preservation_set_id}/refresh
GET    /v1/binding-receipts
GET    /v1/binding-receipts/{binding_receipt_id}
```

These resources should exist so:

- a missing path can be inspected without mutating anything
- detach can be modeled separately from removal or revocation
- repair can return a plan instead of acting like a reconnect shortcut
- preservation coverage is queryable outside one specific delete request
- UI, TUI, and CLI surfaces can all explain the last bind-oriented change from the same public record

## Failure-posture rules

### Missing path

If the current bound path is absent, the mount should degrade to a reviewable `repair-required` state.
The product should not silently bind to a new default path.

### Foreign or damaged markers

If internal service markers look foreign or damaged, the product should surface that as explicit marker drift.
The operator may later choose a repair or rebuild workflow, but the system should not auto-delete the suspect data.

### Duplicate-name candidate paths

If a reconnect or repair target would create a second same-named directory, the product should call that out as a continuity risk, not a harmless convenience detail.

### Preservation asymmetry

If history only captures peer-origin versions, or large files are outside capture policy, the preservation set should say so directly.
The operator should not discover that limit only after a repair or restore path fails.

## Outcome

If the safest answer to a broken path is still “remember the hidden folder name, delete the marker, remove the share, and hope you preserved the right archive first”, the product has not actually exposed the model.

AnonSync should instead make bind, detach, repair, preservation, and restore look like one coherent operator surface with one evidence grammar and one receipt trail.
