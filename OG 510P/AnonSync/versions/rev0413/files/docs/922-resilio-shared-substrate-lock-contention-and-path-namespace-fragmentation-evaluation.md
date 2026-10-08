# Resilio shared substrate, lock contention, and path-namespace fragmentation evaluation

## Why this pass exists

The archive already had strong work on route reachability, activation timing, and contested repair.
What it still lacked was one narrower current Resilio pass about another ordinary operator question:

> what kind of storage substrate is this really, which runtime identity is actually touching it, which path namespace is authoritative, and what sort of writer contention or notification loss comes with that choice?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Sync and SMB file shares` still says Sync can work with SMB shares, but only with caveats: Sync and the user who runs it need full permissions, SMB shares may not support file-update notifications unless both ends are SMB `3.0+`, locked files can remain inaccessible after network/app failure, and simple Samba setups can corrupt or roll back files when third-party applications access the same data outside of SMB.
- `How soon does synchronization start?` still says filesystem notifications are the fast path, but some storages are not expected to support them correctly, explicitly including `NFS` and `SMB2` mounted shares, with scheduled scan every `600` seconds as the fallback.
- `Locked files` still says another application can block Sync from transferring data, that the UI can list the locked objects and jump to them, but Sync still cannot identify which application holds the lock.
- that same `Locked files` article still points the operator toward manual investigation and restart rather than pretending the locker identity is known.
- `Power user preferences` still publishes both `enable_file_system_notifications` and `recheck_locked_files_interval`, which means notification posture and lock-recheck cadence are real tunable parts of the runtime contract rather than incidental internals.
- `Sync Service Troubleshooting on Windows` still says mapped drive letters do not exist for the service because they are created on interactive logon, recommends UNC-style entry instead, warns that this loses update notifications so changes are discovered only on rescan or restart, and says switching the service to `Local System` creates a different storage folder and therefore an empty/new Sync state that requires re-adding and re-sharing folders.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that storage substrate choice changes behavior materially

Current docs do not pretend `local filesystem`, `SMB share`, and `service-visible UNC path` are equivalent.
Notification quality, permissions, lock behavior, and even which folders are visible to the runtime can all change.
That honesty is valuable.

### 2) It admits that writer contention is not just a generic sync error

Current docs still distinguish `some other application locked this file`, `SMB-side lock got stranded`, `notifications will only arrive during rescan`, and `this topology may corrupt or roll back files`.
That distinction is worth keeping.

### 3) It admits that runtime identity and path namespace matter

Current docs still say the Windows service cannot see mapped drives the way the interactive user can, and that switching the service account changes storage-folder state and requires re-adding/re-sharing.
That means runtime identity is not just a hidden implementation detail.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `what storage contract do I really have here?` the operator may still need to combine:

- SMB-share caveats
- notification-timing docs
- lock-file troubleshooting
- power-user notification / recheck settings
- Windows service namespace/account notes
- rescan / restart fallback behavior

That is too much archaeology for one ordinary setup or repair decision.

### 2) Access-path authority is still too implicit

Current Resilio preserves the facts, but the operator still has to infer whether the real authority path is:

- local direct filesystem access
- SMB / UNC path access
- service-visible but not user-visible path namespace
- mixed access through both SMB and direct-on-host writers

AnonSync should not leave that classification scattered.

### 3) Mixed-writer topology is still more support warning than owned product boundary

Current docs tell the truth that direct-on-host writes plus Samba-mediated writes can damage or roll back files.
But that truth still feels like a cautionary article instead of a first-class reviewed boundary.
AnonSync should not let dangerous topology live as folklore.

### 4) Lock truth and notification truth are still too weakly joined

`locked`, `notifications absent`, `service cannot see mapped drive`, and `falling back to rescan` are all parts of one operator reality: the substrate changed the quality of synchronization.
AnonSync should productize that as one page family.

## Hard decisions now locked for AnonSync

1. **Storage substrate is a first-class contract object.** `local fs`, `network share`, `service-visible UNC`, and `mixed external writer topology` are separate classes.
2. **One synced subject gets one authoritative write-path contract.** Direct-on-host writes and SMB-mediated writes do not silently share one safe sentence.
3. **Runtime identity and path namespace are part of subject truth.** Service account, storage location, and path visibility are not hidden trivia.
4. **Lock contention is a first-class blockage object.** Unknown locker identity must remain explicit, and recheck cadence must be inspectable.
5. **Notification floor is public.** `full notifications`, `rescan-dependent`, and `restart-dependent discovery` are separate grades.
6. **Mixed access that can corrupt or roll back data must be a reviewed boundary, not a buried warning.**

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Storage substrate contract sheet**
- **Shared substrate topology review**
- **Lock contention watch**
- **Mixed access boundary warning**
- **Substrate lineage receipt**
- **Substrate drift / topology regression alert**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that storage substrate, service identity, notifications, and lock behavior change the real sync contract. But it still makes one ordinary operator answer — `what path is authoritative here, who is really writing it, and what quality of detection or repair can I honestly expect?` — depend on SMB caveats, service-account troubleshooting, lock articles, and power-user timing notes instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
