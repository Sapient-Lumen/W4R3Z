# DeriveBSD rev0605: Fixture repository snapshot admission

Selected historical snapshot for the W4R3Z / OG 510P showcase. This page is a new editorial reconstruction dated 2026-10-06, written from the restored supplied archive after an interrupted assembly. It does not recover the exact bytes of the missing earlier editorial guide. The ZIP and source files retain their original bytes, wording and metadata.

## What to notice

The latest supplied snapshot describes a local dry-run runtime that admits a byte-bound fixture repository snapshot before package catalog projection and dependency closure. Its current-status documents also make the unfinished product boundary explicit: the executable core, authoritative package inputs and real host behavior still need work. Read that admission alongside the growing evidence machinery.

## Identity and preserved material

- Original ZIP: [DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten.zip](DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten.zip)
- Filename revision label: `rev0605`
- Leading changelog cut: `2026-06-18r630`
- Original ZIP size: 7,363,788 bytes
- Extracted file members: 3,462
- Original ZIP SHA-256: `8228e0e3492b1ff6978aac230199efe2140efbc143c01d29ef1cead23a4a84e2`

The filename revision label is `rev0605`; the leading changelog, current README and session review identify semantic cut `2026-06-18r630`. The session review explicitly records the package revision and semantic cut separately. Older compatibility notes inside the README remain historical source text.

The original file-member paths begin directly under `contents/`. The unchanged ZIP sits beside that tree. Original archive metadata remains in the ZIP; extracted filesystem timestamps are not claimed as a restoration of original metadata. Source dates and ZIP timestamps are carried metadata, not independently authenticated chronology. These are selected uploads, not a complete release or Git history.

## Read the source

- [README.md](contents/README.md)
- [CHANGELOG.md](contents/CHANGELOG.md)
- [docs/current/runtime-golden-thread.md](contents/docs/current/runtime-golden-thread.md)
- [docs/current/start-here-now.md](contents/docs/current/start-here-now.md)
- [validation/runtime-golden-thread/current/run.summary.json](contents/validation/runtime-golden-thread/current/run.summary.json)
- [validation/runtime-package-repository/current/snapshot.json](contents/validation/runtime-package-repository/current/snapshot.json)
- [session-reviews/DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten-review.md](contents/session-reviews/DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten-review.md)

## Evidence boundary

The preserved run summary reports `cloudtainer-local-dry-run`, the lock → plan → build → activate → explain → rollback sequence, and `no-freebsd-system-mutation`. These are carried run records, not a fresh execution by the curator. The repository snapshot explicitly sets `authoritative_package_index` to false and identifies checked-in fixture material. The current README calls the project pre-product and expressly withholds claims of an authoritative FreeBSD package index, actual `bectl` activation, bhyve launch or imported real-host proof. The session review’s reported 52 passing release-critical checks were not rerun here. Historical host-proof work orders are preserved context, not current instructions to run them.

This curation used static inspection and byte-integrity checks. It did not execute uploaded programs, checkers, bytecode, shell scripts or historical work orders. “Passed,” “validated,” and similar wording inside the source remains a carried project claim unless separately identified as a fresh curatorial check.

The recovered archival notes record that no repository-wide license grant was identified in a bounded earlier review. Public visibility does not establish reuse rights or full privacy clearance; see [archival notes](../../ARCHIVAL-NOTES.md) and the [preservation manifest](../../ARCHIVE-MANIFEST.json).

[Back to selected DeriveBSD history](../../README.md)
