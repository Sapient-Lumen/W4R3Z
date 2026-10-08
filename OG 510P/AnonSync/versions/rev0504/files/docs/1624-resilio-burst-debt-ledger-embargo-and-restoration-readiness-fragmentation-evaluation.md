# Resilio burst-debt ledger, embargo, and restoration-readiness fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish ordinary award from temporary burst borrow
- record who authorized the exception, how much extra room was borrowed, when it expired, and what payback class was owed
- keep authorized burst, expired burst, unauthorized overdraw, and payback-open states separate

What it still lacked was the next operator answer after the burst ends or begins to age:

> is the claimant back in good standing, still carrying unpaid burst debt, under a no-new-borrow embargo, or only conditionally restored under a narrower future envelope?

That is the seam this pass locks.
A product that can say `burst exception existed` and `payback is open` but still cannot say `new burst blocked until debt is retired`, `ordinary entitlement not yet restored`, `payback restructured`, or `debt forgiven by typed authority` is still leaving the hardest anti-normalization truth in operator memory.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **post-burst shaping and consequence ingredients**, but not one operator-facing debt-and-restoration contract:

- `File download priority` still says higher-priority files suspend lower-priority downloads, active prioritized queues are capped, and manually altered shares stop following later global priority changes even if later set back to `None`.
- `How to pause syncing` still says pause is useful when transfer speed is low and you want to prioritize other folders by putting less-needed folders on hold, while zero-sized files, deletions, rescans, and indexing still proceed.
- `Sync Preferences` still exposes global pause and global send/receive rate limits plus scheduler controls.
- `Running Sync on schedule` still says paused windows stop ordinary download but can still permit some onward upload, deletion propagation, rescanning, and indexing.
- `How soon does synchronization start?` still says periodic rescans remain a standing source of background work and can be disabled or manually triggered through power-user settings.
- `Some internal tasks are taking time to complete` still says hidden work like checking file blocks, dedup copy, hashing, merging, scanning, reading, transferring, and writing can keep consuming resources for a while.
- `Performance overview` still exposes only short-window charts and current queue/load metrics rather than a durable answer about who is still owed relief after an urgent exception.
- `Power user preferences` still exposes global defaults, rescan cadence, per-job disk threading, parallel indexing, and other contention-shaping knobs, but not one first-class post-exception debt object or restoration gate.

## What current Resilio still gets right

### 1) It admits that temporary favoritism has real after-effects

Priority changes, pause states, scheduler rules, rescans, and hidden work can continue affecting other folders after the urgent moment itself.
That is important candor.

### 2) It exposes several ways an operator can keep shaping the world after a burst

Global limits, per-share overrides, scheduler windows, and background-task settings are all useful operational tools.
That toolkit is worth borrowing.

### 3) It does not pretend all folders are on one flat policy plane

Per-share settings, global defaults, and hidden runtime behavior all remain distinct.
That separation matters.

## Where current Resilio still fragments the operator answer

### A) Payback may be implied, but debt is not a first-class object

Current docs let an operator infer that pausing some folders or prioritizing one folder can disadvantage others.
They still do not preserve one durable debt object naming who is owed relief, how much restoration remains, and what stronger sentence is still blocked until that debt is retired.

### B) New exception eligibility is not tied to debt retirement

Current docs expose controls to prioritize again, pause again, or alter rates again.
They still do not publish one explicit embargo answer to whether a claimant with unpaid burst debt may receive another exception.

### C) Return to normal lacks a typed restoration gate

Lower current usage, reopened bandwidth, or a resumed scheduler cell can all look like `back to normal`.
Current docs still do not preserve one proof that reserve was restored, harmed claimants were relieved, and ordinary entitlement can honestly be spoken again.

### D) Restructured debt and forgiven debt blur into folklore

Operators can manually compensate, wait, retry, or simply move on.
Current docs still do not preserve one typed distinction between `settled`, `restructured`, `forgiven`, `written off with consequence`, and `ignored but still owed`.

### E) Manual detachment worsens normalization risk

Because a manually altered share can stop following later global priority changes, an urgent workaround can silently persist after the emergency.
Current docs still do not make that persistence compile into one visible restoration-readiness verdict.

## Resulting product decision

AnonSync should borrow Resilio's candor that urgent favoritism has continuing consequences and that post-burst shaping still matters.
It should **not** clone a product shape where the operator still has to infer from priority, pause, scheduler, rescan, hidden work, and short-window graphs whether burst debt remains open, whether new exceptions are embargoed, and whether ordinary entitlement has actually been restored.

AnonSync should instead expose:

- one first-class **Burst debt contract sheet**
- one **Debt settlement review**
- one **Restoration readiness proof** page
- one **Burst debt timeline**
- one durable **Burst debt lineage receipt**

## Hard decisions locked by this pass

- **closed exception is weaker than restored good standing**
- **unpaid burst debt blocks a stronger normalcy sentence until settlement, typed forgiveness, or explicit narrowed-afterlife policy says otherwise**
- **new burst eligibility is separate from old burst closure**
- **forgiven debt, restructured debt, overdue debt, and settled debt stay visibly different**
- **ordinary entitlement return requires proof of restored reserve and relieved harmed claimants, not just lower visible activity**
- **restoration receipts must preserve creditor set, debt class, embargo posture, settlement route, and blocked stronger sentence**
