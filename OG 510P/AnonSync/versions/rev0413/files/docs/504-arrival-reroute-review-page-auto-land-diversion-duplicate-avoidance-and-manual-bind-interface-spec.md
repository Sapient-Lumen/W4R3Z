# Arrival reroute review page — auto-land diversion, duplicate avoidance, and manual bind interface spec

## Purpose

`502` chooses a world.
`278` handles deeper existing-bytes equivalence once a target path is under real review.
What still needs its own page is the earlier interruption move:

> the product wants to auto-land this arrival in one default world or drafted root, but I want to stop that and deliberately reroute it before duplicate branches or wrong-world binds are created.

This page makes that interruption first-class.

## Core rule

Whenever a current standing posture or reconnect draft would land an arrival somewhere other than the operator's intended continuity world, the product must offer one first-class **Arrival reroute review** page.

This page is the semantic home of:

- rejected auto-land consequence
- intended destination world
- duplicate-avoidance explanation
- manual-bind or remembered-root handoff

It must not collapse this into a quick `Disconnect`, `Connect`, or `Choose another folder` ritual with no reviewed semantics.

## Fixed review order

Every reroute review should render the same sections in the same order:

1. **Current drafted landing**
2. **Why this draft is being interrupted**
3. **Intended world and intended bind lane**
4. **Duplicate and wrong-world consequences**
5. **Next deeper review handoff**
6. **Commit and receipt**

### 1) Current drafted landing

Show:

- current world that would receive the arrival
- current drafted root/path
- whether this is standing-policy auto-land, reconnect default, or surface limitation fallback
- strongest current consequence if left unchanged

The operator must be able to answer: **what exactly would happen if I do nothing?**

### 2) Why this draft is being interrupted

Allowed interruption reasons include:

- `intended remembered root differs`
- `default root would create duplicate namespace`
- `artifact requires manual destination review`
- `ciphertext custody forbids this draft`
- `path-choice affordance must be regained first`
- `surface fallback is too coarse`

This reason must remain visible in the final receipt.

### 3) Intended world and intended bind lane

Show:

- target world after reroute
- intended lane (`manual bind`, `remembered continuity`, `fresh empty custody root`)
- whether more proof is still needed before commit
- whether another page will own equivalence, occupancy, or custody admission

### 4) Duplicate and wrong-world consequences

Render a two-column comparison:

#### Leave drafted landing unchanged

Show:

- likely auto-created root
- possible indexed-sibling or alternate-root effect
- strongest namespace or continuity risk

#### Interrupt and reroute

Show:

- preserved continuity goal
- proof still required
- whether byte movement is delayed pending deeper review

The page must make `duplicate avoidance` explicit rather than incidental.

### 5) Next deeper review handoff

Show the exact next page and why:

- `Existing bytes intake`
- `Encrypted target admission`
- `Identity successor review`
- `Manual bind target chooser`
- `Keep unplaced`

### 6) Commit and receipt

Allowed verbs:

- `Interrupt auto-land and continue`
- `Keep drafted landing`
- `Stay unplaced`
- `Export reroute receipt only`

The receipt must include:

- interrupted world and lane
- interruption reason
- intended world and lane
- next page handed off to

## States

Use a small stable vocabulary:

- `drafted auto-land`
- `drafted reconnect fallback`
- `reroute required`
- `reroute recommended`
- `keep current draft`
- `reroute committed`

## Detailed surface

### Pane A — Draft strip

Shows current drafted world, lane, and strongest consequence.

### Pane B — Interruption basis

Shows reason code, human explanation, and strongest evidence.

### Pane C — Consequence comparison

Shows `leave as drafted` vs `reroute now`.

### Pane D — Next-page handoff

Shows required deeper review and remaining proofs.

### Pane E — Receipt preview

Shows the reroute receipt skeleton.

## CLI parity

Minimum commands:

- `anonsync arrival-reroute explain <artifact-id>`
- `anonsync arrival-reroute commit <artifact-id> --world <world-id> --lane <lane>`
- `anonsync arrival-reroute keep-draft <artifact-id>`
- `anonsync arrival-reroute receipt <receipt-id>`

## Acceptance criteria

A user can:

- see what drafted landing is being interrupted
- understand whether the risk is duplicate namespace, wrong world, or custody mismatch
- compare `leave drafted` versus `reroute` honestly
- continue into deeper bind/custody review without losing interruption context
- leave behind a receipt proving why auto-land was refused or accepted
