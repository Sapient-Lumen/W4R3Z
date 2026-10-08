---
id: P-0110
title: Passkey Platform Kit — storage-agnostic WebAuthn/Passkeys integration with adapters, diagnostics, and “credential bundles”
status: idea
domains: [security, authentication, web, mobile, interoperability, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/1Password/passkey-rs
  - https://docs.rs/webauthn-rs/latest/webauthn_rs/
  - https://learn.microsoft.com/en-us/windows/apps/develop/security/tools-libraries
  - https://crates.io/crates/passkey
needs:
  - passkeys are “real world auth” now, but Rust apps repeatedly rebuild integration glue (storage, serialization, transports, UX diagnostics)
  - libraries exist (passkey-rs, webauthn-rs) yet teams still struggle with end-to-end *production* ergonomics (DB schema, migrations, recovery flows, client bridging)
  - maintainers need a consistent way to triage auth failures without shipping secrets
---

# Problem

Rust has solid WebAuthn/Passkeys foundations, but the missing piece is a **coherent integration surface**:
storage models, server-framework adapters, device/client helpers, and repeatable diagnostics.

Today, teams frequently reinvent:
- credential serialization and schema choices
- per-framework plumbing (Axum/Actix/Warp)
- “why did registration/auth fail?” triage tooling

# What it provides

## 1) A stable “credential bundle” artifact

A portable, shareable bundle that helps reproduce issues without leaking private material:

`*.passkeybundle.zip`
- `request.json` / `response.json` (normalized CBOR/JSON/base64 inputs, redactions)
- `rp.json` (RP ID/origin settings, allowed transports, UV requirements)
- `server_versions.json` (crate versions + feature flags)
- `diagnostics.json` (reason codes, verification trace *without* secrets)
- optional `testkey/` (dev-only seed keys for deterministic tests)

## 2) Storage-agnostic credential persistence contracts

A small set of traits + reference schemas:
- `CredentialStore` + `UserHandleStore`
- schema guidance for Postgres/SQLite (binary column types; indexing)
- pluggable enc-at-rest (envelope approach: “ciphertext + key_id + policy”)

Adapters:
- `store-sqlx`, `store-diesel`, `store-seaorm`
- optional `store-kv` (sled/rocksdb)

## 3) Framework adapters + example “golden paths”

- `axum-passkeys`, `actix-passkeys`
- shared extractors/response types and cookie/session patterns
- integration docs: origin/rpID pitfalls, reverse proxies, device enrollment

## 4) A cargo-native doctor

`cargo passkey doctor`:
- checks rpID/origin config, TLS settings, allowed algorithms
- validates DB schema and migration presence
- generates a sanitized `passkeybundle` for bug reports

# MVP (4–6 weeks)

- Core bundle spec + redaction policy
- `CredentialStore` trait + `sqlx` adapter (Postgres + Sqlite)
- Axum adapter sample app + integration tests

# v1 (8–16 weeks)

- Support both `passkey-rs` and `webauthn-rs` backends behind a common façade (feature-gated)
- Add `actix` adapter + `diesel` adapter
- Conformance fixtures:
  - registration/auth happy paths
  - counter/clone detection behavior (where supported)
  - algorithm and UV policy matrices

# Architecture sketch

- `passkey-platform-core`: traits, types, bundle spec
- `passkey-platform-backend-{passkey_rs,webauthn_rs}`: backend-specific glue
- `passkey-platform-store-*`: persistence
- `passkey-platform-web-*`: framework adapters
- `cargo-passkey`: doctor + bundle tooling

# Risks and mitigations

- **Spec/interop churn:** treat the kit as an integration layer with strict versioned bundle formats.
- **Secret leakage:** hard rule: bundles never include private keys; offer dev-only deterministic fixtures.
- **Fragmentation:** focus on “one golden path” per framework + storage, not endless options.
