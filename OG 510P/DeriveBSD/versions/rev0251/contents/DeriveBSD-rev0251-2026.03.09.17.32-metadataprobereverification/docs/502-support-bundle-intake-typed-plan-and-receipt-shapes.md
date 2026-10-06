# Support-bundle intake typed plan / receipt shapes

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt, Capsule  

`docs/498-safe-open-support-bundle-intake-and-repro-boundary.md` already decides the safety boundary for foreign support bundles.
This doc makes the next smaller, more implementable decision:
**what are the canonical typed shapes for that intake path, and how do we keep them from turning into a second import subsystem?**

See also:
- ADR: `adrs/ADR-0092-support-bundle-intake-typed-plan-and-receipt-profiles.md`
- safe-open boundary: `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`
- official support handoff: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- canonical schemas: `spec/content.import.support-bundle.plan.schema.json`, `spec/content.import.support-bundle.receipt.schema.json`
- generic import lane: `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`

## Why this needs a hard decision

The archive had already decided that foreign support bundles should go through the generic import lane and stay foreign evidence.
What it had **not** finished deciding was how typed that path should be.

Leaving the path as examples-only creates drift fast:

- reviewers do not know whether the example is illustrative or normative,
- future docs can casually invent a support-specific import subsystem,
- and compatibility formats can quietly redefine the "official" bundle shape.

DeriveBSD needs a smaller answer:
**make the official support-bundle intake path typed, but keep it a profile of the generic import lane.**

## The canonical typed shapes

The archive now carries two constrained schemas:

- `spec/content.import.support-bundle.plan.schema.json`
- `spec/content.import.support-bundle.receipt.schema.json`

These are **typed profiles** over the generic import lane.
They do **not** introduce new `kind` values.
Canonical support-bundle examples therefore remain:

- `kind = content.import.plan`
- `kind = content.import.receipt`

That keeps import authority crisp:
`content.import.*` remains the authority lane,
while the support-bundle typed schemas describe one conservative, canonical shape of that lane.

## What the typed profile fixes

The canonical support-bundle intake profile fixes these review surfaces:

- **subject format:** canonical support-bundle handoff uses `tar.zst`
- **execution:** `microvm` + `network = none` + `lifetime = disposable`
- **operations:** `scan` + `unpack` + `classify`
- **preview posture:** prefer `incident.timeline`, `incident.bundle`, and `bundle.payload.manifest`
- **metadata posture:** preserve or rehydrate quarantine/origin metadata instead of laundering it away
- **outputs:** emit a quarantine-preserving unpacked dataset plus timeline-first preview surfaces

This is intentionally narrow.
It answers "what does the official thing look like?" without trying to model every odd intake adapter.

## Canonical vs compatibility intake

The typed support-bundle schemas model the **canonical `tar.zst` handoff**.
That matches the already-accepted support-bundle contract.

`zip` still exists as a compatibility adapter when some external system requires it,
but it does **not** become the canonical typed support-bundle intake shape.
A `zip` import stays on the generic `content.import.*` lane and may convert or normalize before it produces the same preview/reproduction posture.

This is the key anti-drift decision:
compatibility formats stay compatible,
but they do not get to redefine the official support-bundle contract.

## Why this stays coherent across product shapes

### A) Secure fleet host

Fleet responders get one recognizable intake profile that is easy to audit and automate.
Support imports do not become an excuse for ad-hoc host opening.

### B) Secure workstation

Trusted UI can show one clear default posture for foreign support artifacts.
The user sees the same safe-open rules as other risky content.

### C) General-purpose OS

The system remains locally viable.
Generic import adapters can still exist,
but the official typed support path stays conservative and easy to explain.

### D) Appliance / factory / regulatory

Production support intake keeps an offline-friendly, digest-bound, no-network preview path.
Compatibility adapters remain bounded rather than turning production support into format folklore.

## What this does not decide

Still open:

- the final UX for timeline preview and incident reproduction,
- exact scanning/classification backends,
- exact normalization flow for every compatibility archive format,
- and exact promotion/export policy for imported members.

Those are implementation questions.
The typed support-bundle intake shape is now fixed enough to build against.

Last updated: 2026-03-08r231
