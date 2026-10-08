# Epic Proposal: Credentials Kit (cargo cred)

## One-sentence pitch
Make Rust’s secret/credential handling safe-by-default by standardizing a keychain+OIDC workflow and emitting non-secret evidence reports.

## Deliverables
- `cargo-cred` reference implementation:
  - keychain backends (macOS/Windows/Linux)
  - OIDC minting helpers for common CIs
  - redaction + doctor checks
- Schemas:
  - `cred-report/v0`
  - `cred-policy/v0` (org rules)
- Recipes:
  - crates.io publishing:
    - Trusted Publishing first
    - fallback token in keychain
- Test corpus:
  - known leak patterns + regression tests
  - “bad repo” fixtures (accidentally committed `.env`, tokens in logs)

## Why now (signals)
- Cargo still stores API tokens locally and must warn users not to leak them.  
  https://doc.rust-lang.org/cargo/reference/publishing.html
- crates.io has invested in Trusted Publishing via OIDC, shifting best practice toward short-lived identity-based publishing.  
  https://crates.io/docs/trusted-publishing
- SOPS+age remains a pragmatic “secrets in git” approach in broader infra; Rust dev workflows need a standard adapter layer.  
  https://github.com/getsops/sops

## Non-goals
- Building a new vault product
- Forcing a single secret backend
- Storing any secret values in reports

## Milestones
1) v0: keychain-backed creds for crates.io token + `cred-report/v0`
2) v0.2: doctor + redaction + policy checks
3) v0.3: OIDC helpers and integration with release evidence
4) v1: stable schemas, CI templates, and org policy pack
