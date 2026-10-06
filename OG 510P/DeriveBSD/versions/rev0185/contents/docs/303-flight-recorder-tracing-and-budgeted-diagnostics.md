# Flight recorder tracing + budgeted diagnostics (always-on, bounded, policy-governed)

In practice, the difference between a *recoverable incident* and a *week-long mystery* is often:
- did we have the last 30–300 seconds of high-signal diagnostic context?

Modern systems that “feel operable” often have an always-on **flight recorder** layer:
- in-memory circular buffers
- low overhead
- optionally promoted to disk when an incident triggers

Prior art worth stealing:
- **ETW sessions**: kernel-managed in-memory buffers and low-overhead event ingestion; supports circular buffering.
  Reference: https://learn.microsoft.com/en-us/windows-hardware/test/wpt/sessions

## The DeriveBSD shape

Introduce a first-class *flight recorder* capability for components and the host:

- Components can emit structured events to a **per-component ring buffer**.
- The host maintains a small set of **system ring buffers** (scheduler, VM runtime, network broker).
- When an incident is declared (crash, watchdog, manual breakglass), the system can **promote** the last N seconds into an evidence bundle.

This is not “log everything”. It is:
- **bounded**
- **typed**
- **policy-governed**

## Budgets and drift control

A flight recorder is a capability surface:
- it can leak sensitive information
- it can consume CPU/memory/disk
- it can become a covert channel if unconstrained

So we tie it to the authority budget lane:
- each component has a **diagnostics budget** (buffer sizes, event rates, retention windows)
- budgets are evaluated at Plan time against the compiled IR
- exceptions are timeboxed receipts

See: `docs/298-authority-budgets-and-permission-drift-alarms.md`.

## Access model: debug by lease

- Reading a component’s buffers requires a **diagnostics lease**.
- Exporting promoted traces requires `export.policy` mediation.
- Default mode is *owner-only* (the component itself can introspect) unless policy grants broader access.

See: `docs/194-debugging-by-lease-and-replay-capsules.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

## How it fits the Derive pipeline

### Component descriptor → compiled IR

`derive.unit` can declare:
- flight recorder on/off
- event categories (io, rpc, retries, policy, performance)
- budget (bytes, rate, max window)
- redaction class

Plan compiles this into:
- a **diagnostics profile** per unit
- archivist ingestion rules
- evidence hooks for incident bundles

### Incident snapshots

When an incident bundle is created, it may include:
- last N seconds of selected buffers
- a snapshot of the inspect tree
- correlated broker receipts (net-flow receipts, listen receipts, breakglass receipts)

See: `docs/216-incident-snapshots-and-support-bundles.md`, `docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`.

## Default constraints (safe-by-default)

- Buffers are **in-memory** by default.
- Disk persistence requires explicit policy.
- High-risk categories (payload bytes, raw keystrokes, file contents) are forbidden by default.
- The system provides **rate limiting** and drops when budgets are exceeded (with a counter in the inspect tree).

## Where persisted traces go

If policy allows persisting trace slices, they should become **immutable evidence objects**:
- content-addressed
- sealed (optional signatures)
- exportable via support-bundle flows

A natural home is the evidence vault lane (`docs/350-venti-fossil-write-once-archive-store.md`).

## Open questions

- Which backend is the best FreeBSD-native substrate (DTrace, ktrace, custom ring buffers, or a hybrid)?
- How do we prevent “debug builds” from silently bypassing budgets?
- What is the best cross-host export format (Chrome trace JSON, perfetto, or a minimal Derive format)?

Last updated: 2026-02-26
