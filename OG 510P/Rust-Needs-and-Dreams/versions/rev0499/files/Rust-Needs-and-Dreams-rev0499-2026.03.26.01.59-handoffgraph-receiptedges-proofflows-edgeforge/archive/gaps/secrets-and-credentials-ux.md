# Gap: Secrets & Credentials UX for Rust Tooling (Dev + CI)

## Summary
Rust projects routinely require secrets:
- crates.io API tokens (publishing),
- registry credentials (private registries),
- cloud credentials (release pipelines, artifact signing, deploy),
- database URLs and service keys (runtime).

Today, the “default” is still a mix of `.env`, ad-hoc shell exports, and CI secret stores. There are good tools in the broader ecosystem (SOPS+age, vaults, keychains), and crates.io is investing in **Trusted Publishing** (OIDC), but Rust lacks an opinionated, interoperable **workflow layer** for:
- managing credentials locally without leaking into disk or logs,
- making CI identity/provenance explicit,
- packaging “secret-handling evidence” for audits.

## Ecosystem signals
- Cargo stores the crates.io API token locally (credentials file) and warns it is a secret that must not leak.  
  Source: Cargo Book — publishing (`cargo login`, `~/.cargo/credentials.toml`).  
  https://doc.rust-lang.org/cargo/reference/publishing.html
- crates.io supports **Trusted Publishing** using OIDC identity from CI (reducing long-lived tokens).  
  Source: crates.io docs.  
  https://crates.io/docs/trusted-publishing
- SOPS recommends **age** as a modern mechanism for encrypting files, and is widely used for “secrets-in-git” workflows.  
  Source: SOPS repository docs.  
  https://github.com/getsops/sops

## What “good” looks like
- One CLI entrypoint for secret/credential flows that composes with Cargo and release tooling.
- Strong defaults: keychain support, redaction, leak prevention, explicit scopes.
- CI-friendly: OIDC-first, short-lived credentials, explainable provenance.
- Portable reports (what was required, how it was sourced) without exposing secret values.
