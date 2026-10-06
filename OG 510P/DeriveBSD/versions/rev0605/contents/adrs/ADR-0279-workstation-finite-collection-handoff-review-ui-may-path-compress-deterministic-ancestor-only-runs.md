# ADR-0279: Workstation finite collection handoff review UI may path-compress deterministic ancestor-only runs

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` through `ADR-0278` then narrowed the first cut into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, and fail-closed first-implementation top-level collisions.

That leaves one smaller but still practical review-surface question open in `RFC-0194`: **must trusted review UIs literally render every explicit ancestor directory row, or may they compress purely structural path runs without changing authoritative reviewed state?**

Leaving that open would keep the first richer lane explicit in artifact bytes but still fuzzy in the trusted UI. One implementation could dump every explicit ancestor row as a giant tree, another could compact paths ad hoc, and a third could hide structure in source-path breadcrumbs. All three would claim to review the same collection while giving materially different answers to the operator question “what exactly did I review?”

The archive does not need a file-manager clone here, but it also does not need to force every honest implementation into a noisy fully-expanded tree when the authoritative manifest already carries enough structure to derive a smaller deterministic display.

## Decision

For the first implementation/review surface of the reviewed finite collection handoff family:

1. the **authoritative manifest remains fully explicit and ancestor-closed**; no collapsed display becomes authoritative state.
2. trusted review UIs **may** visually path-compress **deterministic ancestor-only directory runs** for legibility.
3. a collapsible run is a contiguous chain of explicit directory entries derived from the authoritative manifest where each directory in the chain has exactly one reviewed child directory and no direct reviewed file children.
4. empty directories, branch points, and ordinary file rows remain individually visible; the UI must not collapse away the fact that they are distinct reviewed members.
5. any collapsed presentation must be derived only from the authoritative manifest, not from source filesystem breadcrumbs, hidden broker memory, or destination-placement state.
6. the trusted UI must be able to reveal the full explicit rows before approval/export/support, and support/export surfaces continue to rely on the full authoritative manifest rather than collapsed shorthand.
7. any richer tree-view/editor affordance beyond this bounded path-compression rule is a **later explicit RFC/ADR cut**.

## Consequences

### Positive

- keeps the authoritative review/export artifact exact while allowing a smaller trusted review surface
- reduces visual noise from ancestor-closure without erasing real reviewed members
- gives implementations a bounded legibility move that does not require inventing a general file-manager UI
- keeps support/export answers stable because collapsed display never replaces the explicit manifest

### Negative

- adds one more trusted-UI presentation rule for implementations to honor
- some fully-expanded review UIs may still be simpler to ship first, even if they are noisier
- richer tree affordances remain intentionally deferred, so this does not solve every large-collection legibility problem

### Follow-up

Future RFC/ADR work may still define:
- whether path-compressed review should become the default instead of merely allowed,
- whether detached viewers should standardize one exact compressed presentation,
- or whether richer tree-focused review/search/filter affordances are worth the extra trusted-surface complexity.

This ADR only fixes the first review-surface boundary: **authoritative manifest explicit, bounded deterministic path-compression allowed**.
