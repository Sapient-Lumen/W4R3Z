# ADR-0319: Removable-media local fallback keeps owner/mode/mtime/xattr fidelity out of the first lane

Date: 2026-03-26  
Status: Accepted

## Context

`ADR-0313` fixed that imperfect-hardware removable-media fallback stays storage-only, session-scoped, read-only-first, and quarantine-first.
`ADR-0314` fixed that the first buildable local fallback keeps attach and mount authority on the host and projects a read-only mounted tree into a disposable no-network jail.
`ADR-0315` fixed that the host probes with `fstyp` and admits only a finite first-cut filesystem set.
`ADR-0316` fixed that mounted trees stay inert and the mount-hardening tuple is fail-closed.
`ADR-0317` fixed that the ingest walk stays physical, root-pinned, and regular-files-plus-explicit-directories only.
`ADR-0318` fixed that admitted member paths stay relative-clean, Unicode NFC, and collision-fail-closed.

One more portability loophole remained:
**once the worker is walking admitted members with one canonical path grammar, is source filesystem metadata part of the reviewed/imported identity of the first lane?**

Leaving that open is expensive because the admitted families already disagree about metadata semantics enough to create quiet host-specific behavior:

- `mount_msdosfs(8)` can remap ownership and permission ceilings with `-u`, `-g`, `-m`, `-M`, and also has filename-conversion knobs.
- `mount.exfat-fuse(8)` can remap `uid`, `gid`, and `umask`/`dmask`/`fmask`, and documents case-insensitive behavior.
- `mount_cd9660(8)` can synthesize owner/group/mask defaults when Rock Ridge or extended attributes are absent, and can change naming behavior with Joliet / Rock Ridge / version-number options.

If the archive does not choose a metadata floor now, the first implementation can quietly treat receiver-local mount/render choices as if they were reviewed/imported truth.
That would widen a narrow content-import lane into an accidental filesystem-fidelity lane.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0318`:

1. the authoritative reviewed/imported contract stays **path/kind/payload-first**.
2. owner/group fidelity is **out of this lane entirely**.
3. mode-bit fidelity is **out of this lane entirely**.
4. mtime / atime / birthtime / last-modified fidelity is **out of this lane entirely**.
5. xattr / ACL / capability / DOS-attribute / similar filesystem-metadata fidelity is **out of this lane entirely**.
6. source volume labels, mount-time locale/codepage choices, and receiver-local mount option effects are **not reviewed/import identity** in this lane.
7. receiver-local materialization may still apply local owner/mode/time/xattr defaults or preserve some metadata as a convenience, but those outcomes are **receiver-local realization detail**, not portable reviewed state and not detached evidence authority for the import.
8. any later lane that wants filesystem-metadata preservation must return as a **separate explicit RFC/ADR cut** instead of widening this first removable-media lane.

## Consequences

- The first removable-media fallback keeps one coherent cross-filesystem story for B/C instead of inheriting helper-specific ownership/mode/time folklore.
- `device.attach.grant`, `mount.view`, and `content.import.plan` can stay honest about what authority exists: a reviewed path/kind/payload ingest lane, not a filesystem-preserving archive contract.
- A/D do not quietly inherit a wider local-ingest semantics story under the same first-cut fallback.

## Alternatives considered

- **Preserve owner/mode/mtime/xattr fidelity inside the same first lane:** rejected because it silently turns the lane into a filesystem-preserving adapter with higher normalization and support burden.
- **Keep metadata posture open until implementation:** rejected because the admitted filesystem families already expose enough ownership/mode/time knobs that “implementation detail” would become the real contract.
- **Make host-local materialized metadata authoritative after import:** rejected because it promotes receiver-local mount/materialization choices into reviewed/imported truth.

## Related

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
- `adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`
- `adrs/ADR-0286-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/729-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`
