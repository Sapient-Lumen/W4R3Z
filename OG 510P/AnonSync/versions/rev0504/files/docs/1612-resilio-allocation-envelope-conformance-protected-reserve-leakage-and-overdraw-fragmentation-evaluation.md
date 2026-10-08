# Resilio allocation-envelope conformance, protected-reserve leakage, and overdraw fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish free room from reserved room
- arbitrate contested room and publish a winner with protected-reserve and fairness truth
- distinguish award, activation, productive occupancy, idle hold, downgrade, and reclaim

What it still lacked was the next ordinary operator answer:

> after a winner activates and starts consuming room, is that winner still staying inside the room it was actually awarded, or has it drifted beyond the envelope into protected reserve or another claimant's space?

That is the seam this pass locks.
A product that can say `winner active` but still cannot say `winner stayed within the award`, `winner is leaning on tolerated edge`, `winner overran its room`, or `winner breached protected reserve` is still outsourcing a real fairness and capacity truth to dashboards, operator instinct, and post hoc blame.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **allocation-shaping and leakage ingredients**, but mostly as separate queue, rate-limit, scheduler, and hidden-work surfaces rather than one operator-facing envelope-conformance contract:

- `File download priority` still says higher-priority files suspend lower-priority downloads, that the active prioritized queue is limited, and that queue rebuilds may affect performance.
- `Folder Preferences` still says file download priority can be set in share preferences.
- `Power user preferences` still says `folder_defaults.transfer_priority` exists as a global default for shares whose priority was not altered manually.
- `Sync Preferences` still exposes global sending and receiving rate limits plus scheduler controls.
- `How to pause syncing` still says pause can be used to prioritize other folders by putting less-needed folders on hold, while deletions and rescanning/indexing still continue.
- `How soon does synchronization start?` still says scheduled rescans run every 600 seconds by default and can trigger whole-file rehashing when changes are detected.
- `Some internal tasks are taking time to complete` still says hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing may continue for a long time and may self-recover.
- `Performance overview` still exposes only short-window transfer, RTT, disk-load, and queue-depth evidence.

## What current Resilio still gets right

### 1) It admits that real work ordering and pressure shaping exist

Priority rules, per-share overrides, global defaults, global rate limits, and scheduler windows all influence what work gets room.
That candor is worth borrowing.

### 2) It admits that visible activity is not the whole story

Internal tasks, rescans, queue rebuilds, and whole-file rehashing all make it clear that live motion can hide behind deeper resource consumption.
That honesty matters.

### 3) It keeps some control layers distinct

Per-share priority, global default priority, and global send/receive rates are not described as one flat setting.
That separation is useful.

## Where current Resilio still fragments the operator answer

### A) Allocation levers exist, but award-envelope truth does not

Current docs help an operator influence what gets more room.
They still do not define one first-class answer to whether an active winner is staying inside the room it was honestly awarded.

### B) Overdraw can hide inside legitimate-looking activity

Priority, hidden work, rescans, and rehashing can all make a winner look active.
Current docs still do not preserve one durable verdict about whether that activity remains inside the award or has spilled into reserve or adjacent claimants' space.

### C) Protected reserve can be borrowed without one conformance receipt

Operators can combine pauses, limits, and priority changes to make room for urgent work.
Current docs still do not publish one object that says whether an emergency claimant stayed inside a temporary exception or silently normalized that exception into ordinary overdraw.

### D) Split winners and losing claimants do not share one leakage record

A system can have multiple legitimate claimants and different control surfaces affecting them.
Current docs still do not preserve one operator-facing record of when one winner exceeded its own envelope and thereby reintroduced starvation or unfair pressure on the others.

### E) Corrective throttling and reclaim do not begin from one conformance sentence

Current docs expose throttles, pauses, priorities, and diagnostics.
They still do not connect them to one explicit sentence such as `winner active but out of envelope` or `winner active within awarded room`.

## Resulting product decision

AnonSync should borrow Resilio's candor that priority, rate limits, scheduler windows, rescans, and hidden work all shape actual consumption pressure.
It should **not** clone a product shape where the operator still has to improvise whether a live winner is consuming only the room it honestly owns or is quietly bleeding into protected reserve and other claimants' space.

AnonSync should instead expose:

- one first-class **Allocation envelope contract sheet**
- one **Envelope conformance review**
- one **Allocation envelope proof** page
- one **Allocation envelope timeline**
- one durable **Allocation envelope lineage receipt**

## Hard decisions locked by this pass

- **activated occupancy is weaker than envelope-conforming occupancy**
- **within-envelope, edge-of-envelope, ordinary overdraw, protected-reserve breach, and cross-claim bleed stay separate**
- **temporary emergency borrow may justify a narrower exception but may not silently normalize overdraw**
- **corrective throttle, downgrade, reclaim, and reopened contention must begin from an explicit conformance verdict**
- **conformance receipts must preserve award amount, current consumption class, reserve impact, loser impact, and blocked stronger sentence**
