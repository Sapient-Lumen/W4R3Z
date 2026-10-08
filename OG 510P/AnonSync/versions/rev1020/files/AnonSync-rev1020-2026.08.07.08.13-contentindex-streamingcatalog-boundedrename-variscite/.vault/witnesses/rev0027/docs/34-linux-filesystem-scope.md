# Linux-first filesystem scope

This document turns “Linux is first-class” into a more concrete storage/filesystem contract.

## Why this document exists

Without this file, “Linux-first” risks meaning nothing more than:

- we like Linux
- we mostly test on Linux
- we hope the normal filesystems are fine

That is too vague for a sync product where pathname rules, xattrs, ACLs, watchers, and rename semantics affect correctness.

## Support tiers

### Tier 1 — first-class

These are the filesystems the archive should treat as primary v1 correctness targets:

- `ext4`
- `xfs`
- `btrfs`

Interpretation:

- these are the environments where the daemon should aim for the strongest claims
- preflight/adopt/restore/selective workflows should be designed around their semantics first
- bugs here are core-product bugs, not corner-case bugs

### Why these three

They are common real Linux filesystems for desktops, laptops, workstations, servers, and NAS-like boxes.
They also fit the product’s main audience better than a broad “everything Linux can mount” promise.

### Notes

- ext4 is the baseline “ordinary Linux” target
- xfs matters because serious Linux storage users often choose it
- btrfs matters because copy-on-write, reflink, snapshots, and subvolumes are common in advanced Linux setups even if AnonSync does not initially depend on those features

### Tier 2 — supported with warnings

These environments may be workable, but should surface more caution:

- `f2fs`
- local filesystems with unusual mount options or constrained metadata behavior
- overlay/containerized paths where upper/lower semantics matter to operators

These should be probeable and often usable, but the product should not quietly promise parity with Tier 1.

### Tier 3 — best effort

These environments are useful to inspect and sometimes usable, but they should not receive the same correctness claims:

- `nfs`
- `cifs` / `smb`
- many FUSE filesystems
- foreign-compatibility filesystems such as `exfat` or other non-native cases used mainly for exchange/removable media

Operators may still choose them.
The product should simply say out loud that they are weaker terrain.

### Tier 4 — blocked or sharply constrained for sensitive workflows

Some environments should be blocked or strongly constrained for at least some workflows, especially when the probe shows missing metadata or unsafe pathname semantics.

Examples of workflows that may need blocking on weak targets:

- share adoption into a populated path
- relocate with metadata-preserving guarantees
- selective-materialization modes that depend on strong local semantics
- restore workflows expecting strong metadata fidelity

## Semantics that matter

Support tier is not just the filesystem name.
The daemon should probe and surface at least:

- case-sensitivity posture
- normalization posture
- rename/replace safety expectations
- xattr support
- POSIX ACL support
- symlink behavior
- special-file handling
- hardlink handling
- watcher/change-detection posture
- local-versus-networked/FUSE-like environment classification

## Operational rules

### 1) inotify is primary, rescans remain mandatory backup

Linux gives us a strong local watcher story, but the daemon should still retain periodic scan/reconciliation as a correctness backstop and should expose when it is falling back more heavily than intended.

### 2) atomic rename assumptions belong in the support contract

The daemon should rely on strong local rename semantics on Tier 1 targets and should warn more aggressively on weaker/networked environments where related locking/atomicity expectations may vary.

### 3) xattrs and ACLs are not optional trivia

If a share, restore path, or policy assumes metadata fidelity, the daemon should probe that directly.
Tiering should reflect real xattr/ACL support, not only the on-disk filesystem family name.

### 4) reflink is opportunistic, not required

Btrfs and some XFS environments may allow efficient clone-like local behavior.
AnonSync may use that where it helps, but should not make correctness depend on reflink support.

## What “usual Linux filesystems” should mean here

For this archive, the phrase should be interpreted narrowly and usefully:

- ext4, xfs, btrfs are first-class
- f2fs is reasonable but secondary
- networked / foreign / FUSE-like filesystems are probeable and often usable, but not equal
- Windows/macOS semantics should not dictate v1 behavior

## Interface consequences

The CLI and API should let an operator ask:

- what filesystem family is this path on?
- what support tier does the daemon assign to it?
- which semantics are strong here and which are downgraded?
- which workflows are blocked, guarded, or fully supported on this path?

That is why the archive now carries:

- filesystem profiles
- filesystem support tiers
- filesystem compatibility reports
- explicit `fs support` and `fs compare` surfaces

## Practical product posture

The archive should be comfortable saying:

> AnonSync is Linux-first, and for v1 that means ext4/xfs/btrfs first, everything else explicitly classified instead of politely hand-waved.
