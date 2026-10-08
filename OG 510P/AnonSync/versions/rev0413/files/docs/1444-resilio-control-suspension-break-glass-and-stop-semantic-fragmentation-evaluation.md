# Resilio control-suspension, break-glass, and stop-semantic fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- promote a guardrail from a case
- attest whether the control is still trusted
- withdraw trust when evidence decays or worlds drift

What it still lacked was one ordinary operator answer to the next harder question:

> when we intentionally suspend, narrow, or bypass a control for a while, what exactly stops, what still propagates underneath, when does it resume, and what trust sentence must be downgraded immediately?

That is the seam this pass locks.
A real operator cannot afford a vague `paused` badge.
The product needs a first-class answer for **control suspension, break-glass, and stop semantics**.

Current official Resilio material is useful here because it already proves that several `stop`-like actions are materially different:

- `How to pause syncing`
- `Sync Preferences`
- `Running Sync on schedule`
- `Disconnecting and Removing Folders`
- `Synchronization Modes`
- `Setting network interface per share`
- `Settings on mobile platforms`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `How to pause syncing` still says pause only stops bit downloads/uploads in a limited sense and still lets zero-sized files sync, deletions sync, and rescans/indexing continue. So `paused` is not the same thing as `nothing changes`.
- `Sync Preferences` still exposes a global Pause/Resume button that applies only to shares that are not already paused individually. So one stop surface already has scope interplay with another.
- `Running Sync on schedule` still treats `Paused` as a scheduler state but also says paused peers can upload to other non-paused peers, will still sync deletions, and will still rescan and index new files. So a scheduled stop has different surviving effects from what many operators would casually assume.
- `Disconnecting and Removing Folders` still distinguishes disconnect from remove, says disconnect affects one device while remove affects all linked devices, and says reconnect may propose a different default path and create a new directory. So another family of `stop` verbs is really a topology/path mutation rather than a temporary pause.
- `Synchronization Modes` still says disconnected mode moves a folder into a no-data state until connect, while `Remove from this device` in Selective Sync reverts the local copy to placeholders and `Remove from all devices` removes files from all peers and archives them there. Those are different suppression classes again.
- `Setting network interface per share` still says a forbidden network yields `Stopped. Forbidden network`, prevents peer connection for that share, and stops new or updated files from being detected. That is an environment-gated stop, not the same thing as a manual pause.
- `Settings on mobile platforms` still says disabling notifications lowers Sync's priority and may force it to stop working in the background, and still exposes mobile-data gating and battery/auto-sleep controls. So some stop-like behaviors are lane-local and system-mediated rather than chosen from the same page family as desktop pause.
- `User Management` still says disconnecting a peer revokes future updates for that peer while previously synchronized files remain. That is a relationship-level suspension rather than a local share pause.

So current Resilio still clearly admits serious suspension truths:

- `stop` is not one thing
- some stop states still allow deletions, indexing, or uploads
- some stop states are temporary and auto-reversible
- some stop states detach topology or path state and need explicit reconnect
- some stop states are lane-bound or environment-bound rather than operator-bounded
- some stop states withdraw future updates for one peer but preserve already-synced bytes

But those truths still do not become one operator-facing **suspension / break-glass / surviving-effects / resume-proof** object.

## What Resilio still gets right

### 1) It is candid that different stop verbs mean different things

Pause, scheduler pause, disconnect, remove, forbidden network, and peer disconnect are not hidden under one false label.
That distinction is worth borrowing.

### 2) It exposes surviving effects instead of pretending nothing happens

The pause and scheduler articles still say deletions and rescans survive the stop.
That honesty is useful.

### 3) It preserves re-entry and topology costs

Reconnect path drift, Android `Simple mode`, and linked-device remove semantics all show that suspension and resumption are not free.
That is worth preserving.

## Where current Resilio still fragments the operator answer

### A) There is no canonical contract for `what is still happening while this is stopped`

A careful operator can read several KB pages and infer it.
But the product still does not answer in one place:

- what propagation continues
- what detection continues
- what new work is merely deferred
- what scope is detached versus merely paused
- what sentence must be downgraded while the bypass is active

### B) Temporary bypass and durable topology change are too easy to confuse

Pause, forbidden-network stop, disconnect, remove-from-device, remove-from-all-devices, and per-peer disconnect each stop something.
But they do not belong to one typed suspension lattice, so the operator still has to remember which ones auto-resume, which ones preserve placeholders, which ones create new paths, and which ones revoke relationship state.

### C) Re-arming proof is not first-class

Current docs explain how to resume, reconnect, or re-add.
What they do not give is one explicit answer to:

- what proof shows the old control is re-armed
- whether trust is restored automatically or only after new attestation
- which stronger sentence stays blocked during the bypass window

## Hard product decision unlocked by this pass

AnonSync should not let `paused`, `stopped`, `disconnected`, `detached`, and `revoked` collapse into one badge.
It should promote every meaningful override into a first-class object that can separately express:

- requested stop effect
- surviving effects
- scope of suspension
- resume class
- auto-expiry or manual re-arm
- trust downgrade while override is active

That is the right next seam because it answers the operator question that always follows trusted controls:

> if we have to suspend this protection for a while, what exactly are we suspending, what still leaks through, and what must we prove before claiming the system is guarded again?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that stop verbs have materially different semantics
- honesty that some stop states still allow deletes, indexing, or uploads
- explicit reconnect, path, and lane/world consequences

Do not clone from Resilio:

- any contract where `paused` hides surviving propagation
- any workflow where temporary bypass and topology detachment share one vague stop story
- any product shape where the operator must reconstruct resume conditions and trust downgrade from several separate articles

AnonSync should instead ship explicit pages for:

- control suspension contract
- bypass review
- suspension proof
- stop-semantic timeline
- suspension lineage receipt
