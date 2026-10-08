## Execution addendum (rev0455)
Use `design/release-truth-execution-blueprint-2026Q1.md` as the canonical answer to “what should this stack-level pilot actually be proving?” before reading the ranked rollout below.

Interpretation rule:
- the pilots still stand;
- this revision clarifies that they are proving one **producer-side release-truth layer** rather than a generic release-automation story;
- and each pilot should keep source publication, artifact continuity, signature/attestation, rebuild/inventory, and downstream handoff truths visibly separate.

# Design: Release Truth pilot program (`release-truth-pack/v0`)

## Why this needs a stack-level pilot program
The archive already has a release-pipeline pilot, but the stack now needs a slightly higher execution plan that proves **producer-side continuity** across package publication, artifact publication, signatures, rebuild evidence, and downstream handoffs.

Current signals make that worthwhile:
- Cargo publishing is permanent and package-oriented.
  https://doc.rust-lang.org/cargo/reference/publishing.html
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- crates.io Trusted Publishing has become materially stronger and more policyable.
  https://blog.rust-lang.org/2025/07/11/crates-io-development-update-2025-07/
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust’s 2026 flagships keep public/private dependencies and SBOM support on the supply-chain path.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The ecosystem already has real release ingredients (`release-plz`, `cargo-dist`, `cargo-binstall` signing), but still lacks one portable producer-side truth boundary.
  https://github.com/release-plz/release-plz
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://github.com/cargo-bins/cargo-binstall/blob/main/SIGNING.md

That combination argues for a thin, ranked pilot program rather than another umbrella release tool.

## Stack boundaries
This pilot treats the following archive pieces as one execution band:
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md)
- [`design/repro-build-kit.md`](./repro-build-kit.md)
- [`design/inventory-evidence-stack.md`](./inventory-evidence-stack.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)

Design rule: **the pilot is about producer-side continuity first**. Inventory and distribution are critical imports, but they should attach later so the stack does not immediately bloat into a universal supply-chain platform.

## Ranked pilots

### Pilot 1 — Crate-only publish continuity lane
**Who this is for:** ordinary library maintainers publishing source packages.

**Why first:**
- It proves the minimal, durable boundary: package publish facts, release subject identity, attached evidence, and offline reconstruction.
- It avoids binary-installer complexity while still exercising the core release pack.

**Required artifacts**
- `release-pack/v0`
- optional `api-pack/v0`, `policy-pack/v0`, `sbom-evidence-pack/v0`
- `release-truth-brief/v0`

**Acceptance bar**
- A reviewer can answer “what exactly was published, from which commit/issuer, with which attached evidence?” without scraping a host page.

### Pilot 2 — Source + binary coherence lane
**Who this is for:** CLI or app projects that publish a crate and downloadable artifacts.

**Why second:**
- This is where Rust’s release fragmentation becomes operationally obvious.
- It proves one release subject can bind `.crate` publication, tag/commit identity, and binary artifact inventories together.

**Required additions**
- imported binary-artifact manifest (for example `dist-manifest.json`)
- target/archive/checksum inventory
- `release-truth-pack/v0`

**Acceptance bar**
- The stack can show that published source and released binaries are part of one coherent producer-side release rather than parallel workflows.

### Pilot 3 — Signed-binary attachment lane
**Who this is for:** teams that require policyable verification of downloadable binaries.

**Why third:**
- Signature support already exists in the ecosystem; the missing work is durable attachment and review semantics.
- This is the smallest lane that proves signed-install truth can attach without becoming the whole release story.

**Required additions**
- `binpack/v0`
- `binverify-report/v0`
- issuer / key-rotation notes
- explicit release-policy attachment rules

**Acceptance bar**
- A downstream verifier can tell whether verification failure came from missing metadata, unknown issuer, bad signature, or artifact drift.

### Pilot 4 — Independent rebuild attachment lane
**Who this is for:** high-assurance publishers, distro packagers, and skeptical consumers.

**Why fourth:**
- This is where the stack proves it will not flatten signatures/provenance into reproducibility theater.
- It also sharpens what “release evidence” really means.

**Required additions**
- `repro-pack/v0`
- strong/weak rebuild mode labels
- release-truth diff output that keeps rebuild verdict separate from signature / provenance status

**Acceptance bar**
- Reviewers can distinguish a signed release from a reproducibly rebuilt release, and can see why a rebuild was inconclusive or divergent.

### Pilot 5 — Inventory and distribution handoff lane
**Who this is for:** supply-chain, packaging, offline, and incident-response consumers.

**Why fifth:**
- This is strategically important, but only after the producer boundary is coherent.
- It proves the stack can hand off without pretending it owns the full install/runtime world.

**Required additions**
- attached SBOM / inventory evidence pack pointers
- `release-truth-handoff/v0` for distribution/policy/incident consumers
- explicit “producer truth stops here” markers

**Acceptance bar**
- Downstream consumers can import the producer boundary without re-scraping CI or silently treating publication as installation.

## Shared pilot rules
- **Start from the package boundary.** The `.crate` and associated package metadata remain part of the release subject, not incidental prelude.
- **Keep binary verification attachable.** Signed-binary truth stays separate from release identity and policy.
- **Keep rebuild evidence attachable.** Reproducibility stays a distinct verdict with explicit incompleteness markers.
- **Delay distribution complexity.** Do not front-load mirrors, fallback logic, package managers, or installed-state receipts.
- **Prefer importers over rewrites.** Use existing machine-readable outputs whenever possible.
- **Preserve offline reconstruction.** A good pilot should survive after CI logs and host pages disappear.

## Immediate archive decision
Treat [`design/release-truth-stack.md`](./release-truth-stack.md) and [`proposals/epic-release-truth-stack.md`](../proposals/epic-release-truth-stack.md) as the new synthesis/proposal anchors.
Use [`design/release-pipeline-pilot-program.md`](./release-pipeline-pilot-program.md) as the leaf-level release execution plan, and use this file as the stack-level sequence that proves producer-side continuity before widening to inventory/distribution consumers.
