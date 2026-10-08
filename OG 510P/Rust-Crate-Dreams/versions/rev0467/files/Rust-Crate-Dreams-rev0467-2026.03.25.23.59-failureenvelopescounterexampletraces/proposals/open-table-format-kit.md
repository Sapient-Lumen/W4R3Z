---
id: P-0028
title: open-table-format-kit — table-surface receipts, capability profiles, and adapter coupling for Iceberg/Delta/Hudi in Rust
status: idea
domains: [data, storage, analytics, arrow, cloud, lakehouse]
last_reviewed: 2026-03-20
evidence:
  - https://rust.iceberg.apache.org/api/iceberg_datafusion/table/
  - https://github.com/apache/iceberg-rust/blob/main/CHANGELOG.md
  - https://docs.rs/crate/deltalake/latest
  - https://github.com/delta-io/delta-rs/releases
  - https://github.com/apache/hudi-rs
  - https://datafusion.apache.org/blog/2024/12/14/datafusion-python-43.1.0/
  - https://github.com/apache/datafusion/issues/16622
  - https://github.com/apache/iceberg-rust/issues/2236
---

# Problem

Rust now has credible and quickly-moving implementations for major open lakehouse/table formats, but downstream users still do not get one boring answer to the questions they actually need answered:

- Am I looking at a **live catalog table** or a **pinned snapshot**?
- Does this adapter path support only snapshot reads, or also time travel / incremental windows?
- Is this path honestly **read-focused**, **write-capable**, or **maintenance-capable**?
- Does the storage/catalog support exist in the underlying Rust crate but not in the exported binding path?
- Is the integration tightly coupled to an exact DataFusion version, or decoupled through a stable FFI path?

That is a larger practical gap than “there is no trait for table formats.”
The current ecosystem problem is really a missing **surface/capability/coupling contract**.

# What it provides

A support-first crate family rather than a replacement engine:

1. **Table-surface receipts**
- capture whether a subject is catalog-backed with automatic refresh, static-snapshot pinned, time-travel pinned, incremental-windowed, or otherwise narrower than “latest table”

2. **Capability-profile reports**
- declare supported read modes, write paths, maintenance operations, and engine registrations for the exact adapter/binding in view

3. **Integration-coupling receipts**
- declare whether the integration is:
  - native-only,
  - exact-version-coupled to DataFusion,
  - FFI-decoupled for foreign providers,
  - mediated through Python or another binding,
  - or carrying a binding/storage gap

4. **Diff + bundle tooling**
- compare two captures and explain whether the changes were about surface identity, supported capabilities, or compatibility coupling
- emit a compact `.otfbundle.zip`

# What the crate should provide other people

1. **A neutral vocabulary** for table surface and freshness truth above format-specific docs.
2. **Reviewable capability profiles** that stop broad format support claims from hiding adapter asymmetry.
3. **Reviewable integration-coupling receipts** so engine/version lock pain is visible early.
4. **A compact diff surface** for “what changed across this adapter upgrade?”
5. **A shared artifact layer** that query engines, bindings, and platform teams can consume without surrendering to one format implementation.

# Persona / who it’s for

- Query-engine maintainers
- Lakehouse connector authors
- Data-platform engineers
- Rust application teams embedding lakehouse reads/writes
- Teams mixing Iceberg / Delta / Hudi in one stack

# Users & user stories

- **Engine maintainer**: “Show me whether this registration path is a live catalog table or a pinned snapshot, and whether I have to match an exact DataFusion version.”
- **Platform engineer**: “Do not tell me merely that GCS or REST is supported somewhere; tell me whether this exact binding path can use it.”
- **Application team**: “I need to know whether this adapter supports only reads or also merge/update/maintenance operations.”
- **Upgrade reviewer**: “Give me a diff that says whether the change was freshness semantics, capability surface, or coupling debt.”

# Prior art (and why it’s insufficient)

- `iceberg-rust`, `deltalake`, and `hudi-rs` are all real, important substrate.
- `iceberg_datafusion` now provides serious provider shapes.
- DataFusion offers extension points, and Python-facing FFI helps one compatibility lane.

But none of those by themselves provide a **boring, receiver-facing contract** for what another team is actually being asked to depend on.
The missing layer is above the format crates, not in competition with them.

# Design goals

1. **Surface-first** — classify the exposed table/provider surface before inventing more abstraction.
2. **Capability-explicit** — do not infer parity from format family names.
3. **Coupling-honest** — exact-version locks and binding gaps must be first-class facts.
4. **Format-neutral but not flattening** — shared vocabulary without pretending all formats match.
5. **Diffable** — support release-to-release change review.

# Non-goals

- Replacing Iceberg / Delta / Hudi crates.
- Defining a new universal table format.
- Building a full query engine.
- Recreating the metadata / replay / catalog bug-workbench territory of **P-0359**.

# Architecture & API sketch

Crates:
- `otf_model`: shared types for table surfaces, capabilities, coupling, and diffs
- `otf_capture`: capture/import helpers for handles, providers, and config
- `otf_iceberg`, `otf_delta`, `otf_hudi`: optional adapters
- `otf_check`: validation and downgrade rules
- `cargo-otf`: CLI / cargo subcommand

Core outputs:
- `table-surface.receipt.json`
- `capability-profile.report.json`
- `integration-coupling.receipt.json`
- `otf-check.report.json`
- `otf-diff.report.json`

# Minimum lovable MVP

A small library and CLI that can:

1. inspect one Iceberg / Delta / Hudi subject or provider,
2. emit a table-surface receipt,
3. emit a capability-profile report,
4. emit an integration-coupling receipt,
5. diff two captures,
6. and bundle the results into a compact archive.

# De-risk plan

1. Start with **capture + profile + diff**, not with universal execution traits.
2. Keep DataFusion integration optional and honest about exact-version coupling.
3. Treat binding/storage mismatches as first-class findings.
4. Keep examples tiny and deterministic.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Milestones

## 0.1
- table-surface receipts
- capability-profile reports
- integration-coupling receipts
- diff + bundle CLI

## 0.2
- more complete Iceberg / Delta / Hudi adapters
- binding-gap and storage/catalog coverage checks
- DataFusion-facing helpers

## 1.0
- stable bundle/report format
- public fixture corpus
- documented compatibility policy for adapters and diff semantics

# Open questions

- What is the smallest common capability vocabulary that stays honest about asymmetry?
- How much engine/version coupling should the crate infer versus require the maintainer to declare?
- How should binding-only gaps be normalized across Python and other language surfaces?

# Sources

- Iceberg DataFusion providers: https://rust.iceberg.apache.org/api/iceberg_datafusion/table/
- iceberg-rust changelog: https://github.com/apache/iceberg-rust/blob/main/CHANGELOG.md
- Delta Lake Rust docs: https://docs.rs/crate/deltalake/latest
- delta-rs releases: https://github.com/delta-io/delta-rs/releases
- Hudi-rs README: https://github.com/apache/hudi-rs
- DataFusion Python foreign table providers: https://datafusion.apache.org/blog/2024/12/14/datafusion-python-43.1.0/
- DataFusion extension-version friction discussion: https://github.com/apache/datafusion/issues/16622
- Iceberg binding/storage gap example: https://github.com/apache/iceberg-rust/issues/2236
