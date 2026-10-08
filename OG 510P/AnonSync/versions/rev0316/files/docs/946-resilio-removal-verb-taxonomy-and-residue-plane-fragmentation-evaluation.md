# Resilio removal verbs, residue planes, and removal-taxonomy fragmentation evaluation

## Why this seam matters

Current official Resilio docs are candid that `remove` is not one thing.
Disconnecting a folder is different from removing it from linked devices.
Removing a placeholder from this device is different from removing the file from all peers.
Hiding an offline device is different from unlinking it.
Uninstalling Sync is different again, especially when settings, storage folders, `.sync/Archive`, or mobile app sandboxes survive or disappear.

That is exactly why this seam is worth studying and exactly why it should not be cloned as-is.

## What current official docs still get right

They still say plainly that:

- disconnect affects one device and can leave the folder in the file system
- reconnect can propose a different path and accidentally create a new indexed directory
- removing a disconnected folder removes it from all devices linked with the same personal identity, yet can still leave it available on remote devices outside that linked identity
- disconnected folders may have no local path at all
- removing a Selective Sync share removes placeholders from the local file system
- `Remove from this device` reverts a file or subfolder to a placeholder locally while preserving copies elsewhere
- deleting a placeholder with Read & Write access can remove the file from all peers
- power-user settings can disable `Remove from all devices` for Selective Sync shares, but that setting is ignored in Linux WebUI
- clearing an offline device only hides it and it can reappear later
- uninstall can still leave ordinary shared folders and `.sync/Archive` behind on desktop platforms, while iOS and Windows Phone remove synced files from the device with app uninstallation

That candor is valuable.

## Why AnonSync still should not clone it

One ordinary operator question remains too fragmented:

> what exactly will disappear, from where, for whom, and what residue or comeback path survives if I press a remove-like verb here?

In current Resilio, the operator still has to assemble that answer from:

- disconnect/remove folder docs
- selective-sync / placeholder docs
- linked-device cleanup docs
- uninstall docs
- power-user settings docs
- platform-specific interface notes

That is too much documentation archaeology for an operation family built from nearly identical verbs.

## Hard decisions for AnonSync

1. **Removal verbs are typed operations, not one overloaded affordance family.**
2. **Seat-plane cleanup, subject detachment, local material eviction, global delete, and software uninstall remain distinct verbs.**
3. **Every remove-like review must publish residue truth before commit.**
4. **Placeholder-local revert and global file deletion must never share one silent delete path.**
5. **Remote-not-linked survivors must stay visible in global-sounding flows.**
6. **Reconnection risk, duplicate-branch risk, and comeback risk belong in the same workflow family as removal.**
7. **Every serious removal emits a durable receipt with the strongest safe sentence and the stronger rejected sentence.**

## Interface family implied by this evaluation

AnonSync should own this seam with:

- **Removal contract sheet**
- **Removal intent disambiguation**
- **Device-local eviction boundary**
- **Identity-wide removal and remote remainder review**
- **Removal lineage receipt**
