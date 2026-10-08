# Uninstall, offboard, peer tombstone, and hidden-residue attestation interface spec

## Purpose

The archive already had exit review, replacement, recall, and residue-clearance language.
What it still lacked was one tight interface contract for the final and often most misleading transition:

> when the operator believes they are `removing the app`, what exact peer, subject, hidden-state, and leftover-byte truths are they actually closing — and which ones remain?

Current official Resilio docs still make that seam sharp.
They still say that before uninstall the operator should unlink identity and remove remaining Standard shares, otherwise the uninstalled instance will simply continue showing as `offline` on other peers.
They still say Windows service uninstalls require manual deletion of the service storage folder, and macOS/Linux guidance still points at manual cleanup of storage roots and hidden `.sync` folders with Archive inside.
They also still say uninstallation removes the program but does **not** delete folders that were previously shared, while iOS/Windows Phone removals do remove synced files from the device because of platform architecture.

That is not one action.
It is four or five different closures happening at once.

## Core decision

AnonSync should never offer a bare `uninstall` path for a node that has live or remembered relationships.
Instead it should require a reviewed **closure plan** that separates:

- peer-visible tombstone intent
- control-plane residue cleanup
- per-subject hidden residue cleanup
- ordinary shared-folder survival
- platform-forced local-copy loss

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- removing the app can leave the node visible elsewhere as merely offline
- removing the app can leave control-plane storage behind
- removing the app can leave hidden per-share Archive bytes behind
- removing the app can leave ordinary shared folders intact on some platforms but remove synced files on others

So AnonSync should keep one harder rule:

> program removal is not the same as peer departure, subject residue cleanup, or byte destruction, and the UI must say which of those did or did not happen.

## Fixed review order

Every closure/uninstall surface should render the same sections in the same order:

1. **Peer-visible departure**
2. **Control-plane residue**
3. **Per-subject hidden residue**
4. **Ordinary folder fate**
5. **Platform-forced local-copy fate**
6. **Closure receipt**

### 1) Peer-visible departure

This section should show:

- whether the node will publish a deliberate tombstone, a quiet retirement, or no peer-visible exit at all
- whether linked-constellation relationships are being revoked, retired, or simply abandoned
- whether other peers would otherwise keep seeing this node as offline

The operator must be able to answer: **what will others think happened to this node?**

### 2) Control-plane residue

This section should show:

- state roots that remain after program removal unless explicitly cleared
- credentials, logs, databases, and settings that would remain or be deleted
- service-profile storage that needs separate removal if applicable

The operator must be able to answer: **what daemon/control traces will still exist on this machine?**

### 3) Per-subject hidden residue

This section should show:

- subjects that have hidden annex/service bytes on disk
- Archive/history/temp or other managed residue that remains unless explicitly cleared
- subjects whose residue matters for future restore or audit

The operator must be able to answer: **what hidden share-local material survives even if the program goes away?**

### 4) Ordinary folder fate

This section should show:

- ordinary folders that remain untouched
- folders that are simply no longer managed
- whether any folder contents are about to be deleted by reviewed choice rather than as an uninstall side effect

The operator must be able to answer: **what ordinary user data remains browseable after program removal?**

### 5) Platform-forced local-copy fate

This section should show:

- platforms or seats where removing the app also removes locally synced copies
- whether that is platform architecture, not product promise
- what export or recovery step is needed before closure if local copies matter

The operator must be able to answer: **what bytes vanish because of the platform, not because I explicitly asked for destruction?**

### 6) Closure receipt

This section should show:

- departure class
- tombstone publication summary
- control-plane residue summary
- hidden-residue summary
- folder survival summary
- platform-forced deletion summary

## Public objects

### `node_closure_plan`

Fields:

- `node_closure_plan_id`
- `node_ref`
- `peer_departure_mode`
- `control_plane_cleanup_mode`
- `hidden_residue_cleanup_mode`
- `ordinary_folder_mode`
- `platform_forced_copy_loss[]`
- `generated_at`

### `node_closure_receipt`

Fields:

- `node_closure_receipt_id`
- `plan_ref`
- `peer_tombstone_summary`
- `control_plane_cleanup_summary`
- `hidden_residue_summary`
- `folder_survival_summary`
- `platform_forced_copy_loss_summary`
- `created_at`

## Main surface

A compact summary should read like:

- `retire node with peer tombstone · keep ordinary folders · keep hidden archives`
- `remove app only · no peer tombstone · other peers will continue to remember this node as absent`
- `full closure · clear control plane and hidden residues after export`
- `platform warning · local copies on this seat will be removed with the app`

## Event language

Use phrases such as:

- `node retired with explicit tombstone`
- `program removed; ordinary folders left intact`
- `hidden subject residue preserved for later audit/restore`
- `control-plane storage remained because cleanup was not requested`
- `local copies removed due to seat platform architecture`

Avoid phrases such as:

- `Sync uninstalled`
- `device removed`
- `all data cleared`

Those are too ambiguous.

## CLI shape

```text
anonsync node closure review
anonsync node closure apply <review>
anonsync node closure receipt <id>
```

## Edge cases

### Operator wants only program removal

That is allowed, but the surface must say that peers may still remember the node and that hidden residues may remain.

### Operator wants destruction but some residues are needed for audit/restore

The product should force an export or explicit waiver before destruction.

### Platform removes local copies with app removal

The product should warn early and offer export, not teach this later as support lore.

## Non-clone reason

Current official Resilio docs still spread uninstall meaning across unlink instructions, share-removal instructions, service-storage cleanup, hidden `.sync/Archive` cleanup, and platform-specific copy-loss notes.
AnonSync should instead compile those into one reviewed closure plan and one receipt so the operator can prove exactly what ended, what remained, and why.
