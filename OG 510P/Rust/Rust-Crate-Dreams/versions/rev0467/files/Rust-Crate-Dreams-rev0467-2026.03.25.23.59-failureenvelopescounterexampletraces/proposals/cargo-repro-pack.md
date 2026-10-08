---
id: P-0038
title: cargo-repro-pack — reproducible `.crate` packaging and verification
status: idea
domains: [cargo, reproducibility, supply-chain]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/rust-lang/cargo/issues/8612
  - https://github.com/rust-lang/cargo/issues/2607
  - https://lib.rs/crates/cargo-reproduce
  - https://internals.rust-lang.org/t/reproducible-builds-for-rustc-gsoc-25-idea/22532
---

# Problem
Reproducible builds are only as verifiable as the *artifacts* we ship. Today, running `cargo package` / producing a `.crate` archive can differ across machines (file ordering, timestamps, path normalization), making byte-for-byte verification hard and weakening supply‑chain trust.

# Users & user stories
- **Distros / reproducible-builds practitioners**: “I want to verify that the `.crate` I built matches upstream exactly.”
- **Security teams**: “I want to independently rebuild and verify crates (or my own internal crates) without “close enough” hashing.”
- **Crate authors**: “I want my published crate archive to be deterministic so downstream rebuilders don’t file ‘non-repro’ bugs.”

# Prior art (and why it’s insufficient)
- `cargo-reproduce` (2025) is a Cargo subcommand that aims to normalize the build environment and verify bit-for-bit reproducibility. This proposal should **integrate** with it (or extract reusable libraries/specs) instead of duplicating effort; our emphasis is the reproducibility of *published artifacts* (`.crate` archives and pack formats) and their verifiers.  
  Source: https://lib.rs/crates/cargo-reproduce

- Cargo has long-standing issues requesting reproducible crate archives and deterministic build ordering, but there’s no widely adopted, end-user workflow today.
- General reproducible build guidance exists, but it doesn’t solve `.crate` packaging determinism on its own.

# Design goals
- Make `.crate` archives **bit-for-bit reproducible** given the same inputs.
- Provide a **verification tool** usable in CI and by downstream rebuilders.
- Be conservative: **don’t change semantics** of what is packaged, only normalize the archive container.

# Non-goals
- Guarantee reproducible *compiled binaries* across toolchains/OSes (out of scope).
- Replace Cargo’s official implementation (this crate should prototype & inform upstream).

# Architecture & API sketch
Two layers:
1) `cargo repro-pack package` (wrapper):
   - invokes `cargo package --list` and builds a deterministic manifest
   - re-emits the archive with:
     - canonical file ordering (lexicographic, stable)
     - normalized file metadata (mtime from `SOURCE_DATE_EPOCH` or 0)
     - canonical permissions (preserve executable bit only)
     - canonical compression settings if compressed
2) `cargo repro-pack verify`:
   - computes and compares:
     - archive hash
     - normalized manifest hash
   - explains mismatches (which file, which metadata)

Library core:
```rust
pub struct PackOptions { pub source_date_epoch: Option<u64>, /* … */ }
pub fn normalize_crate_archive(input: impl Read, out: impl Write, opt: PackOptions) -> Result<()>;
pub fn normalized_manifest(input: impl Read) -> Result<Manifest>; // stable representation
```

# Security / safety model
- Treat archives as untrusted input: streaming processing, size limits, no path traversal.
- Verification output should be machine-readable (JSON) for policy engines.

# Maintenance & governance plan
- Keep dependencies minimal (prefer `tar` + small helpers).
- Ship a corpus of “known tricky” crates as fixtures.
- Establish conformance: “normalized output must be stable across platforms.”

# Milestones
- **0.1**: normalize `.crate` archives + `verify` (manifest + hash) + fixtures.
- **0.2**: integrate with `cargo publish --dry-run` as a preflight check; GitHub Action.
- **1.0**: stabilize format guarantees; upstream RFC / Cargo PR informed by data.

# Open questions
- Best canonicalization rules for permissions/owners across platforms?
- How to handle non-deterministic file generation inside `cargo package` (if any)?

# Sources
- https://github.com/rust-lang/cargo/issues/8612
- https://github.com/rust-lang/cargo/issues/2607
- https://internals.rust-lang.org/t/reproducible-builds-for-rustc-gsoc-25-idea/22532
