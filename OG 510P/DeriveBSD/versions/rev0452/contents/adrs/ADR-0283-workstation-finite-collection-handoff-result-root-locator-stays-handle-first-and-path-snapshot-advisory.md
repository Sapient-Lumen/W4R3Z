# ADR-0283: Workstation finite collection handoff result-root locator stays handle-first and path-snapshot advisory

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` through `ADR-0282` already narrowed the first reviewed finite-collection handoff lane into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, fail-closed first-implementation top-level collisions, bounded manifest-derived review-surface path compression, optional non-authoritative advisory MIME, successful retrieve receipts that pin the exact created fresh root, and receiver-local advisory placement hints.

That still leaves one expensive ambiguity inside `RFC-0194`: **what kind of locator is the receipt actually supposed to carry for that exact created fresh root?**

If one implementation emits only a mutable path string, another emits only parent-plus-label prose, and a third emits an opaque local handle, then detached support/export still cannot compare receipts honestly. Later rename/move/import actions would keep competing with the original retrieve outcome, and the archive would quietly reintroduce path folklore even after it already decided that placement hints are receiver-local advisory state, not reviewed authority.

## Decision

For the first cut of the reviewed finite-collection handoff:

1. a successful retrieve receipt must carry a **receiver-local stable result-root handle** for the exact created fresh root.
2. that handle is the authoritative local result locator for the original retrieve outcome.
3. an optional human-readable path string, destination label, or display-path snapshot may appear, but it stays **advisory only**.
4. later rename/move/import/promote actions may mint their own receipts, but they do **not** retroactively redefine the original receipt's result-root handle or turn a later path into the original retrieve outcome.
5. the first cut does **not** require the handle to be portable across hosts or profiles, and it does **not** standardize one concrete backend such as bookmark ids, document ids, vnode/file handles, or database keys.

## Consequences

- Detached support/export can join to the original retrieve outcome without trusting mutable path text.
- The richer lane stays compatible with the archive's broader capability posture: stable local handles first, path/display text second.
- Profile-specific redaction/export policy keeps room to hide or suppress display-path text later without losing the authoritative local join key.
- A later lane that wants portable destination paths, sender-directed placement, or bookmark-like long-term reopen semantics must come back as an explicit RFC/ADR instead of inflating this first baseline.

## Follow-ups

This ADR fixes locator posture, not final schema spelling.
Open follow-ups remain:

- the exact field names for the authoritative handle and any advisory display-path snapshot,
- whether later import/promote receipts should carry predecessor-handle joins explicitly,
- and whether any later profile-specific export surfaces should reveal, redact, or omit advisory display-path text by default.
