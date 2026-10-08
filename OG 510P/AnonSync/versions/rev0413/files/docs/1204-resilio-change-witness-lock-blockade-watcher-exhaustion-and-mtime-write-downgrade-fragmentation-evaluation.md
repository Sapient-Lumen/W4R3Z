# Resilio change-witness, lock blockade, watcher exhaustion, and mtime-write downgrade fragmentation evaluation

## Why this pass exists

The archive already had doctrine for freshness, quiescence, chronology, and timestamp authority.
What the current revision chain still lacked was one tighter current Resilio pass about a narrower but more operator-real question:

> when the product says `this file changed` or `this file still has not moved`, what evidence actually exists: a live watcher event, a periodic rescan, a manual `touch`, an intentional quiescence hold, a hard lock blockade, or only database-kept timestamp truth after disk mtime write failed?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- Sync relies on system notifications to detect file updates and considers a file changed when its modified time or size changes.
- manual `touch` is still an official remediation when mtime or size changes were not noted.
- file-class delay still exists for Office, Autodesk, Adobe, and similar extensions, defaults to 10 seconds, and requires restart after edits.
- locked files are still a visible class, but Sync still cannot tell the operator which application owns the lock.
- a separate `recheck_locked_files_interval` still governs later retries for blocked files.
- watcher exhaustion still downgrades change discovery to manual or periodic folder rescans until the system limit is raised.
- `folder_rescan_interval` still defaults to 600 seconds and is still the fallback path for changes that were missed by other means.
- `ignore_mtime_assign_errors` still allows Sync to stop retrying disk mtime writes and keep the correct timestamp only in the database while the file on disk shows a `current` timestamp instead.

That is strong operator candor.
It is also another strong reason not to clone the contract as-is.

## What current Resilio still gets right

### 1) It admits that `changed` is not one flat truth

Resilio does not pretend detection is magic.
Its current docs still admit that a changed file may be seen through notifications, through size/mtime comparison, after periodic rescan, or after manual touch/remediation.
That is worth keeping.

### 2) It admits that waiting can be intentional

Current docs still keep class-based delay and lock retries separate from generic transfer failure.
That matters because `not uploaded yet` can be the healthy result of waiting for a writer to finish rather than evidence of a broken route.

### 3) It admits that detection can silently downgrade

The current watcher-exhaustion article is especially valuable because it tells the truth:
the product can lose live notifications and fall back to rescans.
That is precisely the kind of degradation many products hide.

### 4) It admits that authoritative time can diverge from disk-visible time

The current power-user table is unusually candid that mtime write failure can leave the authoritative timestamp in the database while the on-disk timestamp stays `current`.
That distinction is important and easy to miss.

## Why AnonSync still should not clone it

### 1) Change witness is still too scattered

The ordinary operator still has to reconstruct whether the product really *saw* the edit live, discovered it later on rescan, or only believes it after manual touch.
AnonSync should not let `updated` or `waiting` hide that basis.

### 2) Quiescence and blockade are still too easy to confuse

Current docs still force the operator to stitch together `delay profile`, `locked files`, retry interval, and generic troubleshooting to answer one basic question:

> are we intentionally waiting for a tool to finish, or are we blocked from reading the file at all?

AnonSync should keep those as typed state, not article archaeology.

### 3) Detection downgrade still appears more as warning/procedure than as stable contract

Watcher exhaustion, manual rescan, restart, and touch are still discoverable, but the operator must still reconstruct the active change-discovery class from several places.
AnonSync should publish that class continuously.

### 4) Disk time and authoritative time are still too easy to overmerge

Once `ignore_mtime_assign_errors` becomes relevant, disk-visible mtime stops being trustworthy as the sole public truth.
AnonSync should not let a file row keep implying that disk mtime alone proves chronology or freshness.

## Hard decisions now locked for AnonSync

1. **Change witness is a first-class contract object, not a side effect of notifications and support rituals.**
2. **Live watcher event, periodic rescan discovery, manual touch induction, quiescence hold, lock blockade, and database-only timestamp authority are separate truths.**
3. **`Waiting` is weaker than `quiescence hold`, and `quiescence hold` is different from `lock-blocked`.**
4. **Disk-visible mtime is weaker than authoritative timestamp, and authoritative timestamp is weaker than chronology certainty.**
5. **Every serious detection or publication delay needs one receipt that preserves witness class, hold/block basis, timestamp authority, and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Change-witness contract sheet**
- **Writer-pressure review**
- **Observation proof**
- **Timestamp-authority downgrade review**
- **Change-witness lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that live notifications, rescans, manual touch, delay profiles, lock retries, and database-kept mtimes are materially different truths. But it still makes one ordinary operator answer — `did the product really see this edit, is it intentionally waiting, or is timestamp truth already divorced from the disk view?` — depend on several pages instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.
