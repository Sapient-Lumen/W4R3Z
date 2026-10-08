# Resilio quiet-posture, partial-pause, and catch-up-truth evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit admission that scheduled `Paused` does **not** mean full semantic freeze: zero-sized files and deletions still sync, new files are still rescanned and indexed, and a paused peer may still upload to non-paused peers while not downloading itself
- explicit admission that Sync can work in background on desktop, can be headless on Linux, can be killed by Android task-killers or memory optimizers, and is unavailable in background on iOS
- explicit admission that Android Auto Sleep intentionally takes the core offline between wake intervals, while Battery Saver can force a stop below a charge threshold
- explicit admission that hidden internal work such as hashing, block checking, local-block copy, comparison, read, and write can make Sync look stalled even when it may later recover on its own
- explicit admission that slow transfer can be caused by many small files, relay fallback, remote-upload asymmetry, low-capacity network hardware, security software delay, or local disk-priority settings
- explicit admission that some fetch failures are not transport delay at all but missing-source truth: a peer announced bytes that no one still has in full by the time another peer tries to fetch them
- explicit admission that turning the app off or letting the runtime disappear is not cloud-like continuity; source devices must really be online for direct sync to happen

That is not fake candor.
It is very useful operator truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading at least seven places to answer four basic questions:

1. **Why is nothing moving right now?**
2. **What still propagates even though the product says `Paused` or otherwise looks quiet?**
3. **Is this apparent stall really suppression, hidden work, source absence, or a practical bottleneck?**
4. **If the seat wakes, resumes, or regains source peers, what actually changes and what does not?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary motion answer across schedule semantics, background/runtime notes, battery/network settings, slow-speed troubleshooting, source-unavailable warnings, and hidden-work warnings.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say when quiet is partial rather than absolute**
- **say when hidden work is still progressing even if transfer looks idle**
- **say when the real bottleneck is relay, disk, file shape, or remote-upload ceiling rather than vague slowness**
- **say when catch-up depends on source/runtime return rather than optimistic folklore**

But AnonSync should refuse four weaker habits:

- overloaded `Paused` semantics that require article reading to understand surviving effects
- generic `slow` guidance that mixes route, disk, workload shape, and remote-source absence without one causal page
- runtime-absence truth that hides among platform-specific background notes
- resume stories that require stitching together source-absence warnings, power-policy notes, and overwrite-risk cautions

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `412` — Motion basis
- `413` — Quiet window
- `414` — Bottleneck cause
- `415` — Resume catch-up

These pages keep the Resilio candor and reject the schedule-plus-troubleshooting reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor about quiet windows, background/runtime limits, hidden work, source absence, and practical bottleneck families; refuse any interface contract where `why is nothing moving`, `what still propagates`, `what is actually slow`, and `what will resume change` still depends on reading schedule docs, battery/runtime notes, troubleshooting prose, and warning articles together.
