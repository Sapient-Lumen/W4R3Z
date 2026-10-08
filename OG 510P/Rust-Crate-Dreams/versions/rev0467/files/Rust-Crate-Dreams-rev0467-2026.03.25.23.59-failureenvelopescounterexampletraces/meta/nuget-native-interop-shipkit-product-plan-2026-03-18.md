# NuGet Native Interop ShipKit — product plan (2026-03-18)

This note sharpens **P-0499 NuGet Native Interop ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which RIDs they actually shipped native assets for,
- whether those assets match the managed wrapper and logical library names they expect downstream users to load,
- what exact loader route the package depends on,
- what the deployment posture really is for ordinary JIT runtime, single-file publish, Native AOT, and plugin-style hosts,
- and whether important gaps are honest unsupported boundaries or merely hidden package-layout / probing drift.

It should **not** try to become a replacement for NuGet, MSBuild, `dotnet pack`, `csbindgen`, plugin frameworks, or Native AOT tooling.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For package maintainers, release engineers, downstream .NET consumers, and support reviewers, the crate should provide:

1. **One compact support contract** instead of release truth spread across `.csproj` files, `.nuspec` metadata, CI YAML, generated bindings, and issue-thread folklore.
2. **A RID-coverage report** that states which runtime families actually have packaged native assets and where package claims exceed reality.
3. **A loader-route report** that keeps default probing, `SetDllImportResolver`, and isolated plugin-host loading visibly distinct.
4. **A deployment-posture report** that keeps ordinary runtime, single-file, and Native AOT claims from being treated as the same promise.
5. **A conservative downstream summary** for app teams explaining what package they are actually consuming, which host models are boring, and what still requires manual review.
6. **A diffable release bundle** another person can inspect without recreating the full MSBuild/NuGet release pipeline.

## Three first-class review objects

### 1. RID coverage
This should stay separate from “the `.nupkg` exists.”

Named classes for `0.1`:
- `portable_rid_matrix_complete`
- `rid_asset_gap`
- `legacy_rid_graph_assumption`
- `managed_wrapper_claim_exceeds_assets`
- `manual_review_required`

This object should answer:
- which `runtimes/<rid>/native` directories are actually present,
- whether the package is leaning on portable RID families or older host-specific assumptions,
- and whether the managed wrapper or README claims outrun the asset matrix.

### 2. Loader route
This should answer questions like:
- does the package rely on default unmanaged probing,
- does it set `NativeLibrary.SetDllImportResolver`,
- does it need a custom `AssemblyLoadContext` / `AssemblyDependencyResolver` path,
- do the managed declarations and exported native library names agree,
- and is this package fundamentally ordinary-app-friendly or plugin-host-sensitive?

### 3. Deployment posture
This should stop the product from treating “works in one local app” as the verdict.
It should say explicitly:
- whether the package is only claiming ordinary JIT support,
- whether single-file behavior depends on default search behavior that has changed,
- whether Native AOT requires special policy or always-present native assets,
- and whether support claims for special hosts exceed the package evidence.

## Recommended `0.1` command surface

### `cargo nuget-ship inspect`
Read project facts from `Cargo.toml`, generated C# bindings, package layout, `.nupkg` contents, `.deps.json`, and optional `.runtimeconfig.json` / publish artifacts.
Emit early observations without pretending the release is valid yet.

### `cargo nuget-ship check`
Run policy checks for:
- missing or misleading RID assets,
- package claims based on old RID graph assumptions,
- managed/native library-name drift,
- default probing versus custom resolver mismatches,
- plugin-host / isolated ALC requirements,
- single-file and Native AOT support overclaims,
- and manual-review warnings.

### `cargo nuget-ship diff <old> <new>`
Compare release bundles and classify:
- `rid_matrix_changed`
- `loader_route_changed`
- `deployment_posture_changed`
- `binding_identity_changed`
- `manual_review_boundary_changed`

### `cargo nuget-ship bundle`
Produce one compact `.nugetbundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `nuget_ship_model`
  - shared types for policies, receipts, reports, and diffs
- `nuget_ship_import`
  - package inspection, `.nupkg` parsing, binding import, metadata parsing
- `nuget_ship_check`
  - policy checking and conservative classification
- `nuget_ship_render`
  - markdown summaries and zip bundle export
- `cargo-nuget-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `nuget_ship_csbindgen`
- `nuget_ship_msbuild`
- `nuget_ship_native_aot`

## `0.1` artifact set

Core artifacts should be:
- `nuget-ship-contract.toml`
- `rid-assets.manifest.json`
- `pinvoke-bindings.receipt.json`
- `consumer-intake.report.json`
- `notes.md`

This pass says `0.1` also needs three sharper review artifacts:
- `rid-coverage.report.json`
- `loader-route.report.json`
- `deployment-posture.report.json`

Those matter because the shipkit gets vague again if it only records “a NuGet package exists” without making clear:
- which native assets really shipped,
- how the runtime is expected to find them,
- and which deployment modes the release really supports.

## Discovery order

1. **Artifact inspection**
   - `.nupkg` contents
   - `runtimes/<rid>/native` inventory
   - native library names and bindings
   - generated/imported managed declarations
2. **RID classification**
   - declared versus observed asset matrix
   - portable versus legacy RID assumptions
   - missing or unexpected asset families
3. **Loader-route receipt**
   - default probing
   - explicit resolver hooks
   - plugin-host / isolated ALC posture
   - library-name drift
4. **Deployment-posture receipt**
   - ordinary runtime
   - single-file publish assumptions
   - Native AOT assumptions
   - support-claim drift
5. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “NuGet restore succeeded” as the verdict.
A good `0.1` should keep separate:
- `package_exists`
- `rid_matrix_complete`
- `loader_route_boring`
- `deployment_posture_clear`
- `managed_native_names_aligned`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- NuGet native asset layout rules
- RID catalog and RID guidance
- unmanaged library loading algorithm
- plugin-host guidance via `AssemblyDependencyResolver`
- Native AOT interop guidance
- single-file native-library behavior changes
- `LibraryImport` / P/Invoke best practices
- `csbindgen` bindings substrate

### Do not flatten into one fake verdict
- “the `.nupkg` exists”
- “bindings were generated”
- “default probing worked on one machine”
- “plugin host found the DLL somehow”
- “Native AOT published once”
- “single-file launch worked locally”

## Preferred proving grounds

- a Rust-backed NuGet package shipping Windows/Linux/macOS native assets with generated C# bindings
- a package whose declared support includes a RID family without a matching packaged native asset
- a plugin-host scenario requiring `AssemblyDependencyResolver` and/or a custom unmanaged-library resolver
- a package that works in a local JIT app but overclaims single-file or Native AOT support

## Non-goals

- not another Rust↔C# binding generator
- not a full MSBuild or NuGet publisher
- not a plugin framework
- not a generic interop performance / marshalling analyzer
- not a promise that signed packages or successful publish steps imply downstream load success

## MVP API sketch

```rust
pub enum RidCoverageClass {
    PortableRidMatrixComplete,
    RidAssetGap,
    LegacyRidGraphAssumption,
    ManagedWrapperClaimExceedsAssets,
    ManualReviewRequired,
}

pub fn inspect_release(root: &Path) -> Result<ReleaseInspection>;
pub fn evaluate_rid_coverage(release: &ReleaseInspection) -> Result<RidCoverageReport>;
pub fn evaluate_loader_route(release: &ReleaseInspection) -> Result<LoaderRouteReport>;
pub fn evaluate_deployment_posture(release: &ReleaseInspection) -> Result<DeploymentPostureReport>;
pub fn write_bundle(bundle: &NugetBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow RID and NuGet native-asset guidance closely.
- Follow .NET loading, plugin, single-file, and Native AOT behavior changes closely.
- Follow `csbindgen` and related Rust↔C# authoring substrate closely.
- Preserve `manual review required` whenever the crate cannot safely infer support truth.
