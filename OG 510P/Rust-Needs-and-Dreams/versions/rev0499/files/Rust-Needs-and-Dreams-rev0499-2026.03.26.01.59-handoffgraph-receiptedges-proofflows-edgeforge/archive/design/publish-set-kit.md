# Design: Publish Set Kit (`cargo publish-set`, source-package publication truth, checks, and receipts)

## Goal
Turn Rust source-package publication from a mix of workspace defaults, tarball inspection, CI logs, and registry polling into a **portable publish boundary**.

Read this together with:
- [`design/publish-set-lane-map.md`](./publish-set-lane-map.md)
- [`design/publish-set-pilot-program.md`](./publish-set-pilot-program.md)
- [`proposals/epic-publish-set-kit.md`](../proposals/epic-publish-set-kit.md)

This kit should make six things explicit:
1. **what publish subject was selected**,
2. **what each packaged `.crate` payload actually contained**,
3. **which checks and waivers applied**,
4. **which registry and authority path were used**,
5. **what upload / index receipts exist**,
6. **what downstream consumers may import without redefining the publish event**.

The worthy contribution here is **not** another release bot, version-bump helper, registry dashboard, or trusted-publishing badge.
It is the thin producer-side boundary above Cargo packaging and registry upload that multiple higher layers already need.

## Why now
Fresh upstream signals all point the same way:
- Cargo’s unstable-feature docs now say multi-package publishing was stabilized in Rust 1.90.0, and later note that the `pubtime` index field is stabilized in Rust 1.94.0.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo publish` documents workspace-aware default-members selection, `--workspace`, `--exclude`, registry selection, `--dry-run`, `--no-verify`, authentication expectations, upload behavior, and waiting for index appearance. Cargo’s changelog also says `cargo publish` now blocks until it sees the published package in the index and later fixed `wait-for-publish` for sparse registries.
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo package` now documents workspace-aware packaging, registry-aware lockfile assumptions for inter-dependent crates, and an unstable machine-readable `--message-format json` for `--list`. The package docs also spell out generated-versus-copied file provenance, `.cargo_vcs_info.json`, and the distinction between packaged manifest normalization and authored source state.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo manifest and workspace docs make `publish`, `include`, and `exclude` explicit publish-facing controls, including workspace inheritance for `publish`, `include`, `exclude`, and `version`.
  https://doc.rust-lang.org/cargo/reference/manifest.html
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- The 2025H2 cargo-semver-checks goal explicitly aims at integrating SemVer compliance into the `cargo publish` workflow.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- crates.io’s January 2026 update added GitLab Trusted Publishing, Trusted-Publishing-only mode, blocked risky GitHub triggers, and `pubtime` in the index. The registry-index docs further specify that `pubtime` is the original publish time and should not change on later status changes such as `yanked`.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://doc.rust-lang.org/cargo/reference/registry-index.html
- `cargo package` embeds `.cargo_vcs_info.json` as a best-effort VCS snapshot while explicitly warning that provenance is not verified. That is exactly the pattern where a reusable receipt model is more valuable than log scraping.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html

Taken together, that means the next missing ecosystem contribution is not “make publishing easier.”
It is “make source-package publication **portable, reviewable, and handoff-ready**.”

## Core artifact family

### 1. `publish-brief/v0`
A concise summary for humans and assistants:
- publish subject label
- workspace/package count
- selected registry or registries
- check summary
- receipt status summary
- instability/lossiness markers

### 2. `publish-subject/v0`
Identity for the exact publication subject:
- workspace / package selection
- package order or grouping when multi-package publication is involved
- package versions
- manifest-path / cwd / default-members posture
- registry target(s)
- authority path intent (`token`, `credential-provider`, `trusted-publishing`, `unknown-imported`)
- comparison base or previous published version pointers when available

### 3. `package-file-report/v0`
One package payload with explicit file truth:
- package id
- packaged manifest identity
- packaged file listing
- generated versus copied file origins
- manifest normalization notes (`Cargo.toml.orig`, generated `Cargo.toml`, lockfile posture)
- include/exclude/import notes
- optional best-effort VCS hints with explicit non-verified status
- size / count summary

### 4. `publish-check-report/v0`
The check boundary before or during upload:
- packaging verify result
- metadata warnings / missing-human-metadata posture
- semver-check posture
- policy or org rule imports
- explicit waivers / skips / `--no-verify` posture
- inconclusive states and reasons

Design rule: **passing package verification is not the same thing as passing semver or policy checks, and neither is the same thing as registry acceptance**.

### 5. `publish-receipt/v0`
Producer-side receipt for what happened at upload time:
- upload target registry
- authority path actually used if known
- accepted / rejected / uploaded-but-index-pending status
- upload timestamp or imported CI timestamp when available
- index-visibility result or timeout state
- `pubtime` / version-seen observations when available
- error codes / partial outcomes / retry hints

### 6. `publish-pack/v0`
Portable bundle containing:
- `publish-brief/v0`
- `publish-subject/v0`
- one or more `package-file-report/v0`
- one or more `publish-check-report/v0`
- optional `publish-receipt/v0`
- raw attachments (package file-list NDJSON, CI logs, trusted-publishing metadata, registry responses)
- bounded downstream handoffs

### 7. `publish-diff/v0`
Diffable review artifact for comparing publish attempts:
- subject drift
- package set / order drift
- payload/file drift
- check/waiver drift
- authority/registry drift
- receipt/index drift

### 8. `publish-handoff/v0`
Lossy summaries for downstream consumers such as:
- Release Truth
- Library Productization
- Publisher & Source Identity
- Package Admission
- Support / incident intake

## Reference UX
A reference implementation could expose:
- `cargo publish-set plan` — emit `publish-subject/v0`
- `cargo publish-set inspect` — collect `package-file-report/v0`
- `cargo publish-set check` — emit `publish-check-report/v0`
- `cargo publish-set receipt` — capture upload / index receipts
- `cargo publish-set diff --against <ref|path>` — compare publish attempts without flattening them into whole-release claims
- `cargo publish-set pack` — bundle `publish-pack/v0`

## Theory of change
The key design move is to separate:
- **selected publish subject**,
- **package payload truth**,
- **check / waiver truth**,
- **authority and registry-path truth**,
- **upload / index receipt truth**,
- **later registry/index observation such as `pubtime`**,
- and **downstream handoff**.

That separation matters because today’s Rust tooling often collapses these into one fake story:
- a workspace tag becomes “what was published,”
- a manifest diff becomes “the tarball payload,”
- a successful `cargo publish --dry-run` becomes “accepted by the registry,”
- a Trusted Publishing workflow becomes “the whole trust story,”
- or a release page becomes “the publish receipt.”

If those truths stay flattened together, downstream tools will keep duplicating partial publish-state models and incompatible registry adapters.

## Shared stack role
This kit is a lower-level anchor between the archive’s **Manifest Truth / Publisher & Source Identity / Release Truth** corridor.
It should be treated as:
- a **Manifest Truth** import for packaged payload and normalized manifest facts,
- a **Publisher & Source Identity** consumer for authority/source posture,
- a **Release Truth** input when a release includes registry publication,
- and a reusable anchor for Library Productization, Package Admission handoff, and support archaeology.

## Adjacent kits and boundaries
- **Manifest Truth Stack** owns authored-manifest truth, packaged-manifest diffs, discovery/context, and consumer-import lossiness.
- **Publisher & Source Identity Stack** owns project-family claims, authority/source posture, and trust/policy imports.
- **Release Pipeline Kit** owns broader release subjects including binaries, installers, signatures, provenance, and SBOM attachments.
- **Package Admission Stack** owns publish-time graph/exposure/trust/policy review from the intake side.
- **Distribution Contract Stack** owns consumer-side channel/mirror/fallback/install receipts.
- **Public API Kit** owns semver/public-contract meaning; Publish Set Kit only records whether semver checks were required, skipped, or attached.

## Early pilots
1. **single-package crates.io lane**
   - prove package payload, verify results, and upload/index receipt capture without workspace complexity.
2. **workspace publish-set lane**
   - prove selected package order/grouping and registry-aware packaging for inter-dependent crates.
3. **alternative-registry / auth-required lane**
   - prove registry/index/credential-provider posture can be captured without collapsing into token folklore.
4. **trusted-publishing lane**
   - prove authority-path facts and blocked/allowed issuer posture can be imported without becoming the whole publish story.
5. **semver-check / waiver lane**
   - prove publish-time semver, verify, metadata, and policy checks can attach as their own check families rather than being flattened into one release status bit.
6. **receipt / `pubtime` lane**
   - prove upload acceptance, index visibility, and later original-publish-time observation can coexist without rewriting the original event.
7. **release / package-admission handoff lane**
   - prove Release Truth and Package Admission can import bounded publish facts instead of reconstructing them from CI and registry pages.

## Success criteria
- Tools can answer “what source packages were actually published, under what checks, and with what receipt?” without log archaeology.
- Multi-package and single-package publication share one vocabulary for subject, payload, checks, and receipts.
- Authority-path and registry/index facts remain explicit instead of hidden in CI-specific adapters.
- Release and library consumers can import source-publication facts without swallowing them into broader release/install stories.

## Failure modes to avoid
- A fake universal “publish success” score.
- Treating authored manifest state and packaged tarball state as the same lane.
- Treating CI authority posture as a full trust verdict.
- Treating registry acceptance as the same thing as release completion.
- Swallowing binary artifacts, installer manifests, or install receipts into the kit.
