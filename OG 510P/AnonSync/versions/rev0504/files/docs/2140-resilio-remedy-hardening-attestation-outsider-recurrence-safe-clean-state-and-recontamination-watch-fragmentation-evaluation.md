# Resilio remedy-hardening attestation outsider recurrence-safe clean state and recontamination watch fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a late outsider found the corrected replacement
- the replacement explained its own supersession claim
- the outsider could act without operator help
- the remediation path stayed within an explicit exposure budget
- the outsider finished remediation and reached a self-verifying clean state

That is still weaker than a harder question:

**will that clean state stay trustworthy across the re-open horizon, or can stale state re-enter later through known recontamination channels without the outsider carrying a first-class watch and recurrence contract?**

A clean state now is not yet a recurrence-safe clean state.
A portable clean-state receipt is not yet a watch posture.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several recontamination ingredients, but it still spreads them across separate pages:

- `Using Archive for file versioning and restoring deleted files` says restore is manual, runtime must already be active if the restored file is supposed to replay outward, and otherwise a later rescan can move the restored file back into Archive as older
- `What if several people make changes to the same file?` says a peer that edited offline can later come online and take priority over chronologically later online changes, with overwritten versions moved to Archive
- `How soon does synchronization start?` says change detection can be immediate through filesystem notifications, can fall back to scheduled rescans every 600 seconds and on Sync start, can be widened by configuration, and can be disabled entirely by setting `folder_rescan_interval` to zero
- `How to pause syncing` and `Running Sync on schedule` say paused posture still allows deletions to sync and new files to be rescanned and indexed, so `paused` is not a complete quiet or containment state
- `Agent run out of system notify watchers` says watcher exhaustion pushes discovery onto manual or periodic rescans until limits are raised
- `User Management` says local changes on a Read Only peer suspend further synchronization of the changed files for that peer unless overwrite behavior is chosen
- `Conflict files in Sync` says conflict artifacts correspond to real remote counterparts and should not simply be deleted
- `Sync Main View (Desktop)` says the green checkmark only covers all connected peers and that History is only a 30-day activity view

This is good relapse-channel candor.
It is not yet one first-class answer to **did the outsider's clean state remain trustworthy across the watch horizon, what channels could re-open stale reliance, what detector would catch that, and what proof survives after live UI and recent history are gone?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the outsider once reached a clean state
- the UI currently looks green
- some peers are connected and others are offline
- the last visible activity looked healthy
- archive restore still exists as a reopen surface
- offline peers can later reassert older edits
- pause / scheduler / watcher posture may delay or mute recontamination detection
- Read Only divergence or conflict artifacts may suspend or fork later updates
- the outsider therefore remains recurrence-safe and clean

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **self-verifying clean-state truth is weaker than recurrence-safe clean state and recontamination watch**
- **the outsider finished remediation is weaker than the outsider can remain clean across a named watch horizon with explicit recurrence channels and explicit detection posture**
- **green status, recent history, queue calm, or one successful verification pass may never impersonate `recurrence-safe clean state`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- watch horizon class
- recontamination channel set
- detection posture class
- automatic containment class
- recurrence proof artifact set
- strongest honest recurrence-safe sentence
- blocked stronger recurrence-safe sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **recurrence-watch contract sheet**
- **recurrence-watch review**
- **recurrence-watch proof**
- **recurrence-watch timeline**
- **recurrence-watch lineage receipt**
