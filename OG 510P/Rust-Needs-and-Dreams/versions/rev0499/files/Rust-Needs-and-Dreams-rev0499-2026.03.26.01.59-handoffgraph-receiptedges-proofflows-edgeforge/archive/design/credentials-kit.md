# Design: Credentials Kit (`cargo cred`, cred-report/v0)

## Goal
Provide a *boring, adoptable* workflow for credentials in the Rust toolchain ecosystem by defining:
- a reference CLI (`cargo cred`),
- a portable `cred-report/v0` schema (no secret values),
- adapters for common secret sources (keychain, env, SOPS+age, CI OIDC).

This kit does **not** replace vault products. It standardizes the glue.

## References (signals)
- Cargo publishing: tokens stored locally; “token is a secret”.  
  https://doc.rust-lang.org/cargo/reference/publishing.html
- crates.io Trusted Publishing (OIDC CI publishing).  
  https://crates.io/docs/trusted-publishing
- SOPS recommends age; common “secrets-in-git” encryption.  
  https://github.com/getsops/sops

## Core UX: `cargo cred`
### Local developer workflows
- `cargo cred login crates-io`  
  - prefer OIDC device flow where possible; otherwise store token in OS keychain
  - write a *pointer* into `~/.cargo/credentials.toml` (not the raw secret)
- `cargo cred set <name>` / `cargo cred get <name>`  
  - store/retrieve via keychain providers (macOS Keychain, Windows Credential Manager, libsecret)
- `cargo cred redact`  
  - scan common logs/artifacts and redact known secret patterns
- `cargo cred doctor`  
  - check for:
    - tokens accidentally committed,
    - `.env` files in git,
    - unsafe env var practices,
    - overly broad CI secrets.

### CI workflows
- `cargo cred oidc mint --audience <...> --scope <...>`  
  - produce short-lived credentials derived from CI identity
- `cargo cred report`  
  - emit `cred-report/v0` documenting sources, scopes, freshness, and redaction rules (NO secrets)

## Artifact: `cred-report/v0`
A release/CI attachable report describing secret *handling*, not values:
- project ID + git commit
- required credentials (names, scopes, consumers)
- source types used:
  - `OIDC`, `KEYCHAIN`, `ENV`, `SOPS_AGE`, `VAULT`, `FILE`
- policy flags:
  - `NO_PLAINTEXT_ON_DISK`
  - `NO_LONG_LIVED_TOKENS`
  - `REDACT_LOGS`
- issuer identity (for OIDC) + audience
- expiry windows (min/max)
- “leak checks performed” list

## Integration points
- Release Pipeline Kit: attach `cred-report/v0` to release evidence packs.
- Trust Signals Kit: record `PUBLISHING_CONTROL` signals (OIDC vs long-lived token).
- Hermetic Build Kit: enforce allowlists for env vars and files (secrets-as-inputs).

## Safety constraints
- Never print secret values; default redaction for known patterns.
- Provide opt-in “break glass” modes with explicit warnings and audit trails.
- Explicitly model build deps/proc-macros separately (higher risk posture).

## Evaluation plan
- Measure adoption friction:
  - does it remove the need to touch `~/.cargo/credentials.toml` directly?
  - does it reduce token leakage incidents?
- CI pilots:
  - publish via Trusted Publishing (OIDC) where possible
  - generate `cred-report/v0` and store it with other release evidence
