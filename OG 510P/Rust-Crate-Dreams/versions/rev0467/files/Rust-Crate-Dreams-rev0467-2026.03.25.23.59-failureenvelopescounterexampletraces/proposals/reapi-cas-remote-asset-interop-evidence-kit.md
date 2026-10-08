---
id: P-0375
title: Remote Execution API (REv2) + CAS + Remote Asset Interop & Evidence Kit — action/profile locks, digest-path diagnostics, and portable remote-build bug bundles
status: idea
domains: [build-systems, remote-execution, caching, devtools, infrastructure, interoperability, ci]
last_reviewed: 2026-03-06
evidence:
  - https://github.com/bazelbuild/remote-apis
  - https://github.com/bazelbuild/remote-apis/releases
  - https://bazel.build/remote/rbe
  - https://bazel.build/community/remote-execution-services
  - https://crates.io/crates/bazel-remote-apis
  - https://crates.io/crates/reapi
  - https://github.com/buildbarn/bb-remote-execution
---

# Problem

Rust already has serious build reproducibility and sandboxing proposals in this archive, and the Remote Execution API ecosystem is mature enough that the next gap is not “invent remote builds.” It is the missing crate for **debuggable, portable evidence** at the seam between:

- action digests and input-root completeness,
- CAS uploads/downloads and bytestream behavior,
- platform properties and worker capability assumptions,
- remote execution versus cache hits,
- and remote-asset qualifiers versus the digests they resolve to.

Teams still debug these failures with service-specific logs instead of an exchangeable artifact that proves what action, digest graph, platform properties, and server capabilities were actually in play.

# What it provides

- `reapi.lock` — pins digest function, instance name, execution/cache expectations, platform properties, bytestream quirks, and remote-asset assumptions.
- `action-irx` — a neutral IR for commands, directory trees, digest graphs, action results, server capabilities, and remote-asset mappings.
- `cas-audit` — checks for missing blobs, digest mismatches, path normalization drift, and tree incompleteness.
- `exec-replay` — replays cached or recorded action requests against adapters or captured server traces.
- `cargo reapi-evidence` — emits `*.reapibundle.zip` with action lockfile, digest graph, normalized findings, and support notes.

# What the crate should provide other people

1. **A boring default artifact for remote-build failures**.
2. **Explicit action/platform locks** instead of implicit scheduler/worker assumptions.
3. **Digest-path diagnostics** that explain missing or inconsistent CAS state.
4. **Portable evidence across REAPI implementations**.
5. **A bridge from Rust bindings to build-farm incident workflows**.

# Persona / who it’s for

- Build-system authors in Rust
- Infra teams operating remote execution or cache services
- CI/release engineers diagnosing action/cache failures
- Tooling authors integrating REAPI into Rust build workflows

# Users & user stories

- **Build engineer**: “Prove whether this was an execution failure, a cache inconsistency, or a missing blob.”
- **Infra operator**: “Capture a reproducible incident bundle without exposing all service logs.”
- **Client author**: “Compare the same action against two REAPI servers or two capability profiles.”
- **Migration owner**: “Pin which instance/platform/property assumptions are allowed in this rollout.”

# Prior art (and why it’s insufficient)

- REv2 and Remote Asset APIs are mature and widely implemented.
- Bazel documents remote execution concepts and services.
- Rust has protocol bindings and some adjacent build/cache tooling.
- Buildbarn and related implementations provide real backends.

What Rust still lacks is the **shared artifact layer** that makes action graphs, CAS state, capabilities, and remote-asset mappings exchangeable and explainable.

# Design goals

1. **Digest-graph first** — make the content-addressed model auditable.
2. **Implementation-neutral** — support multiple REAPI servers via adapters.
3. **Incident-ready** — focus on bundles that help operators and client authors collaborate.
4. **Deterministic** — evidence should be CI-friendly and comparable.
5. **Scope-controlled** — this is not a full remote execution service.

# MVP surface

- Minimal types: `ReapiLock`, `ActionGraph`, `CasFinding`, `CapabilitySnapshot`, `ReapiBundle`
- Minimal functions:
  - `inspect_action()`
  - `audit_cas()`
  - `diff_capabilities()`
  - `write_bundle()`
- Feature flags:
  - `reapi-v2`
  - `remote-asset`
  - `bytestream`
  - `recording`
  - `redaction`

# Compatibility story

- Works above existing Rust REAPI bindings rather than replacing them.
- Treats each server implementation as an adapter/provider.
- Can start from recorded action requests and capability snapshots.
- Keeps lockfile and bundle schema stable even as adapters widen.

# Conformance & fixtures

- Tiny fixtures for missing blobs, wrong digest sizes, directory-tree mismatches, and platform-property drift.
- Goldens for “cache hit should have been miss”, “execution fallback occurred”, and “remote asset resolved to unexpected digest”.
- Capability snapshots for different server profiles.
- Redaction tests for command arguments, environment variables, and repository identifiers.

# Path to boring stability

- Stabilize lockfile, action-graph schema, and finding taxonomy before adding many server integrations.
- Keep the first scope at audit/replay/evidence, not scheduling or worker execution.
- Publish a small public corpus of action/CAS edge cases.
- Make digest-function and platform-property assumptions explicit from day one.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that inspect a recorded REAPI action plus capability snapshot, audit the digest graph, and emit a compact `*.reapibundle.zip` describing action structure, CAS gaps, and cross-server differences.

# De-risk plan

1. Start from recorded actions and CAS audits before trying live execution orchestration.
2. Keep the first adapter set tiny and protocol-focused.
3. Treat command/env redaction as a first-class feature.
4. Use public protocol fixtures and tiny synthetic trees rather than real monorepos.

# Non-goals

- Not a remote execution server.
- Not a scheduler or worker implementation.
- Not a full build system.
- Not a replacement for existing REAPI implementations.

# Architecture & API sketch

```rust
pub struct ReapiLock {
    pub instance_name: Option<String>,
    pub digest_function: String,
    pub exec_properties: Vec<(String, String)>,
}

pub fn inspect_action(bytes: &[u8]) -> Result<ActionGraph>;
pub fn audit_cas(graph: &ActionGraph, cas: &dyn CasReader) -> Result<Vec<CasFinding>>;
```

Bundle draft: `reapi.lock`, `action.pb`, `graph.json`, `capabilities.json`, `cas-findings.json`, `remote-asset.json`, `notes.md`.

# Security / safety model

- Treat action payloads, digests, and remote metadata as untrusted input.
- Support redaction of arguments, env vars, repository URLs, and credentials.
- Record server capability snapshots and adapter versions in every bundle.
- Keep outputs deterministic for CI and issue exchange.

# Maintenance & governance plan

- Keep the core focused on lockfiles, audits, capability diffs, and bundle semantics.
- Version live-server adapters independently where possible.
- Publish a small public corpus of digest-tree and capability edge cases.
- Avoid drifting into “remote execution platform in a crate”.

# Milestones

## 0.1
- action inspection
- lockfile schema
- CAS audit findings

## 0.2
- capability diffs
- remote-asset overlays
- evidence bundle writer

## 1.0
- stable `*.reapibundle.zip`
- public fixture corpus
- documented compatibility guarantees for supported surfaces

# Open questions

- Which capability fields matter enough to pin in the MVP lockfile?
- How should remote-asset qualifier semantics be normalized across implementations?
- What is the best small corpus for proving digest-tree correctness and reproducibility?

# Sources

- Remote APIs repository: https://github.com/bazelbuild/remote-apis
- Remote APIs releases: https://github.com/bazelbuild/remote-apis/releases
- Bazel remote execution overview: https://bazel.build/remote/rbe
- Remote execution services: https://bazel.build/community/remote-execution-services
- `bazel-remote-apis`: https://crates.io/crates/bazel-remote-apis
- `reapi`: https://crates.io/crates/reapi
- Buildbarn remote execution: https://github.com/buildbarn/bb-remote-execution
