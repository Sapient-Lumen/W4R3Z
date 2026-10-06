# ADR-0318: Removable-media local fallback member paths stay relative-clean, NFC-canonical, and collision-fail-closed

Date: 2026-03-26  
Status: Accepted

## Context

`ADR-0313` fixed that imperfect-hardware removable-media fallback stays storage-only, session-scoped, read-only-first, and quarantine-first.
`ADR-0314` fixed the first execution floor: host-controlled attach and read-only mount, then a disposable no-network jail through `mount.view` with block-empty `devfs` there.
`ADR-0315` fixed the first finite `fstyp`-probed filesystem-admission set.
`ADR-0316` fixed that admitted mounted trees stay inert input only under `ro,nodev,nosuid,noexec,nosymfollow`.
`ADR-0317` fixed that the first ingest walk stays physical, root-pinned, and regular-files-plus-explicit-directories only.

That still left one more expensive ambiguity in the first buildable lane:
**once the worker is walking admitted regular files and directories beneath `/ingest`, what exact member-path language is authoritative for review, receipts, and implementation behavior?**

Without a hard answer here, the archive can still quietly inherit host/filesystem naming folklore:
- FAT-style helpers can expose longname/shortname and locale-conversion choices,
- exFAT is case-insensitive,
- ISO-9660/Joliet/Rock Ridge media can present more than one naming story,
- and implementations can otherwise disagree about slashes, dot segments, Unicode normalization, or collision repair while claiming to ingest the same tree.

The archive already solved the analogous path-normalization problem for the first richer workstation finite-collection handoff in `ADR-0272` and `ADR-0273`.
The removable-media fallback should reuse the same narrow lesson instead of leaving member paths implicit.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0317`:

1. every admitted member path is interpreted as a **non-empty, member-root-relative UTF-8 path normalized to Unicode NFC**.
2. **`/` is the only separator**; backslash is never a separator.
3. normalized member paths have **no leading slash**, **no trailing slash**, **no empty segments**, and **no `.` / `..` segments**.
4. **U+0000 NUL is forbidden** in member-path text.
5. explicit directories are identified by **member kind**, not by a trailing slash convention.
6. if two discovered source members collapse to the same normalized member path after normalization, ingest creation must **fail closed**.
7. the first cut **does not silently auto-rename**, inject wrapper roots, prepend volume labels, or append copy-style suffixes to repair collisions.
8. normalized member paths are **review/import identity paths**, not destination-placement hints or source writeback handles.
9. any later raw-name-preserving, case-fold-aware aliasing, wrapper-root, or filesystem-fidelity lane must come back as an explicit follow-on RFC/ADR decision.

## Consequences

- The first removable-media fallback now has one portable member-path language instead of replaying whatever the admitted source filesystem helper happened to expose.
- Receipts, review surfaces, and support bundles can compare imported trees without reimplementing host/path cleanup folklore.
- B/C stay implementable on imperfect hardware without silently growing into a filesystem-preserving archive/import subsystem.
- A/D do not inherit a wider ambient ingest namespace under the same first-cut local-fallback story.

## Alternatives considered

- **Treat source member names as raw filesystem output with no canonicalization:** rejected because canonical-equivalent Unicode spellings, slash cleanup, and dot-segment handling would remain hidden implementation state.
- **Allow silent auto-rename or wrapper-root repair on collisions:** rejected because it changes reviewed/imported identity while pretending the same source tree was ingested.
- **Preserve source volume labels, provider IDs, or parent paths as automatic prefixes:** rejected because that smuggles source-local placement folklore into the reviewed namespace.
- **Defer path grammar entirely to a later compatibility lane:** rejected because the first admitted filesystems already differ enough that waiting would make the first implementation non-portable.

## Related

- `adrs/ADR-0272-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `adrs/ADR-0273-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`
