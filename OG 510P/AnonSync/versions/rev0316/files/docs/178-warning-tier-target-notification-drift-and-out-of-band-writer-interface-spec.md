# Warning-tier target, notification drift, and out-of-band writer interface spec

## Purpose

The archive already had filesystem fidelity and degraded-target flows.
What it still lacked was one concrete steady-state interface contract for targets that are *allowed* but semantically weaker:

> when a share is bound onto NAS, SMB, network, or translation-heavy storage, what page keeps the operator aware of notification loss, locked-file risk, blocked entry classes, and out-of-band writer danger after setup day?

Current Resilio docs sharpen this seam.
They still say SMB targets may lack notifications and then rely on periodic rescans, that permissions loss can halt delivery, that locked files can linger depending on the SMB implementation, and that direct access outside Samba can damage files or roll back changes.
Separate docs still show platform-dependent symlink behavior.
That is valuable honesty.
It should become a first-class target contract, not a warning banner the operator forgets after bind.

## Core decision

Any target whose semantics are knowingly weaker than local-native fidelity must publish one persistent **warning-tier target contract**.
The operator should not have to reconstruct target risk from setup-time warnings, background logs, or platform trivia.

That contract should answer five questions at all times:

1. **What kind of target is this?**
2. **Which semantics are fully trusted, degraded, blocked, or unknown?**
3. **What runtime drift has been observed?**
4. **Which outsider behaviors can damage truth?**
5. **What reviewed actions are admissible now?**

## The target contract card

Every non-local-native mount should surface one target contract card with these rows:

- target class (`local-native`, `network-reviewed`, `warning-tier`, `blocked`)
- notification posture (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- lock posture (`ordinary`, `stale-lock-risk`, `implementation-defined`)
- out-of-band writer posture (`safe`, `unsafe`, `unknown`, `blocked`)
- blocked entry classes (`symlink`, `junction`, `xattr-full`, `special-file`, `case-risk`, etc.)
- last verified time
- drift severity

A target card is not a one-time preflight echo.
It is the steady-state public truth.

## The fixed review order

When the operator opens the card, the detail page should render sections in this order:

1. **Current semantics promised here**
2. **Observed drift since bind**
3. **Out-of-band writer and lock risk**
4. **Blocked or virtualized entry classes**
5. **Admissible next actions**
6. **Receipt shelf**

### 1) Current semantics promised here

Show explicitly whether this mount promises:

- continuous notifications or only periodic discovery
- strong rename/move observation or delayed reconciliation
- full metadata/xattr fidelity or portable subset only
- local-native special-entry handling or blocked classes
- exclusive target custody or shared-outside-writer risk

The operator should be able to answer:

> what exactly is trustworthy on this target right now?

### 2) Observed drift since bind

Show runtime drift such as:

- notification watchers exhausted or absent
- permissions narrowed
- target moved from local-native to network-reviewed
- lock behavior now stale or inconsistent
- recent rescans replacing event-driven confidence

The page should classify each drift as `watch`, `guarded`, `high`, or `blocked`.

### 3) Out-of-band writer and lock risk

This section should make outsider risk impossible to miss.
It should answer:

- can other apps or users write here through a path the daemon cannot coordinate safely?
- are there stale lock risks that can stall delivery or reconciliation?
- is this target only safe if all writes traverse one protocol boundary?

The product should never flatten `SMB works` into `all write paths are equally safe`.

### 4) Blocked or virtualized entry classes

Show classes that cannot be represented faithfully on this target:

- symlinks/junctions
- hard links
- full xattrs or streams
- special files
- case-folding hazards
- path-normalization hazards

For each, say whether the product will:

- block
- omit with receipt
- virtualize with side storage
- preserve only on other mounts

### 5) Admissible next actions

Primary actions should be explicit:

- `Keep current warning-tier contract`
- `Narrow to safer behavior`
- `Move to local-native target`
- `Acknowledge drift and continue`
- `Freeze writes pending review`
- `Retire target and rehome subject`

The product should not suggest `everything is fine` when the honest answer is `allowed, but weaker and watched`.

### 6) Receipt shelf

Every reviewed target acceptance or drift acknowledgement must emit a receipt proving:

- target class
- promised semantics
- active degradations and blocked classes
- outsider-risk acknowledgement
- drift state at time of review
- chosen action

## What must never happen automatically

The product must never automatically:

- downgrade a target from event-driven to periodic without public drift state
- imply outsider writes are safe simply because syncing still appears to work
- hide blocked entry classes behind later conflict artifacts
- treat a warning-tier target as fully local-native in summaries or receipts

## Why this is worth the trouble

A serious sync product can support weaker targets without pretending they are ordinary.
AnonSync can do better than one-time warnings by keeping warning-tier targets legible as durable contracts with visible drift and outsider-risk truth.
