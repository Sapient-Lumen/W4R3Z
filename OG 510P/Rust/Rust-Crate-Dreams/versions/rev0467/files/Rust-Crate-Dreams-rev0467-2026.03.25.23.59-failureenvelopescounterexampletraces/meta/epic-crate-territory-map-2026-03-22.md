# Epic crate territory map — 2026-03-22

This note is the archive’s wide-angle map after a broad March 2026 refresh.
It exists to keep the repo thinking in **territory** rather than in one favorite subsystem.

## Main judgment

A worthy epic crate contribution in Rust usually does one of three things:

1. turns tacit ecosystem knowledge into a reviewable decision artifact,
2. turns a messy support story into a compact contract another engineer can inspect,
3. or turns fragmented substrate into one honest handoff bundle.

The most important question is not “is the idea cool?”
It is:

> What stable thing does this crate provide other people?

## Territory by use case family

### 1. Universal local productivity — highest leverage

Missing value:
- faster feedback loops with honest patch/restart truth,
- rebuild causality explanation,
- lock-contention evidence,
- and stronger debugging support bundles.

Best current archive lanes:
- **P-0537** compile iteration feedback
- **P-0469** cargo rebuild explanation
- **P-0490** cargo lock contention witness
- **P-0486** debuggability support
- **P-0035** cargo-build-insights

### 2. Ecosystem navigation and “which crate should we use?” — highest leverage

Missing value:
- task-oriented crate selection,
- frozen starter-set decisions,
- and provenance-aware crate knowledge exports.

Best current archive lanes:
- **P-0509** crate ecosystem pathfinder
- **P-0536** crate knowledge pack
- **P-0011** crate health
- **P-0535** dependency lifecycle transition

### 3. Regulated / safety-critical / long-lived systems — very high leverage

Missing value:
- reviewable evidence bundles,
- lifecycle transitions,
- toolchain/target readiness,
- unsafe-contract authority,
- and coverage/evidence honesty.

Best current archive lanes:
- **P-0535** dependency lifecycle transition
- **P-0484** toolchain & target support
- **P-0120** unsafe contract auditor
- **P-0433** MC/DC coverage workbench
- **P-0459** clippy safety profile & waiver kit
- **P-0460** unsafe field invariant ledger kit

### 4. Embedded / `no_std` / device-heavy work — high leverage, but often shared-lane leverage

Missing value:
- support truth more than one-off device wrappers.

Best current archive lanes:
- **P-0484** toolchain & target support
- **P-0535** dependency lifecycle transition
- **P-0532** async runtime assurance
- **P-0036** MSRV workspace lab
- **P-0121** FFI boundary conformance

### 5. Polyglot / FFI / cross-language interop — high leverage

Missing value:
- interface authority,
- projection parity,
- callback lifecycle,
- portable support bundles.

Best current archive lanes:
- **P-0121** FFI boundary conformance
- **P-0443** open namespace migration planner (for crate-family naming changes)
- shipkits only when the boundary contract is already sharp.

### 6. Async / cloud / services — high leverage

Missing value:
- runtime-family assurance,
- runtime lock-in truth,
- interop-aware crate selection,
- and supportive observability surfaces.

Best current archive lanes:
- **P-0532** async runtime assurance
- **P-0509** crate ecosystem pathfinder
- **P-0518** crate observability surface pack
- **P-0091** observability workbench kit

### 7. GUI / games / interactive apps — high leverage

Missing value:
- iteration-loop contracts,
- hot-reload versus restart truth,
- asset/visualizer/debug bundle support.

Best current archive lanes:
- **P-0537** compile iteration feedback
- **P-0491** debugger visualizer compatibility
- **P-0486** debuggability support
- **P-0098** GUI testing harness kit

### 8. Docs / search / LLM / support tooling — high leverage

Missing value:
- provenance-aware crate understanding,
- compact export policy,
- excerpt lineage,
- docs-example support truth.

Best current archive lanes:
- **P-0536** crate knowledge pack
- **P-0455** doctest extraction pipeline kit
- **P-0481** doctest runtool profile kit
- **P-0476** rustdoc coverage review bundle kit
- **P-0472** docs.rs build parity evidence kit

### 9. Supply chain / provenance / stewardship — high leverage

Missing value:
- support truth,
- trusted publishing route truth,
- dependency transition receipts,
- publish/release bundle joins.

Best current archive lanes:
- **P-0011** crate health
- **P-0175** trusted publishing tooling kit
- **P-0535** dependency lifecycle transition
- **P-0176** cargo publish receipt join kit

### 10. Wasm / plugin / component ecosystems — medium-high leverage

Missing value:
- artifact conformance,
- deployment/support bundles,
- runtime boundary truth, not just codegen.

Best current archive lanes:
- **P-0444** stable plugin host
- **P-0510** wasm component artifact conformance kit
- **P-0506** wasm plugin kit

### 11. Data / science / ML / AI-adjacent domains — medium leverage unless artifact-first

Missing value:
- format/crosswalk/conformance bundles,
- model or artifact interoperability receipts,
- reproducible evidence, not just another SDK wrapper.

Good examples already in the archive:
- **safetensors-gguf model artifact interop workbench**,
- **open-table-format kit**,
- **iceberg/delta/uniform interop evidence**,
- **mlir pipeline kit**.

## What should count as an epic crate after this map

A serious candidate should usually satisfy at least six of these:

1. solves a recurring pain seen across teams or releases,
2. stands on real substrate rather than imaginary future infrastructure,
3. emits receipts/reports/contracts/bundles rather than only runtime behavior,
4. is useful to another engineer who did not set it up,
5. preserves honesty by keeping adjacent truths separate,
6. can be diffed across versions or environments,
7. has a plausible MVP a small team could maintain.

## Elimination rule

If an idea is mostly:
- a thin wrapper around one existing library,
- a fashionable portal/UI without a durable artifact,
- or another niche domain lane when the real missing value is a shared support contract,

then the archive should synthesize or eliminate it instead of adding proposal count.

## Freshness anchors

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://docs.rs/subsecond
- https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/
