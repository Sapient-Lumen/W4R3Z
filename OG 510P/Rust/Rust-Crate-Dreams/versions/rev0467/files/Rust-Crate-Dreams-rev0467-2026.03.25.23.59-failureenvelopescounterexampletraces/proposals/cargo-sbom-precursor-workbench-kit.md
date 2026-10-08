---
id: P-0125
title: Cargo SBOM Precursor Workbench Kit — precursor capture locks, normalized build-graph transforms, and diffable review bundles
status: idea
domains: [cargo, security, supply-chain, compliance, devtools]
last_reviewed: 2026-03-23
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://github.com/rust-lang/rfcs/pull/3553
---

# Problem

Cargo SBOM support is no longer a distant curiosity.
It is now an explicit 2026 stabilization target, and Cargo already has real substrate:

- the unstable `sbom` build config emits `*.cargo-sbom.json` precursor sidecars alongside executable and linkable artifacts,
- `CARGO_SBOM_PATH` gives crates a discovery hook for generated precursor files,
- the precursor schema already records fully-qualified package IDs, enabled features, dependency edges, and rustc provenance,
- Cargo’s external-tools JSON already exposes the primary `compiler-artifact` stream that downstream tools can correlate against,
- and recent Cargo changes are still refining SBOM behavior (for example clarifying that package ID specifications are fully qualified).

That is enough substrate to prove that Cargo-level SBOM generation is becoming real.
It is **not** enough to make ordinary teams or tool authors boringly successful.

Today the workflow is still fragile:

- maybe enable `-Z sbom` in one nightly job,
- maybe collect `*.cargo-sbom.json` files from wherever the build left them,
- maybe guess which precursor belongs to which promoted artifact,
- maybe transform the precursor into CycloneDX or SPDX,
- maybe compare two outputs with a format-specific diff,
- and maybe lose the exact build scope, toolchain, and discovery source that made the result trustworthy.

The missing crate is not simply “yet another SBOM emitter”.

The missing crate is a **Cargo SBOM precursor workbench**: a crate and cargo-adjacent tool that turns Cargo’s precursor sidecars into a durable **capture lock, normalization report, transform receipt, diffable review bundle, and policy/VEX handoff surface**.

## 2026-03-23 implementation refresh — capture route, artifact coverage, and claim ceilings

The current Cargo docs now make three more receiver-facing review objects worth promoting.

### 1. Capture route needs to be first-class

Cargo now documents two especially meaningful discovery surfaces:

- direct precursor discovery via `CARGO_SBOM_PATH`, and
- per-step artifact context via `compiler-artifact` JSON messages.

Those are stronger than a later directory scan, and a worthy crate should preserve that difference.
A reviewable `0.2` should therefore promote **`capture-route.receipt.json`** into first-class status.

### 2. Artifact coverage needs to be explicit

The unstable Cargo docs now say precursor files are generated only for **executable and linkable outputs** that are **uplifted into the target or artifact directories**.
That means some Cargo outputs are simply outside the precursor surface and should not be reported as “missing SBOM evidence”.
A worthy crate should therefore promote **`artifact-coverage.report.json`** into first-class status.

### 3. Claim ceilings need to stay visible

The external-tools docs say `compiler-artifact` messages can be emitted with `fresh = true`, meaning Cargo may report an artifact even when rustc was not executed in the current invocation.
Combined with imported target trees or artifact-dir copies, this makes “precursor exists” weaker than “precursor was generated now in this reviewed invocation”.
A worthy crate should therefore promote **`coverage-ceiling.report.json`** into first-class status and join it into one portable **`sbom-workbench-bundle.manifest.json`**.

# What it provides

- `sbom-precursor.capture-lock.json` — pins workspace selection, targets, profile, toolchain, acquisition mode, and redaction posture.
- `precursor-ingest.report.json` — records which precursor files were observed, how they were discovered, which primary artifacts they were matched to, and which matches remain ambiguous.
- `capture-route.receipt.json` — records whether evidence came from one direct build, imported target/artifact tree, imported bundle, or manual reconstruction, and which discovery sources were used.
- `artifact-coverage.report.json` — records which Cargo outputs were eligible for precursor generation, which were observed, and which were outside the documented precursor surface.
- `coverage-ceiling.report.json` — records where imported trees, copied outputs, fresh-cache reuse, or non-linkable outputs fence the strongest honest claim.
- `normalized-build-graph.report.json` — one stable internal representation of packages, edges, feature sets, targets, and rustc provenance.
- `sbom-transform.report.json` — records which format(s) were emitted, which precursor fields were preserved exactly, and which required normalization or dropped information.
- `vex-stub.report.json` — optional starter artifact for exploitability or “not affected” workflows, grounded in the normalized graph rather than one emitter’s private assumptions.
- `sbom-diff.report.json` — compares two precursor bundles and classifies `component_added`, `component_removed`, `edge_kind_changed`, `feature_set_changed`, `root_artifact_changed`, `provenance_changed`, and `manual_review_required`.
- `evidence-source.receipt.json` — states whether evidence came from direct precursor capture, sidecar scan, imported bundle, or conservative reconstruction.
- `cargo sbom-workbench capture` — run one build or import one build directory and emit a precursor bundle.
- `cargo sbom-workbench transform` — precursor bundle → normalized graph → CycloneDX/SPDX outputs plus receipts.
- `cargo sbom-workbench diff <old> <new>` — compare two bundles without pretending format-level diffs alone are enough.
- `*.sbomworkbench.zip` — portable artifact for CI, release review, internal security, auditors, or downstream packagers.

# What the crate should provide other people

1. **A boring capture-route artifact** for how SBOM precursor files were obtained and whether the bundle came from a direct build or imported output tree.
2. **An artifact-coverage report** that says which outputs were eligible, observed, missing, or out of scope.
3. **A coverage-ceiling report** that says where copied exports, imported trees, or fresh-cache reuse stop stronger claims.
4. **A stable normalized graph** that multiple format emitters or policy engines can share.
5. **A transform receipt** that says what stayed exact versus what was normalized or lost.
6. **A diffable review layer** for release-to-release supply-chain changes.
7. **A bridge** between Cargo’s precursor sidecars and downstream SBOM / VEX / policy workflows.

# Persona / who it’s for

- release and CI engineers who need reproducible supply-chain artifacts
- security/compliance teams who want reviewable SBOM generation inputs
- tool authors building Cargo-native CycloneDX / SPDX / VEX / policy tooling
- workspace maintainers who need evidence bundles rather than logs and ad-hoc scripts

# Users & user stories

- **Release engineer**: “Capture the exact precursor evidence behind this release SBOM so another team can verify how it was produced.”
- **Security reviewer**: “Tell me whether this release changed because dependencies changed or because target/features/toolchain/provenance changed.”
- **Tool author**: “Give me one normalized graph instead of making me rediscover Cargo’s precursor semantics for myself.”
- **Auditor**: “Show which parts of the final SBOM came directly from Cargo precursor data versus later normalization or policy overlays.”

# Prior art (and why it’s insufficient)

- Cargo’s `-Z sbom` support is the right substrate, but it is still a raw precursor sidecar, not a durable workflow artifact.
- Cargo’s external-tools JSON identifies built artifacts, but it does not freeze how SBOM precursor discovery and artifact matching were performed.
- Existing Cargo SBOM tools prove demand, but they usually combine ingestion, normalization, emission, and policy in one tool-local stack.
- The archive already has **P-0479 Cargo Artifact Sidecar Contract Kit**. That proposal is narrower: it is about attachment and schema drift for sidecars in general. This proposal is specifically about **turning Cargo’s SBOM precursor into a normalized, reviewable supply-chain bundle**.
- The archive also has publish-surface, public-dependency, and provenance proposals. Those are adjacent but different: they answer **who published**, **what is publicly exposed**, or **how identity/provenance is joined**, not the **precursor-to-SBOM workflow** itself.

What remains missing is a **precursor capture + normalization + diff + review bundle** above Cargo’s raw SBOM substrate.

# Design goals

1. **Precursor-first** — start from Cargo’s own build-time evidence instead of reconstructing everything later from `cargo metadata`.
2. **Route-honest** — preserve direct build capture versus imported target/artifact trees.
3. **Coverage-explicit** — distinguish eligible outputs from out-of-scope outputs.
4. **Exactness-honest** — distinguish direct precursor facts from conservative reconstruction or format-specific normalization.
5. **Format-neutral core** — CycloneDX, SPDX, VEX, or policy layers should sit on top of one stable internal graph.
6. **Artifact-aware** — preserve which precursor sidecar belongs to which promoted output.
7. **Supply-chain-layered** — stay distinct from publish identity, trusted publishing, and general sidecar attachment crates.

# MVP surface

- Minimal types: `SbomPrecursorCaptureLock`, `PrecursorIngestReport`, `CaptureRouteReceipt`, `ArtifactCoverageReport`, `CoverageCeilingReport`, `NormalizedBuildGraphReport`, `SbomTransformReport`, `VexStubReport`, `SbomDiffReport`, `EvidenceSourceReceipt`, `SbomWorkbenchBundle`
- Minimal functions:
  - `capture_precursor_bundle()`
  - `ingest_precursor_sidecars()`
  - `capture_route_receipt()`
  - `compute_artifact_coverage()`
  - `compute_coverage_ceiling()`
  - `normalize_build_graph()`
  - `transform_to_sbom()`
  - `diff_precursor_bundles()`
  - `write_workbench_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `cyclonedx`
  - `spdx`
  - `vex`
  - `markdown`

# Compatibility story

- Works first on nightly because Cargo SBOM precursor support remains unstable.
- Must record whether precursor files came from direct build capture, `CARGO_SBOM_PATH`, sidecar filename scan, or imported bundle.
- Should remain useful if Cargo stabilizes SBOM support, because normalization, diffing, and review artifacts still live above the raw precursor files.
- Must preserve the distinction between Cargo-native precursor facts and later policy / exploitability / provenance overlays.
- Should interoperate with general sidecar-contract crates rather than replacing them.

# Conformance & fixtures

- One fixture with a single binary and one precursor sidecar captured directly from the build.
- One fixture where an `rlib`-only output is honestly classified as out of precursor scope.
- One fixture where an imported `--artifact-dir` export cannot prove same-invocation precursor generation.
- One fixture where the same package appears multiple times because target/features/profile change the compilation shape.
- One fixture where artifact matching is ambiguous and the result must stay `manual_review_required`.
- One fixture where a release diff is caused by feature or target changes rather than component version churn.
- Goldens for `captured_directly`, `sidecar_scanned`, `normalized_with_loss`, `format_projection_changed`, and `manual_review_required`.

# Path to boring stability

- Stabilize the capture lock, ingest report, normalized graph, and diff report before growing policy DSLs.
- Start with CycloneDX and SPDX as thin output layers rather than making them the core model.
- Keep the first VEX story intentionally shallow: starter stubs and evidence linkage, not full vulnerability intelligence.
- Prefer exact provenance labels over pretending every field is equally trustworthy.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one Cargo SBOM precursor run, match precursor sidecars to built artifacts, normalize the build graph, emit one transform receipt plus one stable diff surface, and export a bundle another tool or reviewer can actually inspect.

# De-risk plan

1. Start with precursor capture + normalization + diff before adding policy gates.
2. Treat CycloneDX and SPDX emitters as adapters over one normalized graph.
3. Validate on one single-binary crate, one multi-target workspace, and one ambiguous-artifact case.
4. Refuse to silently guess when precursor-to-artifact matching is not exact.

# Non-goals

- Not a general supply-chain policy engine.
- Not a trusted-publishing or provenance attestation system.
- Not a replacement for a general sidecar attachment contract crate.
- Not a promise that one emitted SBOM format can losslessly express every Cargo precursor fact.

# Architecture & API sketch

```rust
pub struct SbomTransformReport {
    pub schema_version: String,
    pub output_format: String,
    pub exact_fields: Vec<String>,
    pub normalized_fields: Vec<String>,
    pub dropped_fields: Vec<String>,
}

pub fn capture_precursor_bundle(root: &Path) -> Result<SbomWorkbenchBundle>;
pub fn ingest_precursor_sidecars(bundle: &SbomWorkbenchBundle) -> Result<PrecursorIngestReport>;
pub fn normalize_build_graph(bundle: &SbomWorkbenchBundle) -> Result<NormalizedBuildGraphReport>;
pub fn transform_to_sbom(bundle: &SbomWorkbenchBundle, format: &str) -> Result<SbomTransformReport>;
pub fn diff_precursor_bundles(old: &SbomWorkbenchBundle, new: &SbomWorkbenchBundle) -> SbomDiffReport;
```

Bundle draft: `sbom-precursor.capture-lock.json`, `capture-route.receipt.json`, `precursor-ingest.report.json`, `artifact-coverage.report.json`, `coverage-ceiling.report.json`, `normalized-build-graph.report.json`, `sbom-transform.report.json`, `vex-stub.report.json`, `sbom-diff.report.json`, `evidence-source.receipt.json`, `sbom-workbench-bundle.manifest.json`, `notes.md`.

# Security / safety model

- Treat precursor files, manifests, and imported build directories as untrusted input.
- Support redaction of local filesystem paths, private registry URLs, and unpublished package identities.
- Never silently upgrade conservative reconstruction into “exact Cargo evidence”.
- Keep the evidence-source receipt mandatory so downstream consumers can make conservative trust decisions.

# Maintenance & governance plan

- Track Cargo SBOM RFC / tracking-issue movement and precursor schema changes closely.
- Keep the normalized graph and diff vocabulary compact and versioned.
- Maintain fixtures for ambiguous artifact association, duplicate compiled crates, feature/target drift, and transform loss surfaces.
- Publish guidance for how this workbench composes with sidecar attachment crates, provenance crates, and publish-surface review tools.

# Milestones

## 0.1
- precursor capture lock
- ingest report
- normalized graph report

## 0.2
- CycloneDX / SPDX transform receipts
- precursor diffing
- VEX starter stubs

## 1.0
- stable bundle schema
- curated precursor fixture corpus
- adapters for policy and release-review workflows

# Open questions

- What is the smallest normalized graph that still preserves the hard Cargo-specific facts people need later?
- Which precursor-to-format losses should always force `manual_review_required`?
- How much artifact matching ambiguity can be tolerated before the crate must refuse to emit a “ship-grade” bundle?

# Sources

- Rust in 2026: Cargo SBOM precursor stabilization and secure-supply-chain flagship: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo unstable SBOM feature and precursor schema: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo external tools / `compiler-artifact` messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo changelog (`-Z sbom` package ID clarification): https://doc.rust-lang.org/cargo/CHANGELOG.html
- RFC 3553 pull request: https://github.com/rust-lang/rfcs/pull/3553
