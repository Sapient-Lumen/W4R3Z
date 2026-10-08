---
id: P-0041
title: cargo-prebuilt-artifacts — verified precompiled dependencies for faster, safer builds
status: idea
domains: [cargo, build-systems, supply-chain]
last_reviewed: 2026-03-01
evidence:
  - https://internals.rust-lang.org/t/add-some-form-of-precompiled-artifact-support-to-cargo/22871
  - https://github.com/rust-lang/compiler-team/issues/876
  - https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
---

# Problem
Rust builds can be slow in large workspaces, and many environments (CI, enterprise, air-gapped) would benefit from sharing precompiled dependencies. But “just caching” doesn’t solve trust: we need a way to **distribute and verify prebuilt artifacts** with clear provenance and policy controls.

# Users & user stories
- **CI/build engineers**: “I want prebuilt deps across pipelines without relying on a single shared cache that can be poisoned.”
- **Enterprise/air-gapped**: “We want to ship a ‘dependency binary pack’ internally with verification.”
- **Crate maintainers**: “We want optional precompiled artifacts for heavy builds (e.g., proc-macro Wasm future, large codegens).”

# Prior art (and why it’s insufficient)
- Build caches exist (sccache, CI caches), but they are typically **trust-blind**.
- Discussion exists about adding precompiled artifacts to Cargo, but end-user tooling and policy aren’t there yet.

# Design goals
- Provide a **format + tooling** to:
  - build precompiled artifact packs for a resolved dependency graph
  - verify them (hashes + attestations)
  - apply them deterministically to a build
- Integrate with the ecosystem’s broader verification/mirroring direction.

# Non-goals
- Replace Cargo’s internal compilation pipeline.
- Solve cross-compiler ABI stability (artifacts are tied to toolchain + target triples).

# Architecture & API sketch
- `cargo prebuilt build-pack`: build artifacts for a lockfile + toolchain + target(s)
- `cargo prebuilt apply`: populate a local store and drive Cargo with appropriate overrides
- Pack format:
  - `manifest.toml` (toolchain, target, features, crate graph)
  - `objects/` (rlibs/metadata) with digests
  - optional attestations (SLSA/in-toto) and signatures

Policy:
- allow-list which crates may use prebuilt artifacts
- require attestations from trusted builders
- enforce maximum artifact age

# Security / safety model
- Packs must be verifiable offline.
- Defense against rollback and substitution (tie to lockfile + toolchain hash).

# Maintenance & governance plan
- Keep the core pack format small and versioned.
- Provide reference builder/verifier libraries for reuse by org tooling.

# Milestones
- **0.1**: local prebuilt pack builder + verifier + apply for a single target/toolchain.
- **0.2**: CI integration + signatures + policy file.
- **1.0**: broader target coverage + upstream collaboration on a stable interface.

# Open questions
- What’s the least invasive way to “apply” prebuilt artifacts to Cargo today?
- How to handle proc-macro execution compatibility and host/target splits?

# Sources
- https://internals.rust-lang.org/t/add-some-form-of-precompiled-artifact-support-to-cargo/22871
- https://github.com/rust-lang/compiler-team/issues/876
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
