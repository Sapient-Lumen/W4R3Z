# Pro-function loss page — capability floor, live impact, and recovery ladder interface spec

## Purpose

The archive already had a generic entitlement-expiry review.
What it still lacked was one ordinary page for the simpler runtime question:

> this seat just lost higher-tier behavior — what exactly stopped, what still exists, and what is the correct recovery path from here?

Current official Resilio docs make this seam concrete.
They still describe seats reverting to Free, owner-expiry propagating to shared seats, local shares ceasing to sync after license loss, and some server-mismatch situations where a key appears present but sharing and linking stop.
That is useful truth.
It should not remain an error-article scavenger hunt.

## Core decision

AnonSync must expose one first-class **Pro-function loss** page whenever a seat's effective capability floor narrows because of expiry, revocation, owner replacement, seat reclamation, host-role mismatch, or version-family conflict.

The page exists to answer five things in one place:

1. what was lost and when
2. which capabilities narrowed or stopped
3. which live subjects are now impacted
4. what recovery ladder is actually valid
5. what the safe degraded floor is if recovery is not chosen

## Fixed page order

1. **Loss verdict**
2. **Capability delta**
3. **Live subject impact**
4. **Recovery ladder**
5. **Safe degraded-floor actions**

### 1) Loss verdict

Show:

- `pro_function_loss_page_id`
- seat in scope
- current `loss_verdict` (`no-loss`, `reverted-to-lower-floor`, `shared-seat-lost`, `owner-expired`, `host-mismatch-narrowed`, `conflicted`, `unknown`)
- strongest honest summary
- effective time or first observed time

The operator must be able to answer:

> what exact higher-tier behavior did this seat lose?

### 2) Capability delta

Show capability rows with before/after state for, at minimum:

- advanced-governance actions
- identity-linked conveniences
- local edges / local shares
- subject classes gated by higher tier
- current surface affordances that narrowed or disappeared

Each row must classify the change as `gone`, `frozen`, `degraded`, or `unchanged`.

### 3) Live subject impact

Show:

- affected active subjects
- whether bytes remain on disk
- whether sync has stopped, narrowed, or only lost governance controls
- whether any dependent local edges are now inactive
- whether other seats are indirectly impacted by the same owner or shared-seat event

The operator must be able to answer:

> what real work is now blocked or drifting because of this loss?

### 4) Recovery ladder

Show the valid recovery paths in order of honesty, for example:

- re-apply correct local key
- restore owner entitlement
- request seat re-share
- move to supported host / usage claim
- cut over to supported line or seat family
- accept lower capability floor

The page must distinguish immediate repair from recreation, cutover, or policy correction.

### 5) Safe degraded-floor actions

If recovery is not chosen, actions may include:

- `Freeze and keep bytes`
- `Detach dependent local edge`
- `Open capability availability`
- `Export continuity receipt`
- `Accept lower floor`

These actions must never imply that higher-tier behavior silently continues.

## Public object

### Pro-function loss page

Fields:

- `pro_function_loss_page_id`
- `seat_ref`
- `loss_verdict`
- `capability_delta_rows[]`
- `affected_subject_refs[]`
- `recovery_ladder[]`
- `safe_degraded_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. seat
2. loss verdict
3. strongest live impact
4. first valid recovery step
5. safest degraded-floor action

Example:

```text
backup-node-04     shared-seat-lost     local edge inactive, governance narrowed     Request seat re-share     Freeze and keep bytes
```

## Non-goals

This page does **not** replace generic billing history or full release-line migration planning.
It proves only **what higher-tier behavior this seat lost, what still survives, and how recovery honestly works from here**.
