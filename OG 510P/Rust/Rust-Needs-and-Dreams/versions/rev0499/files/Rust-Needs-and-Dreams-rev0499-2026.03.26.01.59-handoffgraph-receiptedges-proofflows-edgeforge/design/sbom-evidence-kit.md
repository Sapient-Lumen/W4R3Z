# Design: SBOM Evidence Kit (`cargo inventory`, `inventory-pack/v0`)

## Goal
Make Rust dependency inventory **reviewable, portable, and composable** by defining:
- a reference CLI (`cargo inventory`),
- a normalized subject schema (`inventory-subject/v0`),
- a capture/provenance report (`inventory-capture-report/v0`),
- a component/relationship graph (`inventory-graph/v0`),
- an artifact-link report (`artifact-inventory-report/v0`),
- a format-projection report (`inventory-projection-report/v0`),
- a diff surface (`inventory-diff-report/v0`),
- and a portable bundle (`inventory-pack/v0`).

This is not “yet another SBOM exporter”.
The point is to create a **Rust-native evidence boundary** that can feed CycloneDX, SPDX, trust/policy tools, release packs, incident analysis, and binary/container scanners without pretending those layers are the same thing.

## References (signals)
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo unstable `sbom` docs: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo `sbom` tracking issue: https://github.com/rust-lang/cargo/issues/16565
- RFC 3553 / cargo-sbom: https://github.com/rust-lang/rfcs/pull/3553
- CycloneDX Cargo plugin: https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/main/README.md
- CycloneDX issue on resolver-v2 / build-vs-runtime misclassification risk: https://github.com/CycloneDX/cyclonedx-rust-cargo/issues/760
- Cargo metadata feature-resolution bug: https://github.com/rust-lang/cargo/issues/7754
- `cargo-auditable`: https://github.com/rust-secure-code/cargo-auditable

## Lane map
Read this kit together with [`design/sbom-evidence-lane-map.md`](./sbom-evidence-lane-map.md).
The archive should now keep six distinct lanes explicit:
1. Cargo-native precursor capture,
2. source-project standards export,
3. embedded binary recovery,
4. release-attached standards documents / attestations,
5. scanner/import views,
6. downstream consumer handoffs.

The kit owns the portable artifact family that records those lanes without flattening them into one universal SBOM story.

## Core UX: `cargo inventory`
- `cargo inventory capture`
  - capture Rust-native inventory evidence for a selected subject and emit `inventory-capture-report/v0`
- `cargo inventory export --format cargo|cyclonedx|spdx`
  - project captured evidence into a requested format and emit `inventory-projection-report/v0`
- `cargo inventory from-binary <path>`
  - recover embedded or scanner-observable inventory facts from a binary / wasm artifact and attach them as another capture lane
- `cargo inventory diff --against <ref|version|path>`
  - emit `inventory-diff-report/v0`
- `cargo inventory explain <component|edge|artifact>`
  - show how a fact was derived and from which capture lanes
- `cargo inventory pack`
  - produce `inventory-pack/v0`
- `cargo inventory verify-pack <path>`
  - verify schema versions, checksums, and attachment integrity

## Artifacts
### `inventory-subject/v0`
Describes what is being inventoried:
- workspace/package/member identity
- selected target(s), profile(s), features, cfgs, and toolchain
- subject class:
  - workspace build
  - package build
  - compiled artifact
  - shipped binary
  - container image / bundle attachment
- baseline or comparison identity when relevant

Design rule: **workspace inventory, artifact inventory, and binary-recovered inventory are related but not interchangeable.**

### `inventory-capture-report/v0`
Records how inventory facts were obtained.

Should capture:
- capture lane(s):
  - Cargo SBOM precursor
  - standards export from source/project tooling
  - Cargo metadata / lockfile approximation
  - embedded auditable section
  - standalone release attachment / image attestation
  - scanner recovery / import
  - manual/native dependency supplement
- tool / adapter versions
- directness level:
  - observed during build
  - recovered from artifact
  - inferred from metadata
  - manually asserted
- unsupported or lossy areas
- known caveats such as workspace-wide feature overapproximation or unresolved non-Rust/native components

Design rule: **capture provenance is part of the evidence, not hidden implementation detail. Keep Cargo-native precursor truth, project-export truth, embedded recovery, release attachments, and scanner-import truth visibly distinct.**

### `inventory-graph/v0`
A normalized component + relationship graph.

Should include:
- component identity:
  - package id / source / version
  - optional purl / SPDX identifiers / CycloneDX identifiers when available
- compilation posture where relevant:
  - target kind(s)
  - feature set
  - host vs target lane
  - duplicated crate instances compiled differently
- dependency edge classes:
  - runtime
  - build
  - proc-macro
  - dev
  - unknown / inferred
- optional annotations:
  - direct vs transitive
  - target-specific cfg guards
  - public-API exposure pointer when attached from Public API Kit

Design rule: **the graph should preserve Rust-specific scope and compilation facts before any export flattens them.**

### `artifact-inventory-report/v0`
Links component facts to shipped outputs.

Should capture:
- produced artifact identity (binary/library/wasm/archive/container attachment)
- which component set is claimed for that artifact
- whether the fact came from build-time precursor, embedded metadata, binary recovery, or scanner correlation
- mismatches / unresolved cases:
  - present in workspace graph but not proven in artifact
  - recovered from binary but absent from build capture
  - native / foreign dependency omitted

Design rule: **a workspace dependency graph is not automatically a shipped-artifact statement.**

### `inventory-projection-report/v0`
Describes exports into external formats.

Should capture:
- target format (`cargo-precursor`, `CycloneDX`, `SPDX`, others)
- exporter identity and version
- source reports used
- lossiness / approximation markers, for example:
  - build-vs-runtime collapse
  - duplicate-component merge
  - native dependency omission
  - missing artifact linkage
- produced document digests / paths

Design rule: **format exports are projections of the evidence, not the evidence source of truth.**

### `inventory-diff-report/v0`
Structured inventory change report.

Should include:
- added / removed / changed components
- changed scope or edge class
- changed artifact linkage
- changed capture-lane confidence / directness
- changed export-lossiness status

Design rule: **inventory review should not require diffing giant XML or JSON documents by hand.**

### `inventory-pack/v0`
Portable bundle containing:
- `inventory-subject.json`
- `inventory-capture-report.json`
- `inventory-graph.json`
- `artifact-inventory-report.json` (optional)
- `inventory-projection-report.json` (optional, one or more)
- `inventory-diff-report.json` (optional)
- attachment digests and provenance notes
- optional raw attachments:
  - Cargo SBOM precursor JSON
  - CycloneDX/SPDX exports
  - embedded-auditable extraction outputs
  - scanner summaries

## Design principles
- **Rust-native truth first, format projection second.** Cargo-specific build facts should remain explicit before exporting to general-purpose standards.
- **Capture lanes stay visible.** Observed, recovered, inferred, and manually asserted facts are not interchangeable.
- **Scope is first-class.** Runtime, build, proc-macro, dev, host, and target lanes need durable modeling.
- **Artifact linkage matters.** “In the workspace graph” and “in the shipped binary” are separate claims.
- **Diffability beats giant blobs.** Review and CI should consume small structured reports, not raw BOM documents alone.
- **Do not overclaim completeness.** Upstream Cargo explicitly scopes out non-Rust dependencies for the precursor; the kit must preserve that limitation honestly.


## Recommended execution posture
The archive should now treat this kit as the inventory-truth keystone inside the broader [`design/inventory-evidence-stack.md`](./inventory-evidence-stack.md).
The ranked rollout lives in [`design/inventory-evidence-pilot-program.md`](./inventory-evidence-pilot-program.md).

That means the next credible move is no longer “emit one exporter and stop”.
The better execution order is:
1. Cargo precursor capture lane
2. standards projection lane with explicit lossiness
3. binary-recovery / artifact-link cross-check lane
4. package-to-release attachment lane
5. distribution / install receipt lane

The point is to prove **inventory continuity** across package publication, released artifacts, and consumer installation without flattening Cargo-native precursors, source-project exports, embedded binary recovery, release attachments, scanner imports, and downstream consumer subjects into one fake SBOM truth.

## Stack boundary relative to Package Admission, Release Truth, and Distribution
- **Package Admission Stack** should import inventory evidence when deciding what package was admitted, but should not redefine the inventory subject model.
- **Release Truth Stack** should carry inventory attachments, but should not collapse inventory into signatures, provenance, or rebuild verdicts.
- **Distribution Contract Stack** should import release/package inventory lineage and selection receipts, but should not pretend install-path truth is the same as build-time capture.
- **Trust / Policy / Incident** consumers should treat this kit as imported evidence rather than as a verdict engine.

## Integration points
- **Release Pipeline Kit** for attached inventory evidence in releases
- **Trust Signals Kit** as one input source, not as a trust verdict by itself
- **Policy Kit** for license / advisory / org-policy evaluation over normalized inventory
- **Incident Kit** for exposure analysis and remediation planning
- **Repro Build Kit** for correlating rebuild subjects with inventory evidence without conflating reproducibility with inventory completeness
- **Public API Kit** for distinguishing public dependency exposure from mere dependency presence
- **Signed Binaries Kit** and provenance/attestation systems for artifact linkage

## Hard problems (explicitly scoped)
1. **Non-Rust/native dependencies**
   - upstream Cargo’s precursor does not aim to solve this by itself; v0 should allow supplements and explicit incompleteness rather than fake completeness.
2. **Metadata versus build truth**
   - `cargo metadata` approximations are useful but can misclassify scopes or features.
3. **Artifact linkage ambiguity**
   - not every graph node is necessarily present in every shipped artifact.
4. **Format mismatch**
   - CycloneDX, SPDX, binary-embedded metadata, and Cargo precursor facts do not line up perfectly.
5. **Container/image workflows**
   - Rust artifacts often become part of larger bundles where multiple inventory sources exist.
6. **Review noise**
   - large dependency graphs need filtered diff and explain views, not only raw exports.

## Overlap boundaries
- **Not Trust Signals Kit:** inventory says *what is present and how we know*; trust says *how to evaluate risk and credibility*.
- **Not Policy Kit:** policy decides pass/warn/fail; this kit supplies normalized inventory evidence.
- **Not Release Pipeline Kit:** release tooling carries and publishes packs; this kit defines the inventory evidence inside them.
- **Not Repro Build Kit:** inventory does not prove bit-for-bit equivalence.
- **Not Incident Kit:** incident workflows consume inventory plus advisories and mitigation steps.
- **Not one canonical SBOM format:** preserve multiple export lanes and lossiness notes instead of pretending one document is the whole truth.

## Evaluation plan
Pilot on three classes of projects:
1. a library crate exporting a CycloneDX document from Cargo precursor input
2. a CLI app built with `cargo-auditable`, with binary recovery cross-checks
3. a containerized Rust service where build-time Cargo inventory and image-level SBOM output must be related but not confused

Success bar:
- a maintainer can attach one `inventory-pack/v0` to a release or incident review
- downstream tools can distinguish observed versus inferred inventory facts
- build/runtime/proc-macro scope survives export and diff workflows
- reviewers can answer “what changed, for which artifact, and how certain are we?” without reverse-engineering exporter-specific output
