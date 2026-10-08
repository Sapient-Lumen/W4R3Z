# Local mutation on narrow seat page — suspend, overwrite, isolation, and repair interface spec

## Purpose

The effective seat posture page states the contract.
What still needs its own page is the moment that contract is exercised by a real local mutation on a narrowed seat:

> someone edited, deleted, renamed, or added bytes here — what now?

This page exists so a user does not discover the answer only from a stalled item, a restored file, or silent unsynced residue.

## Core decision

Whenever a seat with a narrowed or special posture performs a local mutation that is not ordinary read-write propagation, the product must open one first-class **Local mutation on narrow seat** page.

The page is event-shaped.
It explains one mutation against one posture.

## Fixed page order

1. **Mutation event and current posture**
2. **Propagation verdict**
3. **Local consequence**
4. **Remote / source consequence**
5. **Repair and containment options**
6. **Post-action proof**

### 1) Mutation event and current posture

Show:

- seat identity
- subject identity
- touched path(s)
- mutation class (`edit`, `rename`, `delete`, `add`, `mixed`)
- current posture basis

The operator should be able to answer: **what happened, where, and under what posture?**

### 2) Propagation verdict

Possible verdicts include:

- `will propagate normally`
- `blocked from propagating`
- `suspends sync for touched items`
- `authoritative source will overwrite`
- `local residue remains unsynced`
- `cannot yet determine until broader source returns`

The page must name the strongest reason, such as:

- read-only posture
- ciphertext-custody posture
- derived-child ceiling
- source absence
- conflict with stronger remote state

### 3) Local consequence

Show what will happen on this seat:

- edit retained
- edit reverted
- deleted file restored
- renamed file left in place while original returns
- newly added file kept as local-only residue
- touched item held in suspended state pending repair

### 4) Remote / source consequence

Show what will happen elsewhere:

- no remote mutation emitted
- remote peers still advertise earlier authoritative state
- source peers attempt restore/overwrite
- descendants remain unaffected
- uncertainty until a broader peer becomes reachable

The operator should be able to answer: **did this seat change the world, or only itself?**

### 5) Repair and containment options

Allowed actions include:

- `Restore authoritative version here`
- `Keep local residue and isolate it`
- `Promote this path through reviewed export / handoff`
- `Wait for broader source and retry`
- `Open rights review for this seat`
- `Open evidence compare before forcing a result`

The page must say which actions preserve current governance and which ones create a new artifact or side branch.

### 6) Post-action proof

The resulting record should preserve:

- posture at event time
- propagation verdict
- actual local result
- any newly created residue or branch
- repair chosen or abstained

## Public object

### `narrow_seat_mutation_review`

Fields:

- `narrow_seat_mutation_review_id`
- `seat_ref`
- `subject_ref`
- `path_refs[]`
- `mutation_class`
- `effective_posture_ref`
- `propagation_verdict`
- `local_consequence[]`
- `remote_consequence[]`
- `suggested_actions[]`
- `generated_at`

## Main surface

A compact **Local mutation on narrow seat** card should show:

- mutation class chip
- propagation verdict chip
- strongest local consequence chip
- safest next action chip

## Detailed surface

The detailed page should keep four panes.

### Pane A — Event facts

Rows:

- touched path
- event class
- event time
- posture basis

### Pane B — Consequence ladder

Rows:

- local result
- remote result
- uncertainty or dependency

### Pane C — Safe choices

Rows:

- action
- governance effect
- reversibility

### Pane D — Proof after action

Rows:

- resulting state
- residue created or cleared
- linked receipt

## CLI parity

Minimum commands:

- `anonsync narrow-seat-mutation show <event-id>`
- `anonsync narrow-seat-mutation resolve <event-id> --action <action>`
- `anonsync narrow-seat-mutation receipt <receipt-id>`

## Acceptance criteria

A user can:

- see immediately whether a local edit on a narrowed seat will propagate, suspend, revert, or remain local residue
- distinguish local-only residue from a world-changing mutation
- choose a repair or containment path without guessing from sync symptoms
- preserve a durable record of what posture governed the event
