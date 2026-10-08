# Resilio reservation-allocation activation, idle occupancy, and reclaim fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish free room from reserved room
- surface contested future room and publish a typed allocation verdict
- preserve winners, losers, protected reserve, preemption basis, and starvation guard

What it still lacked was the next ordinary operator answer:

> after a claimant wins contested room, did that winner actually activate and consume the room, or is the room now being idly held while losing claimants continue to wait?

That is the seam this pass locks.
A product that can say `winner selected` but still cannot say `winner activated, winner stalled before use, winner is consuming room, or winner lost the room back to reclaim` is still outsourcing a real operator truth to dashboards, pauses, and memory.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **activation and non-use ingredients**, but mostly as separate queue, blocker, and hidden-work surfaces rather than one operator-facing allocation-occupancy contract:

- `File download priority` still says higher-priority files suspend lower-priority downloads and that the active prioritized queue is limited.
- The same article still says queue rebuilds can affect performance and that queue order shown in the UI may still appear alphabetical rather than actual execution order.
- `Some internal tasks are taking time to complete` still says background work like checking blocks, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still says a peer may announce new or updated files that other peers later cannot actually download because the source disappeared.
- `Locked files` still says another application can block access to files and make transfer impossible.
- `Performance overview` still exposes active transfer, peer speed, RTT, disk load, and queue depth, but only through short-window graphs and troubleshooting panes.
- `How to pause syncing` still says pause can be used to prioritize other folders by putting less-needed folders on hold.

## What current Resilio still gets right

### 1) It admits that winning work may still be bottlenecked by reality

A priority setting does not magically mean immediate byte delivery.
Locked files, missing sources, and long internal tasks all make that clear.
That candor is worth borrowing.

### 2) It admits that visible queue order and actual execution can diverge

The docs are candid that the queue can appear alphabetical even when priority rules control real execution.
That is exactly the kind of truth an allocation-activation surface must preserve.

### 3) It exposes blocker classes that are not the same thing as inactivity

No-source-peer, locked-file, and internal-task cases are materially different.
That distinction matters.

## Where current Resilio still fragments the operator answer

### A) Winning priority does not compile into one activation verdict

Current docs help an operator influence ordering.
They still do not define one first-class answer to whether the winning claimant actually activated and started consuming the awarded room.

### B) Busy-looking work can still be zero net occupancy

Internal tasks, queue rebuild, scanning, and retries can make the system look alive.
Current docs still do not preserve one durable occupancy verdict that says whether awarded room is being meaningfully consumed.

### C) Idle winners and blocked losers do not share one fairness receipt

A higher-priority claimant can suspend lower-priority downloads.
Current docs still do not publish one operator-facing object that says when a winner has gone idle long enough that losing claimants deserve reclaim or re-arbitration.

### D) Blocked activation does not become one typed reclaim basis

Locked files and no-source-peer states are described candidly.
Current docs still do not connect them to one explicit contract about when an awarded slot stays protected, when it downgrades, and when it is reclaimed.

### E) There is no durable record of idle occupancy debt

An operator can infer that awarded room is not being productively used.
Current docs still do not preserve the activation window, idle age, reclaim trigger, or stronger blocked sentence that remained unavailable while the winner sat on room.

## Resulting product decision

AnonSync should borrow Resilio's candor that priority, hidden work, source disappearance, and lock blockers are all real reasons a winner may fail to consume awarded room.
It should **not** clone a product shape where the operator still has to improvise whether a winner has activated, stalled before use, drifted into idle occupancy, or should lose the room back to reclaim.

AnonSync should instead expose:

- one first-class **Reservation activation contract sheet**
- one **Allocation activation review**
- one **Reservation occupancy proof** page
- one **Allocation occupancy timeline**
- one durable **Allocation occupancy lineage receipt**

## Hard decisions locked by this pass

- **allocation verdict is weaker than activated occupancy**
- **allocated-not-started, activated-consuming, activated-no-net-progress, idle-held, downgraded, and reclaimed stay separate**
- **losing-claimant starvation resumes when a winner fails its activation window**
- **emergency or reserve-borrow winners need stricter activation and reclaim rules than ordinary winners**
- **reclaim must be a first-class verdict event rather than a silent timeout**
