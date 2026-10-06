# Structured diagnostics via Inspect-style trees (state you can query, not logs you grep)

Logs are necessary but insufficient:
- they are lossy (you only log what you thought mattered)
- they are hard to diff (text is not a schema)
- they create privacy risk (people over-log to compensate)

A greenfield system can bake in a better default: **components expose structured diagnostic state as a tree**.

Prior art worth stealing:
- **Fuchsia Inspect**: components expose a typed hierarchy (“Inspect”) that tools can query; an **Archivist** ingests and attributes data, then serves it through a single query surface.
  References: https://fuchsia.dev/fuchsia-src/development/diagnostics/inspect , https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics

## The DeriveBSD shape

Introduce a first-class diagnostics lane:

- Each component may expose an **inspect tree** (structured, typed key/value hierarchy)
- The host runs a **diagnostics archivist** service that:
  - collects inspect trees, structured logs, and selected traces
  - attributes data to a component identity (unit id + tree digest)
  - enforces retention, redaction class, and access control
  - emits receipts when data is exported

### Why trees (not “metrics only”)

Metrics are excellent for aggregates, but incidents often need **current state**:
- queue depths, retry backoffs, circuit-breaker state
- cached config epochs and active policy hash
- last successful reconcile / last error code
- connection pool saturation and timeouts

A tree enables:
- **stable paths** for dashboards and automation
- schema evolution with explicit versioning
- safe defaults: *don’t log secrets; expose minimal state instead*

## Profile-shaped default

Structured diagnostics are now governed by the product-default boundary in `docs/478-evidence-collection-posture-by-profile.md`:

- **A / fleet host** keeps inspect-style diagnostics available as bounded always-on local evidence.
- **B / workstation** keeps them locally useful and exportable, but richer sharing/capture must stay trusted-UI-visible.
- **C / general OS** keeps them local by default and makes remote collectors/support agents explicit.
- **D / appliance/factory** treats them as inputs to deterministic redacted bundles rather than ambient production telemetry.

## Access model: diagnostics are a lease

Diagnostics are powerful and can become ambient surveillance.
Bake in the same stance as networking and portals:

- Viewing another component’s diagnostics requires a **diagnostics lease**
- Leases are timeboxed and recorded into evidence
- Exporting diagnostics (support bundles, ticket uploads) goes through `export.policy` and emits receipts

See: `docs/192-observability-as-capability.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

## How this fits the Derive pipeline

### Spec → Plan

A component descriptor (`derive.unit`) declares diagnostics intent:
- whether the component exposes an inspect tree
- which categories are allowed (state, performance, counters)
- retention class (tiny ring vs incident-grade)
- redaction class (public/internal/sensitive)

Plan compiles that into canonical IR:
- per-component **diagnostics profile** (collection + retention + access policy)
- archivist routing rules (where data is stored and how it’s queried)

### Artifact / runtime

At runtime:
- the component publishes to a local sink (e.g., a unix socket or shared memory region)
- the archivist ingests, attributes, and serves queries

## Minimal invariants

- Inspect trees are **typed** (numbers/strings/bools/arrays) and versioned.
- The archivist enforces **bounded retention** by default (no “log everything forever”).
- Access is **explicit** (lease) and **attributed** (who queried what, when).
- Export is always mediated and receipted.

## Open questions

- What is the lowest-friction API for producing inspect trees in C/Rust/Go on FreeBSD?
- Do we store inspect snapshots in the structured event journal, or in a separate store with hashes referenced by events?
- What is the default redaction taxonomy, and how does it compose with support-bundle export policies?

Last updated: 2026-03-06r206
