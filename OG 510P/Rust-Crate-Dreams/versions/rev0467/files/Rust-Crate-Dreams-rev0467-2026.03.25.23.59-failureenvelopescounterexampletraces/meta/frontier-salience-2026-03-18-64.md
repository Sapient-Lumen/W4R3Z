# Frontier salience snapshot — 2026-03-18 (64)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0499 NuGet Native Interop ShipKit** — because the archive still lacked a believable answer to “what exact .NET / NuGet support promise is this Rust release making, and how can another person review it without replaying local MSBuild, package-layout, and runtime-probing lore by hand?”

## Main judgment

The next worthy move here was **not** another binding generator, another MSBuild helper, another C# interop DSL, or another generic NuGet publisher.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **NuGet native interop shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **RID coverage** — which RID families actually have native assets in the package, and whether old RID-graph or wrapper claims exceed what shipped.
- **loader route** — whether downstream resolution depends on default probing, `NativeLibrary.SetDllImportResolver`, or plugin-style isolated load contexts.
- **deployment posture** — whether the package is only boring for ordinary runtime or is also honestly prepared for single-file and Native AOT environments.

That move is better grounded now because:

- NuGet still documents `runtimes/<rid>/native` as the native-asset contract and notes that SDK copying flattens directory structure under that tree;
- the current RID catalog and .NET 8 compatibility guidance now keep portable RID usage and host-selected asset resolution explicit;
- .NET’s unmanaged-library-loading docs still keep resolver hooks and `AssemblyLoadContext` in the actual algorithm rather than as trivia;
- the current plugin tutorial still makes `AssemblyDependencyResolver` the mainstream pattern for isolated plugin loading;
- Native AOT still has its own interop rules, and .NET 10 now changes single-file native-library search behavior enough that deployment-mode truth should stay explicit;
- and the current Rust substrate now clearly includes `csbindgen` plus current `LibraryImport`-first interop guidance rather than only hand-written `DllImport` folklore.

So the gap is no longer “Rust cannot ship .NET-native packages.”
The gap is that teams still rarely get a **reviewable cargo-native NuGet bundle** above RID inventories, loader routes, and deployment-mode claims.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
8. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library shipping-kit lane with explicit policy pressure.
9. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm shipping-contract opportunities.
10. **P-0467 Apple XCFramework & SwiftPM ShipKit** — now one of the clearest Apple-SDK shipping-contract opportunities because the substrate exists but the boring contract above slices, wrappers, and trust posture still does not.
11. **P-0499 NuGet Native Interop ShipKit** — now one of the clearest .NET shipping-contract opportunities because the substrate exists but the boring contract above RIDs, loader routes, and deployment posture still does not.
12. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-facing ship-contract opportunities.

## Why this won over adjacent candidates right now

- It beat **P-0500 JAR/JNI Native ShipKit** because the .NET lane already has a clearer official package-layout / probing / deployment contract and sharper current behavior changes.
- It beat **P-0501 RubyGems Native Extension ShipKit** because the NuGet lane currently has stronger official vocabulary around native assets, RIDs, and load behavior.
- It beat **another Rust↔C# binding generator** because `csbindgen` already exists and the sharper pain is release-contract truth above it.
- It beat **package-signing or provenance-first follow-ons** because RID / loader / deployment truth remains the more immediate support bottleneck.

## What changed in the archive

Added:
- `entries/2026-03-18-244.md`
- `meta/frontier-salience-2026-03-18-64.md`
- `meta/nuget-native-interop-shipkit-product-plan-2026-03-18.md`
- `fixtures/nuget-native-interop-shipkit/README.md`
- `fixtures/nuget-native-interop-shipkit/rid-coverage.report.schema.json`
- `fixtures/nuget-native-interop-shipkit/loader-route.report.schema.json`
- `fixtures/nuget-native-interop-shipkit/deployment-posture.report.schema.json`
- `fixtures/nuget-native-interop-shipkit/scenarios/portable_rid_claim_exceeds_shipped_assets/`
- `fixtures/nuget-native-interop-shipkit/scenarios/plugin_host_requires_custom_unmanaged_resolution/`
- `fixtures/nuget-native-interop-shipkit/scenarios/single_file_and_native_aot_claims_exceed_package_evidence/`

Updated:
- `proposals/nuget-native-interop-shipkit.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- RID assets,
- managed binding generation,
- unmanaged library probing,
- plugin-host loader behavior,
- and single-file / Native AOT deployment claims

into one fake “.NET support” story.
