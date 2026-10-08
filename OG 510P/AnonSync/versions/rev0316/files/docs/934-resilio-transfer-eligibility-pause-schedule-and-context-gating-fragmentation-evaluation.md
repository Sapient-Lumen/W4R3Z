# Resilio transfer eligibility, pause/schedule semantics, and context-gating fragmentation evaluation

## Why this pass exists

The archive already had strong work on stop truth, route exposure, activation timing, contested repair, and shared substrate.
What it still lacked was one narrower current Resilio pass about another ordinary operator question:

> will bytes move now, and if not, what still mutates anyway — transfer, detection, deletion, indexing, visibility, wake-up checks, or later automatic retry?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `How to pause syncing` still says pause stops only bits downloads/uploads while zero-sized files and deletions still sync and new files are still rescanned and indexed.
- `Running Sync on schedule` still says the scheduler's `Paused` state behaves similarly: upload/download speed becomes zero, but zero-sized files and deletions still sync, paused peers may still upload to non-paused peers, and rescans/indexing still happen.
- `Sync Preferences` still exposes both a global pause/resume and a weekly scheduler rather than one unified eligibility model.
- `Configuring Auto Sleep & Battery Saver (Android)` still says Auto Sleep can turn the core actually off when idle, peers then do not see the device online, and Sync wakes periodically to check for changes; Battery Saver can force Sync to stop below a charge threshold.
- `Settings on mobile platforms` still says `Use mobile data` is a device-level gate, and disabling Android notifications lowers system priority so background work may stop.
- `Setting network interface per share` still says a share can be `Stopped. Forbidden network`, meaning it will not connect to peers for that share and new or updated files will not be detected.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that `pause` is not the same as `nothing changes`

Current docs still plainly say pause does not freeze every lane.
That honesty is valuable.

### 2) It admits that context gates are real

Battery level, charging state, mobile-data posture, network restriction, and background priority are all treated as materially different conditions.
That distinction is worth keeping.

### 3) It admits that some states are neither `running normally` nor `fully stopped`

`Paused`, `Forbidden network`, `Auto-sleep`, `Battery saver stop`, `Wi‑Fi only waiting`, and scheduled zero-speed windows are all real operational states.
That is good candor.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `will this move now, and what still mutates?` the operator may still need to combine:

- pause docs
- scheduler docs
- sync preferences
- mobile settings
- auto-sleep / battery docs
- per-share network restriction docs
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
These are all different truths and should not be reconstructed from settings archaeology.

### 4) Next-wake and next-check truth is not owned as one page family

Auto Sleep periodically wakes.
Wi‑Fi-only waits for a network.
Forbidden network blocks share detection.
Battery Saver forces stop below threshold.
Scheduler resumes on time boundaries.
Those are all different `not now` stories, but current docs leave the operator to assemble them.

## Hard decisions now locked for AnonSync

1. **Transfer eligibility is a first-class contract object.** `can transfer now`, `can detect only`, `can publish deletes only`, `core asleep`, `context-blocked`, and `fully stopped` are separate states.
2. **Bit movement, local detection, deletion propagation, zero-byte propagation, indexing, and peer visibility are separate lanes.**
3. **Pause/offline/sleep/forbidden-network/battery-stop/scheduled-zero are typed verdicts, not one badge family.**
4. **Every blocked or reduced state must publish its current gate basis and next-wake / next-eligibility witness.**
5. **Policy gate and context gate remain separate.** `Wi‑Fi only` is different from `currently on cellular`.
6. **Every consequential eligibility mutation emits a receipt.**

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Transfer eligibility contract sheet**
- **Mobility and power budget review**
- **Paused-but-still-mutating page**
- **Transfer eligibility proof**
- **Eligibility boundary receipt**
- **Wake / gate drift alert**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that pause, scheduler zero-speed windows, mobile-data policy, forbidden networks, auto-sleep, battery gating, and background priority all materially change whether bytes move. But it still makes one ordinary operator answer — `will this move now, and if not, what still mutates anyway?` — depend on several documents instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
