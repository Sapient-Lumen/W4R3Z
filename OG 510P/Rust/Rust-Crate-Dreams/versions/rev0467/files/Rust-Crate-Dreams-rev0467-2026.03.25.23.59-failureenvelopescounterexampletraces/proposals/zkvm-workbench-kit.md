---
id: P-0149
title: ZKVM Workbench Kit
status: idea
domains: [security, cryptography, zero-knowledge, wasm, toolchain, conformance, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/risc0-zkvm/
  - https://crates.io/crates/sp1-zkvm
  - https://doc.rust-lang.org/beta/rustc/platform-support/riscv32im-risc0-zkvm-elf.html
  - https://dev.risczero.com/api/zkvm/install
  - https://docs.succinct.xyz/docs/sp1/getting-started/quickstart
---

# Problem

Rust zkVMs (e.g., **RISC Zero** and **SP1**) are increasingly “real developer tooling”: you write ordinary Rust, run a prover, and publish a receipt/proof. That’s powerful—but the current experience is still *project-specific* and hard to operationalize:

- Reproducibility is brittle (toolchains, guest build flags, host/prover versions, feature sets).
- Debugging failures is non-portable (prover logs, guest traces, cycle counts, witness size, etc.).
- Cross-zkVM portability is a mess: “it compiles” is far from “it proves”.

We’re missing a **shared workbench layer** that makes zkVM programs testable, reproducible, comparable, and debuggable—*as artifacts*.

# What it should provide

## 1) A portable “proof attempt bundle” format

A standard `zkbundle.zip` with:

- `manifest.json` (schema version, zkVM flavor, toolchain fingerprints, guest crate metadata)
- `guest/` source snapshot (or content hashes + provenance pointers)
- `build/` normalized build plan (exact rustflags/target/features)
- `run/` inputs (redactable), cycle limits, determinism seeds
- `outputs/` receipts/proofs + verification transcript
- `logs/` normalized prover + host logs
- `metrics.json` (cycles, proving time, memory, proof size, etc.)

This is the “share a failing proof” equivalent of `repro.zip`.

## 2) A cargo-native UX

A companion tool (either a crate + `cargo-zk` subcommand or a standalone CLI) with:

- `cargo zk doctor` — detect common footguns (unsupported syscalls, non-determinism, alloc patterns)
- `cargo zk bundle` — produce a `zkbundle.zip` from a workspace
- `cargo zk verify` — verify receipts in a hermetic mode
- `cargo zk diff` — compare bundles (toolchain drift, performance regression)
- `cargo zk matrix` — run the same guest across multiple zkVM backends (where possible)

## 3) Backend adapters and a “lowest common denominator” API

- Adapter crates for **risc0** and **sp1** first.
- A core abstraction: `GuestBuild`, `Prove`, `Verify`, `ReceiptLike`, `Metrics`.
- Capability flags: “supports recursion”, “supports syscalls X”, “guest target triple”, etc.

## 4) Conformance / portability kits

A curated set of minimal guest programs (fib, hashing, signature verify, JSON parse, etc.) with:
- Known-good receipts/proofs
- Performance baselines
- Failure mode tests (OOM, timeouts, unsupported ops)

# MVP scope (2–4 weeks)

- `zkbundle.zip` schema v0 with `manifest.json` + `metrics.json`
- RISC Zero adapter:
  - build guest for `riscv32im-risc0-zkvm-elf`
  - bundle + verify
- “Doctor” rules:
  - warn on obvious non-determinism (time, randomness without seeding)
  - detect disallowed syscalls / target mismatch
- CI: publish bundle artifacts on failure

# v1 scope (2–3 months)

- Add SP1 adapter (`cargo prove`/SP1 workflow integration)
- `diff` tool for bundle-to-bundle regression tracking
- Redaction tooling: `cargo zk redact` (remove inputs, keep hashes)
- Minimal conformance suite + golden receipts

# Design notes and pitfalls

- **Artifact-first**: treat proof attempts like test runs—portable, replayable, and diffable.
- **Determinism contract**: explicit seeding and a “no ambient sources” policy.
- **Security posture**: bundles may contain sensitive inputs; default to redaction support and safe-by-default packaging.
- **Ecosystem impact**: this kit benefits *every* zkVM project by turning “it failed to prove” into a shareable, diagnosable object.

# Success metrics

- A maintainer can reproduce a proving failure from a `zkbundle.zip` without bespoke setup.
- A project can track proving performance regressions in CI via `cargo zk diff`.
- Basic “write Rust → prove → verify” workflows are consistent across at least two zkVM backends.
