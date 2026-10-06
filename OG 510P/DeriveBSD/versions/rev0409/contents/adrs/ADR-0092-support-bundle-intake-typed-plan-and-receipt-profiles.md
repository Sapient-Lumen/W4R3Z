# ADR-0092: Support-bundle intake typed plan / receipt profiles

Date: 2026-03-08
Status: Accepted

## Context

`adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md` already fixed the safety boundary for foreign support bundles:
use the generic `content.import.plan` / `content.import.receipt` lane,
inspect in a disposable no-network compartment first,
and keep imported bundle bytes as foreign evidence rather than host authority.

The archive still had one expensive source of drift:
that workflow existed as docs + canonical examples, but the promised typed shapes were missing.
That left three bad outcomes available at once:

- the "official" support-bundle intake path could remain example-only folklore,
- future editors could invent a parallel support-specific import kind,
- or the generic import lane could silently drift because nothing pinned the canonical support-bundle shape.

The narrow question is therefore not whether support-bundle intake is special enough for a new subsystem.
It is whether the archive should type the canonical support-bundle intake workflow as a **profile of the generic import lane**.

## Decision

DeriveBSD accepts the following boundary:

1. **The canonical foreign support-bundle intake workflow gets typed specialization schemas.**
   The archive now carries:
   - `spec/content.import.support-bundle.plan.schema.json`
   - `spec/content.import.support-bundle.receipt.schema.json`

2. **These are constrained profiles of the generic import lane, not new authority kinds.**
   Canonical support-bundle examples stay:
   - `kind = content.import.plan`
   - `kind = content.import.receipt`

3. **The typed support-bundle profile models the canonical `tar.zst` handoff only.**
   `zip` and other compatibility wrappers remain adapter territory on the generic import lane.
   They may be imported, scanned, converted, or unpacked,
   but they do not redefine the canonical typed support-bundle handoff shape.

4. **The typed plan / receipt profile fixes the default reviewable shape.**
   The canonical support-bundle intake profile requires:
   - `execution.isolation = microvm`
   - `execution.network = none`
   - `execution.lifetime = disposable`
   - `scan` + `unpack` + `classify` operations
   - timeline-first preview members (`incident.timeline`, `incident.bundle`, `bundle.payload.manifest`)
   - preserved or rehydrated quarantine/origin metadata

5. **Deeper incident reproduction still stages imported digests into a disposable workspace.**
   The typed intake profile does not make the support bundle itself authority.

## Consequences

### Positive

- The archive now has an actual typed contract for the official support-bundle intake path.
- Reviewers and implementers get a concrete target without inventing a second import subsystem.
- Example filenames, risk-register text, and the support docs now point at real artifacts.
- Compatibility adapters remain possible without redefining the default handoff.

### Negative / trade-offs

- The canonical typed profile is intentionally narrower than the full generic import lane.
- Some incoming support artifacts will stay on generic `content.import.*` objects until tooling converts or normalizes them.
- Editors now need to keep the generic import lane and the typed support-bundle profile distinct.

## Non-goals

This ADR does **not** decide:

- the final GUI or CLI for support-bundle preview,
- exact scanner backend choices,
- the final conversion flow for every compatibility archive format,
- or the final policy for promoting imported members out of quarantine.

Those remain implementation or future RFC work.
