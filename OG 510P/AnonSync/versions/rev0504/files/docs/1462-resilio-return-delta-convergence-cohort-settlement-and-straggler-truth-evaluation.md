# Resilio return-delta convergence, cohort settlement, and straggler-truth evaluation

## Why this pass exists

The archive already knew how to:

- suspend a control truthfully
- bring activity back through typed return paths
- expose changed-but-working return states as explicit parity debt
- keep owner, expiry, rereview, and claim ceiling attached to each tolerated mismatch

What it still lacked was the next ordinary operator answer:

> once many changed returns are active at the same time, how do we settle them as a group without silently promoting drift, hiding stragglers, or overclaiming that the whole baseline is back?

That is the seam this pass locks.
A real operator does not just manage one tolerated delta.
They inherit a field of them.
The product needs a first-class answer for **return-delta convergence, cohort settlement, and straggler truth**.

Current official Resilio material is useful here because it already proves that large parts of this work happen today, but mostly as repeated per-folder or per-device maneuvers:

- `Folders are duplicating with an index (i) in their name`
- `How to manually set the location of the folders synced across linked devices?`
- `Disconnecting and Removing Folders`
- `Can I connect two pre-populated pre-existing folders?`
- `Folder not empty`
- `Can I move or rename a syncing folder?`
- `User Management`
- `Running Sync in configuration mode`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Folders are duplicating with an index (i) in their name` still says that when linked devices are in Selective Sync or Synced mode, arriving folders are auto-created in the default storage location, and if a same-name folder exists Sync adds an index. The fix is a per-folder disconnect and reconnect to the right location. That is already convergence work, but handled one object at a time.
- The same article still says that choosing Disconnected mode is how operators force manual placement for future arrivals. So there is a coarse default lever, but not one settlement workspace for subjects already drifted.
- `How to manually set the location of the folders synced across linked devices?` still says custom placement requires switching the device to Disconnected mode, then using `Connect` for each arriving folder; on Android it still requires disabling Simple mode. That means cross-subject re-homing still routes through repeated local decisions rather than one cohort plan.
- `Disconnecting and Removing Folders` still says reconnect may propose a different default path, may create a new directory, and may append `(1)` if a same-name folder already exists. So convergence is not merely toggling a flag back on; it can be structural settlement.
- `Can I connect two pre-populated pre-existing folders?` still says linked-device workflows can require switching to Disconnected, then connecting a specific folder to an existing directory, with non-empty-folder confirmation. So merge-style reconciliation is still performed share by share.
- `Folder not empty` still says reconnecting or adding into an already existing directory can overwrite or delete already-present files. That means settlement waves need explicit safety fences; they are not just hygiene chores.
- `Can I move or rename a syncing folder?` still says renames are local-only and moving to another partition on Windows or Mac requires disconnect and reconnect. So some path/name debt can be retired only through structural re-entry, not through one global rename-normalize action.
- `User Management` still says disconnecting a peer suspends future updates while already-synchronized files remain. So some subjects can remain visually healthy while no longer belonging to the same future-update cohort.
- `Running Sync in configuration mode` still says configuration mode helps apply the same settings to a number of different machines. That is useful, but it is startup configuration and parameter distribution, not a first-class settlement campaign for already diverged live subjects.

So current Resilio still clearly admits serious convergence truths:

- many return-delta repairs are repeated local reconnect or placement operations
- default-mode changes can affect future arrivals without settling already drifted subjects
- some settlement steps are structural and risky rather than cosmetic
- subjects may still look healthy while not sharing the same path, mode, or future-update posture
- a broad defaulting tool can exist without answering how to settle a heterogeneous live field of debts

But those truths still do not become one operator-facing **convergence campaign / cohort settlement / straggler truth** object.

## What Resilio still gets right

### 1) It is candid that convergence often happens one subject at a time

Disconnect, reconnect, connect-to-existing-directory, and mode changes are openly described as discrete operations.
That honesty is worth borrowing.

### 2) It exposes that defaults help, but defaults are not retroactive truth

Default storage location, default synchronization mode, Android Simple mode, and config mode all show that broad levers matter.
That is useful.

### 3) It preserves real safety warnings during normalization work

`Folder not empty`, merge workflows, and `(1)` duplicate path behavior all admit that cleanup can be destructive or at least structurally meaningful.
That matters.

## Where current Resilio still fragments the operator answer

### A) There is no canonical cohort settlement object

A careful operator can manually track a list of folders and devices.
But the product still does not give one place to answer:

- which subjects belong in this settlement wave
- which ones route to exact restore versus successor promotion
- which ones are too risky and must reopen instead
- which ones are stragglers blocking the stronger sentence

### B) There is no durable truth about partial success

Current docs explain how to reconnect, repoint, merge, or change default mode.
What they do not provide is one durable answer to:

- how much of the affected cohort is actually settled
- whether the current stronger claim applies to all subjects or only a bounded subset
- whether a few drifted survivors are acceptable holdouts or a reason to keep the whole claim ceiling low

### C) There is no first-class aging model for stragglers

Current docs tell operators how to do the mechanics.
They do not tell them when unresolved survivors become the next real problem.
The product still lacks one object that can say:

- which subjects were intentionally deferred
- what keeps them deferred instead of reopened
- when the wave may honestly claim completion
- which stronger sentence remains blocked by uncovered or failed subjects

## Hard product decision unlocked by this pass

AnonSync should not let a collection of tolerated deltas dissolve into background noise.
It should promote any material multi-subject cleanup into a first-class **convergence campaign** that can separately express:

- target cohort
- intended end state per subject
- route per subject: exact restore, successor promotion, keep temporary, split out, reopen
- safety fences before destructive reconciliation steps
- settlement coverage and residual stragglers
- exact scope of any upgraded claim

That is the right next seam because it answers the operator question that always follows visible debt accumulation:

> we now have many changed-but-working states at once; how do we settle them without pretending the whole baseline is back just because most of them look close enough?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that convergence often requires repeated reconnect and placement work
- explicit admission that defaults help future arrivals more than already drifted subjects
- honesty that normalization can be risky, merge-heavy, and only partially successful

Do not clone from Resilio:

- any workflow where multi-subject settlement lives only as repeated per-folder memory work
- any contract where partial success silently rounds up to cohort success
- any product shape where unresolved stragglers do not keep the stronger sentence blocked

AnonSync should instead ship explicit pages for:

- convergence campaign contract sheet
- convergence shaping review
- convergence proof and settlement class
- convergence timeline
- convergence lineage receipt
