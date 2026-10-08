# Resilio cleanup intent, witness survival, and preservation-before-cleanup evaluation

## Why this pass exists

The archive already had reclaim previews, uninstall closure, recovery horizon, and retention mutation review.
What it still did not own tightly enough was the operator question that joins those together:

- I need to free space, detach a share, remove a linked copy, or uninstall the app
- which of those are merely local cleanup
- which ones narrow later rollback or audit evidence
- what should be preserved *before* cleanup happens
- what sentence is still safe after cleanup completes

Current official Resilio docs still make that seam very real.
They are candid that disconnect, remove, remove-from-this-device, remove-from-all-devices, iOS storage clear, and uninstall are all different.
They are also candid that hidden `.sync/Archive` state can survive some of those actions while local files disappear under others.

That honesty is useful.
The problem is that the product still makes the operator assemble one cleanup truth from several separate articles.

## What current Resilio still gets right

Current official docs still publish several truths that are operationally valuable.

- **Cleanup verbs are not collapsed into one lie.** Current `Disconnecting and Removing Folders` docs still distinguish disconnecting one device from removing the folder across linked devices, while also saying non-linked remote devices may still keep the folder.
- **Selective local eviction is distinct from share-wide deletion.** Current `Synchronization Modes` docs still say `Remove from this device` reverts a local copy to a placeholder while `Remove from all devices` removes the file from all peers and archives it there.
- **Placeholder visibility is itself part of cleanup fallout.** Current `Selective Sync` docs still warn that removing a Selective Sync share removes placeholders from the local filesystem.
- **Mobile storage cleanup is posture-bound.** Current `Storage Management on iOS` docs still say local copies can be cleared from a sync share only when Selective Sync is enabled, and that the iOS storage menu also mixes service data with downloaded user data.
- **Uninstall is not universal erasure.** Current `How to uninstall Sync?` docs still say uninstall removes the program but not previously shared folders, still requires manual removal of some settings/storage roots, and still warns that hidden `.sync/Archive` bytes are not removed automatically.
- **Platform architecture can still remove local bytes even when the product is not claiming destruction.** Those same uninstall docs still say iOS uninstallation removes synced files from the device because of platform architecture.
- **The current v3 line is still live.** The official v3 change log still runs through `3.1.2.1076` dated 31/Oct/2025.

That is good candor.
Resilio is still willing to admit that cleanup, detach, and app removal do not all mean the same thing.

## Where current Resilio still stays too article-shaped

### 1. Cleanup intent and witness survival are still separate memories

The ordinary operator question is not just `what does this button remove?`
It is also:

- what later recovery witness survives
- what hidden residue remains
- what claim ceiling gets weaker
- whether I should export or pin evidence first

Current official docs still leave that answer spread across disconnect/remove, selective-sync, storage-management, archive, and uninstall articles.

### 2. `Free space` and `preserve evidence` still lack one shared review

Resilio currently documents enough facts for a careful operator to behave well.
But it still does not give one stable workflow-owned page that answers:

> before I clean this up, should I preserve anything first?

That missing bridge matters because the product can be fully honest article-by-article and still let ordinary cleanup accidentally narrow later rollback or audit truth.

### 3. Cleanup outcomes still need reconstruction after the fact

After an action, operators still have to reconstruct whether the outcome means:

- local bytes gone, placeholders remain
- local bind gone, ordinary folder remains
- linked-device presence removed, external retainers still possible
- app gone, shared folders intact, hidden archive still on disk
- app gone, local synced bytes removed because of platform architecture

Those are different receipts.
Current Resilio still tends to publish them as scattered caveats rather than one durable cleanup receipt.

## What AnonSync should do instead

AnonSync should make cleanup and evidence preservation one shared contract.
The product should own four page families:

1. **Cleanup intent review**
   - classify the requested action as local reclaim, detach, linked removal, hidden-witness prune, uninstall, or full local clearance
   - show what witness classes are currently at risk
   - force the product to say whether preservation should happen first

2. **Witness survival forecast**
   - forecast which byte, event, placeholder, and hidden-state witnesses survive each cleanup option
   - show which surfaces still reach them afterward

3. **Preserve-before-cleanup**
   - explicit export / pin / move-to-other-host / extend-retention choices
   - safe language when the operator declines preservation intentionally

4. **Cleanup outcome receipt**
   - requested cleanup versus effective cleanup
   - freed scope versus surviving witness
   - strongest safe post-cleanup sentence
   - stronger forbidden overclaim

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that cleanup verbs, local eviction, linked removal, and uninstall are materially different. But it is not worth cloning the way current operators still have to infer *what witness should be preserved first, what evidence survives cleanup, and what sentence is safe afterward* by stitching together several help articles.

## New replacement pages added in this revision

- `547` Cleanup intent review
- `548` Witness survival forecast
- `549` Preserve-before-cleanup
- `550` Cleanup outcome receipt
