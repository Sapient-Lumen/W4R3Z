# Diagnostic export, packet freeze, and self-serve support boundary interface spec

## Purpose

The archive already had diagnostic-probe, evidence-bundle, and external-escalation language.
What it still lacked was one tighter operator-facing contract for the common troubleshooting question:

> when something is wrong, how do I collect a useful diagnostic package from the product itself, what stays private for local diagnosis, what becomes a frozen shareable packet, how long is it retained, and am I entering a self-serve or staffed-support path?

Current Resilio docs still make this seam concrete.
Their current debug-log guides still say v3 direct technical support is not available, encourage forum/help-center use, allow logging through UI or a `debug.txt` file in storage, require restart to ensure logging is enabled, expect at least 15 minutes of collection, and send operators into hidden storage paths that vary by OS and service account.
Other current docs split automatic report submission, mobile log pickup, crash-dump collection, and log-size expansion into separate rituals.
That is not one transparent diagnostic surface.

## Core decision

AnonSync must expose diagnostics as a first-class, reviewed export workflow with one hard split:

- **private incident evidence** for local diagnosis
- **frozen escalation packets** for outside disclosure

Every diagnostic export action should declare:

- collection depth requested
- retention and existing evidence already available
- redaction posture
- support mode (`self-serve`, `trusted collaborator`, `staffed support`, `private archive`)
- whether the result remains private, becomes a held-unsent packet, or is actually sent
- proof of what was exported and what was intentionally left out

## Why this matters

Current Resilio behavior still leaves too much meaning scattered across support pages and hidden paths:

- logging may be enabled by UI or by filesystem ritual
- restart is needed to be sure the setting took effect
- logs live in different hidden locations for desktop, Linux, Android, and services
- v3 troubleshooting leans on self-serve docs/forum rather than one product-native export ladder
- cleanup, log TTL, profiler controls, automatic uploads, and crash artifacts are disconnected from the moment an operator actually needs evidence

AnonSync should instead hold one stronger rule:

> diagnosis is a reviewed incident workflow, and outside disclosure is a separate frozen packet decision.

## Fixed review order

Every diagnostic export surface should render the same sections in the same order:

1. **Issue scope**
2. **Collection depth and retained evidence**
3. **Redaction posture**
4. **Support mode and packet state**
5. **Evidence and disclosure receipts**

### 1) Issue scope

Show:

- incident or case id
- affected seats / subjects
- time window requested
- whether the export is live-following or retrospective
- the short incident summary that will lead any later packet

### 2) Collection depth and retained evidence

Show:

- currently retained logs/evidence already available
- additional capture requested (`light`, `standard`, `deep`, `profiled`)
- storage budget impact
- retention expiration
- whether restart or reproduction is required to collect the missing depth
- whether deeper capture is still private incident evidence only

### 3) Redaction posture

Show:

- identifiers included
- network/path data included
- subject names or aliases included
- optional field stripping or hashing
- residual local copies after export or after probe stop

### 4) Support mode and packet state

Show:

- `self-serve diagnosis`
- `share with trusted collaborator`
- `formal support request`
- `private archive only`

And show one packet state:

- `private evidence only`
- `held-unsent packet draft`
- `sealed packet ready to send`
- `sent with receipt`

The operator must be able to answer:

> am I creating local evidence for myself, freezing a recipient-specific packet, or actually disclosing something to another party, and what support promise applies here?

### 5) Evidence and disclosure receipts

The receipts must preserve:

- incident ref
- evidence classes included
- redaction profile used
- support mode chosen
- packet state reached
- expiry / deletion policy
- hash or manifest of the frozen or sent package

## Main surface

The product should expose one **Diagnostics** page with explicit actions such as:

- `Collect light evidence for self-review`
- `Collect reproducible issue pack`
- `Prepare held-unsent redacted packet`
- `Seal recipient-specific support packet`
- `Inspect retained diagnostics before sending`

The operator should never need to know a hidden storage path before they can start.

## Object model implications

### Diagnostic export review

Fields:

- `diagnostic_export_review_id`
- `incident_ref`
- `seat_refs[]`
- `time_window`
- `requested_depth`
- `retained_evidence_refs[]`
- `restart_required`
- `reproduction_required`
- `support_mode`
- `packet_state`
- `estimated_bundle_size`

### Redaction profile

Fields:

- `diagnostic_redaction_profile_id`
- `identifier_policy`
- `path_policy`
- `network_policy`
- `subject_name_policy`
- `residual_copy_policy`

### Diagnostic export receipt

Fields:

- `diagnostic_export_receipt_id`
- `review_ref`
- `redaction_profile_ref`
- `support_mode`
- `packet_state`
- `bundle_manifest_ref`
- `retention_expires_at`
- `recorded_at`

## Explicit non-goals

AnonSync should not:

- require operators to discover hidden log paths before they can export evidence
- blur self-serve forum-style diagnosis together with staffed support escalation
- turn on deep collection without showing restart/reproduction cost
- export sensitive identifiers without an explicit redaction posture
- imply that sending evidence is the default or morally preferred outcome

## Relationship to nearby specs

This spec is the diagnostics-facing companion to:

- `139-diagnostic-probe-approval-and-minimization-interface-spec.md`
- `140-external-escalation-packet-and-redaction-review-interface-spec.md`
- `141-remediation-recipe-catalog-and-reversibility-review-interface-spec.md`
- `198-preseed-reuse-dedup-proof-and-local-block-witness-interface-spec.md`

Those documents define deeper probes, frozen escalation packets, and later remediation.
This one fixes the operator-facing export workflow that bridges self-diagnosis, held-unsent packet preparation, and outside help.


## Relationship to nearby specs

`250-runtime-status-bridge-live-health-verdict-and-dossier-escalation-interface-spec.md` now provides the lighter everyday-status lane that may exist before this fuller diagnostic/export workflow is needed.
This document remains the heavier incident / packet boundary once escalation is justified.
