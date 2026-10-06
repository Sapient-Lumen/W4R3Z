# Removable-media local fallback `fstyp`-probed filesystem admission stays finite

**Tier:** B (Implementation floor)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt, Registry→Diff→Gate

`docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed *where* the first local fallback executes.
This page fixes the next smaller but still costly choice:

> after the host has the removable device, which filesystem families may the first cut actually admit?

The answer is intentionally finite:

> **probe with `fstyp`, admit only `msdosfs`, `exfat`, `ufs`, and `cd9660` in the first cut, keep mounts read-only on the host, and fail closed on richer families until a later explicit lane earns them.**

See also:
- ADR: `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- previous boundary: `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- workflow doc: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- device authority: `docs/278-device-grants-and-devfs-rulesets.md`
- userspace filesystems: `docs/365-userspace-filesystems-puffs-fuse.md`

## Accepted boundary

### 1) Filesystem detection is explicit and typed before mount

The first local-fallback mount path must start with `fstyp`.
That gives the host a machine-parsable filesystem-family answer before it decides whether the medium belongs in this lane at all.

So the boundary is:

- classify the removable storage device,
- issue the session-scoped `device.attach.grant`,
- run `fstyp` on the host side,
- admit or deny based on a small reviewed allowlist,
- then perform the host-controlled **read-only** mount if and only if the family is admitted.

No file-extension guessing, no “try mounting several things until one works”, and no remembered convenience exceptions.

### 2) The first admitted family set is intentionally small

The first-cut allowlist is:

- `msdosfs`
- `exfat`
- `ufs`
- `cd9660`

This set is small on purpose:

- `msdosfs` and `exfat` cover the highest-value exchange media for B/C,
- `ufs` keeps same-family operational/admin media viable,
- `cd9660` keeps immutable ISO-like media obvious and honest,
- and the first local fallback still stays narrow enough to review as one implementation target.

### 3) `exfat` is real, but still adapter-shaped

This page deliberately chooses **to keep `exfat` in the first cut**.
That is a hard decision in favor of practical workstation/general-OS viability.

But the archive also stays honest that `exfat` is not “free” on FreeBSD:

- it relies on the explicit exFAT helper path,
- it should still be mounted **read-only** in this lane,
- and it should remain a reviewed compatibility-shaped dependency rather than ambient host convenience.

So the first cut says **yes to exFAT interoperability, no to pretending that means the lane is now open-ended.**

### 4) The first cut fails closed on richer families and provider semantics

The first local-fallback lane does **not** admit:

- `ext2fs`
- `ntfs`
- `zfs`
- `geli`
- unknown / unrecognized probe results
- nested filesystem/container images discovered as ordinary files

These denials are not accidents.
They keep the first cut honest about what it is **not** yet trying to solve:

- `ext2fs` is tempting, but modern ext volumes bring semantic expectations the first cut should not quietly inherit,
- `ntfs` widens helper/package compatibility pressure too early,
- `zfs` and `geli` are provider/pool/import stories rather than “mount an untrusted removable tree and project it into a disposable jail” stories,
- and image-in-file workflows deserve their own later typed lane instead of silent recursive parsing inside the same baseline ingest path.

### 5) Admit-once still means host-mounted read-only then projected into the jail

This page does **not** change the execution boundary from `docs/724-*`.
Even for admitted families:

- the host still keeps mount authority,
- the mount is still explicit and read-only,
- the disposable ingest worker still receives a projected tree through `mount.view`,
- and the jail still receives **no raw block-device nodes**.

So this is a filesystem-admission cut, not a mount-authority rollback.

## Canonical first-cut example stack

The first-cut example stack now has an explicit common-case probe story:

- `spec/examples/device.profile.removable-media-local-ingest.exfat.json`
- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/devfs.view.plan.removable-media-local-ingest.json`
- `spec/examples/mount.view.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`

Together they say:

- the removable device is classified as storage-only ingest material,
- the host uses `fstyp`,
- the admitted example family is `exfat`,
- the allowlist remains finite,
- and execution still stays host-mount → disposable-jail ingest.

## Why this cut is worth making now

Without this decision, the archive still pays a repeated implementation tax:

- coding cannot tell whether unsupported filesystems should fail closed or “best effort” mount anyway,
- support cannot explain why a given stick mounted or did not,
- B keeps asking for convenient compatibility while D keeps asking for auditable narrowness,
- and C keeps drifting toward “everything the host can mount is part of the baseline”.

This page stops that drift with one finite first-cut answer.

## What remains open

Still intentionally open:

- whether a later explicit compatibility lane should add `ext2fs`, `ntfs`, or HFS+,
- whether stronger microVM/device-domain parsing lanes should carry a broader family set,
- exact deny/recovery UX for unsupported media,
- and whether image-in-file import deserves a later dedicated typed plan/receipt family.

Last updated: 2026-03-26r456
