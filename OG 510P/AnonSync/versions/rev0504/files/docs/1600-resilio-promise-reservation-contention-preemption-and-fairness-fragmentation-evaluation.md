# Resilio promise-reservation contention, preemption, and fairness fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish available promise capacity from genuinely reserved future room
- keep soft holds, hard reservations, protected reserve, provisional options, and expired holds separate
- expose ghost reservations and stale holds as visible risk instead of silent capacity theft

What it still lacked was the next ordinary operator answer:

> when several valid-looking claimants all want the same future room, who wins, who is split, who is preempted, which reserve stays protected, and what fairness rule prevents invisible starvation?

That is the seam this pass locks.
A product that can say `this room is held` but still cannot say `which hold prevails when the room is oversubscribed` is still leaving real allocation truth in chat threads, side spreadsheets, and operator memory.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **priority and contention ingredients**, but mostly as separate queue, pause, scheduler, and override surfaces rather than one operator-facing reservation-arbitration contract:

- `File download priority` still says download priority can be set per share or through the global power-user default, that higher-priority files suspend lower-priority downloads, that the active prioritized queue is limited, and that queue rebuilds can affect performance.
- The same article still says a share manually assigned its own priority is no longer affected by later changes to the global default, even if the share is manually set back to `None`.
- `How to pause syncing` still says pause can be used to set priority for other folders by putting less-needed folders on hold.
- `Sync Preferences` still exposes global send/receive limits, a scheduler, and a Global Pause/Resume control that excludes shares already paused individually.
- `Running Sync on schedule` still says paused windows stop ordinary upload/download but still allow zero-sized-file sync, deletions, rescanning, indexing, and some onward uploads.
- `Power user preferences` still exposes a global `folder_defaults.transfer_priority` default whose effect depends on whether a share kept or broke inheritance.

## What current Resilio still gets right

### 1) It admits that competing work really can be reordered

Higher-priority files can suspend lower-priority downloads.
Pause can be used to make room for something else.
That operational candor is worth borrowing.

### 2) It exposes multiple control layers that can compete

Per-share settings, global defaults, pause controls, scheduler rules, and global rate limits are all real allocation ingredients.
That honesty matters.

### 3) It admits that visible order and actual execution order can diverge

The queue may still appear alphabetical in the UI even when priority rules are controlling actual work.
That is exactly the sort of truth a real arbitration surface must preserve.

## Where current Resilio still fragments the operator answer

### A) Priority ingredients exist, but claimant arbitration does not

Current docs can help an operator influence ordering.
They still do not define one first-class answer to who should win when several legitimate future claims collide.

### B) Override breaks inheritance without becoming one allocation verdict

A share can detach from the global default and stay detached even after being set back to `None`.
That is useful candor, but still not a durable arbitration story.

### C) Pause can act like ad hoc preemption without a fairness receipt

Operators can pause some work to favor other work.
Current docs still do not preserve one object that says whether that was emergency preemption, ordinary reprioritization, or protected-reserve enforcement.

### D) Protected reserve and starvation guard are still implicit

Current docs expose the levers that create winners and losers.
They still do not publish one operator-facing rule for what may never be preempted, how long a claimant may wait, or when a long-held claimant must be escalated.

### E) There is no durable receipt for blocked claimants

An operator can infer that one hold lost to another.
Current docs still do not preserve the exact losing claimant, the preemption basis, or the stronger blocked sentence that remained unavailable because a different claimant won.

## Resulting product decision

AnonSync should borrow Resilio's candor that queues, pause controls, scheduler lanes, global defaults, and per-share overrides all shape real work ordering.
It should **not** clone a product shape where the operator still has to improvise which future claim wins when the same headroom is contested.

AnonSync should instead expose:

- one first-class **Reservation contention contract sheet**
- one **Contention arbitration review**
- one **Reservation verdict proof** page
- one **Reservation contention timeline**
- one durable **Reservation contention lineage receipt**

## Hard decisions locked by this pass

- **reservation truth is weaker than reservation-allocation truth under contention**
- **winning claimant, protected reserve, split allocation, defer, deny, and preempted claimant stay separate**
- **manual override and emergency pause are not allowed to masquerade as allocation doctrine**
- **starvation guard and protected-reserve rules must stay explicit whenever one claimant loses room to another**
- **contention receipts must preserve claimant set, winning basis, preemption class, reserve boundary, and blocked stronger sentence**
