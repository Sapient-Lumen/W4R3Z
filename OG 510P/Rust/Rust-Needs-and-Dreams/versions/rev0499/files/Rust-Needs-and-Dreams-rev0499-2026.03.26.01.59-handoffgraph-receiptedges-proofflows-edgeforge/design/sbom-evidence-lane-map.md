# Design: SBOM Evidence lane map (Cargo precursor, project export, embedded binary recovery, release attachments, and scanner imports)

## Goal
Sharpen **SBOM Evidence Kit** so the archive stops treating “Rust SBOM support” as one bucket.
The live ecosystem already spans materially different inventory lanes, and they differ in **which subject is being described**, **how facts are captured**, **whether evidence is observed during build or recovered later**, **whether a standards document is canonical or projected**, **what artifact linkage is actually proven**, and **what downstream trust/policy/support tooling may honestly conclude**.

The archive should therefore keep SBOM review grounded in a lane map instead of one flattened “we generated an SBOM” story.

## Signals from the current ecosystem
- Rust’s 2026 flagship supply-chain theme explicitly names **SBOM generation**, and the goal slate separately names **stabilize SBOM support**. That makes this an active upstream seam rather than a side quest.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable `sbom` docs say `-Z sbom` generates **SBOM pre-cursor files alongside each compiled artifact**, exposes them through `CARGO_SBOM_PATH`, and preserves duplicate crate entries when the same crate is compiled differently. That is direct evidence that Cargo is defining a build-lane precursor, not a complete standards document.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-cyclonedx` says it creates a CycloneDX SBOM for a Cargo project by calling into Cargo, and its README explicitly warns that invoking it on untrusted projects has the same arbitrary-code risk as Cargo itself. That is a distinct project-export lane, not just a file-format view of the precursor.
  https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/main/README.md
- The CycloneDX plugin’s resolver-v2 issue says `cargo metadata` can misreport some build-only dependencies as runtime dependencies and explicitly says this would be fixed with a better Cargo-emitted SBOM data source. That is direct evidence that metadata/lockfile export and Cargo-native build truth must stay separate.
  https://github.com/CycloneDX/cyclonedx-rust-cargo/issues/760
- `cargo-auditable` says the end goal is for Cargo itself to encode dependency information in binaries, already supports a nightly mode that uses Cargo’s native SBOM precursor for more accurate recording, and lists real downstream consumers like cargo-audit, Trivy, Grype, Syft, wasm-tools, and auditable-to-CycloneDX converters. That is a real binary-recovery lane, not merely another exporter.
  https://github.com/rust-secure-code/cargo-auditable
- Trivy’s Rust docs keep source scanning and binary scanning separate: `Cargo.lock` plus `Cargo.toml` improve source-tree results and remove dev dependencies, while binary scanning only applies to artifacts built with `cargo-auditable`.
  https://trivy.dev/docs/latest/coverage/language/rust/
- cargo-dist’s changelog keeps two different producer-side lanes explicit: `cargo-auditable` embeds dependency data directly into binaries, while `cargo-cyclonedx` emits a standalone `bom.xml` that is distributed with the software. That difference matters to release packs and downstream consumers.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md

## The lanes

### 1) Cargo-native precursor lane (`.cargo-sbom.json` next to compiled artifacts)
This is the upstream build-lane inventory source that Cargo itself is growing.

What defines it:
- per-artifact precursor files emitted during build
- Rust-specific dependency kind, feature, target, and compiler context
- duplicate crate entries when compile posture differs
- explicit out-of-scope posture for non-Rust/native completeness

Why it deserves its own lane:
- Cargo explicitly calls it a precursor rather than a finished standards document
- it is the closest thing to build-observed Rust inventory truth in-tree today
- later exporters and recoverers should explain themselves against this lane, not silently replace it

Design rule:
- keep Cargo-native precursor truth separate from every projected/exported/recovered lane layered above it

### 2) Source-project export lane (`cargo-cyclonedx`, metadata/lockfile-driven standards output)
This is the lane where a project directory is examined and directly exported into a standard like CycloneDX.

What defines it:
- project/workspace subject rather than a specific built artifact
- exporter-owned format mapping and normalization
- possible use of Cargo data sources that are weaker than build-observed precursor data
- output optimized for standards consumption, not Rust-specific review first

Why it deserves its own lane:
- it is useful immediately and widely deployed
- it is not automatically per-artifact truth
- known resolver-v2 / build-vs-runtime misclassification pressure means approximation must stay visible

Design rule:
- keep project-export standards documents separate from Cargo-native precursor truth and separate from shipped-artifact claims

### 3) Embedded binary recovery lane (`cargo-auditable`, wasm metadata, binary-to-CycloneDX adapters)
This is the lane where inventory is carried inside the produced artifact and recovered later.

What defines it:
- artifact/binary subject rather than workspace/project subject
- recovered-from-binary posture
- possible dependence on a wrapper or special build mode
- downstream adapters that may translate recovered data into JSON or CycloneDX

Why it deserves its own lane:
- it answers “what does this binary say about itself?” rather than “what did this source tree resolve?”
- it can corroborate or challenge build-time/project-time claims
- it is strategically important for distro, fleet, and container scanning workflows

Design rule:
- keep embedded/recovered artifact truth separate from source-project export truth and separate from package/release/install continuity claims

### 4) Release-attached standards lane (standalone `bom.xml`, release-pack attachments, container SBOM attestations)
This is the producer-side lane where a standards document is shipped or attached alongside released artifacts or images.

What defines it:
- release/bundle/container attachment subject
- standalone standards document or attestation rather than embedded binary data
- producer-chosen packaging and hosting behavior
- artifact family or image attachment posture that may span multiple files

Why it deserves its own lane:
- cargo-dist explicitly distinguishes standalone CycloneDX files from embedded auditable binary metadata
- container/image attachment workflows have different distribution and verification behavior
- this lane is central to release engineering, but it is not automatically the same as build-lane precursor truth

Design rule:
- keep release-attached documents separate from both binary-embedded recovery and source-project export truth

### 5) Scanner/import lane (Trivy, Grype, Syft, osv-scanner, converter pipelines)
This is the lane where a consumer-side tool scans source trees, binaries, images, or attached documents and emits its own recovered or normalized view.

What defines it:
- scanner-owned subject discovery
- source-tree versus binary versus image mode differences
- importer/converter identity and version affecting the result
- possible collapse of Rust-specific distinctions into a broader scanner data model

Why it deserves its own lane:
- the same scanner family may produce meaningfully different truth depending on whether it sees `Cargo.lock`, `Cargo.toml`, a cargo-auditable binary, or an attached CycloneDX document
- scanner success is not proof of Cargo-native completeness
- this lane is where many downstream consumers first meet the evidence

Design rule:
- keep scanner/import truth separate from producer-side capture truth and separate from downstream policy or trust verdicts

### 6) Downstream consumer lane (policy, admission, incident, distro, support)
This is the lane where inventory evidence is used rather than generated.

What defines it:
- imported evidence from one or more earlier lanes
- explicit decision or analysis goals (policy, advisories, incident triage, distro packaging, support)
- bounded conclusions conditioned on available evidence and known lossiness

Why it deserves its own lane:
- the archive already has separate Trust, Policy, Package Admission, Release Truth, Incident, and Distribution layers
- these consumers should import inventory evidence, not redefine the inventory subject
- this lane is where overclaim risk is highest if the earlier lanes are blurred together

Design rule:
- keep downstream verdicts separate from inventory capture itself, even when the same pack carries both

## Lane transitions the archive must keep explicit
1. **Cargo-native precursor ↔ source-project export**
   - a standards document exported from a project is not automatically the same truth as a per-artifact Cargo precursor.
2. **source-project export ↔ embedded binary recovery**
   - a workspace/project graph is not the same subject as a produced binary or wasm module.
3. **embedded binary recovery ↔ release attachment**
   - metadata embedded in a binary is not the same thing as a standalone BOM shipped beside a release or attached to an image.
4. **release attachment ↔ scanner import**
   - a scanner’s normalized output is not the same truth as the attached document it consumed.
5. **scanner import ↔ downstream verdict**
   - vulnerability, trust, policy, or support conclusions must not silently replace the imported evidence.
6. **Cargo precursor ↔ package/release/install continuity**
   - a build-lane precursor alone does not prove what was published, what was shipped, or what a consumer actually installed.

## What should change elsewhere in the archive
- **SBOM Evidence Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Inventory Evidence Stack** should keep composing SBOM evidence with Package Admission, Release Truth, and Distribution Contract instead of letting one lane quietly become the whole lifecycle story.
- **Package Admission Stack** should import inventory evidence for publish-time review, but should not redefine capture-lane or artifact-link semantics.
- **Release Truth Stack** should carry attached BOMs, auditable recovery reports, or precursor-derived attachments without silently replacing inventory truth with provenance/signature/rebuild truth.
- **Distribution Contract Stack**, **Policy Kit**, **Trust Signals**, **Incident Kit**, and support/productization layers should import bounded inventory summaries rather than narrating a hidden universal inventory model of their own.

## Worthy contribution, sharpened
The worthy contribution here is **not** another SBOM exporter wrapper, registry badge, scanner one-liner, or universal supply-chain score.
It is a thin `cargo inventory` / `inventory-pack/v0` layer whose lane reports, artifact-link reports, projection-lossiness records, recovery imports, and bounded consumer handoffs make Rust inventory claims reviewable across build, release, scanner, and downstream consumer workflows without semantic collapse.
