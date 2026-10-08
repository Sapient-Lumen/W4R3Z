# File intent, deviation, and restore spec

## Problem this spec resolves

The archive already had pieces of this model:

- explicit `evict` versus `remove --scope share`
- preservation reports for risky file mutations
- deviation policies for non-authoritative mounts
- history and restore surfaces

What it still lacked was one dedicated answer to the operator question:

> what exactly am I asking the product to do to this file, what scope would that touch, what survives if I am wrong, and how does read-only or mirror drift render from the same public model?

That gap matters because a deeper Resilio pass keeps landing on the same seam from different directions:

- Selective Sync turns local deletion into placeholder reversion in some paths, while `Remove from this device` and `Remove from all devices` split local versus replicated effect
- disconnect/remove flows can also remove placeholder-visible local state while leaving remote state intact
- read-only peers may suspend synchronization for changed files unless `Overwrite any changed files` is enabled, and that option itself is disabled for read-only folders with Selective Sync on
- manual Archive restore still depends on a hidden directory or a desktop-only affordance, with timing caveats if Sync is not already running
- power-user defaults can pre-enable some of those behaviors, which means the operator contract is still partly held together by mode memory

AnonSync should not inherit that seam.
File intent, local deviation, preservation posture, and restore scope should be ordinary supported state.

## Core rule

Every file-affecting action must declare four things explicitly:

1. **intent** — fetch, pin, evict, remove locally, delete from share, restore locally, restore to share, or resolve a deviation case
2. **scope** — this mount only, this device only, the replicated share, or a reviewed share-wide plan
3. **preservation posture** — what bytes, versions, and replicas remain if the action succeeds
4. **deviation posture** — whether the target path is authoritative, non-authoritative, or currently in locally-deviated state

If any of those must still be inferred from mount mode, placeholder state, hidden archive layout, or a per-platform context menu, the model is not explicit enough.

## Vocabulary

### File intent

The operator-meaningful category of a requested file action.
Examples:

- `fetch`
- `pin`
- `evict-local-bytes`
- `remove-local-view`
- `delete-from-share`
- `restore-local`
- `restore-share`
- `resolve-deviation`

### Deviation case

A first-class record describing one locally observed add, modify, delete, or path-state deviation on a non-authoritative mount.
This is the public object that should exist instead of “that read-only folder got weird again”.

### File-intent receipt

A durable explanation record emitted after a scope-sensitive file action completes, is blocked, or is cancelled.
It exists so later audit can answer what intent the operator chose, what proof was attached, and whether local or replicated state changed.

## Non-negotiable design rules

1. **No overloaded remove.**  
   A product may offer convenience affordances, but it may not leave operators guessing whether a file operation was local reclamation or replicated deletion.

2. **Deviation is not a hidden mode caveat.**  
   When a read-only, receive-only, backup, or encrypted target drifts locally, that must surface as a public case with a stable ID, not just stalled sync behavior.

3. **Restore is not archive spelunking.**  
   Hidden history stores may exist, but ordinary restore should never require filesystem ritual or daemon-timing folklore.

4. **Scope must survive projection changes.**  
   The same file action must mean the same thing in CLI, TUI, web workbench, or future context-menu affordances.

5. **Preservation proof comes before destructive scope expansion.**  
   If a file action could eliminate the easiest rollback path, preservation posture must render before any destructive apply becomes primary.

6. **Non-authoritative mounts need explicit remediation state.**  
   The system must be able to say whether local evidence was preserved, reverted, quarantined, copied aside, or is blocking review.

## Object-model refinements

### Deviation case

A durable record for one locally observed deviation on a non-authoritative mount.

Fields:

- `deviation_case_id`
- `share_ref`
- `mount_ref`
- `path`
- `class` (`local-add`, `local-modify`, `local-delete`, `local-rename`, `path-drift`)
- `policy_ref`
- `current_state` (`detected`, `preserved`, `auto-remediated`, `quarantined`, `blocked`, `resolved`)
- `remediation_mode` (`preserve-and-flag`, `re-fetch`, `auto-revert`, `conflict-copy`, `block-pending-review`)
- `remote_progress` (`continue-with-warning`, `paused-for-path`, `blocked-for-mount`)
- `local_artifact_state` (`preserved`, `copied-aside`, `quarantined`, `reverted`, `none`)
- `detected_at`
- `last_transition_at`
- `report_ref` nullable
- `decision_trace_ref` nullable
- `provenance_ref` nullable

This object exists so the operator can inspect actual drift, not just the reusable policy that would normally govern drift.

### File-intent receipt

A durable record for one file-level action whose scope matters.

Fields:

- `file_intent_receipt_id`
- `share_ref`
- `mount_ref` nullable
- `path`
- `intent` (`evict-local-bytes`, `remove-local-view`, `delete-from-share`, `restore-local`, `restore-share`, `resolve-deviation`)
- `scope` (`mount-local`, `device-local`, `share`, `share-plan`)
- `history_entry_ref` nullable
- `deviation_case_ref` nullable
- `preservation_report_ref` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `blocked`, `cancelled`, `reverted`)
- `provenance_ref` nullable

This receipt does not replace plans or reports.
It exists so later audit can answer one simple question cleanly: “what kind of file action was this actually?”

## Intent matrix

### 1) Fetch

Effect:

- materializes bytes locally
- does not change share namespace or authority

Primary questions:

- is plaintext reachable
- is only ciphertext reachable
- is this mount allowed to materialize here

### 2) Evict local bytes

Effect:

- removes local bytes while keeping local path or placeholder-visible state as policy permits
- never deletes replicated share state

Primary proof:

- preservation report should answer whether later re-fetch is still plausible and from what source classes

### 3) Remove local view

Effect:

- removes local path or local placeholder-visible state on this mount/device only
- may keep incoming visibility if policy says so
- must not masquerade as replicated delete

Primary proof:

- binding/preservation state and resulting local visibility after action

### 4) Delete from share

Effect:

- requests replicated deletion
- usually needs preservation preview first
- may require plan/apply on sensitive targets or weak preservation posture

Primary proof:

- preservation report plus authority delta where relevant

### 5) Restore locally

Effect:

- materializes an earlier or deleted version only on this device or mount
- does not rewrite replicated share state

Primary proof:

- candidate history entry, local target path compatibility, and overwrite risk

### 6) Restore to share

Effect:

- writes a chosen historical version back into replicated share state
- should often be plan-bearing for sensitive or shared paths

Primary proof:

- candidate history entry, preservation report, current share settlement posture, and authority delta

### 7) Resolve deviation case

Effect:

- takes one explicit action against a public deviation case
- may preserve, copy aside, revert, or approve a path-specific exception according to policy and role

Primary proof:

- deviation case, effective deviation policy, and any preservation impact if local evidence would be discarded

## Workbench implications

The share detail page should expose a dedicated **File actions & local deviation** card or side panel.

It should answer:

- what action would happen if the operator clicks the current primary button
- whether the selected path is authoritative or non-authoritative here
- whether this is a local-only action or a replicated action
- what history candidates exist
- whether any active deviation cases already exist for this path
- what receipt will be emitted afterward

### Required actions

The panel should be able to surface:

- `Fetch`
- `Pin`
- `Evict local bytes`
- `Remove local view`
- `Preview delete from share`
- `Restore locally`
- `Prepare restore to share`
- `Review deviation case`

### Deviation-case drawer

When the operator opens a deviation case, the drawer should show, in order:

1. what local action was observed
2. what effective policy says should happen next
3. whether remote progress is still continuing
4. whether local evidence survives under the available actions
5. what receipt will be emitted after apply

## CLI surface

Suggested commands:

```text
anonsync deviation case list --mount mnt_01J...
anonsync deviation case show devc_01J...
anonsync deviation case resolve devc_01J... --action preserve-and-keep-blocked
anonsync deviation case resolve devc_01J... --action revert-local
anonsync file check vault Secrets/Taxes/report.pdf --for remove-share
anonsync file remove vault Secrets/Taxes/report.pdf --scope local
anonsync file remove vault Secrets/Taxes/report.pdf --scope share --plan
anonsync file restore vault Secrets/Taxes/report.pdf --entry hst_01J... --scope local
anonsync file restore vault Secrets/Taxes/report.pdf --entry hst_01J... --scope share --plan
```

Expected semantics:

- `deviation case list` renders actual drift instances, not just reusable policies
- `deviation case resolve` acts on one case and must say whether local evidence survives
- `file remove --scope local` is never allowed to become a silent replicated delete because of mount mode or placeholder state
- `file restore --scope share` should normally carry a plan on sensitive targets even when `restore --scope local` may act directly
- every scope-sensitive completion should emit a file-intent receipt

## API surface

A daemon API should expose at least:

```text
GET    /v1/deviation-cases
GET    /v1/deviation-cases/{deviation_case_id}
POST   /v1/deviation-cases/{deviation_case_id}/resolve
GET    /v1/file-intent-receipts
GET    /v1/file-intent-receipts/{file_intent_receipt_id}
```

These resources should exist so:

- local drift on a read-only or mirror target is queryable as a real object
- clients do not need to reverse-engineer deviation state from stalled transfers or warning strings
- later audit can explain one file action in terms of explicit intent and scope
- workbench, TUI, and CLI clients can all attach the same case or receipt to review flows

## Failure-posture rules

### Placeholder-visible path with weak preservation

If a selected file currently exists only as placeholder-visible local state and preservation posture is weak, the interface should not treat `Remove local view` as obvious harmless cleanup.
The operator still needs to know whether later re-fetch depends on an offline or encrypted-only source.

### Read-only path with local edits

If a read-only or receive-only path has local edits, the interface should surface a deviation case rather than leaving the path to look merely stalled.

### Restore candidate collides with newer local-only work

If a local restore target would overwrite newer local-only content, the product should force a review choice instead of assuming the historical version wins.

### Share-scope restore with degraded settlement

If a restore-to-share action would write into a share whose settlement confidence is degraded for the chosen intent, the product should render that explicitly and may force plan/apply.

## Outcome

If a user still has to remember that one delete gesture merely reverts to placeholder, another propagates deletion, a read-only edit might quietly stall until some checkbox changes, and actual restore still means walking a hidden archive path, the product has not actually exposed the model.

AnonSync should instead make file intent, deviation remediation, and restore scope look like one coherent operator surface with one evidence grammar and one receipt trail.
