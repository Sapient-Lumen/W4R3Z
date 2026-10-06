# DeriveBSD rev0409: Finite-collection manifest design

Selected historical snapshot for the W4R3Z / OG 510P showcase. This page is a new editorial reconstruction dated 2026-10-06, written from the restored supplied archive after an interrupted assembly. It does not recover the exact bytes of the missing earlier editorial guide. The ZIP and source files retain their original bytes, wording and metadata.

## What to notice

A reviewed finite-collection handoff is shaped around a small exact manifest: normalized review path and member kind for every entry, plus payload digest and byte length for each regular file. Explicit directory entries remain reviewed members. Richer stat fidelity stays advisory or deferred.

## Identity and preserved material

- Original ZIP: [DeriveBSD-rev0409-2026.03.22.14.41-manifestentryfloorcontentidentityfirststatlight.zip](DeriveBSD-rev0409-2026.03.22.14.41-manifestentryfloorcontentidentityfirststatlight.zip)
- Filename revision label: `rev0409`
- Leading changelog cut: `2026-03-22r409`
- Original ZIP size: 4,375,995 bytes
- Extracted file members: 2,315
- Original ZIP SHA-256: `fb89145d37ae5b188d0f111219fcb2116cf722d7cfa91d4d2e62225c90956302`

The leading changelog and README “Last updated” line identify r409. The preserved README also carries `Version: 2026-03-22r395`. The older version line is retained as received.

The original file-member paths begin directly under `contents/`. The unchanged ZIP sits beside that tree. Original archive metadata remains in the ZIP; extracted filesystem timestamps are not claimed as a restoration of original metadata. Source dates and ZIP timestamps are carried metadata, not independently authenticated chronology. These are selected uploads, not a complete release or Git history.

## Read the source

- [README.md](contents/README.md)
- [CHANGELOG.md](contents/CHANGELOG.md)
- [docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md](contents/docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md)
- [rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md](contents/rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md)

## Evidence boundary

The focused document calls this an RFC-shaping cut, and RFC-0194 remains explicitly `draft`. It describes a distinct, finite, read-only handoff with regular files and explicit directories, while rejecting symlinks and special objects in the first cut. It does not finalize the richer schema family or demonstrate a shipped handoff implementation. The archival preservation manifest for this showcase is a separate curatorial record; its existence should not be mistaken for an implementation of this draft protocol.

This curation used static inspection and byte-integrity checks. It did not execute uploaded programs, checkers, bytecode, shell scripts or historical work orders. “Passed,” “validated,” and similar wording inside the source remains a carried project claim unless separately identified as a fresh curatorial check.

The recovered archival notes record that no repository-wide license grant was identified in a bounded earlier review. Public visibility does not establish reuse rights or full privacy clearance; see [archival notes](../../ARCHIVAL-NOTES.md) and the [preservation manifest](../../ARCHIVE-MANIFEST.json).

[Back to selected DeriveBSD history](../../README.md)
