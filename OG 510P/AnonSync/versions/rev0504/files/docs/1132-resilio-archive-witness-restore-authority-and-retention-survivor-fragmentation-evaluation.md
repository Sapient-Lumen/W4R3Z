# Resilio archive witness, restore authority, and retention-survivor fragmentation evaluation

## Why this pass exists

The archive already has strong work on materialization, non-authority convergence, maintenance salvage, and hidden sidecar state.
What it still lacked was one tighter current Resilio pass about another ordinary operator question:

> I can see old bytes in Archive — what exactly do those bytes witness, who is allowed to restore them, how long do they survive, and when are they already too weak to call recovery?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Using Archive for file versioning and restoring deleted files` still says Archive receives the older or deleted copy on **other peers** when a peer updates or deletes a file, keeps files by default for **30 days on desktops and 1 day on mobiles**, requires **manual restore only**, is not accessible on iOS, and depends on Sync still running during restore so the resurrected file is not immediately re-archived as older.
- the same article still says Archive can be turned on or off per folder, `sync_trash_ttl` can be set to `0` so Archive never auto-deletes, and `max_file_size_for_versioning` can prevent large files from being versioned at all.
- `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` still says each synced folder gets a hidden `.sync` folder and that Archive inside it stores old versions of files deleted or modified on **other devices**.
- current `Encrypted folders` docs still say an encrypted node has Archive, but cannot restore a deleted file back into the swarm because it follows the deleted state and is read-only.
- current config-mode docs still say per-folder `use_sync_trash` is a real authored setting.
- current uninstall docs still say uninstall does **not** remove archived files inside hidden `.sync` folders.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that Archive is not the same thing as backup

Current docs still distinguish:

- remote-change witness on this device
- local trash / recycle-bin recovery for files you deleted locally
- manual resurrection from Archive
- retention horizon
- file-size versioning ceiling
- platform visibility and access limits
- encrypted-seat inability to publish restored bytes back out
- uninstall survivor residue

That honesty is valuable.

### 2) It admits that restore authority and byte presence are different truths

A seat can visibly hold historical bytes and still be unable to restore them authoritatively into the mesh.
That distinction is worth preserving.

### 3) It admits that restore success depends on runtime posture, not just copying bytes out

Current docs still say a peer must have Sync running while the file is taken out of Archive; otherwise rescan can compare mtimes and archive it again.
That is not mere implementation trivia — it is contract-shaping truth.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `what does Archive prove here and can this seat really restore from it?` the operator may still need to combine:

- Archive/versioning docs
- `.sync` sidecar docs
- power-user preferences
- config-mode authored settings
- encrypted-seat caveats
- uninstall residue guidance

That is too much archaeology for one ordinary decision.

### 2) `Archive` still compresses too many different meanings

The same label can mean:

- historical witness of a remote change
- limited-time salvage cache
- no-version coverage because file exceeds size ceiling
- unavailable surface on iOS
- inaccessible-on-SD-card behavior on Android
- visible historical bytes on an encrypted seat that still cannot publish a restore
- hidden residue surviving app uninstall

AnonSync should not inherit that compression.

### 3) Restore authority still rides on hidden conditions

`manual restore only` is not enough.
The operator also needs to know:

- whether this seat may publish restored bytes outward
- whether Sync must already be running
- whether timestamp ordering will treat the restored file as stale
- whether retention and size ceilings already removed earlier versions

Current Resilio docs leave too much of that truth scattered.

## Hard decisions now locked for AnonSync

1. **Archive witness is a first-class contract object.** `historical-byte witness`, `restorable-by-this-seat`, `restorable-only-through-another-seat`, `retention-expired`, `size-excluded`, and `unknown` are separate verdicts.
2. **Witness presence and restore authority stay separate.** A seat can hold bytes yet still lack authority to republish them.
3. **Archive is weaker than backup.** It is remote-change witness with retention and authorship limits, not a general safety promise.
4. **Manual resurrection is a reviewed act.** Runtime witness, timestamp risk, and publication authority belong on the page before restore language becomes strong.
5. **Retention and visibility limits are product state.** Desktop/mobile TTL, iOS visibility absence, Android SD-card caveat, and max-file-size exclusion cannot remain footnotes.
6. **Receipts preserve the strongest safe sentence and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Archive witness contract sheet**
- **Archive restore review**
- **Archive retention and platform visibility page**
- **Archive salvage proof**
- **Archive lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that Archive is a real recovery-adjacent object with remote-change provenance, manual-only restore, retention ceilings, platform visibility limits, and encrypted-seat authority cliffs. But it still makes one ordinary operator answer — `what do these archived bytes witness, can this seat truly restore them, and how long do they survive?` — depend on versioning docs, `.sync` docs, encrypted-seat caveats, config tables, and uninstall notes instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
