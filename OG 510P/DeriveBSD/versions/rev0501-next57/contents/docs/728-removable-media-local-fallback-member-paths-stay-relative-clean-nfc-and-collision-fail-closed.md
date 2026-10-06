# Removable-media local fallback member paths stay relative-clean, NFC-canonical, and collision-fail-closed

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` already fixed the fallback boundary, `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed the host-mount→disposable-jail execution floor, `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` already fixed the finite admitted filesystem set, `docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md` already fixed inert mount posture, and `docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md` already fixed the first member-kind floor.

This page closes the next smaller implementation seam:

> **the first removable-media local-ingest lane now uses one tiny portable member-path grammar: relative-clean Unicode NFC text, slash-separated, collision-fail-closed, and no silent auto-rename.**

See also:
- ADR: `adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`
- analogous workstation path-normalization cuts: `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`, `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- removable-media posture by profile: `docs/458-removable-media-and-usb-posture-by-profile.md`

## Why this needs a hard decision

The first local-ingest lane now knows **which devices** it can touch, **which filesystems** it can admit, **how mounts must be hardened**, and **which member kinds** it may walk.
But it still did not say what the walked names are allowed to mean.

That is expensive to leave open because the admitted first-cut filesystem families already differ enough to create hidden behavior:
- `mount_msdosfs(8)` exposes longname/shortname and locale-conversion choices,
- `mount.exfat-fuse(8)` documents case-insensitive behavior,
- and `mount_cd9660(8)` can expose Joliet/Rock Ridge/version-handling differences.

If the archive does not choose one portable member-path language now, the first implementation will quietly inherit those naming semantics as if they were reviewed/imported truth.

## Accepted cut

For the first host-local removable-media ingest lane:

- every admitted member path is a **non-empty member-root-relative UTF-8 path normalized to Unicode NFC**
- **`/` is the only separator**; backslash is never a separator
- normalized member paths have **no leading slash**, **no trailing slash**, **no empty segments**, and **no `.` / `..` segments**
- **U+0000 NUL is forbidden**
- explicit directories are identified by **member kind**, not by a trailing slash marker
- if two discovered source members collapse to the same normalized member path after normalization, ingest creation must **fail closed**
- the first cut performs **no silent auto-rename, wrapper-root injection, volume-label prefixing, or copy-style suffix repair**
- normalized member paths are **review/import identity paths**, not destination-placement hints or source writeback handles

## Why this is the right first cut

### 1) It makes the first admitted filesystem set portable enough to share one ingest story

The archive deliberately admitted a small first-cut filesystem set for B/C.
That only stays coherent if the member-path surface is smaller than the union of all helper quirks.

### 2) It keeps import identity separate from materialization convenience

The first local-ingest lane is still content-import-shaped.
It should identify what was reviewed/imported, not smuggle in destination-layout policy or source-device folklore.

### 3) It avoids teaching the first cut to silently repair hostile or ambiguous trees

Silent renaming, wrapper-root insertion, or case-fold-based repair would turn implementation policy into reviewed/imported identity.
Failing closed is cheaper and more honest.

## What this still does not decide

This page does **not** decide whether a later compatibility lane should preserve raw source names as advisory metadata.
It does **not** decide whether a later filesystem-fidelity lane should preserve case-folding aliases, richer path metadata, or volume labels.
It does **not** decide whether a later tree/collection-shaped import lane should mint a dedicated manifest artifact family.
It does **not** decide whether a later explicit lane should support reviewed aliasing UX for collisions.

Those remain valid later questions, but the archive no longer leaves first-cut member-path semantics implicit.

## Related docs

- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`
- `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`

Last updated: 2026-03-26r459
