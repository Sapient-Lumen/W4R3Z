---
id: P-0086
title: Confidential Attestation Kit (TEEs: Nitro/SEV/TDX/SGX, key binding, policy, conformance)
status: idea
domains: [security, confidential-computing, tee, attestation, crypto, cloud]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/nitro_attest
  - https://aws.amazon.com/blogs/compute/validating-attestation-documents-produced-by-aws-nitro-enclaves/
  - https://github.com/CCC-Attestation/formal-spec-TEE
---

# Problem

Confidential computing (TEEs like AWS Nitro Enclaves, AMD SEV-SNP, Intel TDX/SGX) is becoming “normal infra”, but Rust teams still re-build the same brittle glue:
- parsing/verifying attestation documents
- binding session keys to attestation evidence
- integrating “remote key release” (KMS / HSM policies) with app identity
- writing conformance tests and golden vectors for security-sensitive parsing logic

The ecosystem has pieces (per-vendor crates and blog posts) but lacks a *standard, testable, auditable* foundation that other crates can depend on.

# What it provides

A **Confidential Attestation Kit** that others can build on:

## 1) A stable trait model
- `AttestationEvidence`: structured evidence + raw bytes
- `Verifier`: verify signature chain + claims + freshness + policy
- `Claims`: normalized claims (`measurement`, `signer`, `platform`, `debug`, `nonce`, `timestamp`, `tcb`, etc.)
- `KeyBinding`: derive/bind session keys to claims (e.g., X25519 + HKDF; AAD conventions)

## 2) Pluggable backends
- `nitro` (AWS): document parsing + verification + policy helpers
- `sev_snp`, `tdx`, `sgx` backends (initially “verify-only” with feature gates)
- A `mock` backend for tests with deterministic fixtures

## 3) Policy & “remote key release” helpers
- a small policy DSL (deny-by-default) that compiles into:
  - claim predicates (measurement allowlists, debug flags, signer constraints)
  - freshness/nonce checks
- helpers for generating “KMS recipient” / key-release requests (vendor-specific adapters, but common UX)

## 4) Conformance & security harness
- versioned **test vector packs** (`.attvec`) that include:
  - evidence bytes
  - expected claims
  - expected verification results under named policies
- fuzz targets (parsers/CBOR/COSE as applicable)
- CI profiles: “fast”, “paranoid”, “fuzz-smoke”, “audit”

# Users & user stories

- **Platform teams**: “We want a single crate to verify enclave identity and gate secrets.”
- **App teams**: “Give me a 5-line API to bind a TLS session key to attestation.”
- **Security reviewers**: “Show me conformance vectors and fuzzing coverage; no bespoke parsing.”

# Prior art (and why it’s insufficient)

- Vendor-specific helpers exist (e.g., Nitro attestation crates), but there is no shared abstraction layer, conformance format, or cross-TEE policy UX.
- Cloud vendor documentation shows how to validate documents, but examples are usually in other languages or too bespoke for reuse.

# MVP (6–8 weeks)

- Core traits + policy predicates
- Nitro backend (verify + claim normalization)
- `.attvec` format + a small runner CLI (`attestkit verify --policy policy.toml vectors/`)
- Fuzz targets for evidence parsing

# v1 path

- Stabilize claims schema and policy surface.
- Add at least one more backend behind a feature gate (SEV-SNP or TDX).
- Publish “how to integrate with your service” cookbook: TLS binding, gRPC interceptor, secret materialization patterns.

# Non-goals

- Writing full enclave runtimes or SDKs.
- Replacing vendor-specific provisioning tools; this is a *verification + binding* foundation.

# Design risks / mitigations

- **API churn in TEEs**: isolate vendor code behind feature-gated modules; commit to stable claims normalization.
- **Security footguns**: deny-by-default policy; “doctor” command that flags missing nonce/freshness checks.
