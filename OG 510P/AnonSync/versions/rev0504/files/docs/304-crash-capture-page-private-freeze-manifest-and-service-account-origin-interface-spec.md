# Crash capture page — private freeze, manifest, and service-account origin interface spec

## Purpose

The archive already has diagnostic bundles, probe approval, escalation packets, and diagnostic export logic.
What still remained under-specified was one ordinary page for the operator question:

> a crash or deep failure happened — what evidence already exists, what more capture requires restart or reproduction, where will it come from, and when does it become a frozen disclosure packet?

Current Resilio docs still make this seam concrete through storage-folder, debug-log, crash-report, mini-dump, and NAS core-dump guides.
Those docs are practical, but still too hidden-path and service-account shaped to clone directly.

## Core decision

AnonSync must expose one first-class **Crash capture** page whenever crash artifacts exist or deeper local evidence capture is the honest next move.

## Fixed page order

1. **Existing artifact inventory**
2. **Capture prerequisites**
3. **Origin and custody**
4. **Freeze / disclosure boundary**
5. **Retention and destruction**

### 1) Existing artifact inventory

Show:

- `crash_capture_page_id`
- `artifact_rows[]` grouped by type (`recent-log`, `rotated-log`, `crash-report`, `mini-dump`, `core-dump`, `trace-window`, `config-snapshot`)
- `time_window_covered`
- `coverage_verdict` (`enough-for-local-review`, `needs-reproduction`, `needs-deeper-capture`, `no-useful-artifacts-yet`)

The operator must not need to know hidden file paths to learn what already exists.

### 2) Capture prerequisites

Show:

- whether restart is required
- whether repro duration is required
- whether deeper logging changes performance or retention cost
- whether the seat must remain foreground/background/SSH-launched for capture
- whether the requested capture remains private evidence only

### 3) Origin and custody

Show:

- `artifact_origin_rows[]`
- runtime principal / service account / state-root that produced each artifact
- whether the artifact belongs to the current active world or another state root
- whether the artifact was imported, copied, or locally produced

This section is crucial for hosts that can run as desktop user, service account, or headless instance.

### 4) Freeze / disclosure boundary

Show:

- `packet_state` (`private-only`, `held-unsent`, `sealed-for-recipient`, `sent`)
- recipient or destination if any
- redaction profile if any
- exact manifest/hash of the frozen packet
- what stayed local only

The page must keep `collect evidence` separate from `freeze and disclose evidence`.

### 5) Retention and destruction

Show:

- local retention expiry
- packet retention expiry
- auto-destruction / manual destruction controls
- residue after capture stops
- receipts proving destruction or sealing

## Object model implications

### Crash capture page

Fields:

- `crash_capture_page_id`
- `incident_ref`
- `artifact_rows[]`
- `coverage_verdict`
- `prerequisite_rows[]`
- `origin_rows[]`
- `packet_state`
- `manifest_ref` nullable
- `redaction_profile_ref` nullable
- `retention_rows[]`
- `receipt_refs[]`
- `next_honest_action`

### Artifact origin row

Fields:

- `artifact_origin_row_id`
- `artifact_ref`
- `origin_runtime_profile`
- `origin_principal`
- `origin_state_root_ref`
- `locality` (`current-world`, `other-local-world`, `imported`, `unknown`)
- `collection_path_class` (`product-managed`, `system-managed`, `external-shell-step`, `ssh-session`, `unknown`)

## Explicit non-goals

AnonSync should not:

- make operators hunt through hidden service-account directories just to learn whether evidence exists
- blur local crash capture together with outside disclosure
- imply that a crash packet is authoritative without showing origin runtime/state-root
- leave old artifacts lying around without retention and destruction truth

## Relationship to nearby specs

This page is the crash/deep-failure companion to:

- `139-diagnostic-probe-approval-and-minimization-interface-spec.md`
- `232-diagnostic-export-log-redaction-and-self-serve-support-boundary-interface-spec.md`
- `140-external-escalation-packet-and-redaction-review-interface-spec.md`
- `291-state-root-page-active-world-identity-custody-and-clone-risk-interface-spec.md`
