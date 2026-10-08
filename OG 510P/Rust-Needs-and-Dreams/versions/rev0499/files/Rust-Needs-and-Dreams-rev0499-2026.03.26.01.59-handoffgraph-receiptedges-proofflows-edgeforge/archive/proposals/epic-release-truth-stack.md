## Execution addendum (rev0455)
Treat `design/release-truth-execution-blueprint-2026Q1.md` as the canonical answer to “what should this epic actually ship?” before reading the proposal below.

Interpretation rule:
- the epic pitch is unchanged;
- this revision clarifies that the epic's primary shape is **reference layer + report/pack command + attachment/import corpus**;
- and the proposal should keep producer-side release truth bounded below distribution/update/runtime claims and above raw package/artifact/signature/rebuild/inventory leaves.

# Epic Proposal: Release Truth Stack (`cargo release-truth` + `release-truth-pack/v0`)

## One-sentence pitch
Make Rust release evidence boring by standardizing a portable **producer-side** release boundary that composes package publication, artifact publication, signatures, rebuild evidence, and inventory attachments without confusing them with consumer-side installation.

## Deliverables
- `cargo release-truth` reference tool
- schemas:
  - `release-truth-brief/v0`
  - `release-truth-diff/v0`
  - `release-truth-pack/v0`
  - `release-truth-handoff/v0`
- adapters/importers for:
  - `release-pack/v0`
  - `binpack/v0`
  - `binverify-report/v0`
  - `repro-pack/v0`
  - `sbom-evidence-pack/v0`
  - selected package-admission / policy attachments
- docs:
  - crate-only release recipe
  - source+binary release recipe
  - signed-binary and rebuild attachment guide
  - producer-side handoff guide for distribution / policy / incident consumers

## Why now (signals)
- Publishing on crates.io is permanent and starts from an explicit package boundary.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- crates.io Trusted Publishing has become real ecosystem infrastructure, with GitHub Actions support in 2025 and GitLab support / TP-only mode / blocked risky triggers in 2026.
  https://blog.rust-lang.org/2025/07/11/crates-io-development-update-2025-07/
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust’s 2026 flagship work keeps public/private dependencies and SBOM support on the active supply-chain roadmap, which increases the value of release-native attachment points.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo and the ecosystem already expose serious ingredients (`cargo ship` concepts, `cargo-dist` manifests, signed-install conventions, rebuild evidence concepts), so the missing work is the shared contract layer rather than another bespoke workflow wrapper.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md
  https://github.com/release-plz/release-plz

## Non-goals
- replacing `release-plz`, `cargo-release`, `cargo-dist`, or `cargo-binstall`;
- defining consumer-side install/update/fallback semantics;
- pretending signatures, provenance, SBOMs, and rebuilds are one status bit;
- making GitHub Releases, crates.io pages, or any host page the only authoritative release record.

## Strategic value
This deserves promotion because it gives the archive a **release-native composition point**.
With it:
- library teams can publish crate releases with attached API/policy/inventory evidence;
- CLI and app teams can keep source publish and downloadable binaries tied to one release subject;
- security/compliance reviewers can require signatures, rebuilds, or inventory attachments without rewriting release pipelines;
- downstream packagers and install tools can import producer-side facts instead of reverse-engineering host pages.

The prize is not another release wrapper.
The prize is a reviewable producer-side boundary that other tools can import.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import `release-pack/v0` as the core producer boundary;
2. attach `binpack/v0` / `binverify-report/v0` when prebuilt binaries exist;
3. attach `repro-pack/v0` when rebuild evidence exists;
4. attach inventory evidence packs without flattening them;
5. emit `release-truth-handoff/v0` for downstream distribution/policy/incident/support consumers;
6. provide release-to-release diffing that preserves lane distinctions.

## Critical design bet
The critical bet is that **release truth should stop at producer-side publication and evidence**.
That means:
- package publication is included,
- built artifact publication is included,
- signatures and rebuild evidence are attached,
- inventory continuity is attached,
- but mirror ordering, fallback logic, and installed-state receipts stay downstream.

Without that boundary, the stack will either stay too weak to matter or bloat into a fake universal supply-chain platform.

## Milestones
1. **v0 schemas + crate-only lane**
   - `release-truth-brief` / `release-truth-pack`
   - import `release-pack/v0`
2. **v0.2 source+binary lane**
   - ingest artifact-manifest inputs
   - tie `.crate` and binary artifacts to one release subject
3. **v0.3 signed-binary lane**
   - attach `binpack` / `binverify-report`
   - expose explicit policyable verification outcomes
4. **v0.4 rebuild lane**
   - attach `repro-pack`
   - preserve rebuild strength and diff reasons in stack-level diffs
5. **v1 inventory / downstream handoffs**
   - attach inventory evidence
   - emit bounded handoffs for distribution / policy / incident consumers

## Execution order
Use [`design/release-truth-pilot-program.md`](../design/release-truth-pilot-program.md) as the stack-level rollout:
1. crate-only publish continuity lane,
2. source + binary coherence lane,
3. signed-binary attachment lane,
4. independent rebuild attachment lane,
5. inventory and distribution handoff lane.

Use [`design/release-pipeline-pilot-program.md`](../design/release-pipeline-pilot-program.md) as the leaf-level release-pipeline execution guide beneath it.

## Success metrics
- maintainers can reconstruct producer-side release facts offline from one pack;
- binary-verification and rebuild evidence can attach without being flattened;
- inventory evidence can travel with the release without silently becoming the release;
- downstream consumers can import producer-side truth without re-scraping CI or host pages;
- the ecosystem gets one release-native evidence boundary instead of several incompatible mini-manifests.
