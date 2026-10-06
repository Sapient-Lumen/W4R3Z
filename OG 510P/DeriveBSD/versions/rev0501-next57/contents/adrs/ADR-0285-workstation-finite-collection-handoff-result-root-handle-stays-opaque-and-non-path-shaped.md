# ADR-0285: Workstation finite collection handoff result-root handle stays opaque and non-path-shaped

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` through `ADR-0284` already narrowed the first reviewed finite-collection handoff lane into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, fail-closed first-implementation top-level collisions, bounded manifest-derived review-surface path compression, optional non-authoritative advisory MIME, successful retrieve receipts that pin the exact created fresh root, receiver-local advisory placement hints, a receiver-local stable result-root handle that stays authoritative while any path/display snapshot remains advisory, and retrieve-frozen advisory display snapshots when present.

That still leaves one implementation-shaped ambiguity inside `RFC-0194`: **what stops an implementation from making the “stable result-root handle” just a dressed-up path string or URI?**

If the archive leaves that open, one implementation can mint a truly opaque local handle, another can serialize the current path into the handle field, and a third can smuggle bookmark-like reopen or sender-visible locator semantics behind a path-shaped token. That would reopen exactly the mutable-path and placement-authority drift the last few cuts just closed.

## Decision

For the first cut of the reviewed finite-collection handoff:

1. the authoritative **result-root handle** remains receiver-local and stable for the original retrieve outcome.
2. that handle must be **opaque and non-path-shaped** to callers and support/export readers in the contract-visible surface.
3. the handle must **not** be a filesystem path, URI, sender-provided reviewed name, destination-label string, or other human-facing placement text reused as the authoritative locator.
4. implementations may back the handle with bookmark ids, document ids, database keys, filesystem-handle adapters, or other local mechanisms, but those backend choices stay non-normative as long as the contract-visible handle remains opaque and non-path-shaped.
5. any human-facing path string, destination label, or display snapshot remains advisory only and follows `ADR-0284` when present.
6. any later lane that wants portable destination paths, bookmark-like reopen semantics, or path-derived authoritative locator text must return as a separate explicit RFC/ADR cut.

## Consequences

- The archive now closes the loophole where “handle-first” could still secretly mean “path-first with a different field name.”
- Support/export can treat the authoritative local join as a local opaque handle and the display/path text as descriptive only.
- Implementers keep backend freedom without drifting back toward path parsing or pathname stability folklore.
- Later richer reopen/bookmark portability work remains possible, but it must be explicit rather than sneaking in under this first reviewed retrieve lane.

## Follow-ups

This ADR fixes handle posture, not final schema spelling.
Open follow-ups remain:

- the exact schema field names and grammar for the opaque result-root handle,
- whether some export/support surfaces should redact or hash the opaque handle by default,
- and whether later successor receipts should carry explicit predecessor-handle joins.
