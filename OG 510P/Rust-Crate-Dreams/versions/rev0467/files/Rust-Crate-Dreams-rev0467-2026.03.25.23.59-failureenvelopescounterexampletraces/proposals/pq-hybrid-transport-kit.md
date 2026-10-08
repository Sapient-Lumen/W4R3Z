---
id: P-0098
title: Hybrid Post‑Quantum Transport Kit — practical PQC/hybrid KEM+sig integration for rustls/QUIC/SSH stacks
status: idea
domains: [crypto, security, networking, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://blog.projecteleven.com/posts/the-state-of-post-quantum-cryptography-in-rust-the-belt-is-vacant
  - https://github.com/rustpq/pqcrypto
needs:
  - pqc primitives exist, but **application integration** is fragmented and error-prone
  - easy, safe "hybrid now" defaults for real-world threat models
---

# Problem
Rust has several post‑quantum implementations/bindings, but most teams that want “PQC-ready” transports still face:
- **No drop‑in, well‑tested hybrid profiles** for common stacks (TLS/QUIC/SSH-like protocols)
- Confusing algorithm choice, negotiation, and downgrade handling
- Missing interop test harnesses and “policy” tooling for security reviewers

The result is that PQC adoption either stalls or ships as bespoke crypto glue.

# What it provides
- **Policy-first PQC profiles** (opinionated but configurable)
  - `HybridKx::X25519_ML-KEM-768` (example), `Sig::Ed25519_SLH-DSA` (example)
  - explicit goals: “hybrid for the next N years”, “interop with X”, “no dynamic alloc”
- **Integration adapters**
  - `rustls` provider glue: key schedule + transcript binding + clear error surfaces
  - QUIC adapter hooks (e.g., for `quinn`-like stacks): session resumption + 0‑RTT policy
  - optional SSH-like handshake module (feature-gated; focus on the shared handshake core)
- **Interoperability & conformance suite**
  - golden vectors + transcript fixtures
  - “negotiation matrix” tests (what happens when peers support different sets)
  - downgrade/fallback tests with explicit expected behavior
- **Auditability ergonomics**
  - `cargo pqc doctor`: prints the negotiated algorithms and policy, emits a `pqc-report.json`
  - “key separation checklist” and invariants encoded as tests

# MVP (4–6 weeks)
- `hybrid-transport-core` crate:
  - traits for `KEM`, `SIG`, `HKDF`, transcript, serialization
  - one hybrid KEM composition and one signature option (behind features)
- `rustls` integration crate:
  - a minimal end‑to‑end handshake example
- test harness:
  - vector runner + negotiation matrix + fuzzing entrypoints

# Design notes
- **Provider model**: don’t hardcode primitives; accept providers (pure‑Rust or FFI).
- **Feature gating**: allow “pure‑Rust only” vs “FFI allowed” builds.
- **No silent downgrades**: expose downgrade as an explicit policy decision.
- **Zeroization**: consistent secret handling and drop order; require `zeroize` behind a feature.

# Testing & evidence artifacts
- `fixtures/handshake/*.json` transcript fixtures
- `artifacts/pqc-report.json` emitted by doctor
- differential tests across providers (where possible)

# Adoption path
- Start as a **non-standard** integration kit (opt-in crates)
- If patterns stabilize, propose upstream PRs / RFCs to the relevant stack maintainers

# Non-goals
- Competing with low-level PQC primitive crates
- Defining new crypto standards

# Related work
- PQ primitive/binding landscape summaries and gaps in Rust PQC tooling: see Project Eleven’s survey. 
