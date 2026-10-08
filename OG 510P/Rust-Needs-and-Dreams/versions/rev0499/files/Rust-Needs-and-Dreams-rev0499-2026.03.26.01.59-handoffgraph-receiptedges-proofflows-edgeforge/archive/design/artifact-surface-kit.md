## Execution addendum (rev0443)
For questions about **what this kit should actually become in a real contribution rather than only as a promoted seam**, read `design/cargo-artifact-contract-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- this file remains the concrete kit beneath the blueprint;
- the sharper answer is now **reference layer + report/pack command + acceptance corpus**;
- and future edits should preserve selected subject, evidence path, final artifact identity, origin/staging, sidecar attachment, and bounded consumer handoff as separate review lanes.

## Refresh note (rev0398)
This file is now the archive's promoted **build-system/plumbing-shaping** seam.
Read it as the concrete kit beneath `design/cargo-artifact-contract-2026Q1.md`, not as an isolated final-output curiosity.

Why the promotion happened now:
- Cargo's official plumbing roadmap explicitly enumerates build phases and leaves **stage final artifacts** as a real phase boundary;
- the 2025 GSoC plumbing prototype reached `plan-build` but not final-artifact staging;
- Cargo's build-dir-layout work is flushing out tools that still depend on unspecified path structure;
- and Cargo now has richer artifact-adjacent semantics (`--artifact-dir`, custom final-artifact uplift discussion, SBOM precursors) than the ecosystem has a shared handoff boundary for.

Interpretation rule:
- keep **build subject truth**, **evidence-path/plumbing truth**, **final artifact identity**, **origin/staging truth**, **sidecar truth**, and **downstream handoff truth** visibly separate;
- do not flatten JSON messages, target-dir copies, package listings, uplifted outputs, and release-manifest conclusions into one fake artifact story.

# Design: Artifact Surface Kit (`cargo artifacts`, final output identity, location, and handoff)

## Goal
Turn Cargo’s final-output story from a mixture of JSON streams, layout assumptions, and release-tool folklore into a **portable artifact surface**.

This kit should make six things explicit:
1. **what build subject was selected**,
2. **which final outputs belong to it**,
3. **where those outputs originated and where Cargo exposed them**,
4. **which outputs are Cargo-native versus Cargo-mediated uplift/imports**,
5. **which sidecars attach at the artifact layer**,
6. **what downstream consumers may import without redefining the build.**

The worthy contribution here is **not** another target-dir scraper, release manifest clone, or universal packaging wrapper.
It is the thin Cargo-facing boundary above final outputs that multiple higher layers already need.

## Why now
Fresh upstream signals all point the same way:
- The March 2026 build-dir-layout-v2 testing call says many projects still rely on unspecified build-dir details because the right Cargo features are missing.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s build-cache docs now publicly distinguish **final artifacts** in `target-dir` from **intermediate artifacts** in `build-dir`.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo’s compiler-layout docs now say `artifact-dir` is part of Cargo’s public API, while `build-dir` remains internal.
  https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/layout/index.html
- Cargo’s unstable `--artifact-dir` docs say exact final filenames are otherwise hard to determine and generally require parsing JSON output.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93’s custom-final-artifacts discussion sketches explicit Cargo-mediated uplift, collision checks, and selected-package rules instead of direct build-script writes to `artifact-dir`.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo’s external-tools surface still gives third-party tools stable package metadata and message-format JSON, but not a first-class final-artifact subject/handoff pack.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo’s unstable SBOM precursor support now emits precursor files next to executable/linkable outputs and carries them into target/artifact-dir uplift paths, proving that artifact-linked sidecars are now a real upstream concept.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-dist` now keeps a machine-readable release manifest for downstream build/distribution work. That proves demand for artifact-level machine contracts, but it remains a downstream release layer rather than a Cargo-native final-output contract.
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://docs.rs/crate/cargo-dist/latest

Taken together, that means the next missing ecosystem contribution is not “show me files in `target/`.”
It is “make Cargo final outputs **portable, reviewable, and handoff-ready**.”

## Core artifact family

### 1. `artifact-brief/v0`
A concise summary for humans and assistants:
- subject label
- command/build lane
- selected package/target count
- artifact-class summary
- instability/lossiness markers
- review freshness

### 2. `artifact-subject/v0`
Identity for the exact build subject being discussed:
- workspace / package selection
- command class (`build`, `test`, `bench`, `doc`, `package`, custom tool lane)
- target triple(s)
- profile
- feature selection
- host/target posture
- toolchain identity
- configured `target-dir`, `build-dir`, and `artifact-dir` posture if known
- comparison base or invocation/session reference when available

### 3. `artifact-entry/v0`
A single final output, with identity and origin separated from path trivia:
- entry id
- package id and producing Cargo target
- target kind / crate type / doc/package class
- origin class:
  - `CARGO_NATIVE`
  - `RUSTDOC_OUTPUT`
  - `PACKAGE_OUTPUT`
  - `BUILD_SCRIPT_UPLIFT`
- freshness (`FRESH`, `REBUILT`, `UNKNOWN`)
- primary produced path(s)
- copied / uplifted / mirrored path(s)
- executable/linkable/doc/package classification
- selected sidecar references
- explicit unknowns or lossy inference notes

### 4. `artifact-manifest/v0`
The portable final-artifact collection:
- one `artifact-subject/v0`
- zero or more `artifact-entry/v0`
- public-layout facts (`target-dir`, `artifact-dir`, doc/package subtrees if relevant)
- selection rules and omissions
- sidecar attachment table
- collision / overwrite / shadowing notes
- export timestamps and integrity metadata

### 5. `artifact-report/v0`
Explain what a consumer should worry about:
- missing expected outputs
- path drift
- selected-package drift
- target/profile drift
- uplift/import collisions
- sidecar presence/absence drift
- nightly-only / unstable dependency notes
- downstream handoff hints

### 6. `artifact-pack/v0`
Attachable bundle linking:
- `artifact-brief/v0`
- `artifact-manifest/v0`
- `artifact-report/v0`
- raw Cargo JSON or normalized extracts when needed
- optional sidecar files or pointers
- bounded consumer handoff documents

### 7. `artifact-handoff/v0`
Lossy but explicit summaries for downstream consumers such as:
- Release Truth
- Inventory / SBOM workflows
- Reproducibility verification
- Support / incident intake
- Host-package / native-edge / firmware / client-product consumers

## Reference UX
A reference implementation could expose:
- `cargo artifacts collect` — emit `artifact-manifest/v0`
- `cargo artifacts report` — explain path/origin/selection/sidecar status
- `cargo artifacts diff --against <ref|path>` — compare final-output sets without flattening them into release/install claims
- `cargo artifacts handoff --to <consumer>` — emit bounded downstream summaries
- `cargo artifacts pack` — bundle `artifact-pack/v0`

## Theory of change
The key design move is to separate:
- **selected build subject**,
- **final output identity**,
- **origin class**,
- **location/copy behavior**,
- **sidecar attachment**,
- and **downstream handoff**.

That separation matters because today’s Rust tooling often collapses these into one fake story:
- a file found under `target/` becomes “the release artifact,”
- an uplifted file becomes “a Cargo output,”
- an SBOM precursor becomes “the artifact identity,”
- a `dist-manifest` becomes “the build truth,”
- or an install receipt becomes “what Cargo produced.”

If those truths stay flattened together, downstream tools will keep duplicating partial scanners and incompatible artifact models.

## Shared stack role
This kit is a lower-level anchor inside the archive’s **Tooling Contract / Release Truth corridor**.
It should be treated as:
- a **Tooling Contract** import for final-output identity and handoff,
- a **Release Truth** input when shipped artifacts come from Cargo-managed outputs,
- a **bounded sidecar link point** for Inventory/Repro/Support consumers,
- and a reusable anchor for Host Package, Native Edge, Firmware, Client App, and CLI productization lanes.

## Adjacent kits and boundaries
- **Build Cache Kit** owns intermediate-state topology, locks, reuse, and retention.
- **Build Extension Kit** owns authored/generated-output declaration and Cargo-mediated uplift requests.
- **Build Interop Kit** owns workspace/config/plan/event contracts.
- **Inventory Evidence Stack** owns dependency/component meaning, export, and lossiness semantics.
- **Release Truth Stack** owns source-package/release-bundle/signature/rebuild continuity.
- **Distribution Contract Stack** owns channel selection, verification/fallback, and install receipts.
- **Repro Build Kit** owns independent rebuild verdicts over final artifacts, not artifact enumeration itself.

## Early pilots
1. **Cargo-native binary/library lane**
   - prove package/target/profile/toolchain truth and final-output enumeration without target-dir scraping.
2. **doc + package lane**
   - prove `cargo doc` and `cargo package` outputs can be modeled without flattening them into release truth.
3. **build-script uplift lane**
   - prove Cargo-mediated custom-final-artifact uplift can attach honest origin/collision notes.
4. **SBOM-sidecar lane**
   - prove precursor sidecars attach to artifact entries without becoming the artifact story.
5. **downstream handoff lane**
   - prove Release/Inventory/Repro/Support consumers can import bounded summaries instead of reconstructing the build.

## Success criteria
- Tools can answer “what final artifacts did Cargo actually produce?” without target-dir spelunking.
- The ecosystem gains one artifact vocabulary that release/support/repro/inventory tools can reuse.
- Nightly/stable, public/internal, and native/uplifted distinctions remain explicit instead of getting papered over.
- New Cargo features like artifact uplift or sidecars can attach to an existing artifact surface rather than forcing each downstream tool to rediscover them.

## Failure modes to avoid
- A fake universal artifact score.
- Treating final artifacts and intermediate build state as the same lane.
- Treating release bundles or install receipts as if Cargo itself produced them.
- Swallowing every non-Cargo output into the kit.
- Pretending `artifact-dir` alone solves selection, identity, and handoff.
