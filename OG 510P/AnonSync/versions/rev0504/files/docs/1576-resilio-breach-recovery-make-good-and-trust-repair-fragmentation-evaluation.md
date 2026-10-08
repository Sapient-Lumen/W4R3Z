# Resilio breach recovery, make-good, and trust-repair fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- forecast remaining work and finishability
- publish deadlines as explicit commitments rather than vibes
- distinguish aspiration, target, conditional commitment, hard commitment, miss, renegotiation, withdrawal, and breach

What it still lacked was the next ordinary operator answer:

> once a commitment is actually missed or breached, what is now owed, what part of the original promise still survives, what narrower recovery scope is allowed, and when may anyone honestly publish a new promise again?

That is the seam this pass locks.
A product that can say `breach` but still cannot say what recovery duty now governs is still leaving too much truth in side threads, apology language, and improvised follow-up commitments.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **post-miss and recovery ingredients**, but mostly as separate operational surfaces rather than one operator-facing recovery contract:

- `Performance overview` still gives only short real-time windows — 1 minute, 10 minutes, and 1 hour — plus per-peer speed, latency, and disk queue detail, which help detect motion but not what is owed after a miss.
- `How soon does synchronization start?` still says discovery can be immediate through filesystem notifications or delayed until scheduled rescan every 600 seconds and on start, and that `folder_rescan_interval = 0` disables rescans even on restart.
- `Running Sync on schedule` still says paused windows stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, or rescanning/indexing.
- `My files don't sync` still routes operators through peer review, status warnings, History, upload/download queues, restart, re-add, disk checks, and timestamp correction rather than one recovery-duty object.
- `Locked files` still says another application can block access entirely, which means recovery may depend on a condition outside the original promise path.
- `Collecting debug logs manually` still says direct technical support is available only for Sync Business and not Sync v3, and still requires enablement, restart, reproduction, and at least 15 minutes of capture.

## What current Resilio still gets right

### 1) It is candid that a miss often opens a new operational phase

Resilio's troubleshooting and artifact-capture articles make clear that after delivery trouble the operator may need new observation, new intervention, or a new route.
That honesty is worth borrowing.

### 2) It preserves that blockers can survive the original promise window

Scheduled pauses, delayed rescans, external locks, missing sources, and heavier evidence collection all show that `keep trying` is not the same thing as a clean repaired obligation.

### 3) It admits that diagnosis and recovery can require a heavier rung than the original task

Restart, re-add, log capture, and support-style artifact collection are all real cost increases.
That operational escalation is useful product truth.

## Where current Resilio still fragments the operator answer

### A) The product can help recover motion, but not define post-breach duty

Current docs can help an operator troubleshoot and attempt recovery.
They still do not compile one explicit answer to what exact obligation survives after miss or breach.

### B) Recovery scope still has to be improvised

Current docs help decide whether to restart, wait, re-add, reconnect, or collect logs.
They still do not render one first-class answer to whether the recovery promise is for the full original scope, a narrowed scope, a substitute scope, or only a diagnostic checkpoint.

### C) Trust repair still has to be inferred from separate operational success

A restarted transfer, cleared lock, or renewed motion can be useful.
But current docs still do not give one operator-facing place that says whether trust in the original commitment posture is restored, still degraded, or blocked from re-promise.

### D) The surviving sentence after breach still lives outside one durable receipt

Current docs expose ingredients for recovery effort.
They still do not preserve one canonical answer to what can now be said publicly: `breach still open`, `recovery plan published`, `partial make-good only`, `full scope restored`, or `trust not yet repaired`.

## Resulting product decision

AnonSync should borrow Resilio's candor that post-miss recovery is shaped by short observation windows, discovery lag, schedule pauses, external blockers, troubleshooting ladders, and evidence-capture cost.
It should **not** clone a contract where the operator still has to improvise what is now owed after a miss, whether scope narrowed, and when a new promise is truthful again.

AnonSync should instead expose:

- one first-class **recovery commitment contract sheet**
- one **recovery-shaping review**
- one **breach recovery proof** page
- one **recovery timeline**
- one durable **recovery lineage receipt**

## Hard decisions locked by this pass

- **breach is weaker than recovery duty resolution**
- **original promise, surviving obligation, recovery promise, make-good scope, and trust-repair status stay separate**
- **full make-good, partial make-good, substitute make-good, and diagnostic-only recovery stay separate**
- **a new promise may not be published merely because motion resumed**
- **recovery receipts must preserve breach class, surviving obligation, narrowed or substituted scope, re-promise gate, and trust-repair status**
