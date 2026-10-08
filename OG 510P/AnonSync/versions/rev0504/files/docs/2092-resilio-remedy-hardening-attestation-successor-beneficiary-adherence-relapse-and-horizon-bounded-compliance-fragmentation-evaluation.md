# Resilio remedy-hardening attestation successor beneficiary adherence, relapse resistance, and horizon-bounded compliance fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the beneficiary is legitimate
- the later correction is legitimate
- the beneficiary stayed on the right future-correction lane
- the beneficiary may have noticed and acknowledged the correction
- the beneficiary may even have switched to the corrected working state

That is still weaker than a sharper question:

**after the beneficiary switched, did that corrected working state actually persist across the governed horizon, or did the beneficiary later relapse into stale use through restore, offline comeback, pause-window drift, local divergence, delayed detection, or other reversion surfaces?**

A single observed switch is a point event.
Adherence is an interval claim.
An interval claim needs a horizon, relapse channels, tolerated interruption rules, and recovery language.
Without those, `beneficiary adopted the correction` quietly expands into folklore about uninterrupted compliance.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several relapse surfaces, but it still spreads them across separate pages:

- `Using Archive for file versioning and restoring deleted files` says restoring an archived older file can re-upload it if Sync is running, and if Sync is not running the later rescan can compare modification timestamps and move that restored file back into Archive as older
- `What if several people make changes to the same file?` says an offline peer's file version can later take priority when it comes online, even over later online changes
- `Folder Preferences` says Archive can be disabled per folder, read-only folders can overwrite local changes, and that destructive overwrite option is disabled for read-only folders with Selective Sync on
- `How to pause syncing` says paused peers stop uploads and downloads, but deletions still sync and new files are still rescanned and indexed
- `Sync Preferences` says Scheduler can pause syncing or limit speed during chosen hours
- `How soon does synchronization start?` says some environments rely on filesystem notifications while others rely on scheduled rescans every 600 seconds by default
- `Folder Types and Management` says local changes in read-only folders can leave those files no longer receiving updates

This is good operational candor.
It is not yet one first-class answer to **did this named beneficiary stay switched to the corrected working state through the governed horizon, and if not, exactly where did relapse remain open?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the correction was adopted once
- the current snapshot happens to look corrected
- Sync is resumed now
- no contradiction is visible in the current UI
- an old version was restored then later archived again
- an offline stale edit briefly took priority
- a read-only divergence temporarily suspended future updates
- the beneficiary therefore stayed compliant throughout the governed horizon

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **beneficiary adoption is weaker than durable adherence across the governed horizon**
- **recovery after a relapse is weaker than uninterrupted adherence**
- **pause, scheduler holds, delayed rescans, archive restore, offline stale comeback, and read-only divergence must stay first-class relapse channels instead of dissolving into generic sync noise**
- **`currently synced`, `latest bytes present`, and `current snapshot looks corrected` may never impersonate `the beneficiary stayed switched throughout the governed horizon`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source beneficiary-adoption receipt identifier
- named beneficiary and governed slice
- governed horizon start, end, and closure rule
- tolerated lapse budget
- relapse channel set
- last confirmed corrected working-pointer state
- relapse incident ledger
- recovery incident ledger
- unresolved relapse risk
- strongest honest adherence sentence
- blocked stronger uninterrupted-compliance sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **successor beneficiary-adherence contract sheet**
- **successor beneficiary-adherence review**
- **successor beneficiary-adherence proof**
- **successor beneficiary-adherence timeline**
- **successor beneficiary-adherence lineage receipt**
