---
id: P-0105
title: Secrets Envelope & Policy Kit
status: idea
domains: [security, secrets, devops, policy]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/getsops/sops
  - https://github.com/FiloSottile/age
  - https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html
  - https://docs.rs/secrecy
---

# P-0105 — Secrets Envelope & Policy Kit (SOPS/age/KMS-aware)

## One-liner
A Rust-first way to ship **policy-governed secret envelopes**: decrypt/rotate/validate secrets with auditable policy and ergonomic app integration.

## What it provides other people
- A **typed “secret envelope” format** (`secrets.toml` + encrypted payloads) with:
  - schema validation
  - key provenance metadata
  - rotation history
- Pluggable backends:
  - **SOPS-compatible file envelopes** (age/PGP/KMS) as a first-class import/export path citeturn0search1turn0search9
  - optional cloud KMS integration hooks (AWS/GCP/Azure) via feature flags.
- A small **policy engine**:
  - “which service can decrypt which secret”
  - environment scoping (dev/stage/prod)
  - time-based/rotation constraints
- `cargo secrets {check,rotate,doctor,export-sops}`:
  - `check` emits `secrets-report.json` for CI
  - `doctor` detects footguns (missing rotation, over-broad access, dev keys in prod)

## MVP (0.x)
- Envelope spec + serde types + CLI.
- SOPS import/export and “decrypt for runtime” (into memory only).
- Policy checks + CI report output.

## v1 goals
- “Sealed secrets” patterns for application configs (not just Kubernetes):
  - per‑env keysets, per‑service scopes, explicit audit trails.
- Standard library-style ergonomics:
  - `Secret<T>` wrapper with explicit “expose” boundaries
  - redaction-friendly logging.

## Non-goals
- Not a replacement for Vault/ESO/etc; this is a **developer-facing envelope + policy kit** that interoperates with existing secret stores.

## Why now / why missing
- SOPS is widely used for encrypted config files across environments (age/PGP/KMS). citeturn0search1turn0search9
- Rust has crypto primitives and secret-string wrappers, but there’s no canonical **application-level workflow** tying together: envelope format → policy → rotation → CI gates.

## Design risks
- Key management UX: keep defaults safe and “boring” (age-only MVP).
- Avoid “magic”: explicit policy files and explicit “decrypt points” in code.
