# Crate Off-Ramp Pack Kit — product plan (2026-03-19)

This note sharpens **P-0515 Crate Off-Ramp Pack Kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a registry policy engine, a security scanner, or a universal migration assistant.
It should be a **small crate family plus CLI** that helps crate maintainers publish one reviewable answer to:

- what exactly is being sunset,
- what successor class or stopgap applies,
- which exit recipes were actually checked,
- and where downstream users still need manual review.

The missing value is the **boring exit-contract layer** above today’s deprecation, yank, advisory, outdated-version, and docs substrate.

## What the crate should provide other people

For maintainers, downstream adopters, security teams, and tooling authors, the crate should provide:

1. **One successor map** instead of scattered docs notes, warning strings, and issue links.
2. **One stopgap-horizon receipt** instead of improvised “pin this for now” folklore.
3. **One checked exit-recipe manifest** instead of unverified migration prose.
4. **One sunset diff workflow** that explains what changed between releases.
5. **One compact off-ramp bundle** that can travel between maintainers, security reviewers, and downstream teams.

## Three first-class review objects

### 1. Successor map report

Named classes for `0.1` should focus on successor intent such as:

- `compatible_shim`
- `drop_in_successor`
- `partial_replacement`
- `fork_successor`
- `security_only_last_safe_version`
- `no_successor`
- `manual_review_required`

This object should answer:

- whether the off-ramp applies to a whole crate, feature lane, API lane, or version range,
- what successor target is being recommended,
- whether the successor is direct, partial, stopgap-only, or absent,
- and which lanes remain manual.

### 2. Stopgap-horizon receipt

Named classes for `0.1` should focus on sunset basis and temporary lanes such as:

- `deprecated_signal_imported`
- `advisory_signal_imported`
- `yank_signal_imported`
- `shim_window_declared`
- `last_safe_version_declared`
- `migrate_now_required`
- `sunset_deadline_unknown`

This object should answer:

- which deprecation/advisory/yank facts shaped the off-ramp,
- whether a compatibility shim or last-safe pin exists,
- when a temporary lane is supposed to expire,
- and where the crate still lacks a date, version, or policy boundary.

### 3. Exit recipe manifest

Named classes for `0.1` should focus on recipe truth such as:

- `manifest_dependency_rename_checked`
- `import_path_rewrite_checked`
- `feature_mapping_checked`
- `adapter_required`
- `behavior_review_required`
- `recipe_not_witnessed`

This object should answer:

- what the smallest before/after migration recipe looks like,
- which feature/target/runtime combinations were actually exercised,
- whether an adapter or behavior review is required,
- and whether the “recipe” is really only prose.

## Recommended `0.1` command surface

### `cargo off-ramp capture`
Capture maintainer-authored and imported sunset facts and emit:
- `successor-map.report.json`
- `deprecation-surface.receipt.json`

### `cargo off-ramp check`
Run selected migration fixtures and emit:
- `offramp-recipe.manifest.json`
- `successor-compat.report.json`
- `sunset-check.report.json`

### `cargo off-ramp diff`
Compare two off-ramp bundles and emit:
- `offramp-diff.report.json`

### `cargo off-ramp summary`
Render a compact human review note from the structured artifacts.

### `cargo off-ramp bundle`
Produce one compact `.offrampbundle.zip` containing reports, notes, and selected fixture outputs.

## Recommended crate/workspace split

- `offramp_model`
- `offramp_import_cargo`
- `offramp_import_rustsec`
- `offramp_import_docs`
- `offramp_recipe_check`
- `offramp_diff`
- `cargo-offramp-kit`

## `0.1` artifact set

Core artifacts should be:
- `offramp-pack.toml`
- `successor-map.report.json`
- `deprecation-surface.receipt.json`
- `offramp-recipe.manifest.json`
- `successor-compat.report.json`
- `sunset-check.report.json`
- `offramp-diff.report.json`
- `sunset-notes.summary.md`

## Discovery order

1. **Import sunset signals**
   - deprecations
   - yank state
   - advisory references
   - docs links
2. **Normalize successor intent**
   - whole-crate vs lane-specific
   - successor class
   - stopgap vs long-term successor
3. **Check recipes**
   - manifest rename
   - import rewrite
   - feature mapping
   - adapter/manual-review flags
4. **Verify horizon**
   - shim windows
   - last-safe versions
   - unresolved deadlines
5. **Bundle export**
   - reports
   - notes
   - manual-review zones

## Ranking discipline

A good `0.1` should not treat “a deprecation exists” as the verdict.
It should keep separate:

- `sunset_signal_known`
- `successor_intent_known`
- `stopgap_horizon_known`
- `recipe_witness_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- rustc deprecation signals and docs
- Cargo SemVer guidance around deprecations
- Cargo yank and update behavior
- crates.io Security tab / RustSec references
- ad hoc docs.rs rename notes and redirect crates
- outdated/advisory tooling where it helps surface the current state

### Do not flatten into one fake verdict
- “the crate is deprecated”
- “the version is yanked”
- “there is a RustSec advisory”
- “a redirect crate exists”
- “the migration note mentions a replacement”

## Preferred proving grounds

- a renamed crate that preserves a compatibility shim
- a security-driven off-ramp where a last-safe pin exists but is not the long-term answer
- a one-to-many successor split where only part of the old surface is directly covered
- a retired crate where the honest answer is manual containment or redesign

## Non-goals

- not another advisory scanner
- not a registry ownership-transfer workflow
- not a generic maintenance-scoring dashboard
- not a universal code-rewrite engine

## MVP API sketch

```rust
pub fn capture_successor_map(input: &OffRampInput) -> Result<SuccessorMapReport>;
pub fn capture_stopgap_horizon(input: &OffRampInput) -> Result<DeprecationSurfaceReceipt>;
pub fn validate_exit_recipes(input: &RecipeInput) -> Result<OffRampRecipeManifest>;
pub fn check_successor_compat(input: &RecipeInput) -> Result<SuccessorCompatReport>;
pub fn diff_offramp_bundles(old: &OffRampBundle, new: &OffRampBundle) -> Result<OffRampDiffReport>;
pub fn write_bundle(bundle: &OffRampBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Track registry/security-signal changes through importer modules rather than a monolithic parser.
- Preserve `no_successor` and `manual_review_required` as honest outputs.
- Keep recipe checking small and fixture-driven.
- Compose with pathfinder, upgrade-pack, and crate-health work rather than blur into them.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-yank.html
- https://doc.rust-lang.org/cargo/commands/cargo-update.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/cargo-audit/latest/cargo_audit/
- https://docs.rs/cargo-deny/latest/cargo_deny/
- https://docs.rs/crate/cargo-outdated/latest/source/
- https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- https://docs.rs/crate/sello-crypto/latest
