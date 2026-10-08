# Resilio temporary envelope-exception, burst borrow, and restitution fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish awarded room from reserved room
- arbitrate contested room and publish a winner
- distinguish activation from productive occupancy
- distinguish within-envelope use from overdraw, protected-reserve breach, and cross-claim bleed

What it still lacked was the next ordinary operator answer:

> when a winner goes out of envelope for a real urgent reason, do we treat that as simple wrongdoing, or as a typed temporary exception with expiry, reserve harm, claimant harm, and payback duty?

That is the seam this pass locks.
A product that can say `winner overdrawn` but still cannot say `temporary borrow authorized`, `temporary borrow expired`, `reserve must be repaid`, `neighbors are owed relief`, or `exception normalized into abuse` is still collapsing two very different truths into one noisy pressure story.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **temporary reprioritization and room-shaping ingredients**, but mostly as separate control surfaces rather than one operator-facing exception contract:

- `File download priority` still says higher-priority files suspend lower-priority downloads, the active prioritized queue is limited, and queue rebuilds may affect performance.
- The same article still says a global `folder_defaults.transfer_priority` can apply to existing unchanged shares and new shares, while manually changed shares stop following later global-default changes even if later reset to `None`.
- `How to pause syncing` still says pause is useful when transfer speed is low and you want to set priority for other folders by putting less-needed folders on hold.
- `Sync Preferences` still exposes Global Pause/Resume plus global send and receive rate limits and scheduler controls.
- `Running Sync on schedule` still says a paused window stops ordinary upload/download but still allows zero-sized-file sync, deletion propagation, rescanning, indexing, and some onward uploads.
- `How soon does synchronization start?` still says scheduled rescans run every 600 seconds by default and can trigger whole-file rehashing when changes are detected.
- `Some internal tasks are taking time to complete` still says hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover.
- `Performance overview` still exposes only short-window transfer, RTT, disk-load, and queue-depth evidence.

## What current Resilio still gets right

### 1) It admits that urgent work can be pushed forward temporarily

Priority raises, pauses, limits, and scheduler shaping all let operators favor some work over some other work.
That candor is worth borrowing.

### 2) It admits that the side effects of those moves are not zero

Suspension, queue rebuilds, rescans, hidden internal work, and changed transfer order all make clear that favoring one claimant can cost another.
That honesty matters.

### 3) It keeps some control layers distinct

Per-share priority, global priority defaults, global rate limits, and pause/scheduler behavior are not all described as one flat switch.
That separation is useful.

## Where current Resilio still fragments the operator answer

### A) Reprioritization exists, but exception authority does not

Current docs help an operator make one folder go first.
They still do not define one first-class answer to whether that move counts as a lawful temporary exception, who authorized it, how much extra room was borrowed, and when the exception expires.

### B) Temporary borrow and unauthorized overdraw still blur together

A winner can be pushed forward through pause, priority, rate changes, or scheduler shape.
Current docs still do not preserve one durable verdict distinguishing `authorized temporary borrow` from `plain envelope failure`.

### C) Payback and harmed-claimant repair do not begin from one object

Current docs expose the levers that can disadvantage other work.
They still do not publish one contract for what is owed after the urgent exception ends: reserve restoration, claimant restitution, renewed starvation protection, or narrowed follow-on room.

### D) Expiry exists operationally, but not as exception truth

Some controls clearly operate for a while and then change state again.
Current docs still do not preserve one explicit exception window with expiry, renewal, and denial lineage for temporary extra room.

### E) Normalization risk still lives in operator memory

Once a folder has been manually altered, it can stop following later global changes.
Current docs still do not preserve one operator-facing answer to whether an urgent exception was retired cleanly or silently became the new entitlement baseline.

## Resulting product decision

AnonSync should borrow Resilio's candor that operators really do need to favor urgent work temporarily through priority, pause, limits, and schedule shaping.
It should **not** clone a product shape where the operator still has to improvise whether a live out-of-envelope state is an authorized burst exception, an expired exception, an unpaid reserve draw, or plain unauthorized overdraw.

AnonSync should instead expose:

- one first-class **Burst borrow contract sheet**
- one **Burst authorization review**
- one **Burst borrow proof** page
- one **Burst exception timeline**
- one durable **Burst borrow lineage receipt**

## Hard decisions locked by this pass

- **unauthorized overdraw is weaker than typed temporary exception truth**
- **authorized temporary borrow, expired borrow, overdraw-without-authority, and unpaid payback stay separate**
- **reserve restoration and harmed-claimant relief must be explicit after exception use**
- **renewal, denial, throttle-back, reclaim, and reopened contention must begin from an explicit exception verdict**
- **exception receipts must preserve authority basis, borrowed amount, expiry, harmed claimants, payback state, and blocked stronger sentence**