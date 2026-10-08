# Resilio activity-posture, pause/throttle semantics, sleep state, and network-gate fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `Sync Preferences` docs still say there is a global pause/resume control plus explicit receiving/sending rate limits and a weekly scheduler
- those same current preference docs still say rate limits apply to Internet connections by default and require `rate_limit_local_peers` to force the same limit in LAN
- current `How to pause syncing` docs still say pause does **not** mean the folder becomes inert: zero-sized files still sync, deletions still sync, and new files are still rescanned and indexed while the folder is paused
- current `Running Sync on schedule` docs sharpen that again: a scheduled `Paused` slot still says zero-sized files sync, deletions sync, and new files are rescanned and indexed, while upload/download semantics are described separately from ordinary pause prose
- current `Configuring Auto Sleep & Battery Saver (Android)` docs still say Auto Sleep turns the core off when no actual syncing is taking place, connected peers stop seeing the device online, and the app wakes on a configured interval to check for local or remote changes; Battery Saver can then force Sync to stop below a chosen charge floor
- current `Setting network interface per share` docs still say a share can be restricted to Any network, Wi‑Fi only, or a specific network, and a prohibited network produces `Stopped. Forbidden network` where the peer is not connected and new or updated files are not detected

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **is this share merely rate-limited, or is it genuinely unwilling to move bytes right now?**
2. **is it prevented from downloading only, prevented from both directions, or still allowed to announce deletes / metadata?**
3. **is the device visible to peers right now, asleep on a wake interval, battery-stopped, or network-forbidden?**
4. **will change detection still happen while transfer is paused, or has observation itself been suspended?**
5. **are LAN peers exempt from the stated limit, making the apparent throttle only partly real?**
6. **what is the strongest truthful sentence about this node's present work willingness, duty cycle, and traffic budget?**

Current Resilio docs still spread those answers across preferences, pause help, scheduler help, Android battery docs, and mobile network-per-share docs.

The gap is even sharper because the ordinary English word `paused` does not carry one stable contract.
One current article describes paused peers as not downloading/uploading anything while still syncing deletions and indexing new files.
Another current article describes scheduled `Paused` as a state where only bit downloads are stopped and non-paused peers may still receive uploads from the paused peer.
Even before arguing about runtime reality, the operator is already being asked to infer too much from one reused label.

So a user can learn all the pieces and still not get one stable product answer to:

> what exactly is this node willing to do right now — discover, announce, upload, download, relay deletes, wake later, or stay completely dark — and what resource or policy gate is responsible?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow six habits directly:

- **say openly when transfer budget and detection liveness are different truths**
- **say openly when a node is asleep/offline on a wake cadence rather than truly gone**
- **say openly when network policy, battery policy, and operator pause are different causes**
- **say openly when LAN traffic escapes the visible speed cap**
- **say openly when delete propagation and byte transfer are not governed by the same gate**
- **say openly when a label like `paused` has narrower or broader meaning than the operator may assume**

But AnonSync should reject six weaker habits:

- one overloaded `paused` badge that hides directionality and residual behaviors
- one overloaded `offline` badge that hides sleep cadence, battery stop, or forbidden-network gating
- throttle indicators that do not publish whether LAN peers are exempt
- pause indicators that do not publish whether indexing and delete propagation continue
- mobile gating surfaces that do not say whether observation is still happening
- traffic controls expressed only as settings prose rather than as current runtime contract state

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1265` — Activity-posture contract sheet
- `1266` — Pause semantics review
- `1267` — Work-willingness proof
- `1268` — Duty-cycle timeline
- `1269` — Activity-posture lineage receipt

These pages keep the Resilio candor and reject the scattered-duty-cycle semantics problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that pause, throttle, sleep, battery stop, network restriction, indexing, delete propagation, and LAN-exempt rate limits are different truths; refuse any interface contract where the operator must reconstruct present work willingness and duty-cycle meaning from several help articles instead of one explicit activity-posture object.
