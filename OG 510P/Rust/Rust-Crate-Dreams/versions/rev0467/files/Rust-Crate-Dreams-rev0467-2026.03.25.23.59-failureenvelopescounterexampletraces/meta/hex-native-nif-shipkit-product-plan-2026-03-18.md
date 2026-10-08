# Hex Native NIF ShipKit — product plan (2026-03-18)

This note sharpens **P-0502 Hex Native NIF ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- what Hex tarball they actually built,
- whether the mandatory checksum file truly shipped inside that tarball,
- what precompiled NIF artifacts exist and which NIF-version window they claim,
- what exact fallback triggers force a local build,
- how the BEAM is expected to load the NIF,
- and whether important gaps are honest unsupported boundaries or merely hidden package/release drift.

It should **not** try to become a replacement for Hex, Mix, `rustler`, `rustler_precompiled`, or GitHub Releases.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For package maintainers, release engineers, downstream BEAM consumers, and support reviewers, the crate should provide:

1. **One compact support contract** instead of release truth spread across `mix.exs`, checksum files, GitHub release assets, CI YAML, and changelog folklore.
2. **A checksum-residency report** that states whether the mandatory checksum file is actually in the package and aligned with the observed assets.
3. **A NIF-version-window report** that joins Rustler feature choice, NIF ABI surface, and OTP support claims.
4. **A fallback-trigger report** that states when precompiled delivery works, when local build is forced, and what that build requires.
5. **A conservative downstream summary** explaining what package they are actually consuming, which targets are boring, and what still requires manual review.
6. **A diffable release bundle** another person can inspect without recreating the full Mix/Hex/GitHub release pipeline.

## Three first-class review objects

### 1. Checksum residency
This should stay separate from “a checksum file exists somewhere in the repo.”

Named classes for `0.1`:
- `checksum_residency_ok`
- `checksum_file_missing_from_tarball`
- `checksum_asset_mismatch`
- `manual_review_required`

This object should answer:
- whether `checksum-*.exs` exists,
- whether it is included in the Hex tarball,
- whether it refers to the produced remote artifacts,
- and whether users can install without hitting a checksum/runtime trap.

### 2. NIF-version window
This should answer questions like:
- what minimum NIF version the package was built for,
- which OTP families that version really covers,
- whether newer features require a narrower window,
- and whether README/package claims outrun the actual configured ABI floor.

### 3. Fallback trigger
This should stop the product from treating “source build exists” as enough.
It should say explicitly:
- when target detection will find a precompiled asset,
- when unsupported targets or prerelease versions force a local build,
- whether Rust toolchain / compiler expectations are documented,
- and whether that fallback path is honest or accidental.

## Recommended `0.1` command surface

### `cargo hex-nif-ship inspect`
Read project facts from `Cargo.toml`, `mix.exs`, checksum files, package file lists, produced tarballs, and optional release-asset indexes.
Emit early observations without pretending the release is valid yet.

### `cargo hex-nif-ship check`
Run policy checks for:
- missing checksum files,
- checksum files absent from the package,
- artifact-name drift,
- NIF-version / OTP-window overclaims,
- unsupported-target local-build fallbacks,
- loader-name/path mismatches,
- and manual-review warnings.

### `cargo hex-nif-ship diff <old> <new>`
Compare release bundles and classify:
- `checksum_residency_changed`
- `nif_version_window_changed`
- `fallback_trigger_changed`
- `loader_route_changed`
- `manual_review_boundary_changed`

### `cargo hex-nif-ship bundle`
Produce one compact `.hexnifbundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `hex_nif_ship_model`
  - shared types for policies, receipts, reports, and diffs
- `hex_nif_ship_import`
  - tarball inspection, package metadata parsing, checksum parsing, release-asset import
- `hex_nif_ship_check`
  - policy checking and conservative classification
- `hex_nif_ship_render`
  - markdown summaries and zip bundle export
- `cargo-hex-nif-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `hex_nif_ship_rustler_precompiled`
- `hex_nif_ship_release_assets`
- `hex_nif_ship_mix`

## `0.1` artifact set

Core artifacts should be:
- `hex-nif-shipkit.toml`
- `hex-package.receipt.json`
- `nif-precompiled.matrix.json`
- `beam-loader.receipt.json`
- `support-risk.report.json`
- `notes.md`

This pass says `0.1` also needs three sharper review artifacts:
- `checksum-residency.report.json`
- `nif-version-window.report.json`
- `fallback-trigger.report.json`

Those matter because the shipkit gets vague again if it only records “a Hex package exists” without making clear:
- whether the checksum file truly shipped,
- what ABI window was actually promised,
- and when a user is pushed into local compilation.

## Discovery order

1. **Artifact inspection**
   - Hex tarball contents
   - package file list
   - checksum file inventory
   - release asset inventory
   - NIF file names and target tuples
2. **Checksum-residency receipt**
   - checksum file present or absent
   - tarball inclusion
   - checksum/asset alignment
3. **NIF-version-window receipt**
   - Rustler feature flags / module config
   - minimum NIF version
   - implied OTP support floor
   - claim drift
4. **Fallback-trigger receipt**
   - target covered or uncovered
   - force-build behavior
   - local-build prerequisites
   - honesty of support statement
5. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “Hex publish succeeded” as the verdict.
A good `0.1` should keep separate:
- `package_exists`
- `checksum_residency_ok`
- `nif_window_honest`
- `fallback_contract_honest`
- `loader_route_boring`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- Hex package publishing/build docs
- `hex_core` tarball + outer-checksum vocabulary
- `rustler_precompiled` checksum and build-matrix guidance
- `rustler` NIF-version feature/config behavior
- Erlang `erlang:load_nif/2` and fallback semantics
- OTP caveats around NIF behavior
- real package changelogs showing target drift, checksum-file omissions, and fallback fixes

### Do not flatten into one fake verdict
- “the package published”
- “the checksum file exists in git”
- “a release asset exists”
- “the BEAM loaded a NIF once locally”
- “source build is possible in theory”

## Preferred proving grounds

- a Rust-backed Hex package shipping Linux/macOS/Windows precompiled NIFs with a clean checksum file
- a package whose checksum file is generated in CI but omitted from the Hex tarball
- a package whose declared OTP support exceeds the configured minimum NIF version window
- a package that forces local builds on uncovered targets without documenting that contract

## Non-goals

- not another Rust↔Elixir binding generator
- not a full Hex publisher or release bot
- not a runtime execution harness for BEAM responsiveness
- not a generic NIF correctness or performance analyzer
- not a promise that checksum presence implies supply-chain sufficiency

## MVP API sketch

```rust
pub enum ChecksumResidencyClass {
    ChecksumResidencyOk,
    ChecksumFileMissingFromTarball,
    ChecksumAssetMismatch,
    ManualReviewRequired,
}

pub fn inspect_release(root: &Path) -> Result<ReleaseInspection>;
pub fn evaluate_checksum_residency(release: &ReleaseInspection) -> Result<ChecksumResidencyReport>;
pub fn evaluate_nif_version_window(release: &ReleaseInspection) -> Result<NifVersionWindowReport>;
pub fn evaluate_fallback_trigger(release: &ReleaseInspection) -> Result<FallbackTriggerReport>;
pub fn write_bundle(bundle: &HexNifBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow Hex tarball/checksum guidance closely.
- Follow `rustler` / `rustler_precompiled` changes closely.
- Follow OTP/NIF version changes closely.
- Preserve `manual review required` whenever the crate cannot safely infer support truth.
