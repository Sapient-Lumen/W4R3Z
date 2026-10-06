# ADR-0317: Removable-media local fallback ingest walk stays physical, root-pinned, and regular-files-plus-explicit-directories only

Date: 2026-03-26  
Status: Accepted

## Context

`ADR-0313` fixed that imperfect-hardware removable-media fallback stays storage-only, session-scoped, read-only-first, and quarantine-first.
`ADR-0314` fixed the first execution floor: host-controlled attach and read-only mount, then a disposable no-network jail through `mount.view` with block-empty `devfs` there.
`ADR-0315` fixed the first finite `fstyp`-probed filesystem-admission set.
`ADR-0316` fixed that admitted mounted trees stay inert input only under `ro,nosuid,noexec,nosymfollow,untrusted`.

That still left one more expensive ambiguity in the first buildable lane:
**what member kinds and path-resolution semantics are allowed when the ingest worker walks `/ingest`?**

Without a hard answer here, the archive can still quietly reintroduce ambient authority through the mounted tree:
- following symlinks can escape the reviewed input root or make ingest depend on namespace resolution folklore,
- preserving device nodes, FIFOs, or sockets turns a boring import lane back into active endpoint semantics,
- and preserving hardlink topology pushes filesystem-fidelity expectations into a lane that is supposed to stay content-import-shaped.

The archive already solved the analogous member-kind problem for the first richer workstation finite-collection handoff in `ADR-0268`.
The removable-media fallback should reuse the same narrow lesson instead of inventing a special exception.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0316`:

1. the ingest walk stays **physical** and **root-pinned** to the mounted `/ingest` tree.
2. the first cut admits only **regular files** and **explicit directories** as ingest-walk member kinds.
3. **symlinks are not part of the first cut**; the ingest lane does not silently follow, preserve, or reinterpret them.
4. **special filesystem objects are not part of the first cut**, including device nodes, FIFOs, sockets, and equivalent active or host-coupled objects.
5. unsupported member kinds **fail closed** instead of being silently skipped, followed, or normalized away.
6. **hardlink topology is not preserved in the first cut**; if multiple paths refer to the same underlying file, the lane may treat them only as independent regular-file path selections or deny them, but it must not claim filesystem-topology fidelity.
7. any later symlink-preserving, symlink-following, special-object, image-in-file, or filesystem-fidelity-preserving lane must come back as an explicit follow-on RFC/ADR decision.

## Consequences

- The first removable-media fallback stays a boring host-mount → disposable-jail ingest lane rather than an accidental namespace-resolution or endpoint-activation lane.
- Support can explain denials concretely: admitted filesystem family is necessary but not sufficient; unsupported member kinds still fail closed.
- Implementation can stay on root-fd-relative traversal and path-beneath discipline instead of mixing “whatever the host resolver did” into the evidence story.
- The lane remains honest for B/C while still not widening A/D’s baseline import surface.

## Alternatives considered

- **Follow symlinks during ingest:** rejected because it turns a reviewed input tree back into path-resolution folklore and can widen authority beyond the mounted root.
- **Preserve symlink or special-object members for later handling:** rejected because the first cut is supposed to stay import/content-shaped, not provider/filesystem-fidelity-shaped.
- **Silently skip unsupported members:** rejected because operator review, support explanations, and import receipts would drift away from the real observed tree.
- **Preserve hardlink topology in the first cut:** rejected because that pushes filesystem-fidelity and alias-topology semantics into a lane that is intentionally much smaller than a filesystem-preserving archive/import subsystem.

## Related

- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
