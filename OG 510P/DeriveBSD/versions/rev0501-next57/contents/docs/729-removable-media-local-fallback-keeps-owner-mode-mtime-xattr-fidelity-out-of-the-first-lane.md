# Removable-media local fallback keeps owner/mode/mtime/xattr fidelity out of the first lane

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` already fixed the fallback boundary, `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed the host-mount→disposable-jail execution floor, `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` already fixed the finite admitted filesystem set, `docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md` already fixed inert mount posture, `docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md` already fixed the first member-kind floor, and `docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md` already fixed the portable member-path grammar.

This page closes the next smaller implementation seam:

> **the first removable-media local-ingest lane now keeps owner/group, mode-bit, mtime, xattr, ACL, and similar filesystem-metadata fidelity out of the reviewed/imported contract entirely.**

See also:
- ADR: `adrs/ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`
- analogous workstation cut: `docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- removable-media posture by profile: `docs/458-removable-media-and-usb-posture-by-profile.md`

## Why this needs a hard decision

The first local-ingest lane now knows **which devices** it can touch, **which filesystems** it can admit, **how mounts must be hardened**, **which member kinds** it may walk, and **which member-path grammar** is authoritative.
But it still did not say whether source filesystem metadata belongs to the same reviewed/imported truth surface.

That is expensive to leave open because the admitted first-cut filesystem families already disagree enough to create hidden behavior:
- `mount_msdosfs(8)` can remap ownership and permission ceilings with `-u`, `-g`, `-m`, and `-M`,
- `mount.exfat-fuse(8)` can remap `uid`, `gid`, and `umask`/`dmask`/`fmask`,
- and `mount_cd9660(8)` can synthesize owner/group/mask defaults when Rock Ridge or extended attributes are absent.

If the archive does not choose a metadata floor now, the first implementation will quietly inherit helper-specific ownership/mode/time behavior as if it were reviewed/imported identity.

## Accepted cut

For the first host-local removable-media ingest lane:

- the authoritative reviewed/imported contract stays **path/kind/payload-first**
- owner/group fidelity is **out of this lane entirely**
- mode-bit fidelity is **out of this lane entirely**
- mtime / atime / birthtime / last-modified fidelity is **out of this lane entirely**
- xattr / ACL / capability / DOS-attribute / similar filesystem-metadata fidelity is **out of this lane entirely**
- source volume labels, mount-time locale/codepage choices, and receiver-local mount option effects are **not reviewed/import identity** in this lane
- receiver-local materialization may still apply local owner/mode/time/xattr defaults or preserve some metadata as a convenience, but those outcomes are **receiver-local realization detail**, not portable reviewed state and not detached evidence authority for the import
- any future filesystem-preserving or metadata-fidelity lane must return as a **separate explicit RFC/ADR cut** instead of widening this first removable-media lane

## Why this is the right first cut

### 1) It keeps the admitted filesystem set portable enough to share one ingest story

The archive deliberately admitted a small first-cut filesystem set for B/C.
That only stays coherent if the reviewed/import contract is smaller than the union of their ownership, permission, timestamp, and extended-attribute quirks.

### 2) It keeps import identity separate from local materialization convenience

The first local-ingest lane is still content-import-shaped.
It should identify what was reviewed/imported, not quietly promote host-local mount or materialization choices into reviewed truth.

### 3) It prevents filesystem-preserving archive creep

Once owner/mode/mtime/xattr fidelity becomes normative here, the lane stops being a narrow removable-media import contract and starts becoming a filesystem-preserving adapter.
That might be worth designing later, but only as a separate explicit lane.

## What this still does not decide

This page does **not** decide whether a later compatibility lane should preserve raw source metadata as advisory evidence.
It does **not** standardize one receiver-local materialization policy for owner/mode/time defaults.
It does **not** decide whether a later filesystem-fidelity lane should preserve ACLs, xattrs, or device-native flags.
It does **not** remove the already accepted path/kind/payload, inert-mount, and collision-fail-closed cuts.

Those remain distinct questions, but the archive no longer leaves this first removable-media lane half-way between a portable import contract and a filesystem-preserving archive format.

## Related docs

- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`
- `docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`

Last updated: 2026-03-26r460
