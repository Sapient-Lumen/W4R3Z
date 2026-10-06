# Evidence queries and fact tables (osquery-shaped ergonomics, but derived and receipted)

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain
**Patterns:** Registry→Diff→Gate, Capsule  

DeriveBSD produces a lot of **typed evidence** (plans, receipts, diffs, attestations).
That’s the point.

But a system that is “receipts everywhere” still fails if humans can’t answer:

- “what changed?”
- “what authority exists right now?”
- “who/what touched this device?”
- “which cohort is affected?”

This doc proposes a greenfield UX win: ship a **queryable fact layer** over evidence.

## The steal: osquery’s mental model

osquery popularized the idea that the OS can be exposed as a relational database:
SQL queries over tables for processes, kmods, devices, network connections, etc.

References:
- osquery docs: https://osquery.readthedocs.io/
- Meta’s original intro: https://engineering.fb.com/2014/10/29/security/introducing-osquery/

DeriveBSD should steal the ergonomics, not necessarily the architecture.

## DeriveBSD twist: facts are derived, not scraped

Instead of “run privileged live queries all the time”, prefer:

- facts derived from existing receipts (activation receipts, net topology receipts, device attach events, attestation receipts, etc.)
- explicit live queries only via brokers (Observability-as-capability)

See:
- `docs/192-observability-as-capability.md`
- `docs/215-structured-event-log-as-evidence.md`
- `docs/246-causality-graphs-and-minimal-evidence-bundles.md`

## A minimal design

### 1) Evidence tables

Define a small set of **canonical tables** backed by evidence objects:

- `generations` (id, bootfs snapshot, closure digest, signer, rollout cohort)
- `authority_edges` (from, to, capability, lease id, expiry)
- `devices` (attach/detach events, device domain, risk class)
- `network_flows` (egress grants + flow receipts)
- `updates` (targets, metadata, health gate results)

Tables can be materialized into an embedded SQLite DB or a columnar store.
The important part is that each row can link back to the originating evidence digest.

### 2) Queries as first-class operations

Add a standard query operation that emits a **query receipt**:

- inputs:
  - query text
  - table bundle digest(s)
  - caller identity / authority (lease)
- output:
  - result set (JSON)
  - references to the underlying evidence digests

This makes “what did we know and when?” answerable during incidents.

### 3) Introspection and strong typing (GraphQL-shaped option)

A parallel (optional) approach is a typed schema with introspection:

- GraphQL intro: https://graphql.org/learn/introduction/

This could coexist with SQL:
- SQL for ad-hoc operators
- GraphQL for UI backends (permission center, fleet dashboards)

## Why this matters

- **Ops UX**: “show me all hosts where boot health gate failed” becomes trivial.
- **Auditability**: queries themselves become evidence.
- **Least authority**: live observability is brokered; derived facts remain cheap.
- **Meta-engineering**: new evidence objects can add new tables (or new columns) in a reviewable way.

## Integration points

- Permission center UI can be backed by fact tables:
  - `docs/371-permission-center-and-authority-introspection.md`
- Supply-chain knowledge graph can expose queryable facts:
  - `docs/334-artifact-knowledge-graph-and-supply-chain-queries.md`
- Drift bundles can include a “top queries” section for reviewers:
  - `docs/395-drift-bundles-and-review-summaries.md`

## Open questions

- What is the minimal set of tables to ship in v0?
- Do we want SQL, GraphQL, both, or a smaller DSL?
- How do we budget retention for fact materializations (tables are derivatives of evidence, but can grow large)?

