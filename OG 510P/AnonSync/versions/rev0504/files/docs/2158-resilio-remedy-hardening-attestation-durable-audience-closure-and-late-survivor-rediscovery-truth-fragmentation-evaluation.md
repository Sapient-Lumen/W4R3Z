# Resilio remedy-hardening attestation durable audience closure and late-survivor rediscovery truth fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the outsider reached a clean state
- that clean state was watched across a named horizon
- relapse channels can be named and some can be intercepted
- the governed audience can be described as closed, partly closed, or still carrying explicit survivors
- residual survivor classes can be kept visible instead of wished away

That is still weaker than a harder question:

**if the archive declared closure today, what happens when a late-surviving copy, hidden archive entry, disconnected folder, placeholder-backed shell, expired transfer record, or forwarded file resurfaces tomorrow?**

Point-in-time closure is not yet durable closure.
A closure verdict that cannot survive late survivor rediscovery is still too weak.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several rediscovery-shaped ingredients, but it still spreads them across separate pages:

- `Disconnecting and Removing Folders` says disconnect affects one device only, leaves the folder in the file system, and reconnect may propose a different default path or create a newly indexed directory if a same-name folder is already present
- `Synchronization Modes` says disconnected folders remain visible, selective-sync folders expose placeholder file lists, and `Remove from this device` only reverts the local copy to a placeholder rather than retiring the object everywhere
- `Using Archive for file versioning and restoring deleted files` says hidden `.sync/Archive` material is manually accessible on desktop, Android, and WebUI, default retention is 30 days on desktops and 1 day on mobiles, and `sync_trash_ttl = 0` means Sync will never delete files from Archive
- `Sharing single file` says one-time file transfers can be made never-expiring, everyone with the link can download the files without device or use limits, recipients can share them further, and removing the transfer from Sync UI does not remove it from the device
- `Power user preferences` says Sync can keep expired file transfers in UI independently (`keep_expired_transfer_days`, `keep_expired_transfer_num`), which is a UI-memory knob rather than byte-retirement proof
- `Sharing a folder locally` says local shares remain only on the configured device, do not sync with remote peers directly, are removed if the source folder is disconnected or removed, and do not automatically reconnect later

This is good survivor-surface candor.
It is not yet one first-class answer to **after closure was declared, what late rediscovery surfaces can still reopen the claim, what stronger sentence stays blocked, and what evidence would force the archive to re-open closure?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the link expired
- the transfer disappeared from UI
- a disconnected folder stopped syncing
- the visible peer list looks closed
- a hidden archive entry can still be opened later
- a placeholder-backed shell can still invite refetch
- a forwarded one-time copy can still resurface elsewhere
- the old closure verdict is therefore assumed to remain durable

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **audience-wide closure proof and residual-survival truth are weaker than durable closure and late-survivor rediscovery truth**
- **a closure verdict is weaker than a closure verdict that declares its rediscovery invalidators up front**
- **expired links, removed transfers, and disconnected folders are weaker than rediscovery-safe closure**
- **late survivor rediscovery must automatically narrow or reopen the closure sentence instead of being treated as an exception**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- closure durability horizon
- rediscovery surface set
- latent survivor carrier set
- closure invalidator set
- re-open trigger class
- strongest honest durable-closure sentence
- blocked stronger durable-closure sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **durable-closure contract sheet**
- **durable-closure review**
- **durable-closure proof**
- **durable-closure timeline**
- **durable-closure lineage receipt**
