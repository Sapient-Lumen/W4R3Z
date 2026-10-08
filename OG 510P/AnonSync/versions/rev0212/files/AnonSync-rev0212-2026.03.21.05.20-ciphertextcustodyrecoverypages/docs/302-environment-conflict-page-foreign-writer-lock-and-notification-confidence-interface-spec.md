# Environment conflict page — foreign writer, lock pressure, and notification confidence interface spec

## Purpose

The archive already names writer contention, delay policy, remote-volume posture, and filesystem support tiers.
What still remained under-specified was one ordinary page for the operator question:

> are we waiting on an ordinary local writer, suffering from weak change detection, or running an unsafe mixed-access topology that will keep hurting us until the environment changes?

Current Resilio docs still make this seam concrete through `Locked files`, `Setting Delay Time For Syncing`, `Sync and SMB file shares`, and `How soon does synchronization start?`.
The product truth is real, but it is still reconstructed from too many places.

## Core decision

AnonSync must expose one first-class **Environment conflict** page whenever the product sees evidence of local-write contention, foreign-writer topology risk, weak notification confidence, or a mixture of them.

## Fixed page order

1. **Conflict class verdict**
2. **Topology and writer map**
3. **Notification confidence**
4. **Safe timing / topology actions**
5. **Proof and follow-up**

### 1) Conflict class verdict

Show:

- `environment_conflict_page_id`
- `conflict_classes[]` (`local-lock-pressure`, `delay-window-only`, `foreign-writer-risk`, `notification-weakness`, `mixed`)
- `affected_paths[]`
- `current_risk_verdict` (`delay-only`, `degraded-but-safe`, `unsafe-bidirectional`, `unknown-needs-inspect`)
- `strongest_honest_summary`

The page must distinguish `the product is intentionally waiting` from `the topology itself is unsafe`.

### 2) Topology and writer map

Show:

- local writer candidates the product can observe
- foreign access classes (`same-host direct`, `SMB`, `network share`, `third-party direct-on-server`, `unknown`)
- whether the product can identify the owning writer exactly or only the blocked path
- `exclusive-bind_expectation`
- `mixed_access_risk_reason`

This section should make it ordinary to answer:

> who else may be touching these bytes, through which path family, and is that family compatible with safe bidirectional sync here?

### 3) Notification confidence

Show:

- `change_detection_profile` (`native-notify`, `notify-plus-periodic`, `periodic-only`, `unknown`)
- `notification_confidence` (`strong`, `degraded`, `weak`, `lost`)
- watcher/resource warnings where present
- storage-class reasons for weak confidence
- delay-policy rows if a deliberate batch window is masking immediate propagation

Weak change detection must remain visibly distinct from lock pressure.

### 4) Safe timing / topology actions

Actions should be grouped as:

- `wait for writer to clear`
- `review delay policy`
- `freeze bidirectional propagation`
- `narrow to one safe writer path`
- `move subject to safer storage/topology`
- `open repair plan`

Every action must preview:

- whether bytes keep moving during the action
- whether any writer path remains unsafe afterwards
- whether the action is reversible
- whether stronger topology change is still required

### 5) Proof and follow-up

Show:

- blocked file/path evidence
- last successful change-detection evidence
- topology observations that support the verdict
- receipts for freezes, timing changes, or topology narrowing
- recompute trigger (`writer clears`, `watchers recover`, `topology changes`, `manual inspect done`)

## Object model implications

### Environment conflict page

Fields:

- `environment_conflict_page_id`
- `subject_ref`
- `conflict_classes[]`
- `affected_paths[]`
- `current_risk_verdict`
- `writer_rows[]`
- `topology_rows[]`
- `notification_confidence`
- `delay_policy_rows[]`
- `action_rows[]`
- `proof_rows[]`
- `receipt_refs[]`
- `next_honest_action`

### Writer row

Fields:

- `writer_row_id`
- `writer_kind` (`local-app`, `foreign-process`, `remote-smb-client`, `unknown`)
- `identification_confidence`
- `paths[]`
- `lock_observed`
- `safe_with_current_topology`

## Explicit non-goals

AnonSync should not:

- collapse lock pressure, delay policy, and unsafe mixed access into one generic `busy` state
- recommend `touch files`, restart, or re-add while an unsafe foreign-writer topology still exists
- hide weak change detection behind normal-looking settled state
- imply that every blocked file is just a temporary editor save race

## Relationship to nearby specs

This page compiles and ordinary-izes deeper work from:

- `76-writer-contention-and-quiescence-review-spec.md`
- `190-locked-writer-delay-profile-and-quiescent-commit-interface-spec.md`
- `214-remote-volume-path-class-and-notification-confidence-interface-spec.md`
- `283-mutation-delay-page-file-class-batch-window-and-lock-avoidance-interface-spec.md`
