# Resilio remedy-flight protection, preemption, and interruptibility fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that starting a repair is not the same thing as being protected all the way to finish.
That candor is useful.

The strongest ingredients from the present contract are:

- download priority can suspend lower-priority downloads immediately, even when the interrupted file is nearly complete
- queue rebuilds can happen as file sets change, errors appear, or queue composition changes
- pause and scheduler make it explicit that stopping transfer bits does not stop deletions, rescans, indexing, or some upload behavior
- hidden internal tasks openly admit that hashing, checking, merging, scanning, reading, and writing can delay or disturb apparent forward progress
- watcher exhaustion openly admits that discovery can fall back to manual or periodic rescans
- no-source warnings openly admit that a file that looked available at start can degrade into a ghost file that nobody actually has anymore
- `.sync` corruption or service-file loss openly admits that synchronization for a folder can be suspended outright

## Where the current contract still fragments

The problem is not that Resilio lacks operational warnings.
The problem is that it still lacks a first-class, case-scoped **finish-protection** object.

Today the operator can often infer only weaker facts such as:

- the needed repair is currently runnable and has begun transferring bytes
- this share currently has a higher download priority than competing work
- the scheduler window is open right now
- hidden tasks are present but maybe recoverable
- the source peer was online when the repair started
- no catastrophic error is visible at this exact moment

Those are useful operational clues.
They are not a finish-protection contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `we could start the repair`.
It needs to support claims such as:

- the repair is not only runnable now, but protected against ordinary preemption strongly enough to finish inside the promised window
- the repair has started, but remains honestly classified as interruptible because a higher-priority queue arrival, scheduler pause, or source disappearance could still stop it
- the repair is moving bytes, but finish protection is still weaker than it looks because watcher lag, hidden merge pressure, or service-metadata fragility can still collapse the lane
- the repair can finish for a named pilot cohort but not yet for the full required cohort because one required source can still disappear or stall
- a start receipt exists, but the stronger sentence `finish-protected` stays blocked because interruption risk is still above the permitted floor

AnonSync therefore needs a first-class object for **remedy-flight protection** rather than merely borrowing priority, scheduler, warning, or start-state vocabulary.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `if we start this cure now, how protected is it against ordinary interruption, preemption, source collapse, or runtime suspension before it finishes?` — only by making the operator combine several operational surfaces:

- download-priority settings and queue notes
- pause and scheduler semantics
- hidden-task warnings
- watcher-loss warnings
- no-source ghost-file warnings
- service-files-missing and storage-world corruption warnings

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- cure runway ready
- cure start requested
- cure started but interruptible
- cure in-flight protected for named cohort
- cure in-flight protected for required cohort
- cure preempted or requeued
- cure suspended by schedule or pause
- cure aborted by source loss
- cure aborted by service-state corruption
- finish-protection collapsed

That is why this tranche adds five more first-class pages: **Remedy-flight-protection contract sheet**, **Remedy-flight-protection review**, **Remedy-flight-protection proof**, **Remedy-flight-protection timeline**, and **Remedy-flight-protection lineage receipt**.
