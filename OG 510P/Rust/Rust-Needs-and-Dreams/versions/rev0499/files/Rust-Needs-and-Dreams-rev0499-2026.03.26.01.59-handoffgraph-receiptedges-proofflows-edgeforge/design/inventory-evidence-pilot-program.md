# Design: Inventory Evidence pilot program

## Why this needs a pilot program
The archive already has a strong **SBOM Evidence Kit**, plus explicit package-admission, release-truth, and distribution-contract layers.
What it still lacks is a ranked rollout for **inventory continuity** across those layers.

Current Rust/Cargo signals point to a staged pilot instead of one all-at-once platform:
- Cargo's unstable SBOM support emits precursor files next to compiled artifacts and exposes them through `CARGO_SBOM_PATH`, which is enough to prove a capture lane but not yet enough to settle every consumer workflow.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Rust's 2026 flagships make SBOM generation a current ecosystem milestone rather than a side quest.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The tracking issue still calls for demonstrating end-to-end generation of an industry-standard SBOM from Cargo's precursor, which means projection/export is still a live seam.
  https://github.com/rust-lang/cargo/issues/16565
- `cargo package` and `cargo install` already prove that package and install truth can differ meaningfully, especially around lockfile use and normalized manifests.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- `cargo-auditable` proves binary recovery is practical but explicitly warns that inventory is not a supply-chain verdict. That makes careful staging more important, not less.
  https://github.com/rust-secure-code/cargo-auditable

That combination argues for a **ranked pilot program**: prove durable inventory continuity in narrow, high-value lanes before widening to every consumer.

### Lane-map reminder (rev0341)
This pilot program now assumes the lower-layer SBOM family is split by [`design/sbom-evidence-lane-map.md`](./sbom-evidence-lane-map.md): Cargo-native precursor capture, source-project standards export, embedded binary recovery, release attachments, scanner/import views, and downstream consumer handoffs must stay visibly distinct even when one pack links them.

## Failure modes this pilot must prevent
The pilot program should explicitly prevent five kinds of inventory theater:
1. **export theater** — one CycloneDX or SPDX file treated as the whole truth.
2. **graph theater** — package/workspace dependency graphs silently sold as shipped-artifact facts.
3. **artifact theater** — binary recovery treated as if it explains package publication or install-path choices by itself.
4. **install theater** — a successful install treated as if it proves which package/release inventory was selected.
5. **policy theater** — trust, vulnerability, or compliance conclusions made without preserving inventory provenance and lossiness.

## Ranked pilots

### Pilot 1 — Cargo precursor capture lane
**Who this is for:** maintainers building ordinary libraries and CLIs with Cargo.

**Why first:**
- This is the narrowest lane that still validates the archive's core inventory-subject and capture-provenance ideas.
- It aligns directly with upstream Cargo work instead of inventing a rival source of truth.

**Required evidence**
- `inventory-subject/v0`
- `inventory-capture-report/v0`
- `inventory-graph/v0`
- explicit scope markers for runtime / build / proc-macro / dev / host-target where available

**Acceptance bar**
- A maintainer can answer “what did Cargo directly observe here, and what remains inferred or unsupported?” from one portable pack.

### Pilot 2 — Industry-format projection lane
**Who this is for:** teams that need CycloneDX or SPDX output without losing Rust-native detail.

**Why second:**
- The upstream tracking issue explicitly says end-to-end generation of an industry-standard SBOM is still part of the remaining work.
- Projection is useful immediately, but only after the source layer is stable enough to explain lossiness honestly.

**Required additions**
- `inventory-projection-report/v0`
- explicit exporter identity/version
- lossiness markers for scope collapse, duplicate-compile collapse, native omission, or artifact-link absence

**Acceptance bar**
- A reviewer can explain what a projected CycloneDX/SPDX document preserved, collapsed, or guessed without reverse-engineering exporter internals.

### Pilot 3 — Binary-recovery / artifact-link cross-check lane
**Who this is for:** CLI, service, and distro workflows where the shipped artifact matters more than the workspace graph alone.

**Why third:**
- This is the first lane where build-time capture and artifact-time recovery can corroborate or challenge each other.
- It proves the archive can describe mismatches instead of hiding them.

**Required additions**
- `artifact-inventory-report/v0`
- explicit binary-recovery lane via `cargo-auditable` or comparable adapters
- mismatch classes: build-only, runtime-only, unresolved, recovered-only, missing-artifact-link

**Acceptance bar**
- A maintainer or distro packager can answer “what did we build, what did we recover from the binary, and where do they disagree?” from one review bundle.

### Pilot 4 — Package-to-release attachment lane
**Who this is for:** projects where crate publication and binary release are both first-class events.

**Why fourth:**
- The stack must prove it composes with release truth without pretending to replace it.
- This is where package admission, release manifests, signatures, and inventory evidence first need clean attachment points.

**Required additions**
- explicit package subject ↔ release subject linkage
- inventory attachment conventions inside release packs
- visible statements about what inventory does **not** prove (signatures, rebuild equivalence, install-path choice)

**Acceptance bar**
- A release process can attach inventory evidence that stays clearly distinct from signatures, provenance, and rebuild verdicts.

### Pilot 5 — Distribution / install receipt lane
**Who this is for:** consumer-side installation, mirrors, internal tool catalogs, and downstream support / incident workflows.

**Why fifth:**
- This is where many ecosystems overclaim. Rust can do better by widening only after package/release inventory handoffs are already legible.
- It validates the difference between what was published, what was shipped, and what a consumer actually installed.

**Required additions**
- install-receipt imports into inventory continuity views
- channel / mirror / fallback markers
- packaged-lockfile-used versus recomputed-resolution markers where applicable
- thin downstream summaries with explicit lossiness

**Acceptance bar**
- A downstream consumer can answer “which inventory subject did this install actually come from, by what path, and with what divergence from package or release intent?” without inventing new semantics.

## Shared design rules across pilots
- **Observed, inferred, and recovered facts stay separate.**
- **Package / release / install subjects do not collapse into one lifecycle blob.**
- **Exporter convenience never outranks provenance honesty.**
- **Mismatches are first-class outputs, not embarrassing edge cases.**
- **Policy, trust, and incident workflows remain consumers of inventory continuity, not substitutes for it.**

## Immediate archive decision
Treat [`design/inventory-evidence-stack.md`](./inventory-evidence-stack.md) as the synthesis layer, [`proposals/epic-inventory-evidence-stack.md`](../proposals/epic-inventory-evidence-stack.md) as the stack-level product direction, and this file as the rollout order.

The next credible move is **not** another exporter shootout, registry badge, or scanner wrapper.
It is a thin `cargo inventory-evidence` / `inventory-evidence-pack/v0` layer that proves Rust inventory facts can survive the full path from package admission through release attachment to consumer installation without semantic collapse.
