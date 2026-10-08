# Epic Proposal: Release Pipeline Kit (`cargo ship`, `release-pack/v0`)

## One-sentence pitch
Make shipping Rust software boring by standardizing a portable release boundary that composes publishing, binary artifacts, signatures, SBOMs, provenance, and independent rebuild evidence.

## Deliverables
- `cargo ship` reference tool
- Schemas:
  - `release-subject/v0`
  - `release-intent/v0`
  - `release-manifest/v0`
  - `release-policy/v0`
  - `release-pack/v0`
- Adapters / importers for:
  - `release-plz`
  - `cargo-release`
  - `cargo-dist`
  - `cargo-packager`
  - `cargo-binstall` signing expectations
  - Cargo SBOM precursor outputs / artifact collection lanes
  - attached packs from Public API / Policy / SBOM / Safety / Signed Binaries / Repro Build
- Docs:
  - crate-only vs binary-app recipes
  - signed-install and rebuild-verification attachment guide
  - offline verification / mirror guide

## Why now (signals)
- Publishing is permanent, which makes release-boundary truth more valuable than ephemeral CI logs.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- crates.io Trusted Publishing now supports stronger CI identity controls, including GitLab CI/CD, TP-only mode, and blocked risky triggers.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo is exploring explicit final-artifact uplift and already has unstable SBOM/artifact collection directions, which gives a future release-boundary kit better native attachment points.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- The ecosystem already has serious point tools for release orchestration and distribution (`release-plz`, `cargo-release`, `cargo-dist`, `cargo-binstall`), which means the missing contribution is now the shared contract layer rather than another bespoke pipeline.
  https://github.com/release-plz/release-plz
  https://crates.io/crates/cargo-release
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
- The infrastructure side has stated that the crates.io package format likely is not the final answer for every Rust use case, especially where precompiled material is relevant. That is a strong sign the release/distribution story still needs deliberate ecosystem design.
  https://blog.rust-lang.org/2025/11/25/interview-with-jan-david-nose/

## Non-goals
- Replacing `release-plz`, `cargo-release`, `cargo-dist`, or `cargo-binstall`
- Defining every installer/package-manager format in v0
- Pretending signatures and reproducibility are the same thing
- Treating a hosted release page as the authoritative release record

## Strategic value
This is a worthy contribution because it gives the ecosystem a **release-native composition point**:
- library teams can ship with attached API/policy evidence instead of custom CI glue,
- CLI/app teams can tie crate publishing and downloadable artifacts into one release subject,
- consumers can verify signatures and rebuild evidence without reverse-engineering host pages,
- and many other archive kits finally get a natural place to land.

The real prize is not another release wrapper. The prize is a release pack that humans, CI, mirrors, policy tools, and downstream packagers can all consume honestly.

## Milestones
1. **v0 schemas + crate-only publish lane**
   - `release-subject` / `release-intent` / `release-manifest` / `release-policy` / `release-pack`
   - crates.io publish + attached evidence only
2. **v0.2 CLI binary lane**
   - ingest `dist-manifest.json` or equivalent artifact inventory
   - support `binpack/v0` attachment and signed-install verification reports
3. **v0.3 rebuild lane**
   - attach `repro-pack/v0`
   - add offline verification and mirror-friendly bundle rules
4. **v1 multi-channel convergence**
   - package-manager / installer / desktop-app recipes
   - org policy examples over release packs

## Execution order
Use [`design/release-pipeline-pilot-program.md`](../design/release-pipeline-pilot-program.md) as the ranked rollout for this epic:
1. crate-only publish lane,
2. CLI binary lane,
3. signed-install lane,
4. independent rebuild lane,
5. multi-channel / installer / mirror lane.
