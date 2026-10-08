---
id: P-0112
title: TPM KeyStore & Attestation Flows Kit — safe, ergonomic high-level TPM2 flows with policy, portability, and test vectors
status: idea
domains: [security, hardware, cryptography, attestation, embedded, enterprise]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/tss-esapi
  - https://github.com/parallaxsecond/rust-tss-esapi
  - https://tpm2-tss.readthedocs.io/en/4.1.x/group__esys.html
needs:
  - Rust has TPM2 bindings/wrappers, but lacks an opinionated *flow library* for common tasks (sealed secrets, device identity, remote attestation)
  - TPM policy/auth is subtle; teams need guardrails and a portable “profile” layer
  - CI/testing is hard without simulators, deterministic vectors, and story-based examples
---

# Problem

TPMs are widely deployed (servers, laptops, some embedded), but building safe flows is hard:
- policy sessions and authorization are easy to misuse
- key hierarchies, persistence, and provisioning vary by platform
- testing and reproducibility are painful

Existing crates expose TPM APIs; what’s missing is a **high-level kit**.

# What it provides

## 1) High-level, auditable flows (with profiles)

`tpmsafe` provides safe building blocks:
- `KeyStore`: create/load persistent keys, rotate, export public material
- `Seal`: seal/unseal small secrets to PCR profiles
- `Attest`: generate and verify quotes with a versioned profile

Profiles:
- “server identity” (EK/AK provisioning + quote policy)
- “disk unlock” (PCR-bound sealing)
- “signing service” (restricted keys + usage counters)

## 2) Portable artifact formats + conformance vectors

`*.tpmflow.zip`
- `profile.toml`
- `transcript.json` (operations, handles, PCR selections, nonces)
- `quote.bin` + `signature.bin` + `pubkey.pem`
- `expected.json` (verification results)

A small corpus of vectors that:
- runs against a simulator (where possible) and real TPMs in CI labs
- checks policy invariants and failure modes

## 3) A “doctor” UX

`cargo tpm doctor`:
- detects tpm2-tss availability, permissions, device paths
- validates profiles
- generates a redacted `tpmflow.zip` for bug reports

# MVP

- wrap `tss-esapi` with minimal “safe flows”:
  - create AK + quote
  - seal/unseal to PCR mask
- transcript + artifact format v0.1
- simulator-first test harness (plus optional hardware CI)

# v1

- profile library (opinionated defaults)
- verification utilities (quote verification, chain checks)
- backends for Linux TPM2 device + simulator; leave Windows/macOS as stretch goals

# Risks

- TPM diversity: keep the abstraction small, profile-driven, and fully logged.
- Hardware CI: ship strong simulator coverage + an opt-in hardware runner.
