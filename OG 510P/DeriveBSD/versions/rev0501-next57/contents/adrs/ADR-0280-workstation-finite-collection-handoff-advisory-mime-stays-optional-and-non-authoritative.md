# ADR-0280: Workstation finite collection handoff advisory MIME stays optional and non-authoritative

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff.
`ADR-0264` through `ADR-0279` then narrowed the first cut into something close to implementable: single-retrieve by default, snapshot-shaped directory membership, manifest-first reviewed membership, read-only only, regular-files-plus-explicit-directories, canonical manifest ordering and digest, normalized review paths, explicit top-level names, ancestor-closed structure, overlap-free selected roots, fresh-rooted retrieve, explicit B/C/D profile scope, fail-closed first-implementation top-level collisions, and bounded manifest-derived review-surface path compression.

That leaves one smaller but still practical metadata question open in `RFC-0194`: **does the first richer lane need mandatory MIME classification as part of reviewed identity, or should MIME remain optional descriptive metadata only?**

Leaving that open would keep the first implementation heavier and more ambiguous than it needs to be. One implementation could require detector output, another could rely on filename folklore, and a third could omit MIME entirely while still producing the same reviewed bytes. That would make the first supposedly portable manifest depend on host registries, detector behavior, or policy-local classification rules that the archive has not actually standardized.

The archive already leans toward path/kind/payload identity first. It should not quietly smuggle MIME registries or content-sniffing policy into the first reviewed identity floor.

## Decision

For the first implementation/review surface of the reviewed finite collection handoff family:

1. advisory MIME stays **optional descriptive metadata**.
2. advisory MIME is **not authoritative reviewed identity**.
3. a valid first-cut manifest remains complete without MIME, as long as it carries the already accepted normalized review path, member kind, and regular-file payload digest + byte length floor.
4. if present, advisory MIME must not override member kind, payload digest, byte length, review-path rules, or any fail-closed decision already made by the authoritative manifest floor.
5. no implementation may require a MIME detector, MIME registry, filename-extension table, or broker-local classification service to produce or verify the first-cut authoritative manifest.
6. any later lane that wants mandatory reviewed content classification must return as a **distinct later RFC/ADR cut**, not as silent inflation of this baseline.

## Consequences

### Positive

- keeps the first richer lane portable across B/C/D without detector or registry baggage
- preserves the archive's path/kind/payload-first reviewed identity posture
- makes first implementation smaller and easier to reason about
- keeps advisory metadata available for UI hints or follow-on tooling without turning it into authority

### Negative

- review UIs cannot assume MIME is always present for richer classification or iconography
- later workflows that want stronger type guarantees will need a separate explicit lane
- some implementations may still choose to compute advisory MIME, but that work remains optional and non-authoritative

### Follow-up

Future RFC/ADR work may still define:
- whether any later lane wants mandatory reviewed content classification,
- whether advisory MIME should have a canonical vocabulary when present,
- or whether stronger content-classification guarantees belong in a separate quarantine/import lane instead of this handoff family.

This ADR only fixes the first metadata boundary: **advisory MIME stays optional and non-authoritative**.
