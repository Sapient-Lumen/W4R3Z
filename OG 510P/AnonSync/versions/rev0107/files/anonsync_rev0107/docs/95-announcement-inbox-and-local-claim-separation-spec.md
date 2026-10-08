# Announcement inbox and local-claim separation spec

## Purpose

The archive already says that visibility, path binding, and materialization are different facts.
What still remained too easy to blur was the first mile of that model:

- a share becomes visible to this machine
- this machine decides whether to care yet
- this machine chooses a local path and role
- this machine actually claims the share into local state

Resilio's linked-device model still bundles those steps too tightly.
Its current docs still say linked devices make all folders automatically available, disconnected items are still visible and removable across the linked set, custom placement still commonly routes through `Disconnected` and `Connect`, and default-location behavior can still create `(1)` duplicate directories when a name collides.
That is convenient, but it proves the surface still treats **announcement**, **local claim**, and **path creation** as near-neighbors when AnonSync should treat them as separate public acts.

This document fixes that gap.

## Core decision

A share announcement is not a local claim.

A local claim is not a path bind.

A path bind is not materialization.

The interface should therefore preserve four distinct verbs:

1. `See`
2. `Claim`
3. `Bind`
4. `Materialize`

Any product surface that compresses those back into one generic `Connect`, `Add`, or `Remove` verb has already started to recreate the Resilio seam we are explicitly rejecting.

## Canonical state line

Every announced share on a device should be classifiable along one stable local line:

1. **Announced only** — the share is visible to this machine, but no local claim exists yet
2. **Deferred locally** — the machine explicitly keeps the share visible without path/bind commitment
3. **Claim in review** — a claim object exists, but compare/preflight/review is still incomplete
4. **Claimed and bound** — this machine has accepted the share into a specific local path and role
5. **Hidden on this machine** — the announcement is suppressed only for this machine
6. **Retracted from source domain** — visibility itself was withdrawn by authority or source policy, not merely hidden locally

The product must not pretend states 5 and 6 are the same.
`Hide here` and `Withdraw from constellation` are materially different outcomes.

## Incoming-inbox contract

An incoming-announcement inbox exists so visible shares can be triaged without creating ambient path side effects.

Every inbox row should answer, in one stable order:

1. **Subject** — share label or source subject
2. **Origin** — who or what made it visible here
3. **Local claim posture** — announced only, deferred, under review, claimed, or hidden here
4. **Next honest action** — review, choose path, claim now, keep deferred, or hide here
5. **Review / overflow** — secondary actions and local-vs-domain scope details

### Example rows

```text
WorkDocs          Linked from Studio-Laptop   Announced only          Choose path   Review
Archive-Mirror    Recovery bundle             Claim in review         Continue review Review
TravelMedia       Constellation default       Deferred on this machine Claim later    Review
Cameras-2026      Shared by Maya              Hidden on this machine  Re-show locally Review
```

The important part is that the row says **what happened locally**.
It must not imply a path, placeholder tree, or authority widening merely because the share became visible.

## Review-pane contract

When the operator opens an incoming item or a claim derived from it, the review pane should preserve one fixed section order:

1. **Subject and origin**
2. **Requested local outcome**
3. **Path and bind choice**
4. **Authority and visibility consequences**
5. **Local-only versus domain-wide effects**
6. **Receipt promise**

### 1) Subject and origin

This section should say:

- exact share or offer subject
- which device, contact, recovery artifact, or policy made it visible
- whether visibility arrived through manual share, linked policy, recovery continuity, or bounded introduction

### 2) Requested local outcome

This section should say:

- whether the operator is only deferring visibility, creating a claim, or actually binding locally
- requested local role and materialization posture
- whether this machine will become observer, cache, full replica, or some narrower role

### 3) Path and bind choice

This section should say:

- whether a path is required now
- whether a remembered path suggestion exists and why
- whether compare, custody, or reconciliation review is mandatory before bind
- whether the claim may remain pathless for now without lying about the local outcome

### 4) Authority and visibility consequences

This section should say:

- whether the action changes only this machine or widens grants/authority/defaults
- whether the share merely remains visible, becomes locally mounted, or changes future visibility defaults
- whether any approval or constellation rule is being reused

### 5) Local-only versus domain-wide effects

This section should say:

- whether `hide`, `reject`, `defer`, or `remove` is local only
- whether any action would retract visibility for sibling linked devices
- whether the operator is acting as authority for the domain or only as the local machine steward

### 6) Receipt promise

This section should say:

- which receipt proves the outcome
- whether the receipt proves local hide, local defer, claim creation, or full local adoption
- which follow-up reviews remain open

## Allowed verbs

### Good primary verbs

- `Choose path`
- `Claim now`
- `Continue review`
- `Keep deferred`
- `Hide on this machine`
- `Withdraw from constellation`
- `Reject offer`

### Dangerous ambiguous verbs

- `Connect`
- `Add`
- `Remove`
- `Accept`
- `Hide` without scope
- `Available everywhere`

The archive does not ban those words in explanatory prose.
It bans them as the primary operator contract when they blur local claim, path binding, or wider visibility effects.

## Local hide versus domain withdraw

This is one of the most important distinctions in the document.

### `Hide on this machine`

Means:

- keep the share out of ordinary local inbox/navigation on this machine
- do not retract the share from sibling devices
- do not mutate source authority or constellation defaults
- preserve a durable local receipt so the operator can later answer why this machine is not showing the announcement

### `Withdraw from constellation`

Means:

- authority is retracting future visibility for a wider scope
- sibling devices may lose visibility too
- later receipts must prove the wider scope, not merely local presentation change

The product must never reuse the same `Remove` verb for both actions.

## Batch rules

An incoming-announcement inbox may support batch work, but only if the labels stay truthful.

### Acceptable labels

- `Hide 12 on this machine`
- `Claim 4 reviewed shares`
- `Continue review for 3 compares`
- `Withdraw 2 from constellation`

### Unacceptable labels

- `Connect selected`
- `Remove 18`
- `Apply to all visible shares`

The batch bar must separate local-only actions from authority-widening or authority-withdrawing actions before it speaks.

## Remembered defaults

The product may remember safe defaults such as:

- likely mount root
- preferred local role
- preferred initial materialization posture

But remembered defaults must not silently create a local claim.

A remembered default may prefill the review.
It may not skip the distinction between:

- `visible here`
- `claimed here`
- `bound here`

## Dense and mobile rules

A dense row or mobile card may compress the explanation, but it must still preserve three separate cues:

1. how the share became visible here
2. whether this machine has claimed it yet
3. what the next honest action is

### Allowed collapsed card

```text
Linked default · Not yet claimed here · Choose path
```

### Disallowed collapsed card

```text
Available on this device
```

The disallowed card hides both the claim state and the action boundary.

## CLI and API parity

CLI, TUI, local web, and API-backed automation should all be able to render the same distinctions:

- visible here without local bind
- deferred here without local bind
- hidden here only
- withdrawn by wider authority
- compare required before bind
- claim ready versus claim applied

No surface should have to guess whether `defer` merely hides a row or whether it preserves a pathless visible state.
No surface should have to infer whether `remove` means local hide or domain retract from historical side effects.

## Why this matters

Resilio still proves that a linked-device mesh and selective sync can feel convenient.
But its current docs also still show the costs of convenience when share visibility, local acceptance, path choice, and local path creation live too close together:

- all linked folders become visible across the linked set
- disconnected items remain common linked-set objects
- removing a disconnected item can remove it from all linked devices
- custom location often depends on first forcing `Disconnected`
- default-location behavior can create duplicate-index directories when names collide

AnonSync should not clone that arrival shape.
The product should let a share be visible without path side effects, let a machine defer or hide locally without pretending authority changed, and let final path bind happen only after the review grammar made those consequences explicit.
