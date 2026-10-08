# External blocker handoff, follow-up, and return-proof interface spec

## Purpose

The archive already had browser handoff, control-trust bootstrap, install readiness, discovery-catalog fallback, shell-equivalence, external-editor roundtrip, and support/export review.
What it still lacked was one stronger general contract for a common but easily blurred class of blocker:

> when the product cannot finish the next step inside its own current surface and the operator must do work in a browser, OS dialog, shell, firewall console, filesystem tool, or third-party admin plane, what object keeps that outside step explicit, owned, and provably returned?

Without that contract, serious blockers tend to fail in two opposite ways:

- the local object keeps looking blocked forever even though the real work has already been handed off elsewhere
- the blocker disappears as if resolved even though no durable follow-up object now carries the outside work

## Core decision

Any blocker whose next honest step leaves the current product surface must create one first-class **external blocker handoff** object.

That object must state:

1. why the current surface cannot complete the work locally
2. which outside lane now owns the next step
3. what follow-up handle or request was created there
4. what proof counts when the operator returns
5. when stale or expired outside work must be reviewed again

The product must not reduce this to a vague `Open settings`, `Run this command`, or `Ask your admin` note.

## Why this needs its own spec

Current sync-product reality repeatedly pushes work outside the app:

- browser certificate exceptions or trust import
- firewall or port-consent dialogs
- service restarts
- shell-extension or file-provider repair
- external network tests
- removable-storage or filesystem-permission regrant
- third-party admin changes such as router or NAS configuration

The existing AnonSync specs already model many of those seams individually.
What they did not yet share was one durable follow-up contract for the moment the blocker leaves the current object.
Cross-reading the comparison archives made the missing shape clearer:
current local state and outside follow-up ownership should not silently collapse into one queue row.

## Public objects

### External blocker handoff

A durable follow-up object for one outside-product blocker path.

Suggested fields:

- `external_blocker_handoff_id`
- `source_object_ref`
- `blocker_kind` (`browser-trust`, `os-consent`, `filesystem-permission`, `external-tool`, `network-admin`, `service-control`, `third-party-support`, `other`)
- `outside_lane` (`browser`, `os-dialog`, `shell`, `admin-console`, `vendor-ticket`, `forum-thread`, `other`)
- `current_blocking_effect` (`blocks-now`, `blocks-until-handoff`, `advisory-only`, `explanation-only`)
- `followup_state` (`draft`, `issued`, `awaiting-return-proof`, `satisfied`, `expired`, `abandoned`)
- `followup_handle` nullable
- `created_at`

### Outside step row

One required outside step owned by the handoff.

Suggested fields:

- `outside_step_row_id`
- `handoff_ref`
- `step_kind` (`open-page`, `confirm-dialog`, `run-command`, `edit-setting`, `collect-output`, `ask-admin`, `upload-packet`, `other`)
- `summary`
- `allowed_shortcuts`
- `forbidden_shortcuts`
- `completion_evidence_needed`

### Return-proof row

One fact the product requires before it may claim the blocker changed.

Suggested fields:

- `return_proof_row_id`
- `handoff_ref`
- `proof_kind` (`local-reread`, `runtime-restart-observed`, `receipt-imported`, `artifact-hash-match`, `operator-attested`, `external-response-linked`, `unknown`)
- `state` (`missing`, `present`, `stale`, `contradictory`)
- `summary`

### Handoff receipt

A durable record that proves the handoff was created, updated, satisfied, or allowed to expire.

Suggested fields:

- `handoff_receipt_id`
- `handoff_ref`
- `transition` (`create`, `issue`, `return-checked`, `satisfied`, `expire`, `abandon`)
- `actor_ref`
- `recorded_at`

## Fixed inspection order

Every external blocker handoff surface should preserve this order:

1. **Why the current surface cannot finish locally**
2. **Outside lane and follow-up owner**
3. **Required outside steps and forbidden shortcuts**
4. **What counts as return proof**
5. **Stale or expired handoff policy**
6. **Resume here, escalate further, or abandon**

### 1) Why the current surface cannot finish locally

This section should say why the blocker is truly outside the current object.
Examples:

- `browser trust exception is required before local web can continue`
- `firewall consent is controlled by the host OS, not this page`
- `iperf measurement requires Sync to stop and an external binary to run`

### 2) Outside lane and follow-up owner

This section should name where the work moved.
Examples:

- `browser lane — certificate warning / trust import`
- `os-dialog lane — firewall consent`
- `vendor-ticket lane — waiting for support reply on packet 3`

### 3) Required outside steps and forbidden shortcuts

Examples:

- required: `open named dialog`, `confirm one trust scope`, `return to local-web control page`
- forbidden: `permanently disable verification`, `leave debug capture running indefinitely`, `replace unrelated config values while you are there`

### 4) What counts as return proof

Examples:

- `local reread shows listener reachable on the trusted endpoint`
- `runtime restart observed and probe stop receipt recorded`
- `packet reply linked to this incident and still current`
- `operator assertion alone is not enough for a stronger claim here`

### 5) Stale or expired handoff policy

Examples:

- `support reply older than the current incident state must be re-reviewed`
- `outside admin request with no handle or receipt returns to blocking state`
- `temporary browser trust step expires when the endpoint identity changes`

### 6) Resume here, escalate further, or abandon

Examples:

- `Resume current review with verified return proof`
- `Open stronger escalation packet`
- `Mark handoff abandoned and keep blocker explicit`

## Public rules

### Rule 1 — local blocker state and outside follow-up state are separate

Clearing one must not silently clear the other.

### Rule 2 — out-of-scope work needs an explicit follow-up handle

If the work moved outside the current object, the handoff should create or reference one durable follow-up handle whenever possible.

### Rule 3 — stale outside work needs disposition, not silent disappearance

An old forum reply, admin promise, or vendor note must not continue to count forever without freshness review.

### Rule 4 — return proof is stronger than optimism

The product should prefer local reread, receipt linkage, or verified runtime state over memory or vague assurance.

### Rule 5 — opening an outside lane is not the same as resolving the blocker

A launched browser page or opened shell window is handoff progress, not blocker satisfaction.

## Dense row contract

A dense handoff row should preserve these labels in this order:

- `Blocker`
- `Outside lane`
- `Follow-up`
- `Return proof`
- `Expiry`
- `State`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following:

- why the next honest step left the current surface
- where the outside work now lives
- what exact outside step remains
- what proof must exist before the blocker can change locally
- when an old outside handoff has become too stale to trust


## Relationship to nearby specs

`251-outside-action-follow-through-coverage-and-fix-claim-boundary-interface-spec.md` is the next stricter companion to this handoff contract.
This document opens and tracks the outside lane.
The follow-through spec keeps later request / execution / effect / claim coverage honest after the handoff exists.
