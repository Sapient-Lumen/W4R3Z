# Resilio motion, progress, churn, and net-advance fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- dispatch real work
- prove who accepted custody
- track whether the work still has a live heartbeat
- separate healthy quiet from silent stall and rescue territory

What it still lacked was the next ordinary operator answer:

> if motion is happening, is that motion actually reducing the obligation, or is the system only looking busy through retries, rescans, hashing, merges, conflict creation, or other no-net-gain churn?

That is the seam this pass locks.
A product that can tell you that work is alive but not whether the motion is actually buying progress still leaves too much truth trapped in graphs, queues, and the operator's interpretation of what “busy” means.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **motion / background-work / failure-mode** ingredients, but mostly as separate troubleshooting planes rather than one operator-facing work-progress contract:

- `Performance overview` still exposes real-time ongoing-activity graphs, short time windows, per-peer speeds, latency, and disk queue depth.
- `Some internal tasks are taking time to complete` still says Sync performs many hidden operations — checking file blocks, copying local blocks for deduplication, hashing, merging folder trees, reading, scanning, and transferring — and that these can consume time without meaning the system is permanently stuck.
- `How soon does synchronization start?` still says Sync may discover changes by scheduled folder scan every 600 seconds and on start, and that changed files may be rehashed in full to determine what pieces actually changed.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still shows a ghost-file condition where peers learn of a file and later cannot actually obtain bytes because the source now only has placeholders.
- `Conflict files in Sync` still shows that movement can create conflict artifacts and cleanup debt instead of a clean settled outcome.
- `Locked files` still says some other application can block access to files so Sync cannot transfer the data even though the status surface is active enough to show the problem.

## What current Resilio still gets right

### 1) It exposes several honest motion witnesses

Graphs, peer speeds, disk queues, History, status warnings, and queue surfaces are all real signals.
That candor is worth borrowing.

### 2) It admits that background work and transfer are not the same thing

The internal-tasks article is useful because it explicitly names hashing, deduplication, merging, scanning, and transferring as distinct operations.
That is an important truth.

### 3) It surfaces some cases where announced work is not fulfillable work

Ghost-file conditions, locked files, and conflict-file creation all teach the same lesson:
visible activity does not automatically mean that the named obligation is shrinking.

## Where current Resilio still fragments the operator answer

### A) Ongoing activity is still weaker than net progress

Current surfaces can tell the operator that work is happening.
They still do not compile one explicit answer to whether the motion reduced the outstanding obligation.

### B) Scan, hash, merge, and retry motion still share too much semantic space with real advance

Resilio help usefully names those operations.
But the product surface still leaves the operator to infer when they should count as healthy preparation, acceptable churn, or proof that the work is not actually advancing.

### C) Ghost-file and locked-file conditions still show motion without fulfillment

A peer may have announced files that no source can now provide.
A file may be blocked by another application so bytes cannot move.
Those are important examples of busy-looking states that still fail to buy real progress.

### D) Conflict creation can turn movement into new debt

If the result of motion is more conflict artifacts, cleanup steps, or renamed survivors, the operator needs a product surface that says the work may be alive yet not closer to settled.
Current Resilio help leaves that synthesis outside one canonical page family.

### E) The operator still has to infer when motion has crossed into no-net-gain churn

Current docs explain many ingredients.
They still do not publish one explicit no-net-gain boundary that says when retries, rescans, merges, or conflict loops have consumed enough budget that the plan should change.

## What AnonSync should borrow

- activity witnesses like graphs, queues, and peer tables
- explicit language that names hidden operations instead of pretending all motion is transfer
- warning pages for ghost files, conflicts, locked files, and slow internal work
- direct disclosure that some discovery happens by rescan rather than real-time notification

## What AnonSync should not clone

AnonSync should not clone a world where the operator has to treat any motion as progress by default.
It should not leave the following questions scattered across separate surfaces:

- what outstanding obligation is supposed to shrink?
- what evidence proves a real reduction of that obligation?
- what kinds of churn are tolerated temporarily?
- when does busy-looking work become no-net-gain motion?
- when must the route change because the work is alive but not advancing?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **work progress quality and churn truth**.
That family should make it ordinary to publish:

- claimed obligation and unit of reduction
- last observed motion
- last confirmed net advance
- progress basis versus proxy motion basis
- tolerated churn kinds and churn budget
- no-net-gain boundary
- reroute / rescue owner once motion stops buying progress
- durable progress-quality receipt

## Bottom line

Current Resilio still deserves credit for exposing useful motion, queue, graph, and troubleshooting signals.
But it still does not own one operator-facing answer to:

> if the work is alive, is it actually getting done, or is the system only spending time on motion that has not yet reduced the obligation?

That is why this seam belongs on the non-clone side.
