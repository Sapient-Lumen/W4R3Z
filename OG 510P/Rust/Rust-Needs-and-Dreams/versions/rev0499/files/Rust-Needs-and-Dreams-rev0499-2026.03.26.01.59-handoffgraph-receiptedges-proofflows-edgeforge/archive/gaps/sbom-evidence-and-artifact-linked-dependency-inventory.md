# Gap: SBOM evidence + artifact-linked dependency inventory

Rust now has real momentum around **SBOM generation**, but the ecosystem still lacks a shared, reviewable way to answer the harder practical questions:
- what Rust components were actually part of this build?
- which ones ended up in which shipped artifact?
- which edges were runtime versus build/proc-macro only?
- what was gathered directly from Cargo versus inferred later from metadata or recovered from a binary?
- what was lost or approximated when projecting that information into CycloneDX, SPDX, or other downstream formats?

Today, teams can produce pieces of this story with Cargo’s SBOM precursor, `cargo-cyclonedx`, `cargo-auditable`, container scanners, or custom scripts. What is still missing is a **portable evidence boundary** that keeps those layers honest instead of flattening them into one exported BOM file.

The next correction is therefore not “more SBOM tooling” in the abstract.
It is an explicit lane map that keeps **Cargo-native precursor capture, source-project standards export, embedded binary recovery, release-attached standards documents, scanner/import views, and downstream consumer conclusions** distinct.


## Why this matters now
- Rust’s official 2026 goals include **stabilizing Cargo SBOM precursor** support, and the 2026 flagship supply-chain theme explicitly names **SBOM generation** alongside public/private dependencies and breaking-change detection.
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s unstable `sbom` docs say precursor files are emitted **alongside compiled artifacts**, include dependencies / target / features / compiler identity, and may include the same crate multiple times when it is compiled differently.
  - https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo also exposes `CARGO_SBOM_PATH`, which is a strong signal that build-time producers and post-processors are expected to compose rather than live in one monolith.
  - https://doc.rust-lang.org/cargo/reference/unstable.html
- The new Cargo tracking issue says the remaining work includes demonstrating **end-to-end SBOM generation in an industry-standard format using this data source**, while also explicitly saying that **non-Rust dependencies are out of scope** for the feature itself.
  - https://github.com/rust-lang/cargo/issues/16565
- RFC 3553 says Cargo should emit a **Cargo-specific** SBOM file next to artifacts and let external tools transform it into standards like **SPDX** or **CycloneDX**. That is unusually clear evidence that the right long-term shape is “Rust-native precursor plus explicit format projection,” not pretending one format exporter is the source of truth.
  - https://github.com/rust-lang/rfcs/pull/3553
- The CycloneDX Cargo plugin documents that it uses Cargo data sources today, and its own issue tracker says `cargo metadata` can misreport some build-only dependencies as runtime dependencies under resolver v2. That is direct evidence that inventory-source identity and approximation markers must be first-class.
  - https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/main/README.md
  - https://github.com/CycloneDX/cyclonedx-rust-cargo/issues/760
- Cargo’s long-standing metadata issue says feature resolution can be reported at the workspace level rather than the actual root build being performed. That is further evidence that build-truth and metadata-truth cannot be naively equated.
  - https://github.com/rust-lang/cargo/issues/7754
- `cargo-auditable` shows a second crucial seam: shipped binaries can carry a compact, reproducible-build-friendly dependency list that downstream tools can recover and convert into CycloneDX, but the project also explicitly says SBOMs do **not** by themselves prevent supply-chain attacks or explain the impact of a malicious library that removes itself from the BOM.
  - https://github.com/rust-secure-code/cargo-auditable

## The missing layer
The ecosystem still lacks a standard answer to:
- **Subject identity:** workspace/package/artifact/binary/container-image inventory are related but not identical subjects
- **Capture provenance:** Cargo precursor, `cargo metadata`, embedded auditable section, scanner recovery, and manual/native additions should remain distinguishable
- **Scope truth:** runtime, build, proc-macro, dev, target-specific, and host-only edges need explicit modeling
- **Artifact linkage:** a dependency graph for “the workspace” is not yet a statement about which shipped artifacts actually contain which components
- **Format projection:** Cargo-native facts, CycloneDX documents, SPDX documents, and binary-recovered inventories should cross-reference each other with explicit lossiness markers
- **Diffability:** PRs and releases need inventory changes expressed as structured diffs, not giant machine-generated XML blobs
- **Policy inputs:** downstream trust / policy / incident / release tooling needs a stable attachment point instead of re-scraping ad hoc exporter output

## Why this is more than compliance paperwork
A good solution would help with:
- supply-chain review that distinguishes build-time from shipped/runtime exposure
- release engineering that can attach inventory evidence without choosing one irreversible format too early
- incident response that can answer “was this component only in the build lane, embedded in the shipped binary, or both?”
- distro and enterprise packaging workflows that need diffable dependency evidence
- registry/search/trust tooling that needs normalized inventory inputs without turning them into fake trust scores

## What “done” looks like
A Rust team shipping a library, CLI, service, or containerized app should be able to produce one portable pack that answers:
1. what subject was inventoried?
2. which capture lanes contributed facts, and which were inferred versus directly observed?
3. what components and relationships were present, with explicit runtime/build/proc-macro/host-target scope?
4. which artifacts or binaries actually carried which components?
5. what CycloneDX/SPDX or other exports were derived from that pack, and what fidelity/lossiness notes apply?
6. what changed since the previous release or baseline?

See: `design/sbom-evidence-kit.md` and `proposals/epic-sbom-evidence-kit.md`.
