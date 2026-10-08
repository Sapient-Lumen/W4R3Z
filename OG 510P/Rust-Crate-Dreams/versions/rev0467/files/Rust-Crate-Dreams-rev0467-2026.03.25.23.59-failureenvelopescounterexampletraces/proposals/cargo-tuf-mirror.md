---
id: P-0026
title: cargo-tuf-mirror — TUF-aware mirrors & verification for Rust artifacts
status: idea
domains: [cargo, supply-chain, security, enterprise, offline]
last_reviewed: 2026-03-01
evidence:
  - https://rustfoundation.org/2025/
  - https://hackmd.io/%40cWcJa4-JQNOtacfKywdqxA/ByrMv8JH0
  - https://docs.rs/tuf
  - https://crates.io/crates/tough
---

# Problem

Rust is converging on **TUF** as a trust framework for Rust releases and crates.io, with an experimental deployment expected to start in 2026.
However, most teams that need *verifiable* mirrors and offline workflows don’t have a “Cargo-native, batteries-included” path to:

- mirror artifacts (toolchains and/or crates) into controlled environments
- verify freshness/rollback protections and integrity using TUF metadata
- keep verification keys and trust roots manageable for organizations

# Users & user stories

- **Enterprise / regulated orgs**: “We need to move Rust toolchains and dependencies into an air‑gapped build network, with cryptographic rollback protection.”
- **Linux distros / infra teams**: “We need a mirror that can be audited and independently verified by clients.”
- **CI / supply-chain teams**: “We need an artifact bundle that includes provenance metadata and can be verified offline.”

# Prior art (and why it’s insufficient)

- **`tuf` / `tough`**: solid libraries, but not an opinionated Cargo/rustup workflow with a turnkey UX.
  - They don’t provide the “how to run this in CI + mirror rotation + key ceremony templates” layer.
- **TUF adoption drafts for Rust**: focus on ecosystem-level deployment; less on *end-user operational tooling*.

# Design goals

1. **Cargo-friendly UX**: a subcommand that “feels like Cargo” for mirroring and verification.
2. **Offline-first**: artifact bundles and metadata caches designed for air-gaps.
3. **Explainability**: verification failures should be actionable (which role failed, expired timestamp, threshold not met, rollback, etc.).
4. **Composable**: integrate with existing “offline snapshot” tooling (e.g., P-0001 Cargo Snapshot) instead of replacing it.
5. **Low dependency footprint**: keep crypto choices sane, avoid megadeps where possible.

# Non-goals

- Replacing crates.io or rustup infrastructure.
- Implementing a new signing format; this uses TUF’s existing roles and metadata.
- Solving all “policy” problems (handled in P-0007 Cargo Policy); this crate focuses on transport + verification.

# Architecture & API sketch

Two layers:

## 1) Library: `tuf_mirror_kit`

- `RootStore`: manages trusted roots (pin, rotate, threshold sets)
- `MirrorPlan`: describes what to mirror (toolchain channels, registries, crate sets, allowlists)
- `MirrorRunner`: downloads artifacts + metadata, writes a **portable mirror directory** and a **bundle manifest**
- `Verifier`: verifies an artifact against a mirror cache (integrity + rollback protections)

Pseudo-API:

```rust
let store = RootStore::load_or_init("trust/")?;
let plan = MirrorPlan::for_crates_io()
    .allow_crates(lockfile_crates("Cargo.lock")?)
    .include_targets(["x86_64-unknown-linux-gnu"])
    .offline_bundle(true);

MirrorRunner::new(store, plan).run_to_dir("mirror/")?;

Verifier::new(store).verify_bundle("mirror/bundle.manifest.json")?;
```

## 2) CLI: `cargo tuf-mirror`

- `cargo tuf-mirror init` — initialize trust roots (org templates, key roles)
- `cargo tuf-mirror bundle` — produce an offline mirror bundle for a workspace (works with Cargo.lock)
- `cargo tuf-mirror verify` — verify artifacts/bundles and print a human-friendly explanation
- `cargo tuf-mirror serve` — optional: serve mirror via static HTTP (no signing)

# Security / safety model

- Default to **pinned root metadata** with explicit, logged rotation.
- Prefer threshold keys for critical roles.
- Strict expiry handling with explicit “dangerous override” flags.
- Store trust state in a dedicated directory with clear backups.

# Maintenance & governance plan

- Start as an “opinionated wrapper” around existing TUF crates.
- Publish compatibility guarantees for bundle formats (versioned manifest).
- Aim for multiple maintainers before 1.0; document key ceremony practices.

# Milestones

- **0.1**: verify-only: consume an existing TUF repo + verify downloads; portable cache layout.
- **0.2**: offline “bundle” output with manifest + deterministic layout for air-gap transfer.
- **0.3**: integration hooks for Cargo Snapshot (P-0001) and cargo-dist release pipelines.
- **0.4**: org templates (root rotation playbooks, threshold configs).

# Open questions

- What’s the cleanest integration point with Cargo/rustup without requiring Cargo changes?
- Which bundle format should be canonical (tar + manifest JSON/TOML) and how strict should it be?
- How should we support multiple registries and private indexes cleanly?

# Sources

- Rust Foundation 2025 Year in Review (TUF consensus + 2026 experimental deployment): https://rustfoundation.org/2025/
- TUF adoption draft (crate/release signing): https://hackmd.io/%40cWcJa4-JQNOtacfKywdqxA/ByrMv8JH0
- `tuf` crate docs: https://docs.rs/tuf
- `tough` crate: https://crates.io/crates/tough
