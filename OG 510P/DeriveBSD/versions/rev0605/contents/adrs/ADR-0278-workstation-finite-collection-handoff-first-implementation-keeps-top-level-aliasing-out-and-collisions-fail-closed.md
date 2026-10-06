# ADR-0278: Workstation finite collection handoff first implementation keeps top-level aliasing out and collisions fail closed

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` through `ADR-0277` then narrowed the first cut into something close to a spec-worthy lane: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, and explicit B/C/D profile scope.

One practical ambiguity still remained open in `RFC-0194`: **should the first implementation support trusted-UI top-level aliasing at all**.
The archive had already made two narrower moves:
- top-level reviewed names are explicit reviewed state rather than silent broker repair, and
- collisions must not be auto-renamed away.

But keeping aliasing as a maybe inside the first implementation would still carry real cost:
- the first trusted review UI would need to become a rename/disambiguation editor rather than just a bounded review surface,
- the authoritative manifest would need one more reviewed state family before the basic collection lane is even implemented,
- support/export would inherit one more “was this the source name or the reviewed alias?” explanation burden,
- and collision handling would remain harder to reason about than a simple fail-closed answer.

That is a poor trade for the first implementation, especially now that the archive already has a coherent answer for broader tree/document authority and for later richer lanes.

## Decision

For the **first implementation** of the reviewed finite collection handoff family:

1. trusted-UI top-level aliasing is **not supported**.
2. each top-level selected member uses its normalized reviewed name directly.
3. if two top-level selected members collapse to the same normalized reviewed name, handoff creation must **fail closed**.
4. review/support surfaces may explain the collision and ask the user to revise the selection, but they do not mint reviewed alias state in the first implementation.
5. any future aliasing/disambiguation UX must return as a **distinct later RFC/ADR cut** with explicit typed reviewed state and exact evidence/export semantics rather than being quietly smuggled into the first implementation.

## Consequences

### Positive

- removes one of the last large UI/manifest-shape ambiguities from the first implementation path
- keeps the trusted review surface smaller and easier to reason about
- makes multi-root collision handling boring and portable: collide after normalization, then fail closed
- keeps the first implementation focused on reviewed membership, retrieve semantics, and evidence rather than rename UX

### Negative

- first implementations cannot rescue basename collisions with a reviewed alias affordance
- some practical multi-root handoffs will need the sender to revise selection/source names before creation succeeds
- a later explicit aliasing lane may still be worth designing if real usage proves the pressure is high

### Follow-up

Future RFC/ADR work may still define:
- explicit reviewed alias fields,
- exact receipt/export evidence for alias decisions,
- or a trusted UI review flow for collision disambiguation.

This ADR only fixes the first implementation boundary: **top-level aliasing stays out, and collisions fail closed**.
