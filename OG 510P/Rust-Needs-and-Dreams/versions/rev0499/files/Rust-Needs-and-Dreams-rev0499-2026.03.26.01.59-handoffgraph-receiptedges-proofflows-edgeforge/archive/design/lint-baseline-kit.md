# Design: Lint Baseline Kit (`cargo lintpack`, `lint-pack/v0`)

## Goal
Define a portable lint policy/baseline/report/fix contract for Rust so rustc, Clippy, rustdoc, Cargo-side warning families, and adjacent tools can exchange versioned artifacts instead of forcing every organization to reinvent lint governance from scratch.

This should **not** replace rustc lints, Clippy, rustdoc lints, `cargo fix`, or `rustfix`. It should make them easier to combine coherently.

## References (signals)
- Rust’s 2026 flagships explicitly include establishing a place for safety-critical lints in Clippy.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo manifests now support `[lints]`, and workspaces support `[workspace.lints]`, making selected lint posture a reviewable stable input.
  https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo is experimenting with `[lints.cargo]`, which means Cargo-native warning families are entering the same configuration plane.
  https://doc.rust-lang.org/cargo/reference/unstable.html#lintscargo
- `cargo report` already exposes a first-class report family for future incompatibilities.
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- Clippy already publishes many grouped lint families with different intended usage styles.
  https://rust-lang.github.io/rust-clippy/stable/index.html
- rustc has its own lint listings and lint levels.
  https://doc.rust-lang.org/rustc/lints/listing/index.html
  https://doc.rust-lang.org/rustc/lints/levels.html
- rustdoc has its own lint listings.
  https://doc.rust-lang.org/rustdoc/lints.html
- rustc already emits structured JSON diagnostics suitable for machine processing.
  https://doc.rust-lang.org/rustc/json.html
- `cargo fix` and `rustfix` prove there is real value in machine-applicable lint/code-fix flows, but the Edition Guide and Cargo 1.90 development report show that selective/config-aware fixing is still operationally awkward.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  https://docs.rs/rustfix

## Core components

### 1) `lint-profile/v0`
A human-reviewed declaration of what lint policy is intended:
- engine namespaces (`rustc`, `clippy`, `rustdoc`, optional `cargo`, optional third-party adapters)
- manifest/workspace source of truth and inheritance posture
- explicit lint ids and group references
- expanded group digest / lock information
- severity policy (`allow`, `warn`, `deny`, `forbid` or organization-specific classes)
- target/package/path/edition applicability
- rationale notes for unusual settings
- optional policy tags like `safety_critical`, `style`, `performance`, `docs`, `api_hygiene`

Design rule: the profile must capture **expanded meaning**, not just terse command-line flags or one inherited manifest table.

### 2) `lint-baseline/v0`
A machine-readable snapshot of accepted existing findings:
- finding fingerprints
- originating engine/tool version
- profile digest / expansion lock digest
- scope and suppression reason
- expiration/review metadata
- package/path target selectors

Design rule: a baseline is debt bookkeeping, not silent suppression.

### 3) `lint-report/v0`
The actual findings artifact:
- tool identity + version
- profile digest + baseline digest
- normalized finding ids (`engine::lint_name`)
- severity, spans, rendered message, optional machine-applicable suggestions
- classification (`new`, `baseline`, `resolved`, `changed`, `imported`)
- optional grouped summaries by policy tag or package
- optional import notes for Cargo-side warning/report families

This is the explainable CI/report artifact.

### 4) `lint-fixpack/v0`
A portable fix-suggestion bundle:
- suggested edits grouped by finding
- machine-applicability grade
- preconditions / edition / target assumptions
- conflicts/overlaps with other suggestions
- whether generated from rustc, Clippy, Cargo-side imports, or another adapter

Design rule: fix packs should be reviewable attachments, not implicit auto-apply promises.

### 5) `lint-pack/v0`
Bundle format containing:
- `lint-profile/v0`
- optional `lint-baseline/v0`
- `lint-report/v0`
- optional `lint-fixpack/v0`
- optional raw JSON diagnostic / report attachments
- verification summary

This is the attachable unit for CI, code review, release evidence, migration review, or safety audits.

### 6) `cargo lintpack`
Reference UX:
- `cargo lintpack profile`
- `cargo lintpack baseline`
- `cargo lintpack check`
- `cargo lintpack diff`
- `cargo lintpack fixpack`
- `cargo lintpack pack`

`cargo lintpack` should start as an adapter/normalizer/packer. It does not need to replace `cargo clippy`, `cargo report`, or `cargo fix`.

## Default policy
- **Profiles first, flags second.**
- **Manifest/workspace origin must stay visible.**
- **Baselines are explicit debt, not invisible allowances.**
- **Group expansion should be locked** so policy does not drift silently when lint groups change.
- **Reports must distinguish new findings from accepted debt.**
- **Cargo-side imports must stay visibly imported.**
- **Fix suggestions are attachments, not obligations.**

## What the kit should provide to others
- **Application teams:** one stable lint governance workflow instead of ad-hoc CI scripts.
- **Safety-heavy users:** curated subsets and traceable lint evidence.
- **Tool authors:** a normal form for findings and suggested fixes.
- **Release / policy / migration tooling:** attachable lint evidence packs rather than brittle console logs.
- **Large monorepos:** per-package or per-path rollout with explicit baselines and inherited profile truth.

## Overlap boundaries
- **Not Compile Guidance Kit:** that kit owns maintainer-authored lint/diagnostic catalogs and examples; Lint Baseline Kit owns selected policy, observed findings, and debt/fix artifacts.
- **Not Edit Workflow Kit:** that kit owns selection/application/verification of edits; Lint Baseline Kit owns suggested fixes as evidence.
- **Not Safety Evidence Kit:** that kit reasons about broader evidence and assurance; Lint Baseline Kit supplies one evidence family.
- **Not Cargo Report Kit:** Cargo’s report families remain distinct imported lanes.
- **Not MIR Analysis Kit:** MIR-aware analyzers can emit lint-like findings, but this kit is about lint policy/baseline/report normalization.
- **Not Public API Kit:** semver/MSRV/public-dependency evidence stays there.
- **Not Spec Conformance Kit:** linting policy is not language/toolchain conformance, though conformance or safety profiles may use lint packs as one input.

## Hard problems (explicitly scoped)
1. **Group drift**
   - Clippy groups evolve. v0 must record expanded meaning, not only group names.
2. **Inheritance visibility**
   - workspace/package lint origin and overrides must remain legible.
3. **Fingerprint stability**
   - baselines need stable-enough fingerprints across compiler versions without pretending perfect invariance.
4. **Third-party lint diversity**
   - v0 should allow adapters but not require every tool to fit perfectly on day one.
5. **Fix conflicts and partial applicability**
   - fix packs must preserve uncertainty and overlap rather than flattening into one giant patch.
6. **Policy abuse**
   - make it harder to hide new debt behind vague baselines and easier to review why a baseline exists.
7. **Cargo import confusion**
   - future incompatibility and Cargo-native lint/report families must be importable without pretending they are identical to rustc/Clippy findings.

## Minimal adoption path
1. Publish schemas + validators.
2. Ship a thin `cargo lintpack` that can ingest rustc/Clippy JSON and emit `lint-report/v0`.
3. Add manifest/workspace profile-lock export and baseline support.
4. Add diff mode and Cargo-side import notes.
5. Add `rustfix`-derived `lint-fixpack/v0` attachments.
6. Expand adapters and organization-level profile presets.

## Why this is worth doing
Rust already has excellent lint engines. The missing opportunity is to turn them into durable, reviewable governance artifacts.
A good Lint Baseline Kit would let teams move from “we run some lints” to “we know exactly what policy we enforce, what debt we carry, what changed, what fixes are reviewable, and what downstream consumers may conclude.”
