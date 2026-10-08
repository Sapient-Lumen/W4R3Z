# Resilio transfer eligibility, pause semantics, schedule windows, and context-gating fragmentation evaluation

## Why this pass exists

The archive already has strong work on runtime stop truth, ingress, bootstrap, materialization, health, and same-host topology.
What it still lacked was one tighter current Resilio pass about another ordinary operator question:

> will bytes move now, and if not, what still mutates anyway — transfer, detection, deletion, indexing, visibility, wake-up checks, or later automatic retry?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `How to pause syncing` still says pause stops only bits downloads/uploads while zero-sized files and deletions still sync and new files are still rescanned and indexed.
- `Running Sync on schedule` still says the scheduler's `Paused` state behaves similarly: upload/download speed becomes zero, but zero-sized files and deletions still sync, paused peers may still upload to non-paused peers, and rescans/indexing still happen.
- `Sync Preferences` still exposes both a global pause/resume and a weekly scheduler rather than one unified eligibility model.
- `Configuring Auto Sleep & Battery Saver (Android)` still says Auto Sleep can turn the core actually off when idle, peers then do not see the device online, and Sync wakes periodically to check for changes; Battery Saver can force Sync to stop below a charge threshold.
- `Settings on mobile platforms` still says `Use mobile data` is a device-level gate, that Android notifications affect background priority, and that disabling notifications may force background work to stop.
- `Setting Delay Time For Syncing` still separately changes publish latency for selected file types, which means `eligible` is not the same thing as `immediate`.
- `File download priority` still separately changes which queued files move first and can suspend lower-priority downloads, which means `moving now` is not the same thing as `everything eligible is progressing equally`.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that `pause` is not the same as `nothing changes`

Current docs still plainly say pause does not freeze every lane.
That honesty is valuable.

### 2) It admits that context gates are real

Battery level, charging state, mobile-data posture, network restriction, background priority, wake cadence, and queue priority are all treated as materially different conditions.
That distinction is worth keeping.

### 3) It admits that some states are neither `running normally` nor `fully stopped`

`Paused`, `scheduled-zero`, `auto-sleep`, `battery-stopped`, `Wi‑Fi-only waiting`, `priority-queued`, and `delay-held` are all real operational states.
That is good candor.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `will this move now, and what still mutates?` the operator may still need to combine:

- pause docs
- scheduler docs
- sync preferences
- mobile settings
- auto-sleep / battery docs
- delay-time docs
- download-priority docs
- background-priority caveats

That is too much archaeology for one ordinary decision.

### 2) `Paused` still over-compresses several distinct truths

Current Resilio is candid that `Paused` may still allow:

- zero-sized file propagation
- deletion propagation
- rescanning
- indexing
- some peer upload behavior under scheduler semantics

The label is too small for the meaning.
AnonSync should not inherit that compression.

### 3) Context gates are still scattered across device, share, and runtime planes

A share may be eligible by policy but blocked by current network.
A runtime may be alive but asleep.
A device may be allowed on Wi‑Fi but not cellular.
Notifications may be disabled in a way that reduces background viability.
A file may be eligible but delayed or deprioritized.
These are all different truths and should not be reconstructed from settings archaeology.

### 4) `Not now` and `later` are still mixed together

Auto Sleep periodically wakes.
Wi‑Fi-only waits for a network.
Battery Saver forces stop below threshold.
Scheduler resumes on time boundaries.
Delay rules defer publication for some file classes.
Priority rules can suspend lower-priority queued files.
Those are all different `not now` stories, but current docs still leave the operator to assemble them.

## Hard decisions now locked for AnonSync

1. **Transfer eligibility is a first-class contract object.** `can transfer now`, `can detect only`, `can publish deletes only`, `core asleep`, `context-blocked`, `delay-held`, `priority-deferred`, and `fully stopped` are separate states.
2. **Bit movement, local detection, deletion propagation, zero-byte propagation, indexing, peer visibility, publish delay, and queue priority are separate lanes or modifiers.**
3. **Pause/offline/sleep/battery-stop/scheduled-zero/mobile-data-blocked are typed verdicts, not one badge family.**
4. **Every blocked or reduced state must publish its current gate basis and next-wake / next-eligibility witness.**
5. **Policy gate and context gate remain separate.** `Wi‑Fi only` is different from `currently on cellular`.
6. **Eligibility, immediacy, and queue precedence remain separate truths.** A file can be eligible but delayed, or queued but deprioritized.
7. **Every consequential eligibility mutation emits a receipt.**

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Transfer eligibility contract sheet**
- **Mobility and power budget review**
- **Paused-but-still-mutating page**
- **Transfer eligibility proof**
- **Eligibility boundary receipt**
- **Delay and queue watch surface**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that pause, scheduler zero-speed windows, mobile-data policy, auto-sleep, battery gating, file delay, and queue priority all materially change whether bytes move. But it still makes one ordinary operator answer — `will this move now, and if not, what still mutates anyway?` — depend on several documents instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
