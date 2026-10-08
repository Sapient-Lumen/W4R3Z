# Resilio shell-affordance, placeholder-destruction, restore-parity, and filesystem-shape evaluation

## Purpose

The archive already has stronger answers for trust, intake, byte posture, custody, lineage, hidden service material, exclusion rules, delay windows, and queue truth.
What still remained under-specified was a different class of non-clone reason:

> in current Resilio, too many ordinary byte actions still depend on shell affordances, platform-specific browser/file-manager integrations, or hidden-shape caveats rather than one stable product-owned page.

This document tightens that line.
It does not argue that Resilio lacks useful capability.
It argues that the capability still arrives through page contracts AnonSync should not clone directly.

## Bottom line

Resilio still deserves admiration here.
Current official docs still show all of the following are real and useful:

- Selective Sync / `.rsls` placeholders still compress a genuine on-demand-byte workflow.
- File-browser context actions such as `Sync to this device` and `Remove from this device` are genuinely convenient when they work.
- Archive still provides real version/deletion recovery.
- xattr carriage and symbolic-link handling are treated as serious technical problems rather than ignored entirely.

But the same official docs also show why AnonSync should not clone the interface contract.
Too many ordinary operator truths still depend on:

- whether a shell extension is healthy
- whether the underlying volume is NTFS
- whether the current surface is desktop UI, WebUI, Android, or iOS
- whether the operator knows that deleting a placeholder can actually mean global deletion
- whether metadata and alias-edge caveats are remembered from support articles instead of exposed in one ordinary audit page

That is a strong current reason to borrow the product ideas while refusing the page boundaries.

## The four load-bearing non-clone seams in this pass

### 1) Shell affordances are useful but still not a trustworthy semantic home

Current official docs still say:

- WebUI is the default and only option on Linux-based machines, and also the default UI path for Windows service installs.
- File-browser context actions depend on shell integration that can fail or disappear.
- On macOS, operators may have to reset Finder extensions, relaunch Finder, or manually re-enable the extension with `pluginkit`.
- On Windows, context-menu items appear only on NTFS volumes, depend on `ShellExtensionPath.dll`, and may require DLL registration or Explorer restart.

That is good pragmatic support guidance.
It is not a strong semantic boundary.
The ordinary question `what actions are available for this path on this seat right now?` still depends too much on shell health and platform ritual.

### 2) Placeholder gestures still blur local dematerialization and global destruction

Current official docs still say:

- `.rsls` files are zero-byte placeholders representing names without full content.
- `Remove from this device` reverts a local copy back to a placeholder.
- With read-write access, deleting a placeholder removes it permanently from all peers.
- A power-user switch can disable `Remove from all devices`, but that setting is ignored in Linux WebUI.
- Disconnecting a folder removes placeholder files from the folder on that device.

That means Resilio still offers strong space-saving and on-demand convenience, but the operator can still cross from local byte posture change into share-wide destruction through gestures that are too closely related.
AnonSync should not clone that gesture family without a stricter review boundary.

### 3) Restore/history truth is still platform-asymmetric and manually reconstructed

Current official docs still say:

- Archive keeps prior/deleted versions for 30 days on desktops and 1 day on mobiles by default.
- Restore is manual only.
- Desktops can open Archive from the Sync UI, but WebUI and Android rely on browsing hidden `.sync/Archive`, and iOS cannot access Archive at all.
- The latest archived version is the highest index, while the timestamp shown in Archive is when the file was placed there, not the original edit time.

That is useful recovery, but it is not one stable restore page.
Operators still have to remember where Archive is accessible, which platform lacks it, what the timestamps mean, and how to manually copy bytes back.

### 4) Filesystem shape fidelity is still fragmented across support articles and hidden policy files

Current official docs still say:

- Windows soft links, hard links, junctions, and symbolic links are unsupported and may generate `.Conflict` files.
- On Unix, symbolic links can be synchronized as links while target folders are not synchronized unless separately added.
- xattrs sync according to a hidden `.sync/StreamsList` whitelist.
- When native xattr storage is unavailable, Resilio stores metadata in hidden `.sync/Streams` stubs so it can still propagate the metadata.
- Troubleshooting docs still say disabling xattr syncing can cause macOS bundles like Pages, Keynote, or apps to appear as ordinary subdirectories.

That means Resilio is taking the problem seriously, which is good.
But the operator-facing contract is still too split between alias-edge docs, hidden metadata policy files, and troubleshooting notes.

## Borrow / adapt / reject line for this pass

### Borrow directly

AnonSync should borrow these ideas without embarrassment:

- explicit placeholder-backed versus full-byte posture
- shell accelerators when available
- real history/version retention
- metadata-fidelity and alias-edge awareness

### Adapt instead of clone

AnonSync should adapt these families into stronger public objects:

- shell capability and fallback truth
- local-vs-global byte action review
- history access and restore parity
- filesystem shape audit and fidelity rollup

### Refuse the clone line

AnonSync should not clone:

- shell extension health as the main semantic home of materialization actions
- deleting placeholders as an overloaded path that can collapse into global deletion
- restore access that depends on hidden folders or platform-specific side doors
- metadata / symlink / bundle fidelity truth that lives mainly in hidden policy files and support lore

## Replacement pages AnonSync now owes

This pass therefore claims four more ordinary pages:

1. **Shell capability** — one page proving whether shell acceleration exists, which actions it accelerates, what is missing, and what the product-native fallback is
2. **Byte action review** — one page distinguishing local evict/revert-to-placeholder from share-wide delete and forcing last-copy proof before dangerous transitions
3. **History access** — one page unifying retention window, candidate versions, platform parity, and restore consequences
4. **Filesystem shape audit** — one page rolling up alias-edge, metadata-channel, invalid-name, and shape-changing risks without forcing article archaeology

## Result

The archive now has a sharper fifth-wave answer to `why aren't we cloning Resilio here either?`

The answer is no longer just `hidden files` or `config knobs`.
It is also:

> because current Resilio still lets too much ordinary operator meaning live in shell-extension health, placeholder gestures, platform-specific archive access, and fragmented filesystem-shape caveats.

That is a solid reason to borrow the capability families while replacing the page contracts.
