# Resilio promise capacity, concurrency, and overcommitment fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish forecast from commitment
- distinguish commitment from breach
- distinguish trust repair from restored authority to promise again
- keep scope caps, co-sign rules, and credibility budgets visible after degraded trust

What it still lacked was the next ordinary operator answer:

> even if an actor is once again allowed to publish promises, how many concurrent promises can that actor honestly carry, how much reserve headroom remains, what classes of work consume the same budget, and when must the next promise be deferred or narrowed to avoid overcommitment?

That is the seam this pass locks.
A product that can say `you may promise again` but still cannot say `you have capacity for one more promise` is still letting real commitment risk live in side channels and intuition.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **capacity ingredients**, but mostly as separate performance, scheduler, rate-limit, rescan, and background-work surfaces rather than one operator-facing promise-capacity contract:

- `Performance overview` still says Sync exposes 1-minute, 10-minute, and 1-hour real-time graphs, peer upload/download rates, RTT, and disk queue depth.
- `Sync Preferences` still says global sending/receiving rates can be limited, and a weekly scheduler can pause or limit speed on selected day-hour windows.
- `Running Sync on schedule` still says `Paused` stops ordinary upload/download but still allows zero-sized file sync, deletions, rescanning, and indexing, and that paused peers may still upload to non-paused peers.
- `How soon does synchronization start?` still says scheduled rescans run every 600 seconds by default and that files may be rehashed when changes are detected.
- `Some internal tasks are taking time to complete` still says Sync performs hidden background work such as block checking, deduplicating local copies, hashing, merging folder trees, scanning, reading, transferring, and writing.
- `Power user preferences` still says disk and indexing behavior can be altered through settings such as `disk_low_priority`, `disk_worker_per_job`, `worker_threads_count`, `config_save_interval`, and `config_refresh_interval`, and that settings differ across versions.

## What current Resilio still gets right

### 1) It admits that throughput is only part of the picture

Performance graphs, disk queue depth, peer RTT, scheduler lanes, and hidden preprocessing work are all real.
That honesty is worth borrowing.

### 2) It exposes several genuine throttles and contention levers

Rate limits, scheduler windows, LAN-limit overrides, disk priority, per-job disk workers, and indexing threads are real knobs.
That operational candor matters.

### 3) It admits that motion can continue under restricted windows

Paused windows still allow certain side effects and scans.
That is a useful reminder that capacity is not the same thing as `nothing happening`.

## Where current Resilio still fragments the operator answer

### A) Resource capacity is not commitment capacity

Current docs can tell an operator how busy the runtime looks.
They still do not define how much delivery or response obligation can be safely added without bluffing.

### B) Several lanes consume the same future budget, but not in one contract

Graphs, scheduler, rescans, hidden preprocessing, and queue pressure all affect real headroom.
Current docs still leave the operator to synthesize those costs manually.

### C) Pause windows and background work can mask low headroom

A system can look partially quiet or bandwidth-throttled while still consuming real future commitment budget through scans, merges, hashing, or delayed discovery.
That should not be left to folklore.

### D) There is no durable receipt for promise load posture

Current docs still do not preserve one canonical answer to what commitment load is already admitted, what reserve remains, what work classes compete for the same budget, and what stronger promise is blocked by overcommitment risk.

## Resulting product decision

AnonSync should borrow Resilio's candor that throughput, queue depth, scan cadence, hidden preprocessing, pause windows, and resource throttles all shape real capacity.
It should **not** clone a contract where the operator still has to improvise whether another promise fits by mentally combining graphs, scheduler rules, power-user knobs, and troubleshooting pages.

AnonSync should instead expose:

- one first-class **Commitment capacity contract sheet**
- one **Promise load review**
- one **Commitment capacity proof** page
- one **Promise capacity timeline**
- one durable **Commitment capacity lineage receipt**

## Hard decisions locked by this pass

- **restored promise authority is weaker than available promise capacity**
- **concurrent promise load, reserve headroom, protected capacity, and overcommitment risk stay separate**
- **background work and delayed-discovery work consume real future budget even when outward motion looks modest**
- **a new promise must be deferred, narrowed, or co-signed when it would consume protected reserve**
- **capacity receipts must preserve current admitted load, headroom class, reserve policy, blocked stronger promise, and next release trigger**
