# Gap: Signed Prebuilt Binaries (Install UX + Verification + Policy)

## Summary
Rust’s source-based story is strong, but the “install a tool quickly” workflow is increasingly **prebuilt-binary-first**
(`cargo binstall`, GitHub Releases, package managers). Today:
- Some tools ship signatures, but there’s no standard packaging/metadata contract.
- Verification is inconsistent: many installs rely on TLS + checksums, not end-to-end signatures.
- Org policy (e.g., “only install signed binaries”) is hard to enforce across toolchains.

This gap is about standardizing **signed binary distribution** so that prebuilt installs can be secure-by-default and auditable.

## Ecosystem signals
- `cargo-binstall` supports downloading and verifying package signatures, with `--only-signed` to require signatures.  
  Source: cargo-binstall repository docs (Signatures).  
  https://github.com/cargo-bins/cargo-binstall
- `cargo-binstall` has a signing guide describing signature verification support and current algorithm limitations.  
  Source: SIGNING.md.  
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- GitHub Marketplace action for installing `cargo-binstall` notes signature verification exists, but ecosystem coverage is limited.  
  Source: marketplace action docs.  
  https://github.com/marketplace/actions/install-cargo-binstall
- The Rust Foundation highlights progress on crate signing infrastructure using TUF (Update Framework) and ecosystem resilience initiatives.  
  Source: Rust Foundation 2025 Technology Report (security advancements).  
  https://rustfoundation.org/media/rust-foundations-2025-technology-report-showcases-year-of-rust-security-advancements-ecosystem-resilience-strategic-partnerships/

## What “good” looks like
- A standard metadata contract for “where is the tarball + signature + key + provenance?”
- Verification that composes with:
  - Trusted Publishing identities (OIDC) where possible
  - future index/repository signing (TUF)
- Policy hooks:
  - “only signed”
  - “only trusted issuers”
  - “only reproducible builds” (optional)
- Portable reports that can be attached to releases and used in audits.
