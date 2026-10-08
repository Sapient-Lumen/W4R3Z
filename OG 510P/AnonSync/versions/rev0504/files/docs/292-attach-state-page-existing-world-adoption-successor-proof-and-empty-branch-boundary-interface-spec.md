# Attach-state page — existing world adoption, successor proof, and empty-branch boundary interface spec

## Purpose

The archive already has state-root doctrine and service-promotion language.
What it still lacked was one explicit review page for the high-signal moment when the operator or runtime encounters existing local state and must decide:

> is this the same world I meant to continue, a reviewed successor import, a stale backup, a clean new branch, or a clone-risk copy that must not simply be opened as if nothing happened?

This page exists so attach/import decisions become reviewed continuity boundaries instead of accidental consequences of path choice.

## Core rule

Attaching existing local state is not the same as creating new empty state.
It is also not the same as importing a reviewed successor or opening a concurrent clone.
The product must classify one candidate root into one of these families:

1. `same-world attach`
2. `reviewed successor import`
3. `stale backup / snapshot restore`
4. `clean empty branch`
5. `clone-risk concurrent world`
6. `foreign / unknown world`

The operator may choose among them.
The runtime may not silently guess.

## Fixed review order

Every serious attach-state page should render the same sections in the same order:

1. **Candidate world and source**
2. **Continuity classification**
3. **Consequences of attach vs clean branch**
4. **Blocked choices and safer alternatives**
5. **Receipt and rollback promise**

### 1) Candidate world and source

This section should answer:

- candidate path
- candidate world ID if readable
- how the candidate was found (`operator-chosen`, `startup-discovery`, `service-profile default`, `import bundle`, `backup restore`, etc.)
- strongest available host/provenance evidence

The operator must be able to answer: **what exact world am I being asked to attach, and where did it come from?**

### 2) Continuity classification

This section should classify the candidate as one of the supported families and explain why:

- same-world attach
- reviewed successor import
- stale backup / snapshot restore
- clean empty branch
- clone-risk concurrent world
- foreign / unknown world

The operator must be able to answer: **what continuity claim would I be making if I proceed?**

### 3) Consequences of attach vs clean branch

This section should show:

- what inventory appears after attach
- whether trust/identity continuity is preserved, degraded, or broken
- whether the apparently empty alternative is truly clean or simply the wrong default root
- whether attach would override an existing active world
- whether later reconcile / reconnect work would still be required

The operator must be able to answer: **what world will I actually be living in after this choice?**

### 4) Blocked choices and safer alternatives

This section should show:

- attach blocked because of clone-risk
- import blocked because provenance is insufficient
- clean branch blocked because operator clearly expected continuity
- safer alternatives such as inspect-only, export snapshot, open compare, or stage successor import

The operator must be able to answer: **which choices are safe, and why are the unsafe ones blocked?**

### 5) Receipt and rollback promise

This section should show:

- attach/import/branch receipt that will be emitted
- pre-attach snapshot or compare evidence
- rollback confidence
- any follow-up obligations such as reconnect review or stale-backup quarantine

The operator must be able to answer: **what proof and rollback posture do I get if I commit this attach decision?**

## States

Use a small stable vocabulary:

- `same-world attach ready`
- `successor import review required`
- `stale backup quarantine`
- `clean branch intentional`
- `clone-risk blocked`
- `foreign world inspect only`

## Main surface

A compact **Attach state** card should show:

- candidate world/path
- continuity classification
- strongest risk finding
- primary action: `Review attach state`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Candidate strip

Shows:

- candidate path
- candidate world ID
- discovery source
- primary verdict

### Pane B — Continuity proof

Columns:

- evidence class
- result
- confidence
- contradiction / gap

### Pane C — Choice consequences

Columns:

- choice (`attach`, `import successor`, `start clean`, `inspect only`)
- resulting world
- continuity claim
- inventory outcome
- follow-up required

### Pane D — Blocks and alternatives

Rows may include:

- `blocked by clone-risk`
- `blocked by foreign-world ambiguity`
- `safe inspect only`
- `export snapshot first`
- `open compare before successor import`

### Pane E — Receipts

Shows:

- attach receipts
- import receipts
- clean-branch acknowledgments
- rollback plans
- stale-backup quarantine acknowledgments

## CLI parity

Minimum commands:

- `anonsync state-root attach review --path <path>`
- `anonsync state-root attach apply <review-id>`
- `anonsync state-root import review --bundle <bundle>`
- `anonsync state-root branch create --reason <text>`
- `anonsync state-root attach receipt <receipt-id>`

## Acceptance criteria

A user can:

- distinguish same-world attach from successor import, stale backup, clean branch, and clone-risk copy
- see when an apparently empty world is likely just the wrong root
- preview continuity and inventory consequences before commit
- avoid accidentally opening concurrent clone state
- prove later which continuity claim was accepted and with what evidence

