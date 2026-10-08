# Design: Signed Binaries Kit (`binpack/v0`, `cargo binverify`)

## Goal
Make prebuilt binary distribution reviewable and policyable by defining:
- `binpack/v0`: artifact + issuer + signature metadata for downloadable binaries,
- `cargo binverify`: verification UX,
- `binverify-report/v0`: a portable verification result that other tools can consume.

This kit is **not** the whole release boundary. It is the signed-install attachment layer inside the archive’s **Release Truth Stack**.

## References (signals)
- `cargo-binstall` provides a low-complexity path for installing prebuilt Rust binaries instead of compiling from source.
  https://github.com/cargo-bins/cargo-binstall
- `cargo-binstall` already supports signature verification but requires explicit metadata rather than auto-discovery.
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- `cargo-dist` already produces release artifact manifests and has a published schema crate for them.
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
- `cargo-dist` also added OmniBOR artifact IDs and SBOM support, which are adjacent but distinct attachment surfaces.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- crates.io Trusted Publishing is strengthening publisher identity on the source-release side, which makes artifact-side issuer/signature truth more valuable instead of less.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The Rust Foundation’s 2025 technology report highlights supply-chain security and TUF-related work as active ecosystem investment.
  https://rustfoundation.org/media/rust-foundations-2025-technology-report-showcases-year-of-rust-security-advancements-ecosystem-resilience-strategic-partnerships/

## Core UX
### Producer (maintainers)
- `cargo binpack` (or `cargo dist --binpack`) emits:
  - platform archives / installers
  - checksums
  - signature files
  - `binpack.json` metadata describing artifacts + issuers + signature material / references
- optionally attach this inside `release-pack/v0`

### Consumer (users / orgs)
- `cargo binverify <url-or-path>`:
  - fetches metadata + artifacts
  - verifies checksums + signatures
  - optionally checks issuer policy (trusted keys / allowed CI identity)
  - emits `binverify-report/v0`

## Schemas
### `binpack/v0`
- subject: release subject / package version / commit
- artifacts:
  - target triple
  - url or path
  - sha256
  - size
  - archive / installer kind
- signatures:
  - signature url or attachment
  - algorithm
  - key / issuer reference
- provenance pointers:
  - optional attestation / SBOM / OmniBOR pointers
  - optional `release-pack/v0` backreference

### `binverify-report/v0`
- verification result: PASS / WARN / FAIL / INCONCLUSIVE
- reason codes:
  - `NO_SIGNATURE`
  - `BAD_SIGNATURE`
  - `UNKNOWN_ISSUER`
  - `HASH_MISMATCH`
  - `WEAK_ALG`
  - `METADATA_MISSING`
  - `PROVENANCE_MISSING`
- policy evaluation details
- issuer / key notes

## Design rules
- **Keep installable artifacts distinct from source publish.** A signed tarball is not the `.crate` upload.
- **Do not absorb release policy.** This kit reports signature truth; broader release policy belongs in Release Pipeline Kit.
- **Do not equate signatures with reproducibility.** Rebuild evidence stays in Repro Build Kit.
- **Support explicit incompleteness.** Missing signatures or missing metadata must be representable without pretending the lane passed.

## Integration points
- **Release Pipeline Kit:** `binpack/v0` and `binverify-report/v0` are attachments inside `release-pack/v0`.
- **Distribution Contract Stack:** consumer-side install selection and receipts should import binary verification results rather than recompute or blur them into channel/fallback logic.
- **Policy Kit / Trust Signals Kit:** consume verification reports as explainable release inputs.
- **Repro Build Kit:** combine only at the release layer; do not flatten “signed” and “independently rebuilt” into one claim.
- **TUF future:** repository-level guarantees can sit above `binpack`, not replace it.

## Evaluation plan
Follow the signed-install lane in [`design/release-pipeline-pilot-program.md`](./release-pipeline-pilot-program.md):
- pilot on CLI tools with downloadable binaries,
- test tampered tarball / swapped URL / key rotation / weak algorithm cases,
- require failures to be understandable in one or two screens.
