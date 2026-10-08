# Node-API Package & Prebuild Contract Kit — product plan (2026-03-18)

This note sharpens **P-0498 Node-API Package & Prebuild Contract Kit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which native tuples they actually shipped as prebuilds,
- which loader route downstream users will actually take,
- which Node-API floor and runtime-family claims the release is making,
- whether missing tuples are honest unsupported gaps or merely hidden behind local builds,
- and what publish identity / provenance posture the npm release really has.

It should **not** try to become a replacement for Node-API, `napi-rs`, npm, pnpm, yarn, or CI publishing tools.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For maintainers, release engineers, and reviewers, the crate should provide:

1. **One compact support contract** instead of compatibility folklore spread across CI YAML, `package.json`, JS loaders, and release notes.
2. **A prebuild-coverage report** that states which runtime/platform/arch/libc tuples were actually shipped natively.
3. **A loader-route receipt** that keeps `node-addons`, `default`, local-build, and WASM fallback paths visibly distinct.
4. **A publish-identity report** that records trusted-publisher posture, provenance generation, and manual/token publish facts without pretending those settle runtime support.
5. **A runtime-policy summary** that keeps Node-only support distinct from optional Bun or Deno aspirations.
6. **A diffable release bundle** another person can review without rerunning CI.
7. **A conservative downstream summary** for users explaining what installs as prebuilt native code, what still requires local toolchains, and what is only a universal fallback path.

## Three first-class review objects

### 1. Prebuild coverage
This should stay separate from “CI passed somewhere.”

Named classes for `0.1`:
- `fully_prebuilt`
- `partial_prebuild_matrix`
- `native_gap_hidden_by_local_build`
- `wasm_only_fallback_for_named_tuple`
- `manual_review_required`

### 2. Loader route
This should answer questions like:
- does the package use the `node-addons` path explicitly?
- is there a `default` fallback branch and what does it load?
- does the package try local native builds after missing prebuilds?
- does it prefer WASM only when addons are disabled, or as a general fallback?
- is the generated loader name/path aligned with the actual artifacts?

### 3. Publish identity
This should stop the product from treating release provenance as invisible.
It should say explicitly:
- whether npm trusted publishing is configured,
- whether provenance attestations should exist for this release class,
- whether the publish happened through token/manual flows,
- and whether the publish identity is strong, weak, or still manual-review territory.

## Recommended `0.1` command surface

### `cargo nodeapi-ship inspect`
Read project facts from `Cargo.toml`, `package.json`, generated loader files, `napi` config, and built artifacts if present.
Emit early observations without pretending the release is valid yet.

### `cargo nodeapi-ship matrix`
Import built `.node` artifacts from release outputs and normalize them into:
- `prebuild-manifest.json`
- `prebuild-coverage.report.json`
- `runtime-target-matrix.json`

### `cargo nodeapi-ship check`
Run policy checks for:
- Node-API floor mismatch,
- missing musl/glibc or arch tuples,
- loader-name/path drift,
- `node-addons` versus `default` route confusion,
- unsupported Bun/Deno/runtime claims,
- missing trusted-publisher / provenance expectations,
- and manual-review warnings.

### `cargo nodeapi-ship diff <old> <new>`
Compare release bundles and classify:
- `prebuild_matrix_changed`
- `loader_route_changed`
- `runtime_claim_changed`
- `publish_identity_changed`
- `local_build_policy_changed`
- `manual_review_boundary_changed`

### `cargo nodeapi-ship bundle`
Produce one compact `.nodebundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `nodeapi_ship_model`
  - shared types for policies, matrices, receipts, and diffs
- `nodeapi_ship_import`
  - project inspection, package metadata parsing, and loader import
- `nodeapi_ship_check`
  - policy checking and conservative classification
- `nodeapi_ship_render`
  - markdown summaries and zip bundle export
- `cargo-nodeapi-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `nodeapi_ship_napi_rs`
- `nodeapi_ship_npm`
- `nodeapi_ship_workspace`

## `0.1` artifact set

Core artifacts should be:
- `nodeapi-contract.toml`
- `runtime-target-matrix.json`
- `prebuild-manifest.json`
- `release.receipt.json`
- `notes.md`

This pass says `0.1` also needs three sharper review artifacts:
- `prebuild-coverage.report.json`
- `loader-route.receipt.json`
- `publish-identity.report.json`

Those matter because the shipkit gets vague again if it only records “a native addon exists” without making clear:
- which tuples were really shipped,
- how the package decides among native/default/fallback routes,
- and whether release identity/provenance should be trusted, absent, or manually explained.

## Discovery order

1. **Project inspection**
   - Node-API / `napi-rs` posture
   - `package.json`
   - generated loader files
   - built native artifact inventory
2. **Prebuild classification**
   - tuple coverage
   - libc splits
   - missing-artifact versus local-build policy
3. **Loader-route receipt**
   - `exports` conditions
   - native-first behavior
   - `default` fallback behavior
   - loader filename/path alignment
4. **Runtime policy normalization**
   - Node floor
   - Bun/Deno claims
   - local-build allowance
   - WASM fallback posture
5. **Publish identity check**
   - trusted-publisher posture
   - provenance expectation
   - manual/token release notes
6. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “package published successfully” as the verdict.
A good `0.1` should keep separate:
- `publish_succeeded`
- `prebuilds_shipped`
- `loader_route_clear`
- `runtime_claim_bounded`
- `publish_identity_strong`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- Node-API ABI stability and version floors
- Node package `exports` and `node-addons` routing
- Node context-aware / Worker support rules
- `napi-rs` generated loader/build flows
- npm trusted publishing and provenance rules

### Do not flatten into one fake verdict
- “build succeeded”
- “published to npm”
- “native prebuild exists for one tuple”
- “there is a `default` fallback”
- “trusted publishing was used”
- “Bun or Deno probably work too”

## Preferred proving grounds

- a package shipping Node-only native prebuilds for common glibc/musl/macOS/Windows tuples
- a package whose generated loader falls back to WASM when `node-addons` is disabled
- a package that permits local native builds for a named unsupported tuple
- a package using npm trusted publishing with provenance, while still keeping runtime claims conservative

## Non-goals

- not a replacement for `napi-rs`
- not an npm registry client or release host
- not a universal JS runtime abstraction layer
- not a promise that Bun or Deno compatibility follows automatically from Node-API adoption
- not a generic supply-chain verifier divorced from native-package facts

## MVP API sketch

```rust
pub enum PrebuildCoverageClass {
    FullyPrebuilt,
    PartialPrebuildMatrix,
    NativeGapHiddenByLocalBuild,
    WasmOnlyFallbackForNamedTuple,
    ManualReviewRequired,
}

pub fn inspect_project(root: &Path) -> Result<ProjectInspection>;
pub fn collect_prebuild_manifest(root: &Path) -> Result<Vec<PrebuildReceipt>>;
pub fn evaluate_prebuild_coverage(project: &ProjectInspection, prebuilds: &[PrebuildReceipt]) -> Result<PrebuildCoverageReport>;
pub fn evaluate_loader_route(project: &ProjectInspection) -> Result<LoaderRouteReceipt>;
pub fn evaluate_publish_identity(project: &ProjectInspection) -> Result<PublishIdentityReport>;
pub fn write_bundle(bundle: &NodeBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow Node package-routing and `node-addons` behavior closely.
- Follow npm trusted-publishing and provenance-policy changes.
- Follow `napi-rs` loader/build conventions closely.
- Keep Bun/Deno claims policy-aware before they become automation-heavy.
- Preserve `manual review required` whenever the crate cannot safely infer runtime or publish identity truth.
