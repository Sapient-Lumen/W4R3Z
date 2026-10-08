# Epic Proposal: Signed Binaries Kit

## One-sentence pitch
Standardize signed prebuilt Rust binaries so fast installs can be secure-by-default, policy-driven, and auditable.

## Deliverables
- Schemas:
  - `binpack/v0`
  - `binverify-report/v0`
- Tools:
  - `cargo-binverify` reference implementation
  - adapters:
    - `cargo-dist` emitter
    - `cargo-binstall` policy wrapper (or plugin)
- CI templates:
  - GitHub Actions signing + publish
  - key rotation cookbook
- Corpus + tests:
  - sample `binpack` for popular CLIs
  - verification regression suite

## Why now
- `cargo-binstall` already has signature verification and an `--only-signed` mode, but coverage is patchy and metadata is ad-hoc.  
  https://github.com/cargo-bins/cargo-binstall  
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- Install workflows explicitly admit “secure-ish” status because signatures are not widely produced.  
  https://github.com/marketplace/actions/install-cargo-binstall
- The ecosystem is investing in broader signing and repository security via TUF, suggesting a good time to standardize distribution contracts at the edge.  
  https://rustfoundation.org/media/rust-foundations-2025-technology-report-showcases-year-of-rust-security-advancements-ecosystem-resilience-strategic-partnerships/

## Non-goals
- Replacing OS package managers
- Mandating one signing algorithm forever
- Solving key management for everyone (we provide recipes and adapters)

## Milestones
1) v0: `binpack/v0` + `cargo binverify` (local/URL) + reports
2) v0.2: `cargo-dist` integration and GitHub Actions templates
3) v0.3: policy wrapper for binstall + issuer allowlists
4) v1: stable schemas + key rotation docs + public regression corpus
