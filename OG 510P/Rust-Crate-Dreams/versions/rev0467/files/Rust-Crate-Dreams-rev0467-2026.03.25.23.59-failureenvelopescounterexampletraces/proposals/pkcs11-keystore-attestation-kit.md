---
id: P-0171
title: PKCS#11 KeyStore & HSM Workbench Kit — safe high-level flows + evidence bundles for tokens/HSMs
status: idea
domains: [security, crypto, hsm, hardware, compliance]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/cryptoki/
  - https://crates.io/crates/cryptoki
  - https://github.com/parallaxsecond/rust-cryptoki
  - https://docs.rs/crate/pkcs11/latest
  - https://cryptography.rs/
---

## What it should provide others

A **high-level, safe** operational layer above PKCS#11 that makes “use keys in tokens/HSMs” boring:

- **Profiles** for common devices/providers (SoftHSM2/YubiHSM/HSM-as-a-service adapters).
- **Ergonomic flows** (generate/import, sign, decrypt, wrap/unwrap, rotate, backup escrow policies).
- **Policy gates** (allowed mechanisms, key sizes, label conventions, per-app isolation).
- **Evidence bundles** for incident triage and compliance.

Deliverables:

- `Keystore` abstraction with explicit capabilities:
  - key discovery + selection by policy (slot/token/label),
  - mechanism negotiation (with explicit allow/deny lists),
  - session + concurrency handling patterns.
- `cargo pkcs11 doctor` — detects library path issues, token presence, permissions, and mechanism availability.
- `*.pkcs11bundle.zip` (redacted) for “this broke in prod”:
  - token metadata fingerprints,
  - mechanism list summary,
  - operation transcript (without key material),
  - version + env capture and a stable `report.json`.

## Why this is still missing

Existing crates focus on PKCS#11 bindings/wrappers. What teams still build themselves:

- safe, profile-driven *usage patterns*,
- policy enforcement,
- reproducible debug artifacts that don’t leak secrets.

## Design principles

- **No hidden magic**: everything security relevant is explicit and auditable.
- **Redaction-first**: bundles default to safe export; “unsafe exports” are feature-gated.
- **Testable via emulators**: SoftHSM2-based conformance suite + recorded corpora.

## MVP

- Support core flows (sign/verify; key generation) on top of `cryptoki`.
- SoftHSM2 conformance harness + `pkcs11bundle.zip` schema.
- A tiny policy language (TOML) for allowed mechanisms and minimum sizes.

## v1

- Device profiles; key rotation playbooks; multi-tenant isolation helpers.
- Optional integrations: TPM, KMS envelopes, and attestation tie-ins.

## Key risks / sharp edges

- Vendor quirks and incomplete mechanism support: treat **profiles + conformance suite** as first-class.
- Avoid encouraging insecure defaults; ship a “secure baseline” policy.
