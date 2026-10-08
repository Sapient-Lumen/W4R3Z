---
id: P-0391
title: OpenDAL + object_store Capability Portability Kit — storage locks, semantics tests, and backend-incident bundles
status: idea
domains: [storage, cloud, infrastructure, portability, validation, io]
last_reviewed: 2026-03-06
evidence:
  - https://github.com/apache/opendal
  - https://opendal.apache.org/docs/rust/opendal/struct.Capability.html
  - https://docs.rs/object_store
  - https://github.com/apache/arrow-rs-object-store
---

# Problem

Rust already has strong storage abstraction substrate. Apache OpenDAL exposes a wide `Capability` surface across many services, and the `object_store` crate gives Rust infrastructure teams a focused cross-backend API that already powers serious systems.

But the painful failures happen at the seam between:

- **what a backend nominally supports and what a caller assumes about semantics**,
- **OpenDAL capability flags and `object_store`-level behavior expectations**,
- **multipart/upload/list/delete/conditional-operation edge cases**,
- **local test environments and cloud backends with subtly different guarantees**,
- and **incident handoff artifacts that currently depend on hand-written notes and provider-specific logs**.

The missing Rust contribution is not another storage abstraction crate. It is a **capability portability kit** for explicit storage locks, semantics tests, backend diffs, and portable incident bundles.

# What it provides

- `storage.lock` — pins required operations, conditional semantics, listing assumptions, multipart thresholds, metadata behavior, and backend-specific caveats.
- `capability-matrix` — normalizes OpenDAL and `object_store` capability/behavior surfaces into one explainable view.
- `semantics-probe` — runs deterministic tests for rename behavior, conditional writes, ETag/version assumptions, recursive listing, range reads, and multipart boundaries.
- `portability-diff` — explains which backend/adapter assumption failed and whether the failure is semantic, capability, or policy-related.
- `cargo storage-evidence` — emits `*.storagebundle.zip` with locks, probe outputs, traces, and findings.

# What the crate should provide other people

1. **A boring contract for cross-backend storage assumptions**.
2. **Explainable capability and semantics diffs**.
3. **A shared fixture suite for object-storage edge cases**.
4. **Portable incident bundles** for backend regressions.
5. **A way to compare OpenDAL and `object_store` views of the same backend without hand-waving.**

# Persona / who it’s for

- Infrastructure teams supporting multiple storage backends
- Authors of data systems, backup tools, and ingestion services
- Maintainers of crates built above OpenDAL or `object_store`
- CI engineers running storage compatibility tests

# Users & user stories

- **Infra engineer**: “Tell me whether this breakage is missing capability, semantic mismatch, or provider regression.”
- **Crate maintainer**: “Pin the backend assumptions my library actually requires.”
- **CI engineer**: “Run one semantics probe suite across local, test, and cloud environments.”
- **Support engineer**: “Send a compact bundle instead of raw cloud logs and shell transcripts.”

# Prior art (and why it’s insufficient)

- OpenDAL provides broad storage coverage and explicit capabilities.
- `object_store` gives a focused, portable object-store trait used by data infrastructure.

What Rust still lacks is a **single contract-and-evidence layer** that makes backend semantics, capability drift, and portability assumptions explicit and reproducible.

# Design goals

1. **Semantics-first** — capability booleans alone are not enough.
2. **Adapter-neutral** — work above OpenDAL and `object_store` without forcing convergence.
3. **Provider-honest** — backend-specific caveats must remain visible.
4. **Deterministic probes** — fixtures should produce boring results in CI.
5. **Operator-usable** — findings must map to real mitigation steps.

# MVP surface

- Minimal types: `StorageLock`, `CapabilityMatrix`, `SemanticsProbeResult`, `PortabilityFinding`, `StorageBundle`
- Minimal functions:
  - `probe_backend()`
  - `normalize_capabilities()`
  - `diff_portability()`
  - `write_bundle()`
- Feature flags:
  - `opendal`
  - `object-store`
  - `multipart`
  - `conditional`
  - `redaction`

# Compatibility story

- Builds above OpenDAL and/or `object_store`; does not replace either.
- Can test local FS/memory backends and cloud backends with one bundle schema.
- Treats provider-specific semantics as explicit overlays.
- Keeps provider credentials and raw logs optional and redactable.

# Conformance & fixtures

- Tiny fixtures for conditional puts, recursive listing order, rename semantics, multipart thresholds, ETag stability, and range-read boundaries.
- Goldens for “same API shape, different semantic guarantee”.
- Public provider-neutral fixture corpus plus optional provider adapters.
- Matrix runs comparing OpenDAL-backed and `object_store`-backed views.

# Path to boring stability

- Stabilize `storage.lock` and probe semantics before growing provider adapters.
- Start with object-storage semantics, not every filesystem nuance.
- Keep credential handling out of artifact defaults.
- Version backend caveat packs explicitly.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A library and CLI that pin storage assumptions, run deterministic semantics probes across backends, explain portability gaps, and emit compact `*.storagebundle.zip` artifacts.

# De-risk plan

1. Start with a small provider-neutral semantics suite.
2. Add OpenDAL and `object_store` adapters in parallel.
3. Keep provider-specific caveats as overlay packs.
4. Make redacted incident bundles first-class from the start.

# Non-goals

- Not a new storage abstraction library.
- Not a cloud sync product.
- Not a throughput benchmark suite.
- Not a credential manager.

# Architecture & API sketch

```rust
pub struct StorageLock {
    pub required_ops: Vec<String>,
    pub conditional_profile: String,
    pub listing_profile: String,
    pub multipart_profile: String,
}

pub fn probe_backend(input: ProbeInput) -> Result<SemanticsProbeResult>;
pub fn normalize_capabilities(input: CapabilityInput) -> CapabilityMatrix;
pub fn diff_portability(lock: &StorageLock, result: &SemanticsProbeResult) -> Vec<PortabilityFinding>;
```

Bundle draft: `storage.lock`, `capability-matrix.json`, `probe-results.json`, `findings.json`, `redactions.json`, `notes.md`.

# Security / safety model

- Redact credentials, bucket names, and object identifiers by default.
- Keep raw provider logs optional.
- Record adapter and backend version information in every bundle.
- Bound probe scope to small deterministic objects.

# Maintenance & governance plan

- Keep the core about locks, probes, and evidence.
- Version provider caveat packs independently if needed.
- Publish a small public semantics corpus.
- Resist drift into becoming another general storage abstraction crate.

# Milestones

## 0.1
- `storage.lock`
- capability normalization
- small semantics probe suite

## 0.2
- OpenDAL + `object_store` adapters
- portability diffs
- redacted bundle mode

## 1.0
- stable `*.storagebundle.zip`
- documented backend overlay policy
- public fixture corpus

# Open questions

- Which semantics deserve first-class profiles in MVP?
- How should eventual-consistency findings be represented in deterministic CI output?
- How much provider-specific metadata should be normalized versus left namespaced?

# Sources

- Apache OpenDAL repository: https://github.com/apache/opendal
- OpenDAL capability docs: https://opendal.apache.org/docs/rust/opendal/struct.Capability.html
- Rust `object_store` docs: https://docs.rs/object_store
- `arrow-rs-object-store` repository: https://github.com/apache/arrow-rs-object-store
