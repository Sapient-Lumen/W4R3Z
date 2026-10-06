# ADR-0281: Workstation finite collection handoff receipts pin the exact created fresh root

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` through `ADR-0280` already narrowed the first reviewed finite-collection handoff lane into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, fail-closed first-implementation top-level collisions, bounded manifest-derived review-surface path compression, and optional non-authoritative advisory MIME.

That leaves one practical support/export seam still under-specified even after fresh-rooted retrieve is accepted: **what exact result a successful retrieve receipt has to point at on the receiver side**.

Without a decision here, honest implementations can all claim to honor the same fresh-root rule while leaving detached tooling to reconstruct where the reviewed collection actually landed:
- one receipt points only at the manifest digest,
- another points only at the parent directory the user picked,
- another emits success prose with no result locator at all,
- and another silently treats a later rename/move/import as if it described the original retrieve outcome.

That would put broker logs, local history, or support notes back in charge of answering a question the archive should make boring: **which fresh root did this retrieve actually create?**

## Decision

For the first cut of the reviewed finite-collection handoff:

1. every successful retrieve/materialization receipt must pin the exact **created fresh destination root** for that retrieve.
2. that receipt-visible locator names the **result root that was actually created**, not merely a parent chooser hint, destination label, or requested placement prompt.
3. later rename/move/import/promote actions may mint their own receipts, but they do not retroactively redefine the original retrieve receipt's result root.
4. support/export/detached explanation should be able to answer both **which reviewed manifest digest was retrieved** and **which fresh root was created** without reopening broker-local memory or local-history guesswork.
5. exact local locator syntax remains open for the RFC/spec cut, but the portable contract is no longer optional: a pathless or parent-only success receipt is insufficient.

## Consequences

### Positive

- makes the already accepted fresh-root rule queryable instead of rhetorical
- gives support/export one boring answer to “where did that reviewed collection land?”
- prevents later rename/move/import state from laundering the original retrieve outcome
- keeps the richer lane aligned with the archive's general exact-join / exact-result discipline

### Negative

- forces the future schema family to carry one more exact result field instead of treating retrieve success as unstructured prose
- may require careful local-path redaction/export handling in later profile-specific support surfaces
- removes convenience room for implementations that wanted to treat parent chooser state as good enough evidence

### Follow-up

Future RFC/spec work may still define:
- the exact field names and grammar for the result-root locator,
- profile-specific redaction/export posture for local placement detail,
- or later import/promote receipts that deliberately move the materialized tree elsewhere.

This ADR only fixes the result-evidence rule: **a successful reviewed finite-collection retrieve receipt must pin the exact created fresh root**.
