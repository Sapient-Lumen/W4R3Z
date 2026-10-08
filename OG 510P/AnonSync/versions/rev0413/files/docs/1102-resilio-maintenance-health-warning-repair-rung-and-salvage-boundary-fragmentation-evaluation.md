# Resilio evaluation: maintenance health warning, repair rung, and salvage-boundary fragmentation

Current official Resilio docs are still candid that `busy`, `degraded`, `blocked`, `suspended`, and `rebuild-required` are not the same health truth.
That candor is worth borrowing.
The page contract is still too fragmented to clone.

## Why this seam matters

A sync runtime can look unhealthy for very different reasons.
It may be temporarily busy doing hidden work.
It may have lost live watchers and fallen back to rescans.
It may be blocked by an external locker.
It may have suspended one folder because its database or sidecar spine is damaged.
It may have outgrown available RAM badly enough that the only vendor-advised relief is destructive re-share.
If the product does not own these distinctions in one place, operators guess wrong about severity and jump to destructive fixes too early.

## What current official Resilio docs still distinguish well

Current official docs still preserve all of these as separate operational truths:

- `Some internal tasks are taking time to complete` is not necessarily a stuck runtime; it can be intermittent recovery while disk, network, or file-count pressure is high.
- watcher exhaustion is a detection downgrade where new updates are learned only by manual or periodic rescan unless the watcher budget is raised.
- `Locked files` is a transfer block imposed by some other application, while Resilio admits it cannot identify the locker itself.
- `Database error` is folder-scoped suspension caused by unreadable database fragments, with a repair ladder that starts at restart, rises to disconnect/reconnect of the same destination, and can escalate to re-add across peers.
- `Service files missing` is a broken `.sync` spine that suspends synchronization for that folder and explicitly asks the operator to salvage archive expectations before deleting `.sync` and recreating the sync instance.
- `Out of memory` is not just temporary pressure; current docs say Sync keeps the full tree and deleted operations in memory/database state, and the only way to make it use less RAM is to remove the biggest folders from all peers and share them again.
- `My files don't sync` still treats peer disconnect, ignore mismatch, xattr mismatch, locks, read-only overwrite posture, permission failure, encoding/path-budget issues, tree-merge failure, filesystem damage, notification loss, free-space exhaustion, stuck partial files, and time skew as different causes with different remedies.

That is strong semantic candor.
AnonSync should borrow it directly.

## Why the current contract still should not be cloned

Current official docs still make one ordinary operator answer depend on several article families.
To answer:

> is this share merely busy, degraded but recoverable, blocked by a local actor, suspended due to corruption, or already at a destructive rebuild rung — and what must I salvage before escalating?

an operator still has to merge:

- warning articles
- generic troubleshooting pages
- database and sidecar repair notes
- memory-pressure notes
- lock-contention notes
- support-log escalation instructions

The distinctions are good.
The workflow ownership is still scattered.

## The AnonSync decision

AnonSync should make **maintenance health and repair rung** first-class product structure.
That means:

1. **busy work, degraded detection, blocked transfer, suspended subject, and destructive-rebuild recommendation are separate modeled verdicts**
2. **restart, reconnect-same-destination, re-add, sidecar deletion, and whole-share re-share are separate repair rungs with different state-loss cost**
3. **archive salvage, partial-download residue, and local survivor checks must appear before destructive repair steps**
4. **support escalation should preserve the exact warning basis and the strongest safe sentence, not just `sync failed` folklore**
5. **every serious repair action needs one receipt preserving warning class, chosen repair rung, expected survivors, accepted losses, and the blocked stronger sentence**

## Replacement page family required

This seam adds five more product-owned pages:

- **Health warning contract sheet**
- **Health triage review**
- **Repair rung review**
- **Health proof page**
- **Health lineage receipt**

## Strongest non-clone line

> Borrow Resilio's candor that hidden background work, rescan-only degraded detection, external locks, folder-scoped suspension, `.sync` spine loss, and memory-driven destructive rebuild are materially different truths — but refuse any product contract where the operator still has to reconstruct severity, repair rung, and salvage duty from scattered warning pages and troubleshooting articles before touching live data.
