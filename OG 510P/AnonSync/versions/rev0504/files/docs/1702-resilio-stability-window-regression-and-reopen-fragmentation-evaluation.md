# Resilio stability-window, regression, and reopen fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `green check now`, `all connected peers currently synced`, `offline peers still exist`, `restored version copied out of Archive`, `rescan pending`, `late offline writer returning`, and `state is now stable enough for a stronger sentence` are not one flat truth.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than attainment:

> after the product knows **what effect landed and for which cohort it is currently attained**, it still needs one first-class answer to **whether that attainment has remained clean long enough, across the right observation horizon, with little enough regression risk, to earn the stronger stability sentence**.

Current Resilio materials still do not provide one typed stability object for:

- distinguishing freshly attained from stability-under-observation
- distinguishing observation-window clean from stability-earned
- distinguishing required-cohort calm from connected-cohort calm
- preserving that offline peers may still return with newer-priority or late-coming state
- preserving that rescans, watcher fallback, or archive restores can legitimately reopen the answer
- preserving that manual recovery can produce a transient local success that is not yet stable across the mesh
- preserving what exact regression budget, dwell window, and reopen triggers block the stronger finality sentence

Instead, the operator still has to translate green checks, peer counts, archive behavior, conflict rules, rescan warnings, and troubleshooting residue into a judgment about whether the effect really *stuck*.

## What current official docs still say

Current official docs still jointly show all of the following:

- `Sync Main View (Desktop)` still says a green checkmark means files are synced with all connected peers, and the peer counter still distinguishes online peers from the total including offline peers.
- `What if several people make changes to the same file?` still says Sync propagates the latest file that comes online, so an offline peer that modified a file can later come online and overwrite versions proposed by online peers, with overwritten versions placed in Archive.
- `Using Archive for file versioning and restoring deleted files.` still says only manual restoring is possible and that if a file is restored while Sync is not running, a later rescan can compare mtimes and move it back to Archive as being older.
- `Agent run out of system notify watchers...` still says when watchers are exhausted Sync learns about updates only through manual or periodic rescans.
- `Some internal tasks are taking time to complete` still says background work can continue through hashing, block checking, merging folder trees, scanning, reading, and transferring.
- `Resilio Sync change log` still records historical fixes around newer files being replaced by older ones from offline peers, deleted files returning, folders disconnecting when long-offline peers come online, and older files replacing newer ones after first rescan.

This is strong operational candor.
It is not a first-class stability contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- whether the effect was merely attained at one instant or survived a meaningful dwell window
- whether the calm state covered only connected peers while required but offline peers still had power to reopen the result
- whether a restore, rescan, reconnect, or hidden merge could still downgrade the apparent attainment
- whether later conflict arrival would count as ordinary churn, material regression, or full reopen
- whether a historical bugfix note should make the operator more conservative about overclaiming stability even if the top-line UI currently looks settled
- whether the system should now permit a stronger irreversible sentence such as normalization, release, or closure

That means current official materials can help answer `is the share quiet now`, `are some peers online`, `what happens if an offline writer returns`, `how archive restore behaves`, or `why updates may appear after rescan`.
They still do not directly answer `has the attained effect remained clean enough, long enough, for the required cohort, under a strong enough regression budget, to earn stability?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit distinction between connected peers and total peers
- explicit conflict candor for late offline return
- explicit archive-restore caveats instead of fake magic restore promises
- explicit watcher and rescan candor
- explicit acknowledgement that background work can continue after the UI looks calmer

But AnonSync should replace the page contract with a first-class **stability window** object where each typed effect has its own:

- attainment start time
- required observation horizon
- regression sensitivity class
- allowed noise budget
- required cohort for stable promotion
- currently unobserved or still-dangerous participants
- reopen triggers
- stability-earned threshold
- strongest blocked stronger sentence
- stability lineage receipt

## Product decision tightened here

The new design line is:

- **effect-attained is weaker than stability-earned**
- **freshly attained, under observation, observation-window clean, stability-earned, reopened, and decayed are different truths**
- **late offline return, rescan discovery, archive restore, hidden merge, or clock correction can reopen stronger stability claims**
- **irreversible closure, probation lift, or normalization may require stability-earned rather than mere attainment**
- **later regression does not erase earlier attainment history, but it does block stronger stable sentences until the page earns them again**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for operational candor about connected-vs-total peers, offline-return overwrite risk, archive restore behavior, rescans, and hidden work.
Resilio remains on the non-clone side for the fairness-critical stability contract.

The reason is now precise:

> current Resilio docs still expose connected-peer calm, offline-return overwrite rules, archive restore caveats, rescan fallback, and background tasks as separate operational facts rather than one typed stability object for `did this attained effect remain clean long enough, for the right cohort, under an acceptable regression budget, to support the stronger closure sentence`, so the operator still has to reconstruct whether the result truly stuck instead of merely landing once.
