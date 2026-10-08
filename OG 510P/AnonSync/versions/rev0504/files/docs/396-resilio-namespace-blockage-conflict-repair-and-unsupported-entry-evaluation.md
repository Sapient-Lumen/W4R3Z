# Resilio namespace blockage, conflict repair, and unsupported-entry evaluation

## Why this pass exists

The archive already had strong doctrine for conflicts, portability, and filesystem-shape fidelity.
What it still lacked was one direct current Resilio evaluation for the ordinary moment when an operator is not asking for theory at all, but for one blunt answer:

> why is this path family not converging cleanly, and is the honest answer here `auto-repaired`, `conflicted`, `blocked`, `unsupported`, or `stop and migrate first`?

Current official Resilio docs still show a living, practical product, but they also still show that this ordinary namespace answer leaks across several article families at once:

- conflict-file troubleshooting
- unsupported link / junction guidance
- one-off invalid-name warnings
- troubleshooting checklists for path length, UTF-8, and stalled sync
- move / rename limitations
- power-user toggles that can turn path-conflict handling from visible to share-stalling

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- Conflict files still appear when multiple versions of files or folders attempt to copy to one target path, including case-insensitive collisions, decomposed unicode differences, prohibited symbols, linked junctions, or even storage/controller problems.
- Current docs still warn not to just delete a `.Conflict` file or folder, because that conflict-named object still corresponds to a real remote file/folder.
- Current Windows guidance still says soft links, hard links, and symbolic links are unsupported and may lead to `.Conflict` entries for each item; current Unix guidance still says symbolic links themselves can sync but their target folders will not sync unless added separately.
- Current troubleshooting docs still say stalled sync can come from UTF-8 / encoding mismatch, overlong file/path names, file-system errors, missing change notifications, or the fact that devices cannot merge folder trees.
- Current one-off invalid-name guidance still says names ending with `*` without an extension are unsupported and may be interpreted as system data, causing program errors or sync disruption.
- Current move/rename docs still say share renames are local-only, cross-partition moves can fall into `Folder not found`, and mobile platforms do not support moving sync shares.
- Current power-user docs still expose `fix_conflicting_paths`; when disabled, current docs say conflicting filenames will no longer be surfaced as Conflicts and the share will not sync if such a conflict exists, with unpredictable results.
- Current power-user docs still expose `normalize_unicode_paths`, confirming that unicode path normalization remains part of the real product semantics rather than a purely invisible implementation detail.

So current Resilio still contains a real but scattered answer to `is this namespace actually healthy, or are we only discovering portability/blockage truth through suffixes, warnings, and hidden toggles?`

## What Resilio still gets right

### 1) It is candid that path semantics are not universal

Current docs do not pretend all peers share one filesystem truth.
They still admit case sensitivity, unicode normalization, invalid symbols, path length, and link semantics can differ materially.
That honesty is worth borrowing.

### 2) It does not hide that some conflict-named objects are still live data

The warning not to casually delete `.Conflict` entries is important.
It reminds operators that the suffix is not just cosmetic clutter.
There is still a real counterpart and real scope risk behind it.

### 3) It admits unsupported-entry classes explicitly

Current docs still plainly say Windows link classes are unsupported and Unix symlink targets are not automatically included.
That is better than vague corruption folklore.

### 4) It admits that advanced toggles can change whether the problem is visible or simply stalls

The `fix_conflicting_paths` note is especially valuable because it makes the real tradeoff explicit:
path conflict handling is not ornamental UI polish; it changes whether the share can proceed.

## Why this is still a good reason not to clone them

### 1) One ordinary operator answer still spans too many article families

Current docs still require cross-reading several places to answer one ordinary question:

- is this just a conflict artifact?
- is the share actually blocked?
- is this an unsupported link class?
- is the path merely being rewritten for portability?
- is the right move to rename, split, migrate, or re-add?

That is a strong reason not to clone the page contract.

### 2) Resilio still makes suffixes and warning rows do too much explanatory work

Current docs are candid, but the operator still too often discovers the real namespace problem from:

- `.Conflict` suffixes
- a stalled share
- a clickable warning row
- a troubleshooting checklist
- a support article about one invalid pattern

AnonSync should not ask the operator to assemble namespace truth from fallout.

### 3) Unsupported links and portability failure still lack one first-class consequence page

Current docs do explain the pieces.
But there is still no single stable page that says, in one place:

- what exact entry class was observed
- whether the target bytes behind it will sync, alias, fork, or be skipped
- whether the safest response is rewrite, separate-subject admission, block, or local-only retention

### 4) Visibility and repairability are still too easy to confuse

Current Resilio docs still let a serious ambiguity survive:

- some problems are visible as conflict artifacts
- some are only visible as non-sync / blocked-share symptoms
- some can be normalized automatically
- some require migration or split
- some remain essentially unsupported on one platform family

Those are materially different states and deserve separate page-owned verdicts.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- explicit honesty that path semantics differ across seats
- explicit warnings that `.Conflict` entries are still real data, not disposable trash
- explicit publication of unsupported entry classes
- explicit admission that advanced path-handling policy changes semantics

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- suffix archaeology
- one-off invalid-name warnings
- scattered troubleshooting bullets
- platform-specific link caveats
- hidden power-user toggles

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Namespace blockage** — is this subject converging, auto-repaired, portability-blocked, unsupported, or stalled for another reason?
2. **Conflict evidence** — what exact counterpart does this conflict-named object correspond to, what winner/loser basis exists, and why is direct deletion unsafe?
3. **Unsupported entry** — what link/alias/entry class is this, what target material lies beyond it, and what safe substitution path exists?
4. **Portability repair** — what rename, normalization, split, or migration plan safely resolves case/unicode/invalid-symbol/length failure?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that namespace portability, unsupported-entry honesty, and conflict caution matter, but it is also current evidence that the ordinary operator answer about why a path family is blocked still leaks across conflict docs, troubleshooting notes, link guidance, invalid-name warnings, and power-user settings. AnonSync should copy the candor and refuse the scattered contract.
