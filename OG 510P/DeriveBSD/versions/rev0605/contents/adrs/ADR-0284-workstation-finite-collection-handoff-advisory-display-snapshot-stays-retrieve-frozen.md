# ADR-0284: Workstation finite collection handoff advisory display snapshot stays retrieve-frozen

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` through `ADR-0283` already narrowed the first reviewed finite-collection handoff lane into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, fail-closed first-implementation top-level collisions, bounded manifest-derived review-surface path compression, optional non-authoritative advisory MIME, successful retrieve receipts that pin the exact created fresh root, receiver-local advisory placement hints, and a receiver-local stable result-root handle that stays authoritative while any path/display snapshot remains advisory.

That still leaves one smaller but practical ambiguity inside `RFC-0194`: **if a receipt does carry an advisory human-facing path/display snapshot, is that snapshot allowed to drift later under the same retrieve story?**

If the archive leaves that open, one implementation could record the retrieve-time snapshot once, another could keep rewriting it after local rename/move/import, and a third could show only a current path. Support/export would then have to guess whether the human-facing label was describing the original retrieve result or the object's latest local location. That is unnecessary drift for a lane that is supposed to be close to implementable.

## Decision

For the first cut of the reviewed finite-collection handoff:

1. when a successful retrieve receipt carries any advisory human-facing path string, destination label, or display-path snapshot for the created fresh root, that text is a **retrieve-time snapshot**.
2. that advisory snapshot is **retrieve-frozen** for the lifetime of that original retrieve receipt; later local rename/move/import/promote actions do **not** silently rewrite it in place.
3. later acts may mint their own receipts with their own current human-facing path/display snapshots, but those are successor observations, not retroactive edits of the original retrieve outcome.
4. the original retrieve receipt remains valid even when the advisory snapshot is absent, redacted, shortened, or filtered on some export/support surface.
5. the authoritative local result locator remains the receiver-local stable result-root handle from `ADR-0283`; this ADR only freezes the optional descriptive text so it cannot drift under that same handle.

## Consequences

- Support/export can treat any advisory label/path text on the original retrieve receipt as a stable retrieve-time note rather than wondering whether it was rewritten later.
- The archive keeps human-facing convenience text without letting it quietly become a mutable “current location” truth surface.
- Later rename/move/import/promote lanes stay honest: if they want to describe the current local location, they must mint successor receipts instead of mutating old evidence.
- A later lane that wants one mutable current-location story, durable bookmark semantics, or automatic “latest local path” projection must come back as an explicit RFC/ADR instead of inflating this baseline.

## Follow-ups

This ADR fixes snapshot continuity, not final schema spelling.
Open follow-ups remain:

- the exact field names for any retrieve-time advisory display snapshot,
- whether later move/import/promote receipts should carry predecessor-handle joins explicitly,
- and whether some profile-specific export surfaces should omit or redact retrieve-time display snapshots by default.
