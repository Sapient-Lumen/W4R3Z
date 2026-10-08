# Resilio promise reservation, soft hold, and expiry fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish restored promise authority from actual room to promise
- distinguish admitted load from protected reserve and overcommitment risk
- keep hidden work, discovery lag, and scheduler windows visible as real capacity ingredients

What it still lacked was the next ordinary operator answer:

> even if honest headroom still exists, is that room really free, already softly held, hard-reserved for another near-future promise, partially blocked by protected reserve, or only apparently free because stale tentative claims were never modeled?

That is the seam this pass locks.
A product that can say `there is headroom` but still cannot say `who already has a hold on that headroom and when it expires` is still letting real planning truth live in chats, memory, and side spreadsheets.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **future-room ingredients**, but mostly as separate scheduler, pause, throughput, queue, and hidden-work surfaces rather than one operator-facing reservation contract:

- `Sync Preferences` still says global sending and receiving rates can be limited, exposes a weekly scheduler, and gives a Global Pause/Resume button that only affects shares not paused individually.
- `Running Sync on schedule` still says a `Paused` rule sets upload and download speed to zero for ordinary transfer, but still allows zero-sized-file sync, deletion propagation, rescanning, indexing, and uploads from paused peers to non-paused peers.
- `How to pause syncing` still says ordinary pause leaves deletions and rescanning/indexing alive and that Global Pause excludes shares already paused individually.
- `Performance overview` still says operators only get short real-time graphs — 1 minute, 10 minutes, and 1 hour — plus per-peer speed, RTT, disk load, and queue depth.
- `How soon does synchronization start?` still says scheduled rescans run every 600 seconds and on start unless the interval is changed or set to zero.
- `Some internal tasks are taking time to complete` still says Sync may spend time on block checking, dedup copy, hashing, merging folder trees, scanning, reading, transferring, and writing, and that this can self-recover without obvious visible delivery.

## What current Resilio still gets right

### 1) It admits that future room is distorted by more than visible transfer speed

Queue depth, short-window performance graphs, rescans, pause semantics, and hidden background work are all real ingredients.
That honesty is worth borrowing.

### 2) It exposes several meaningful load-shaping controls

Rate limits, scheduler windows, pause controls, rescan cadence, and power-user knobs are genuine levers.
That candor matters.

### 3) It admits that `paused` and `quiet` are not the same thing as `nothing is consuming room`

Paused windows still propagate deletions, rescan, and index.
Hidden work still consumes time and resources.
That is exactly the kind of nuance a serious reservation object needs.

## Where current Resilio still fragments the operator answer

### A) Capacity is shown, but room ownership is not

Current docs can help an operator decide that the runtime is busy, calm, or throttled.
They still do not define whether future room is already held for a not-yet-issued commitment.

### B) Soft holds and protected reserve do not exist as first-class truths

Resilio exposes the mechanics that affect room, but not the doctrine for reserving that room before a final public promise exists.
Without that, tentative future work remains folklore.

### C) Pause and scheduler lanes can create misleadingly free-looking windows

A lane can look throttled or paused while still consuming real future room via rescans, merges, queue accumulation, or deletion propagation.
That makes `looks quiet` a poor substitute for reservation truth.

### D) Stale holds have no canonical expiry story

Current docs do not preserve one operator-facing object that says who opened a hold, when it expires, what releases it, and when it becomes a ghost reservation that should be reclaimed.

### E) There is no durable receipt for blocked stronger promises caused by reservation

An operator can infer that future room is spoken for.
Current docs still do not preserve the exact stronger promise that remained blocked because the room was held elsewhere.

## Resulting product decision

AnonSync should borrow Resilio's candor that short-window graphs, scheduler windows, pause semantics, rescans, and hidden work all shape real future room.
It should **not** clone a product shape where the operator still has to improvise whether the next promise slot is genuinely free, softly held, hard-reserved, or already stale.

AnonSync should instead expose:

- one first-class **Promise reservation contract sheet**
- one **Reservation shaping review**
- one **Promise reservation proof** page
- one **Promise reservation timeline**
- one durable **Promise reservation lineage receipt**

## Hard decisions locked by this pass

- **available capacity is weaker than explicit reservation truth**
- **soft hold, hard reservation, provisional option, protected reserve, released hold, and expired hold stay separate**
- **ghost reservations must remain visible risk instead of silent capacity theft**
- **future room can be spoken for before a final promise exists, but only through a named owner, expiry, release trigger, and reserve boundary**
- **reservation receipts must preserve hold owner, reserved scope, expiry basis, release trigger, blocked stronger sentence, and reclaim rule**
