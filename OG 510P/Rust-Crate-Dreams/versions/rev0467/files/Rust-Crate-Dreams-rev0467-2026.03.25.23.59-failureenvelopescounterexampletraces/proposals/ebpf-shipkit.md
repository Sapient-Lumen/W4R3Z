---
id: P-0128
title: eBPF ShipKit — production eBPF programs in Rust with repeatable build/deploy/verify
status: idea
domains: [observability, security, linux, networking, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://aya-rs.dev/book/
  - https://docs.rs/aya-ebpf
  - https://crates.io/crates/aya
  - https://github.com/aya-rs/awesome-aya
---

# Problem

Rust can write excellent eBPF programs, but *shipping* them is still bespoke: build modes vary by kernel features, CO-RE/BTF expectations differ, verifier failures are hard to reproduce, and “works on my kernel” is common.

Teams need a repeatable, auditable path from **Rust source → eBPF object → deployment → verifier/compat checks → observability**.

# What it provides

A cohesive crate+tooling stack:

- `ebpf_shipkit` library: high-level APIs for packaging, feature negotiation, kernel capability discovery, and portable logging/metrics patterns for eBPF.
- `cargo ebpf` subcommands:
  - `cargo ebpf build` (profiles for XDP/TC/tracepoints; CO-RE toggles; BTF handling)
  - `cargo ebpf doctor` (kernel + clang/llvm + bpffs + caps + BTF checks; prints actionable fixes)
  - `cargo ebpf verify` (repro “verifier bundle” capture)
  - `cargo ebpf deploy` (pinning maps/programs, versioned rollout)
- Standard artifact: `*.ebpfbundle.zip`:
  - eBPF ELF(s), build metadata, normalized verifier logs, kernel/BTF fingerprints, and a minimal reproducer config.

# Users & user stories

- **SRE / platform**: “I need to roll out an XDP program across heterogenous kernels with a safe canary plan.”
- **Security / runtime hardening**: “I need a repeatable ‘what ran in kernel space’ evidence bundle for incident review.”
- **OSS maintainer**: “Users report verifier failures; I need a portable bundle to reproduce.”

# Prior art (and why it’s insufficient)

- Aya provides strong user-space + kernel-space libraries, but does not prescribe a full shipping pipeline or portable evidence artifact.  
- The ecosystem has useful side-libraries (e.g., logging), but they don’t unify build/deploy/verify + reproducibility across teams.

# Design goals

- **Artifact-first debugging**: verifier failures must be shareable and replayable.
- **Kernel reality**: detect and adapt to BTF/CO-RE availability and kernel feature sets.
- **Operability**: logging/metrics patterns that work in production.
- **Minimal privilege**: clear required capabilities; no “run as root always” posture.

# Non-goals

- Replacing Aya; ShipKit should integrate with Aya projects and patterns.
- Being a universal eBPF framework across all languages.

# Architecture & API sketch

- `HostProbe`: gathers kernel facts (BTF availability, kconfig hints, bpffs, caps).
- `BundleWriter`: emits `ebpfbundle` with deterministic manifest + checksums.
- `VerifierReplay`: runs the verifier check step and normalizes logs for diffs.
- `DeployPlan`: declarative rollout steps (pin/update/unpin, map migrations, canary).

# Security / safety model

- Explicit capability model for each action; default to read-only diagnostics.
- Bundle redaction rules (strip host identifiers unless opted in).
- Signed bundles as an extension point (integrate with provenance tooling later).

# Maintenance & governance plan

- Start as a “thin waist”: stable artifact schema + CLI contracts, with pluggable backends.
- Conformance corpus: a small set of kernel versions/containers that run in CI (plus community-supplied bundles).

# Milestones

- **MVP**: `cargo ebpf doctor` + `ebpfbundle` schema + build profiles (XDP/tracepoint) + verifier normalization.
- **v0.2**: deploy plan + pinning helpers + canary rollout.
- **v1.0**: conformance corpus + CI matrix runner + stable schema guarantees.

# Open questions

- How much of build uses LLVM/clang directly vs relying on existing toolchains?
- Best default redaction policy for bundles (hostnames, kernel build IDs, etc.).

# Sources

- Aya book and getting started guidance.  
- Aya crates documentation and registry pages.  
- Awesome Aya list for ecosystem patterns (logging etc.).
