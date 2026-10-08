# Diagnostic lane lineage receipt page: capture family, send path, and residue boundary interface spec

## Purpose

Every serious diagnostic act needs one durable receipt that answers later:

> what did we turn on, what evidence family did that create, what route did we use or reject, and what local residue boundary was actually proved?

## Receipt object

Emit one **Diagnostic lane lineage receipt** for every meaningful diagnostic-lane mutation, including:

- enabling or disabling debug capture
- changing log rotation budget
- activating profiler capture
- preparing crash-artifact watch or export
- proving or rejecting an outbound support lane
- cleaning up retained local evidence

## Required fields

- `diagnostic_lane_receipt_id`
- `incident_ref` nullable
- `capture_family` (`anonymous-metrics`, `debug-logs`, `profiler`, `crash-artifacts`, `mixed`, `unknown`)
- `activation_route` (`ui-toggle`, `power-user`, `debug-file`, `automatic-feedback`, `manual-export`, `unknown`)
- `support_lane` (`staffed-vendor`, `self-serve`, `billing-form`, `private-only`, `unknown`)
- `restart_boundary_state` (`not-needed`, `required-not-done`, `done`, `unknown`)
- `hold_time_verdict` (`not-applicable`, `too-short`, `sufficient`, `stale`, `unknown`)
- `artifact_set`
- `outbound_route` (`none`, `automatic-feedback`, `manual-attachment`, `upload-link`, `manual-local-extraction`, `unknown`)
- `send_verdict` (`not-attempted`, `blocked`, `sent`, `rejected`, `unknown`)
- `residue_boundary` (`local-artifacts-retained`, `rotation-only`, `cleanup-proved`, `unknown`)
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `timestamp`

## Fixed receipt sections

1. lane mutation summary
2. sufficiency and send summary
3. residue summary
4. blocked stronger sentence

### 1) Lane mutation summary

State:

- what family changed
- how it was activated or deactivated
- what support lane was proven or denied

### 2) Sufficiency and send summary

State:

- whether restart/hold-time requirements were satisfied
- whether an outbound send route was attempted or blocked
- which route was used if any

### 3) Residue summary

State:

- which local artifacts were expected or observed
- whether cleanup is merely available or actually proved

### 4) Blocked stronger sentence

Examples:

- `We proved debug capture was enabled.`
- `We did not prove that staffed vendor support was available for this product line.`
- `We proved a packet was sent.`
- `We did not prove that no sensitive local residue remained afterward.`

## Rules

### Rule 1 — send success may not erase local-residue history

The receipt must preserve what still remained local after export.

### Rule 2 — lane denial is still receipt-worthy

A blocked or self-serve-only support verdict still needs durable memory.

### Rule 3 — one receipt must preserve the stronger sentence that stayed blocked

Future operators should not overread a past capture or send event.
