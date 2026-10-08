# Resilio restoration-creditor waterfall, partial-relief, and probation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- open a burst-debt object once a temporary exception ended or aged
- distinguish settled, overdue, restructured, forgiven, and still-open debt
- embargo new burst requests while open debt survived
- refuse to call a claimant fully restored before reserve and harmed neighbors were actually repaired

What it still lacked was the next hard operator answer when **full repair cannot happen in one step**:

> if restoration room is scarce, who gets repaired first, what partial relief counts, what remains blocked, and what future-burst probation survives while some creditors are still waiting?

That is the seam this pass locks.
A product that can say `burst debt exists` and `good standing not yet restored` but still cannot say `reserve tier cleared first`, `named harmed claimants are only partially relieved`, `cohort relief is still open`, or `future bursts remain manual-only through probation` is still leaving the decisive fairness answer in operator folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **post-burst shaping and after-the-fact evidence ingredients**, but not one operator-facing creditor-waterfall contract:

- `File download priority` still says higher-priority files suspend lower-priority downloads, only active files in the queue are prioritized up to a limit, and manually altered shares stop following later global priority changes even if later set back to `None`.
- `How to pause syncing` still says pause can be used to prioritize other folders by putting less-needed folders on hold, while zero-sized files, deletions, rescans, and indexing still continue.
- `Sync Preferences` still exposes global send/receive limits, scheduler controls, and Global Pause/Resume.
- `Running Sync on schedule` still says paused windows stop ordinary download but can still allow onward upload, deletion propagation, rescanning, and indexing.
- `How soon does synchronization start?` and `Power user preferences` still say rescans are a recurring background mechanism, with `folder_rescan_interval` defaulting to 600 seconds and several disk/indexing knobs continuing to shape contention.
- `Some internal tasks are taking time to complete` still says hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can keep consuming resources and can recover on their own.
- `Performance overview` still exposes only real-time 1 minute, 10 minute, and 1 hour graphs plus peer speeds, RTT, disk load, and queue depth.
- `Sync Main View (Desktop)` still says History shows general syncing activity for the last 30 days.
- `Using Archive for file versioning and restoring deleted files` still says restore is manual and that Archive itself does not provide details on which peer made changes to a file.

## What current Resilio still gets right

### 1) It admits that favoritism and recovery happen over time, not in one instant

Priority changes, pauses, scheduler rules, rescans, hidden work, history, and archive all preserve parts of the afterlife.
That is useful candor.

### 2) It gives operators real tools to shape relief indirectly

Global limits, per-share priorities, scheduler cells, rescans, and archive/history surfaces are all operationally useful.
Those ingredients are worth borrowing.

### 3) It does not pretend all aftermath evidence lives on one surface

Runtime shaping, event history, and archive residue are separate planes.
That separation is honest.

## Where current Resilio still fragments the operator answer

### A) Partial repair exists in practice, but not as a first-class object

Current docs let an operator infer that some harmed folders or peers may be relieved before others.
They still do not preserve one typed answer to which creditor tier was paid first, how much relief each tier already received, and which stronger restoration sentence remains blocked while later tiers are still open.

### B) Available evidence is not durable enough for a real creditor-waterfall verdict

History is described only as general syncing activity for the last 30 days, while Archive says restore is manual and Archive itself does not identify which peer made the change.
That is useful evidence, but it is not a durable multi-creditor restoration ledger.

### C) Reserve-first, named-neighbor-first, and pro-rata cohort relief still blur together

Current docs expose shaping controls and after-the-fact traces.
They still do not publish one contract saying whether the product restores protected reserve first, pays named harmed claimants next, or distributes later relief pro rata inside a broader cohort.

### D) Probation after partial repair is not a first-class truth

A claimant can be calmer, less favored, or manually watched.
Current docs still do not preserve one typed probation window saying `ordinary activity resumed, but future burst requests remain manual-only until the remaining creditor ladder clears or ages out under policy`.

### E) Manual detachment and recurring rescans can recreate the same debt pattern without one durable waterfall receipt

Because a share can detach from global priority inheritance and because rescans, hidden work, and rate shaping keep affecting who advances first, a repeated exception pattern can recur.
Current docs still do not make that recurrence compile into one visible creditor-order and probation receipt.

## Resulting product decision

AnonSync should borrow Resilio's shaping controls, runtime candor, and some of its aftermath evidence surfaces.
It should **not** clone a product shape where the operator still has to infer from priority, pause, scheduler, history, archive, rescans, hidden work, and short-window graphs which creditors were restored first, which tiers remain open, and whether future bursts remain blocked or only manual-only under probation.

AnonSync should instead expose:

- one first-class **Restoration waterfall contract sheet**
- one **Creditor waterfall review**
- one **Partial restoration proof** page
- one **Restoration waterfall timeline**
- one durable **Restoration waterfall lineage receipt**

## Hard decisions locked by this pass

- **partial restoration is weaker than restoration-ready**
- **default creditor order is protected reserve first, then explicitly harmed named claimants, then broader promise-cohort or system-headroom creditors**
- **pro-rata distribution is allowed inside one creditor tier, not across tiers, unless typed waiver authority says otherwise**
- **any uncleared higher-priority creditor tier blocks clean restoration and keeps future bursts blocked or manual-only under probation**
- **waiver, carry-forward, or narrowed-future-award conversion must name who absorbs the residue and what probation survives**
- **restoration receipts must preserve tier order, slice history, remaining residue, probation posture, and blocked stronger sentence**
