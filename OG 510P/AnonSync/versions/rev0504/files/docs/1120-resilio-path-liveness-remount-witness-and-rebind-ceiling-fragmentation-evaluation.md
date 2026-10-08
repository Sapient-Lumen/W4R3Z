# Resilio evaluation: path liveness, remount witness, and rebind-ceiling fragmentation

Current official Resilio docs are still candid that `path missing`, `same-drive move`, `cross-root rehome`, `reconnect to old directory`, and `externally attached target` are not the same continuity truth.
That candor is worth borrowing.
The page contract is still too fragmented to clone.

## Why this seam matters

Operators routinely ask one ordinary question when a synced subject vanishes or an external target disappears:

> did the subject merely move, did its root go away, did a removable root return, or am I really binding a new subject and paying reconnect cost?

That is not a cosmetic question.
It changes whether old peers remain attached, whether path continuity is still honest, whether a default reconnect path is safe, and whether a removable/external target is being treated as the same world or a new one.

## What current official Resilio docs still distinguish well

Current official docs still preserve all of these as separate operational truths:

- `Folder not found / Can't open the destination folder` still says the warning can mean the folder was deleted from the filesystem or moved to another HDD / logical partition, and it still offers restore-from-trash, point-to-correct-location, or remove-and-add-again as materially different remedies.
- `Can I move or rename a syncing folder?` still says rename is local-only, still limits Windows/macOS tracking to moves within the same logical drive, still limits Linux to moves inside the sync parent folder, and still says mobile platforms do not support moving sync shares.
- `Disconnecting and Removing Folders` still says reconnect may propose a default path different from the original, can create a same-name `(1)` sibling, and requires manual path correction plus `Destination folder is not empty. Add anyway?` if the operator wants the old directory back.
- `Can I use Resilio Sync to backup from an internal drive to an externally connected USB drive?` still routes same-computer internal→external work through local sharing rather than ordinary two-seat sharing, and still says older versions could not do one-folder-to-another-folder sync on the same computer that way.
- `My files don't sync` still separately reminds the operator to verify that all drives are mounted properly when path liveness or filesystem reachability is in doubt.

That is strong semantic candor.
AnonSync should borrow it directly.

## Why the current contract still should not be cloned

Current official docs still make one ordinary operator answer depend on several article families.
To answer:

> is this the same subject after a root loss, move, remount, or external-return event — and what exact rebind or re-share cost am I buying if I continue?

the operator still has to merge:

- move/rename FAQ guidance
- missing-path warning guidance
- reconnect/remove guidance
- same-computer external-drive guidance
- generic troubleshooting reminders about mounted drives

The distinctions are good.
The workflow ownership is still scattered.

## The AnonSync decision

AnonSync should make **path liveness and rebind class** first-class product structure.
That means:

1. **live bind, missing root, cross-root rehome, removable-root return, and new-subject adoption are separate modeled verdicts**
2. **path string equality is weaker than root witness, and root witness is weaker than full subject continuity proof**
3. **reconnect suggestion is weaker than safe rebind, and safe rebind is weaker than zero-reconnect-cost continuity**
4. **same-computer external targeting stays visibly separate from ordinary path repair because it may actually be self-edge derivation rather than subject relocation**
5. **every serious missing-path action needs one receipt preserving loss cause hypothesis, returned-root witness, chosen repair rung, reconnect cost, and the blocked stronger sentence**

## Replacement page family required

This seam adds five more product-owned pages:

- **Path liveness contract sheet**
- **Missing path review**
- **Remount and external media review**
- **Rebind proof**
- **Path liveness lineage receipt**

## Strongest non-clone line

> Borrow Resilio's candor that missing paths, same-root moves, cross-root rehomes, reconnect-default drift, and external-target workflows are materially different truths — but refuse any product contract where the operator still has to reconstruct `did this subject move, disappear, remount, or become a fresh bind?` from several FAQs and warning pages before touching live data.
