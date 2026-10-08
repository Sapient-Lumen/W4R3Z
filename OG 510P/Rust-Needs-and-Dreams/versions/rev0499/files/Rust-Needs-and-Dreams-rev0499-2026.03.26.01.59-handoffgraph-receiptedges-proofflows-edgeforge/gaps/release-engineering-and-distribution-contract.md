# Gap: Release engineering still lacks one portable release boundary

## Summary
Rust now has credible tools for **publishing crates, cutting GitHub releases, building installers, emitting machine-readable manifests, embedding dependency metadata, and attaching provenance**. What it still lacks is a shared **release boundary contract** that lets those pieces compose into one reviewable object.

Today, release automation is split across:
- crates publishing (`cargo publish`, `cargo-release`, `release-plz`)
- binary distribution (`cargo-dist`, `cargo-packager`)
- consumer installation (`cargo-binstall`)
- evidence/provenance (`cargo-auditable`, CycloneDX, GitHub artifact attestations, signatures)

That fragmentation is manageable for experts, but it keeps “a good Rust release” from becoming boring, portable, and policyable.

## Why now
- Cargo still treats publishing as a permanent act with important verification steps; that raises the value of stronger release evidence and review boundaries.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- crates.io Trusted Publishing has expanded and can now enforce OIDC-based publishing-only flows, which makes CI-driven release pipelines more standard and more security-sensitive.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- `release-plz` has become a serious Rust-native release workflow for changelogs, version bumps, registry publishing, and GitHub/GitLab/Gitea releases, with `cargo-semver-checks` in the loop.
  https://github.com/release-plz/release-plz
- `cargo-dist` now explicitly covers machine-readable manifests, installers, and release hosting, and its current schema crate proves that one part of the ecosystem already wants a stable manifest contract.
  https://crates.io/crates/cargo-dist
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
- `cargo-dist` has also added SBOM generation via `cargo-cyclonedx` and OmniBOR artifact IDs, which is exactly the sort of evidence attachment point a broader release contract should standardize.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `cargo-binstall` still says signature verification support exists but the ecosystem does not yet produce enough signed metadata consistently; it even points toward formalizing around `dist-manifest.json` rather than fragmenting further.
  https://github.com/cargo-bins/cargo-binstall
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- Cargo itself is also growing adjacent primitives such as SBOM precursor files and `--artifact-dir`, which makes a release-boundary kit feel aligned with the platform rather than bolted on.
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html

## Concrete missing pieces
1. **A versioned release manifest**
   - what was published where
   - which artifacts belong to the release
   - target triples, checksums, signatures, updater/install metadata
   - mapping from source publish → binary artifacts → attached evidence

2. **A portable attachment point for other archive outputs**
   - `api-pack/v0`
   - `coverage-pack/v0`
   - `perf-pack/v0`
   - `policy-pack/v0`
   - signed-binary metadata, SBOMs, provenance, and embedded dependency info

3. **Policy over releases, not just builds**
   - release is blocked if signatures are missing
   - release is blocked if public API changed without semver justification
   - release is blocked if required evidence packs are absent
   - release can distinguish “crate publish succeeded” from “binary distribution complete”

4. **One vocabulary for installers and update channels**
   - archives, installers, app bundles, package-manager metadata, updater feeds
   - enough common metadata that install/verify/update tools stop reverse-engineering each tool’s output

5. **Offline verification**
   - users and CI should be able to verify a release pack without trusting a specific SaaS dashboard

## Desired properties
- Converge existing tools instead of replacing them.
- Treat the release boundary as an artifact graph, not a blob of CI YAML.
- Keep hosting/provider choices flexible.
- Compose with crates.io publishing, not just GitHub Releases.
- Preserve provenance across source crate, built binary, and attached evidence.

## Distinction from nearby archive entries
- **Signed Binaries Kit** focuses on signature metadata and verification for prebuilt installs; this kit defines the **whole release boundary** that signed binaries live inside.
- **Public API / Coverage / Perf / Policy Kits** produce inputs that a release should attach and gate on; this kit does **not** replace those domain-specific reports.
- **Cargo Report Kit** standardizes build/test/session reports; this kit standardizes **shipping outputs and attachments**.


## Distinction from consumer-side distribution receipts
This gap is intentionally about the **producer-side release boundary**: what got published, hosted, signed, and attached.
It should stay distinct from the newer **consumer-side distribution-contract** seam, which owns channel choice, mirror choice, source-build fallback, verification behavior during acquisition, and durable install receipts.

Producer release truth should feed consumer distribution truth later, but it should not pretend that “artifact exists in the release” and “consumer installed this artifact through this path” are the same event.
