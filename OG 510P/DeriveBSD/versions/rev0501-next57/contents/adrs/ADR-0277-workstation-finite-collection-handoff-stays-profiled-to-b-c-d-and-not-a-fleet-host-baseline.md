# ADR-0277: Workstation finite collection handoff stays profiled to B/C/D and not a fleet-host baseline

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` through `ADR-0276` then narrowed the first cut into a concrete lane: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, and fresh-rooted retrieve.

One practical ambiguity still remained open in `RFC-0194`: **which product profiles should actually treat this richer lane as supported**.
The archive metadata on the queue docs already leaned `B/C/D`, but without an explicit decision two different implementation cultures could still claim alignment while disagreeing about whether secure fleet hosts should also grow the same ad-hoc reviewed file-ferry surface under “operator posture” wording.

That drift would be costly:
- **A / fleet_host** would start growing human file-ferry convenience on hosts whose baseline story should stay rollout, support-bundle, import/export, or breakglass shaped rather than ambient “copy these files around” operations.
- **B / workstation** and **C / general_os** would lose the clarity that this richer lane is solving a real human-facing file-handoff problem rather than becoming a universal host admin primitive.
- **D / appliance_factory** would lose the ability to keep the lane bounded to explicit factory / maintenance / review stations and quarantined ingest/export workflows instead of accidentally normalizing it into unattended production-image runtime convenience.

## Decision

For the first reviewed finite collection handoff family:

1. the supported profile scope is **B/C/D**, not **A**.
2. **A / fleet_host** does **not** treat this richer lane as a baseline supported host workflow.
3. when **D / appliance_factory** uses this lane at all, it is for explicit factory, maintenance, approval, or quarantined ingest/export stations and workflows — **not** as ambient production-image runtime convenience.
4. when **A / fleet_host** needs bytes to move in or out, the baseline answers remain artifacted rollout/import/export/support/breakglass lanes rather than widening this workstation finite-collection handoff family.
5. if fleet-host operations later prove they need a richer host-local file-ferry surface, that must return as a **distinct later RFC/ADR lane** with its own artifact family and operator semantics instead of silently widening this family.

## Consequences

### Positive

- keeps fleet-host operations aligned with artifacted rollout/support discipline instead of ad-hoc host file ferrying
- makes the already implied `B/C/D` applicability explicit and portable across implementations
- preserves room for D's human-reviewed ingest/export realities without pretending shipped production images want workstation-style convenience
- reduces the risk that “all product shapes without forks” gets misread as “every richer lane belongs on every host”

### Negative

- closes off a tempting short-term convenience path for fleet-host operators who want the same reviewed collection handoff semantics everywhere
- forces any future richer A-specific operator file ferry to justify itself as a separate lane instead of piggybacking on this one
- requires nearby docs and guardrails to say the profile boundary out loud instead of relying on metadata alone

### Follow-up

Future RFC/ADR work may still define:
- a distinct A-specific operator artifact ferry,
- tighter D-specific maintenance-station posture,
- or exact schema fields that let B/C/D implementations advertise support level.

This ADR only fixes the first product-scope boundary: **the reviewed finite collection handoff family stays profiled to B/C/D and is not a fleet-host baseline**.
