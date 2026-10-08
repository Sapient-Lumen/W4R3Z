# Resilio subject non-arrival cause, absent-state classification, and remedy archaeology evaluation

## Why this pass exists

The archive already had strong pages for warnings, recovery rungs, fetchability, placeholder truth, and proxy artifacts.
What it still did not own cleanly enough was one ordinary operator question that appears **before** many of those surfaces:

- why is this file, folder, or subtree not here yet
- is it absent because policy excluded it, because nobody still has the bytes, because transport is blocked, because local execution is blocked, or because the product is still doing background work
- is the honest next move `wait`, `fetch`, `touch`, `rescan`, `fix permissions`, `free space`, `raise watchers`, `repair continuity`, or `stop pretending the bytes still exist`
- what stronger diagnosis is still unsupported right now

Current official Resilio docs still make that seam very real.
They are candid that `My files don't sync` can mean IgnoreList exclusion, xattrs limits, locks, read-only overwrite issues, missing write permissions, filename/encoding limits, path-length ceilings, merge failure, filesystem errors, missed notifications, low free space, stuck `.!sync` remnants, or time skew.
They are also candid that `Cannot download files` can be a ghost-file condition where the tree still advertises a subject that no peer now has as real bytes, that watcher exhaustion can turn live change discovery into periodic rescan only, and that `Some internal tasks are taking time to complete` may still be ordinary hashing, merge, transfer, or write work rather than a hard stall.

That honesty is useful.
The problem is that the product still leaves one everyday answer too archaeology-shaped:

> `why is this subject absent or not advancing right now, and what is the least-strong intervention that is actually justified?`

## What current Resilio still gets right

Current official docs still publish several operational truths that are worth borrowing.

- **Absence has many named causes, not one generic failure bucket.** Current `My files don't sync` docs still enumerate IgnoreList exclusion, xattrs/StreamsList constraints, file locks, read-only overwrite posture, missing read-write permissions, encoding/path-length issues, merge failure, filesystem errors, missed change notifications, low disk space, stuck partial-download residue, and clock skew.
- **Ghost subjects are named honestly.** Current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` docs still say a peer may have announced new or changed files that later disappeared into placeholder-only state or removal before others downloaded them, leaving a stale tree entry with no current byte source.
- **Background work is not mislabeled as total failure.** Current `Some internal tasks are taking time to complete` docs still say the condition can be recoverable hidden work such as checking file blocks, copying local blocks, hashing, merging folder trees, scanning, transferring, and writing.
- **Notification degradation is named as a specific discovery problem.** Current watcher-exhaustion docs still say running out of system notify watchers means Sync will miss live file updates and only learn changes by manual or periodic rescan until the limit is raised.
- **Locks are admitted without fake precision.** Current `Locked files` docs still say the product can show which files are locked but cannot identify the locking application itself.
- **Continuity break is named separately from ordinary delay.** Current `Service files missing / Cannot identify destination folder` docs still say loss or corruption of `.sync` service files suspends synchronization for that folder and that the repair path creates a new synchronization instance.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is strong candor.
Resilio is still willing to admit that `not here` does not mean one thing.

## Where current Resilio still stays too article-shaped

### 1. Subject absence class still depends on support-memory stitching

The ordinary operator should not need to reconstruct from memory whether a given missing or stale subject is currently best classified as:

- `excluded-by-policy`
- `blocked-by-local-lock`
- `blocked-by-local-permission`
- `read-only-diverged`
- `name-or-path-unportable`
- `notification-gap / rescan-needed`
- `still-processing`
- `ghost-no-source`
- `continuity-broken`
- `filesystem-fault`
- `space-blocked`
- `time-invalid`

Current Resilio still tells those truths, but it still makes the operator stitch them together from troubleshooting, warnings, and related-article hops.

### 2. The product still under-owns the difference between `not yet`, `not possible now`, and `not actually present anywhere`

These are materially different realities:

- the file is still being hashed / merged / transferred
- the file is visible but currently blocked by lock or permission
- the file is visible but only if policy changes
- the file is visible in tree state but no byte source remains
- the share itself has continuity damage and cannot identify the destination safely

Those distinctions should be first-class product verdicts, not things inferred from several troubleshooting pages.

### 3. The least-destructive next move is still too prose-driven

Current docs often suggest a repair, but the operator still has to infer whether the safest next step is:

- wait and observe
- fetch from a healthy source
- touch files
- restart runtime
- rescan only
- align IgnoreList / metadata policy
- free space
- fix permissions
- raise watcher limit
- reconnect same destination
- remove/re-add and accept successor continuity

That ordering still arrives as support prose rather than one typed per-subject review.

### 4. Dismissal and suppression still blur with diagnosis closure

A warning can be hidden, ignored, or disabled.
But the subject-level question can remain open:

- is this item merely hidden from warning view
- is it still missing for the same reason
- did the operator actually restore byte delivery
- is the strongest safe sentence now `waiting`, `blocked`, `ghost`, or `successor rebuilt`

Subject diagnosis should not disappear just because the warning row did.

## What AnonSync should do instead

AnonSync should make **subject non-arrival truth** a first-class reviewed object that can exist even when there is no active warning row and even when the operator began from a missing file rather than a status banner.

The product should own four page families:

1. **Subject delivery review**
   - current subject state
   - strongest honest absence / blockage class
   - whether the issue is policy, source, route, local execution, continuity, or hidden-work delay
   - first safe next move

2. **Absence-cause matrix**
   - evidence by plane: policy, source, transport, local execution, filesystem / continuity, chronology
   - what each plane supports, contradicts, or leaves unknown
   - why a stronger diagnosis is still forbidden

3. **Minimal intervention chooser**
   - requested fix versus least-strong justified intervention
   - wait / rescan / fetch / touch / permission fix / watcher fix / continuity repair / successor rebuild ladder
   - safe language rewrite before apply

4. **Delivery truth receipt**
   - reviewed subject
   - absence class and evidence basis
   - chosen next move or intervention
   - strongest safe sentence afterward

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that `not here` can mean exclusion, blockage, background work, route failure, ghost state, or continuity damage. But it is not worth cloning the way current operators still have to reconstruct, from troubleshooting pages and warning articles, whether a subject is merely delayed, currently blocked, no longer source-backed, or actually broken — and what the least-destructive justified next move is.

## New replacement pages added in this revision

- `562` Subject delivery review
- `563` Absence-cause matrix
- `564` Minimal intervention chooser
- `565` Delivery truth receipt
