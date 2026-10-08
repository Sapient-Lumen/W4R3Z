---
id: P-0499
title: NuGet Native Interop ShipKit — RID coverage, loader routes, and deployment posture for Rust-built .NET packages
status: idea
domains: [dotnet, nuget, ffi, packaging, distribution, ci, desktop]
last_reviewed: 2026-03-18
evidence:
  - https://learn.microsoft.com/en-us/nuget/create-packages/native-files-in-net-packages
  - https://learn.microsoft.com/en-us/dotnet/core/rid-catalog
  - https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/loading-unmanaged
  - https://learn.microsoft.com/en-us/dotnet/core/tutorials/creating-app-with-plugin-support
  - https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/interop
  - https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/10.0/native-library-search
  - https://learn.microsoft.com/en-us/dotnet/core/compatibility/deployment/8.0/rid-asset-list
  - https://learn.microsoft.com/en-us/dotnet/standard/native-interop/best-practices
  - https://github.com/Cysharp/csbindgen
---

# Problem

Rust already has meaningful substrate for shipping native code into .NET ecosystems.

Microsoft documents how NuGet packages should carry **native assets** via `runtimes/<rid>/native`, how **Runtime Identifiers (RIDs)** model platform-specific assets, how **unmanaged library loading** proceeds through resolvers and probing, how plugin-style hosts use `AssemblyDependencyResolver`, and how **Native AOT** changes some interop assumptions. The .NET 8+ and .NET 10 docs now make some of the old folklore even less safe: the host determines RID-specific assets more strictly, portable RIDs are preferred for package restore, and single-file apps no longer get the same native-library search behavior by accident.

On the Rust side, `csbindgen` already generates C# `DllImport` / `LibraryImport` style binding surfaces from Rust `extern "C"` exports.

That means the ecosystem is no longer mainly missing “some way to call Rust from C#”.

The sharper gap is that maintainers still do not have one boring artifact that answers the practical release questions:

- which RIDs a Rust-powered NuGet package actually ships native assets for,
- whether the package’s managed bindings, logical native library names, and file layout agree,
- whether downstream loading depends on default probing, a custom `DllImportResolver`, or a plugin-style isolated `AssemblyLoadContext`,
- whether support claims change for ordinary JIT deployment, single-file publish, Native AOT, or host/plugin embedding,
- and whether a consumer can tell if a failure is a missing RID asset, wrong logical library name, resolver mismatch, or deployment-mode mismatch.

The missing crate is **not** another binding generator.

The missing crate is a **NuGet native interop shipkit**: a crate and cargo-adjacent tool that turns “we publish a Rust native library into the .NET world” into a portable **RID coverage report, binding receipt, loader-route report, deployment-posture report, and support bundle**.

# What it provides

- `nuget-ship-contract.toml` — declares package identity, managed assembly names, logical native library names, supported RIDs, loader policy, deployment-mode claims, and manual-review boundaries.
- `rid-assets.manifest.json` — normalized inventory of native files under `runtimes/<rid>/native`, with digests, linkage names, and per-platform file naming.
- `pinvoke-bindings.receipt.json` — records generated `DllImport` / `LibraryImport` surfaces, entry-point names, calling conventions, and binding-generation facts.
- `rid-coverage.report.json` — explicit classification of declared RIDs versus shipped assets, including portable-RID and host-selection caveats.
- `loader-route.report.json` — whether the package assumes default probing, a custom `NativeLibrary.SetDllImportResolver`, isolated plugin loading, or some host-specific unmanaged load path.
- `deployment-posture.report.json` — support posture for ordinary JIT runtime, single-file publish, Native AOT, and other deployment-specific constraints.
- `consumer-intake.report.json` — compact downstream bundle for one environment: TFM, RID, host model, probing assumptions, and named risk class.
- `cargo nuget-ship inspect` — capture contract, package layout, bindings, and load assumptions.
- `cargo nuget-ship check` — explain whether RID coverage, binding names, loader route, and deployment-mode claims agree.
- `cargo nuget-ship diff <old> <new>` — compare RID coverage, loader routes, and deployment posture across releases.
- `*.nugetbundle.zip` — portable artifact for release review, publish rehearsal, support tickets, or downstream debugging.

# What the crate should provide other people

1. **A boring answer to “which .NET runtime environments does this package actually support?”** instead of scattered `.csproj`, `.nuspec`, and CI glue.
2. **A RID-aware asset report** that makes missing native binaries or wrong folder placement obvious before publish.
3. **A binding receipt** that proves the managed declarations match the Rust library names and calling-convention policy actually shipped.
4. **A loader-route contract** that keeps default probing, custom resolver use, and plugin-style host behavior visibly distinct.
5. **A deployment-posture report** that keeps ordinary JIT, single-file, and Native AOT claims from being treated as interchangeable.
6. **A bridge** between Rust-generated native libraries and NuGet’s packaging/probing conventions, so release review is not trial-and-error on downstream machines.

# Persona / who it’s for

- maintainers shipping Rust-powered NuGet packages to .NET or Unity consumers
- teams generating C# bindings with `csbindgen`
- release engineers building multi-RID native packages
- support engineers diagnosing “DLL not found”, wrong RID, or AOT/probing failures
- downstream teams that need one compact statement of native interop support policy

# Users & user stories

- **Package maintainer**: “Show me whether our NuGet package actually includes the native files every RID claim implies.”
- **Release engineer**: “Give me one bundle that joins RID assets, generated bindings, load assumptions, and deployment-mode claims.”
- **Support engineer**: “Tell me whether this failure is a missing RID asset, a wrong native library logical name, or a probing / AOT / single-file mismatch.”
- **Consumer team**: “Tell us whether this package is safe for Native AOT or single-file deployment, or whether we need a custom resolver story.”

# Prior art (and why it’s insufficient)

- Microsoft already documents NuGet native-file layout, RID conventions, native library loading, plugin load contexts, Native AOT interop, and single-file/native loading changes.
- `csbindgen` already makes Rust→C# binding generation far easier.
- Teams can hand-roll `.csproj`, `.nuspec`, and packaging scripts.
- The archive already has **P-0467 Apple XCFramework & SwiftPM ShipKit**, **P-0482 SDK Release Promise Drift Kit**, **P-0487 Foreign SDK Consumer Doctor Kit**, and **P-0498 Node-API Package & Prebuild Contract Kit**.

What remains missing is the **NuGet producer-side support contract** that answers: “which RIDs, what native file layout, what loader route, what deployment posture, and what downstream support risk?”

# Design goals

1. **RID-contract first** — the package’s runtime asset matrix is a central artifact.
2. **Binding-aware** — managed declarations and native exports must be reviewable together.
3. **Loader-route explicit** — default probing, custom resolvers, and plugin host routes must stay visible.
4. **Deployment-mode honest** — single-file and Native AOT must not silently inherit ordinary-JIT support claims.
5. **Cross-platform honest** — Windows, Linux, and macOS naming/layout differences remain first-class.
6. **Release-review oriented** — this should help package review and support, not become a general .NET build system.

# MVP surface

- Minimal types: `NugetShipContract`, `RidAssetManifest`, `PInvokeBindingsReceipt`, `RidCoverageReport`, `LoaderRouteReport`, `DeploymentPostureReport`, `ConsumerIntakeReport`, `NugetShipkitDiff`, `NugetBundle`
- Minimal functions:
  - `capture_nuget_ship_contract()`
  - `collect_rid_asset_manifest()`
  - `capture_pinvoke_bindings_receipt()`
  - `evaluate_rid_coverage()`
  - `evaluate_loader_route()`
  - `evaluate_deployment_posture()`
  - `evaluate_consumer_intake()`
  - `diff_nuget_shipkits()`
- Feature flags:
  - `csbindgen`
  - `nuget`
  - `serde`
  - `markdown`
  - `native-aot`

# Compatibility story

- Must remain useful whether the package uses `DllImport`, `LibraryImport`, or generated binding code.
- Must treat `runtimes/<rid>/native` layout and RID naming as first-class support facts.
- Should work for default probing flows and packages that use a custom import resolver.
- Must distinguish ordinary .NET runtime support from plugin-host and Native AOT-specific assumptions.
- Must keep single-file posture explicit, especially where native-library search or extraction assumptions differ.
- Should remain useful for Unity-like consumers when the package is still fundamentally a native library plus managed wrapper.

# Conformance & fixtures

- one fixture with a clean portable-RID package layout
- one fixture with a missing native asset for a claimed RID family
- one fixture with mismatched logical library names between C# bindings and packaged native files
- one fixture that requires a custom unmanaged-library resolver for a plugin-style host
- one fixture that claims single-file or Native AOT support beyond the package evidence
- goldens for `portable_rid_matrix_complete`, `rid_asset_gap`, `legacy_rid_graph_assumption`, `custom_resolver_required`, `isolated_plugin_route`, `single_file_sensitive`, `native_aot_sensitive`, and `deployment_claim_exceeds_evidence`

# Path to boring stability

- Freeze the RID / loader-route / deployment-posture vocabulary before adding deeper build-system integrations.
- Treat probing and resolver assumptions as explicit review facts, not hidden magic.
- Keep the first asset manifest simple and package-layout oriented.
- Prefer release-support artifacts over any attempt to become a full NuGet publisher or MSBuild replacement.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read one Rust→NuGet native package layout, record its RID coverage and binding names, inspect its loader route and deployment posture, and emit a support bundle naming any RID, probing, single-file, or Native AOT risks.

# De-risk plan

1. Start with ordinary NuGet package layout plus `csbindgen`-style managed bindings before chasing every .NET host topology.
2. Keep the verdict taxonomy small and release-review oriented.
3. Validate one clean package and one intentionally broken RID matrix.
4. Avoid becoming a .NET build orchestrator, package server, or generic interop framework.

# Non-goals

- Not another Rust↔C# binding generator.
- Not a replacement for NuGet packaging tools or MSBuild.
- Not a full plugin loader framework.
- Not a promise that every .NET deployment mode behaves the same for native library loading.

# Architecture & API sketch

```rust
pub enum DeploymentPostureClass {
    JitDefaultSupported,
    SingleFileSensitive,
    NativeAotSensitive,
    DeploymentClaimExceedsEvidence,
    ManualReviewRequired,
}

pub fn capture_nuget_ship_contract(root: &Path) -> Result<NugetShipContract>;
pub fn collect_rid_asset_manifest(root: &Path, contract: &NugetShipContract) -> Result<RidAssetManifest>;
pub fn capture_pinvoke_bindings_receipt(root: &Path) -> Result<PInvokeBindingsReceipt>;
pub fn evaluate_rid_coverage(contract: &NugetShipContract, assets: &RidAssetManifest) -> Result<RidCoverageReport>;
pub fn evaluate_loader_route(root: &Path, bindings: &PInvokeBindingsReceipt) -> Result<LoaderRouteReport>;
pub fn evaluate_deployment_posture(root: &Path, contract: &NugetShipContract) -> Result<DeploymentPostureReport>;
```

Bundle draft: `nuget-ship-contract.toml`, `rid-assets.manifest.json`, `pinvoke-bindings.receipt.json`, `rid-coverage.report.json`, `loader-route.report.json`, `deployment-posture.report.json`, `consumer-intake.report.json`, `notes.md`.

# Security / safety model

- Treat `.nupkg`, `.deps.json`, `.runtimeconfig.json`, managed wrappers, and generated bindings as untrusted input.
- Support redaction of private package feeds, local file paths, and CI internals.
- Keep deployment-posture reporting separate from broader claims about trustworthiness or supply-chain sufficiency.
- Never imply that “package restore succeeded” means the native interop surface is safe for every host model.

# Maintenance & governance plan

- Track NuGet native-asset and RID guidance closely.
- Track .NET loading / plugin / single-file / Native AOT behavior changes closely.
- Track `csbindgen` and adjacent Rust↔C# substrate closely.
- Keep the receipt schema small and explanation-heavy.
- Maintain fixtures spanning default probing, custom resolver, plugin isolation, and deployment-mode-sensitive releases.

# Keywords

- NuGet
- RID
- P/Invoke
- LibraryImport
- NativeLibrary
- AssemblyDependencyResolver
- Native AOT
- single-file
- .NET interop
- support contract

# Open questions

- How much of loader-route truth can be inferred automatically versus requiring maintainer annotation?
- Which Native AOT details belong in `0.1` versus a later adapter layer?
- Should package-signing or provenance posture be a later fourth review object, or remain a follow-on to RID/loader/deployment truth?

# Sources

- NuGet native files in .NET packages: https://learn.microsoft.com/en-us/nuget/create-packages/native-files-in-net-packages
- RID catalog: https://learn.microsoft.com/en-us/dotnet/core/rid-catalog
- Unmanaged library loading algorithm: https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/loading-unmanaged
- Create a .NET app with plugin support: https://learn.microsoft.com/en-us/dotnet/core/tutorials/creating-app-with-plugin-support
- Native code interop with Native AOT: https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/interop
- Host determines RID-specific assets (.NET 8): https://learn.microsoft.com/en-us/dotnet/core/compatibility/deployment/8.0/rid-asset-list
- Single-file native-library search breaking change (.NET 10): https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/10.0/native-library-search
- Native interop best practices (`LibraryImport`, naming, signatures): https://learn.microsoft.com/en-us/dotnet/standard/native-interop/best-practices
- csbindgen: https://github.com/Cysharp/csbindgen
