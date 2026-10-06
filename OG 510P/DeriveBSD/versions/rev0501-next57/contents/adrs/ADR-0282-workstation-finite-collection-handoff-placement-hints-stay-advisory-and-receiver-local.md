# ADR-0282: Workstation finite collection handoff placement hints stay advisory and receiver-local

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` through `ADR-0281` already narrowed the first reviewed finite-collection handoff lane into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, fail-closed first-implementation top-level collisions, bounded manifest-derived review-surface path compression, optional non-authoritative advisory MIME, and successful retrieve receipts that pin the exact created fresh root.

That leaves one adjacent placement-authority seam still under-specified: **does the first richer lane also standardize sender-directed destination placement or reviewed parent-folder authority on the receiver side?**

Leaving that open would make the first implementation heavier and easier to drift:
- one implementation could let the sender or reviewed artifact require “place this under Downloads/Reports”,
- another could treat a destination label as authoritative reviewed state,
- and a third could keep parent choice purely local UI and still claim the same lane.

That is not a harmless UI difference. It decides whether the richer lane remains a reviewed finite collection handoff or quietly becomes a sender-directed file-placement protocol with profile-specific path folklore, policy baggage, and new laundering surface around local namespace choices.

The archive already decided that reviewed identity is the normalized manifest plus the exact created fresh root in the success receipt. It should not also smuggle destination-parent authority into the first cut.

## Decision

For the first cut of the reviewed finite-collection handoff:

1. any parent chooser, destination label, suggested folder, or “save into …” affordance stays **receiver-local advisory UI state**.
2. such placement hints are **not authoritative reviewed state**.
3. the grant, authoritative manifest, and receipt-visible reviewed identity remain complete without carrying a sender-directed destination parent or reviewed placement hint.
4. a successful retrieve receipt still pins the exact created fresh root, but that does **not** make the earlier chooser hint or destination prompt authoritative reviewed input.
5. implementations may offer local placement convenience UI, but verification, review, support/export joins, and detached explanation must not depend on parent-hint text or sender-directed path folklore.
6. any later lane that wants reviewed placement policy, sender-directed destination targets, or profile-specific drop-zone semantics must return as a **later explicit RFC/ADR cut**.

## Consequences

### Positive

- keeps the first richer lane focused on reviewed collection identity instead of receiver-local namespace policy
- avoids turning parent chooser text or destination labels into hidden cross-profile authority
- keeps support/export anchored to exact result evidence rather than to mutable or advisory placement prompts
- makes later placement-policy work easier to isolate as a separate deliberate lane

### Negative

- first implementations cannot treat sender-suggested destination folders as portable reviewed contract
- some UX ideas that want “drop this exactly here” semantics now need a later explicit lane
- implementations must explain the difference between local placement convenience and reviewed authority

### Follow-up

Future RFC/spec work may still define:
- whether any later lane wants sender-directed destination placement,
- whether profile-specific placement policy deserves typed review or approval,
- or whether advisory placement hints need a canonical vocabulary when present.

This ADR only fixes the first placement-authority boundary: **placement hints stay advisory and receiver-local, not authoritative reviewed state**.
