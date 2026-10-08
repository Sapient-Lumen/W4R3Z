# Epic Proposal: Repro Build Kit (`cargo repro`, `repro-pack/v0`)

## One-sentence pitch
Make Rust release verification stronger than provenance alone by standardizing **lane-aware** rebuild verdicts, diff reasons, attestation attachments, offline-verification bundles, and lifecycle notes.

## Deliverables
- `cargo repro` reference tool
- Design references:
  - `design/repro-build-lane-map.md`
  - `design/repro-build-pilot-program.md`
- Schemas:
  - `repro-subject/v0`
  - `repro-run-report/v0`
  - `repro-compare-report/v0`
  - `repro-attestation-link/v0`
  - `repro-pack/v0`
- Adapters / integrations for:
  - `cargo package` source-package verification context
  - Cargo `sbom` precursor output
  - Cargo `--artifact-dir`
  - dist machine-readable manifests and release assets
  - GitHub provenance and SBOM attestations
  - offline attestation-bundle verification inputs
- Docs:
  - compare modes and strength levels
  - offline verification recipe
  - lifecycle / supersession / stale-evidence guide
  - “common divergence causes” guide for build scripts, debug info, timestamps, native tooling, and post-processing

## Why now (signals)
- Rust 1.91 says **building a crate with `cargo package` should now be independently reproducible**. That is a concrete upstream source-package lane.
  https://doc.rust-lang.org/beta/releases.html
- `cargo package` still verifies by extracting the package and rebuilding it, while also rewriting the manifest and packaging a curated file set. That provides a real boundary to anchor rebuild claims.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo is still pushing `trim-paths`, including remapping all paths to `build.build-dir` and broadening Windows/MSVC coverage. That is active substrate work for final-artifact equivalence.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s unstable `sbom` support now emits precursor files for executable and linkable outputs uplifted into target or artifact directories. That provides stronger artifact-linked inputs for rebuild and release review.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- dist already gives the ecosystem machine-readable release manifests and explicitly says local reruns target ordinary build equivalence, **not bit-level precision**. That is exactly the seam an independent verifier should occupy.
  https://axodotdev.github.io/cargo-dist/book/
- GitHub now provides build-provenance attestations, SBOM attestations, offline verification flows, and lifecycle management. That means the surrounding ecosystem is ready to carry rebuild evidence packs once Rust has a coherent one — as long as provenance stays distinct from equivalence.
  https://docs.github.com/en/actions/concepts/security/artifact-attestations
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline
  https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations

## Non-goals
- Replacing dist, signing tools, or hosted attestation systems
- Promising universal hermetic bit-for-bit reproducibility for every Rust project in v0
- Flattening native dependencies, SDKs, or post-processing steps into a fake Rust-only model
- Treating provenance or SBOM generation as equivalent to rebuild verification
- Treating offline verification bundles as timeless trust anchors

## Strategic value
This is a worthy contribution because it upgrades a lot of adjacent ecosystem work at once:
- **release tooling** gets an independent rebuild check,
- **policy tooling** gets a stronger signal than “workflow passed,”
- **inventory tooling** gets an explicit attachment relationship instead of quiet substitution,
- **air-gapped and mirror-heavy environments** get a portable offline-verifiable artifact,
- **maintainers** get actionable divergence reasons,
- and **the archive’s other kits** gain a clean place to connect source-level evidence to shipped artifacts without collapsing unlike claims.

It also improves the overall coherence of this repo: Release Pipeline Kit, Signed Binaries Kit, SBOM Evidence, Airgap Kit, Policy Kit, and Distribution Contract all become more concrete when there is an honest lane-aware reproducibility contract between them.

## Milestones
1. **v0 source-package and simple-artifact lanes**
   - support `cargo package` subject reports
   - support bitwise and normalized compare modes for simple Rust binaries
   - emit explanation codes for the most common divergence classes
2. **v0.2 native/toolchain and dist lanes**
   - cover `build.rs` / native-tool / linker reasons explicitly
   - ingest dist manifests and release-asset families
   - keep installer/archive compare modes explicit
3. **v0.3 attestation attachment lanes**
   - attach GitHub provenance references
   - attach SBOM-attestation references
   - keep compare absence versus compare mismatch explicit
4. **v0.4 offline + lifecycle lanes**
   - pack + verify workflow for restricted-network use
   - explicit trusted-root and bundle posture
   - stale/superseded/deleted evidence notes
5. **v1 ecosystem convergence**
   - pilot examples across pure Rust, native-dep, and release-pipeline scenarios
   - policy consumers in Release Pipeline / Policy / Incident / Distribution workflows

## Success criteria
- projects can produce rebuild evidence without bespoke CI parsing,
- the evidence explains **which lane** is in play and why divergence happened,
- provenance and SBOM attachments compose without pretending to be equivalence proofs,
- offline verification is first-class but bounded,
- and release/signing/inventory/distribution tooling can attach the result without inventing another one-off format.
