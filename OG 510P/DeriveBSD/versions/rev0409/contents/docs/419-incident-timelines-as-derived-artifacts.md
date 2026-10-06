# Incident timelines as derived artifacts (human-scale debugging)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** operability, reproducibility, supply-chain
**Patterns:** Plan→Apply→Receipt, Capsule  

DeriveBSD already has the raw ingredients for excellent incident response:
- receipts and snapshots (what happened)
- event segments (what was observed)
- causality graphs (what caused what)
- support bundles (what context was shared)

The remaining failure mode is human, not technical:

> “I have the evidence, but I still can’t orient quickly.”

This doc adds a *small* primitive that closes that gap without inventing a new logging stack:

- `incident.timeline` — a **typed, digest-bound** timeline view derived from existing evidence.

It is the “one page” orientation surface that operators always end up making by hand.

## Goals

- Make incidents **legible in minutes**, not hours.
- Keep the view **reproducible**: a timeline must name the inputs (digests) it was derived from.
- Keep the view **export-safe** by default (no secrets; redaction policy governs enrichment).
- Keep it compatible with A–D via **profiles and lanes**:
  - fleets and regulated environments can require it for rollbacks
  - workstations can generate it on-demand and export via portal

## Artifact

See schema: `spec/incident.timeline.schema.json`  
Example: `spec/examples/incident.timeline.json`

A timeline is a derived view with explicit provenance:
- `context` ties it to host/generation/incident ids
- `scope` bounds time
- `inputs` points to the evidence used (event segments, causality graph, transforms)
- `entries[]` are stable, export-safe one-liners with references to deeper evidence

## How this fits existing evidence primitives

### 1) Event segments are the raw time stream
Use `event.segment` digests for the bounded window.

### 2) Causality graphs provide structure
When available, `causality.graph` helps pick the *right* events and attach the *right* references.

See: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`.

### 3) Support bundles carry the shareable package
An official `incident.bundle` SHOULD include a timeline digest by default; timeline omission should be exceptional and explicit.

See: `docs/216-incident-snapshots-and-support-bundles.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.

### 4) Policy traces make “why” legible
Timeline entries may reference `policy-decision` digests and optional `policy-trace` digests.

See: `docs/416-policy-trace-format-and-explain-surfaces.md`.

## CLI affordances (suggested)

- `derive incident timeline --since 30m --json` → emit an `incident.timeline` artifact
- `derive incident bundle --since 30m` → compute and include `incident.timeline` by default for official support handoff
- `derive inspect timeline <digest>` → expand refs into a richer view (local only; export governed)

Timeline generation is a **derived operation**:
- it should emit a receipt if it performs nontrivial selection/redaction transforms
- it should be deterministic given the same inputs and policy

## Profile stance (defaults)

- **A (fleet host):** generate timeline automatically for rollback / failed health gate incidents; store in evidence vault and carry it in official support bundles.
- **B (workstation):** generate timeline by default when a user chooses “collect support bundle”; export remains portal / `export.policy` mediated.
- **C (general OS):** generate timeline by default for `derive incident bundle`; keep sharing explicit.
- **D (appliance/regulatory):** generate automatically and retain with strict redaction; require timeline in official incident bundles.

## Why bake this in now

Other ecosystems eventually build “incident timelines” in spreadsheets, ticket comments, or vendor tools.
If we standardize the object now:
- UIs can render it without scraping logs
- bundle-min can include an operator-ready orientation surface
- postmortems and regression localization become less heroic

See also: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.

Last updated: 2026-03-06r210
