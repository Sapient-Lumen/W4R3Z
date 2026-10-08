# Live repair approval page: contested-line apply boundary, survivor preservation, and overclaim barrier interface spec

## Purpose

Any contested repair that mutates the live line needs a final approval surface that answers:

> what exactly am I about to rewrite, what survivor protections are in place, and what stronger claim am I still not allowed to make afterward?

## Core decision

Every contested repair path that touches the live line must cross one first-class **Live repair approval** page.

This page owns:

- exact live mutation scope
- protected survivor set
- runtime readiness
- recipient / propagation audience
- strongest post-apply claim ceiling
- one-shot approval boundary

## Fixed page order

1. approval claim header
2. live mutation ledger
3. protected survivor ledger
4. runtime readiness card
5. approval barrier and receipt preview

### 1) Approval claim header

Show:

- contested object reference
- chosen repair path
- exact live-line effect sentence
- strongest safe sentence after success
- stronger rejected sentence after success

### 2) Live mutation ledger

Show one row per mutation target:

- in-place content replacement
- restore from archive into live path
- read-only overwrite / revert
- deletion-state restoration
- rename / name reappearance
- promotion of local survivor

Each row shows affected scope and audience.

### 3) Protected survivor ledger

Show all survivors that will remain protected after apply:

- side survivors
- archive losers
- export artifacts
- local-only extras

Also show any survivor that will cease to exist if approval proceeds.

### 4) Runtime readiness card

Show:

- runtime active / inactive verdict
- restart or reread still required
- source presence confidence
- no-source / ghost risk
- reason approval is blocked if blocked

### 5) Approval barrier and receipt preview

Show only clear verbs such as:

- `Approve live repair`
- `Back out and export first`
- `Downgrade to side-by-side restore`
- `Emit non-live inspection receipt`

Preview the receipt fields that will be written if approval succeeds.

## Rules

### Rule 1 — live repair never hides under a small row action

Any repair that mutates the live line must reopen in this dedicated barrier page.

### Rule 2 — survivor preservation stays adjacent to approve

The operator must see what is protected and what is sacrificed in the same screen as the approval control.

### Rule 3 — post-success overclaim stays visible

Even after success, the page must keep one stronger forbidden sentence visible.

## Acceptance criteria

The operator can:

- tell exactly what live mutation will occur
- tell what survivors are preserved or sacrificed
- tell whether runtime is ready
- approve only with a durable receipt preview in view
- avoid overclaiming total reconciliation after apply
