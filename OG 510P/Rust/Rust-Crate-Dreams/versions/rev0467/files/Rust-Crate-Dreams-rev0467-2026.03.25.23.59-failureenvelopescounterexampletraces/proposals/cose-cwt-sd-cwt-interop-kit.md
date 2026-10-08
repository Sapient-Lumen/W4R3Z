---
id: P-0148
title: COSE / CWT / SD-CWT Interop Kit
status: idea
domains: [security, identity, iot, cbor, tokens, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/coset
  - https://crates.io/crates/cose-rust
  - https://lib.rs/crates/common-access-token
  - https://github.com/beltram/esdicawt
---

# Problem

In “constrained” and cross-vendor environments (IoT, device identity, verifiable credentials),
**CBOR + COSE + CWT** stacks are common — but Rust support is fragmented.
There are crates for COSE structures (e.g., `coset`, `cose-rust`) and some token implementations,
yet developers still lack a coherent *interop-first* kit: profiles, key conversions, standardized test vectors,
and safe-by-default verification pipelines.

# What it provides

A crate family and conformance suite that makes “CBOR credentials” boring:

- A versioned set of **profiles**:
  - COSE_Sign1 verification defaults (alg allowlists, crit handling, time checks)
  - CWT claim sets and common “CAT-style” patterns (issuer/audience/time/windowing)
  - SD-CWT / selective disclosure flows (holder/issuer/verifier roles)
- High-level APIs:
  - `verify_sign1(profile, bytes) -> Verified`
  - `verify_cwt(profile, bytes) -> Claims`
  - `issue_*` helpers that emit deterministic encodings
- A portable evidence bundle: `*.cosebundle.zip`
  - input token, normalized parse, verification decisions, key fingerprints
  - minimized failing vectors
- A **conformance corpus**:
  - golden vectors for parse/verify/claim rules
  - fuzz harnesses targeting “gotcha” CBOR/COSE edge cases
- Bridges:
  - key conversion helpers (RustCrypto keys ↔ COSE keys)
  - optional integration points for platforms that want SD-CWT today

# Users & user stories

- **IoT teams**: “Verify device tokens without writing COSE plumbing.”
- **Identity teams**: “Run interop tests and ship stable profiles across services.”
- **Auditors**: “See exactly *why* a token was accepted/rejected.”

# Prior art (and why it’s insufficient)

- `coset` / `cose-rust`: represent structures but don’t provide “policy profiles” and interop UX.
- `common-access-token`: token-level library but not a broad interop suite.
- SD-CWT projects exist, but ecosystem lacks shared vectors + “doctor” workflows.

# Design goals

- Make verification decisions explicit and reviewable (profiles + decision logs).
- Treat test vectors and evidence bundles as first-class artifacts.
- Keep encoding deterministic to support reproducible builds/tests.

# Non-goals

- Not a full verifiable-credential product.
- Not a bespoke crypto layer; rely on well-reviewed primitives.

# Architecture & API sketch

- `cosekit::profiles::{Profile, RuleSet}`
- `cosekit::verify::{Verifier, DecisionLog}`
- `cosekit::bundle::{CoseBundle}`
- `cosekit::vectors::{Corpus, Runner}`

# Security / safety model

- Default-deny algorithms; explicit allowlists per profile.
- Strict time handling with injectable clocks for deterministic tests.

# Maintenance & governance plan

- Keep profiles small and versioned; require corpus updates for profile changes.
- Document “security posture” per profile (tradeoffs, intended deployment).

# Milestones

- **MVP**: COSE_Sign1 verify + decision log + bundle schema + starter corpus.
- **v0.5**: CWT claim validation + key conversion helpers.
- **v1.0**: SD-CWT support + expanded corpus + fuzz regression CI.

# Sources

- `coset` (COSE types): https://crates.io/crates/coset
- `cose-rust` (COSE encode/decode): https://crates.io/crates/cose-rust
- Common Access Token library (CWT-ish patterns): https://lib.rs/crates/common-access-token
- SD-CWT crates and draft-oriented implementation: https://github.com/beltram/esdicawt
