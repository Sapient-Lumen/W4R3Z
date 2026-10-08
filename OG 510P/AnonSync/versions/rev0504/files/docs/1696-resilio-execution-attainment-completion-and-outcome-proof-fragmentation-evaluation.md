# Resilio execution attainment, completion, and outcome-proof fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `executed`, `currently active`, `green check shown`, `pause applied`, `hidden work ongoing`, `file announced`, `file downloadable`, `peer online`, and `fully attained outcome` are not one flat truth.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than execution mandate:

> after the product knows **who was allowed to execute and how**, it still needs one first-class answer to **what effect actually landed, for which cohort, under what verification basis, with what residue, and what stronger completion sentence remains blocked**.

Current Resilio materials still do not provide one typed attainment object for:

- distinguishing execution-attempted from effect-locally-committed
- distinguishing locally committed effect from propagated effect
- distinguishing propagated effect from verified required-cohort attainment
- distinguishing `all connected peers` from `all required peers`
- distinguishing transient activity calm from verified durable completion
- distinguishing no-source ghost residue from true absence of obligation
- preserving when hidden internal tasks, rescans, watcher exhaustion, offline peers, or partial files should keep stronger completion claims blocked

Instead, the operator still has to translate green checks, pause state, warnings, rescans, background operations, peer counts, and troubleshooting cues into completion meaning.

## What current official docs still say

Current official docs still jointly show all of the following:

- `Sync Main View (Desktop)` still says Sync statuses show the current activity, that a green checkmark means files are synced with all connected peers, and that the peer counter distinguishes online peers from total peers including offline ones.
- `How to pause syncing` still says pause stops only bit downloads/uploads while zero-sized files and deletions still sync, and new files are still rescanned and indexed.
- `Some internal tasks are taking time to complete` still says hidden background operations include checking file blocks, hashing, copying local file blocks, merging folder trees, scanning files, reading files, and transferring.
- `Agent run out of system notify watchers` still says when file watchers are exhausted Sync will not be notified about file updates and will only learn about them again through manual or periodic rescans.
- `Cannot download files / There are no source peers online for too long time` still says a peer may announce a file, other peers may delay while rechecking and merging, and by the time they try to download the file the source may only have a placeholder left, creating a `ghost file` that nobody actually has anymore.
- `My files don't sync` still says file-system errors can make Sync abandon syncing, partially downloaded `.!sync` files can remain, and touching or rescanning may be needed before upload resumes.
- `Synchronization Modes` still says disconnected folders can be visible without content, Selective Sync peers may expose placeholders, syncing a placeholder requires some peer that actually has the file online, and the source computer may appear `Synced` from the beginning because it has the full data.

This is strong operational candor.
It is not a first-class attainment contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- whether the act merely started or actually landed locally
- whether the visible calm state covers only connected peers or the full required cohort
- whether offline peers, disconnected peers, or placeholder-only peers still leave the stronger completion sentence blocked
- whether background merge, hashing, rescans, or watcher exhaustion mean the system is still catching up even when the top-line UI looks stable
- whether a warning-free state means there is no residue, or only that the current UI is not surfacing it strongly
- whether a file that was announced but became no-source should count as attained, failed, ghosted, or reopened
- whether later reconnect, rescan, or touch operations can strengthen or weaken the earlier completion claim

That means current official materials can help answer `is Sync doing work`, `are some peers online`, `is a folder paused`, `why is a warning present`, or `why might a transfer be delayed`.
They still do not directly answer `did the intended effect truly land for the required cohort, under what proof basis, and what stronger completion sentence remains blocked?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit activity and peer-count candor
- explicit pause caveats rather than a fake total-stop promise
- explicit background-task candor
- explicit warnings for watcher exhaustion and no-source cases
- explicit distinction between visible metadata presence and actual downloadable / usable content

But AnonSync should replace the page contract with a first-class **execution attainment** object where each typed effect has its own:

- intended cohort
- currently covered cohort
- required completion threshold
- local-commit status
- propagation status
- required-cohort attainment status
- durable verification basis
- residue / ghost / no-source posture
- reopen conditions
- strongest blocked stronger completion sentence
- attainment lineage receipt

## Product decision tightened here

The new design line is:

- **execution-complete is weaker than effect-attained**
- **effect-attained is weaker than verified required-cohort attainment**
- **local commit, propagation, connected-cohort completion, required-cohort completion, and durable verification are different truths**
- **offline peers, placeholder-only peers, no-source residue, hidden tasks, rescans, and watcher failures degrade stronger completion claims instead of remaining cosmetic**
- **later reconnect, rescan, correction, or dispute can reopen attainment validity**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for operational candor about status, pause, hidden work, rescans, and no-source warnings.
Resilio remains on the non-clone side for the fairness-critical attainment contract.

The reason is now precise:

> current Resilio docs still expose green-check activity, peer counts, pause behavior, hidden tasks, watcher exhaustion, placeholder states, and ghost-file warnings as separate operational facts rather than one typed attainment object for `what effect truly landed, for which required cohort, under what verification basis, and with what residue still blocking a stronger completion sentence`, so the operator still has to reconstruct whether the outcome was actually attained instead of merely active, quiet, or partially propagated.
