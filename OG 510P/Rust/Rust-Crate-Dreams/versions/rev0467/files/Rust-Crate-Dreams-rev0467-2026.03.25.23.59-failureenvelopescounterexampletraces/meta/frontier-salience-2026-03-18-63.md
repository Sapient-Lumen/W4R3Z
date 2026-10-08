# Frontier salience snapshot — 2026-03-18 (63)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0467 Apple XCFramework & SwiftPM ShipKit** — because the archive still lacked a believable answer to “what exact Apple SDK support promise is this Rust release making, and how can another person review it without replaying local build scripts, Xcode settings, or bespoke packaging lore by hand?”

## Main judgment

The next worthy move here was **not** another binding generator, another Xcode project template, another Swift package wrapper helper, or another codesign automation script.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Apple SDK shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **slice coverage** — which Apple platform / architecture / simulator slices are actually present in the XCFramework versus only implied by docs or wrappers.
- **package alignment** — whether the SwiftPM binary-target wrapper, checksum, module naming, and deployment claims really match the artifact that shipped.
- **trust posture** — whether the release has signatures, origin-verification expectations, and privacy-manifest inclusion in a shape another reviewer can actually reason about.

That move is better grounded now because:

- Apple still centers XCFramework bundles for Swift-package binary distribution and keeps explicit checksum semantics for binary targets; 
- Swift Package Manager still documents `binaryTarget(url:checksum:)` and `binaryTarget(path:)` as the binary-package boundary for Apple-platform artifacts;
- Apple’s origin-verification guidance still treats signed XCFramework identity as a first-class downstream review surface;
- Apple’s privacy-manifest docs still keep third-party SDK packaging responsibilities visible, including XCFramework and Swift-package distribution paths;
- Apple’s third-party SDK requirements page now makes privacy manifests mandatory for listed SDKs and signatures required when those listed SDKs are used as binary dependencies;
- and the current Rust substrate now clearly includes UniFFI Swift/Xcode integration, `cargo swift`, and the `xcframework` crate rather than only hand-rolled shell-script folklore.

So the gap is no longer “Rust cannot ship Apple SDKs.”
The gap is that teams still rarely get a **reviewable cargo-native Apple bundle** above slice inventories, wrapper/checksum drift, and trust-policy facts.

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
11. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-facing ship-contract opportunities.

## Why this won over adjacent candidates right now

- It beat **P-0499 NuGet Native Interop ShipKit** because the Apple lane already had clearer current policy seams around wrapper checksums, signatures, and privacy posture.
- It beat **P-0500 JAR/JNI Native ShipKit** because the Apple lane already had a more explicit binary-distribution contract and a cleaner near-term `0.1` story.
- It beat **another UniFFI / Swift wrapper helper** because the sharper pain is release-contract truth above existing authoring substrate, not another authoring helper.
- It beat **consumer-side doctoring first** because the producer-side Apple release contract still needs to exist before downstream diagnosis can inherit it cleanly.

## What changed in the archive

Added:
- `entries/2026-03-18-243.md`
- `meta/frontier-salience-2026-03-18-63.md`
- `meta/apple-xcframework-swiftpm-shipkit-product-plan-2026-03-18.md`
- `fixtures/apple-xcframework-swiftpm-shipkit/README.md`
- `fixtures/apple-xcframework-swiftpm-shipkit/slice-coverage.report.schema.json`
- `fixtures/apple-xcframework-swiftpm-shipkit/package-alignment.report.schema.json`
- `fixtures/apple-xcframework-swiftpm-shipkit/trust-posture.report.schema.json`
- `fixtures/apple-xcframework-swiftpm-shipkit/scenarios/ios_binary_target_checksum_matches_but_simulator_slice_missing/`
- `fixtures/apple-xcframework-swiftpm-shipkit/scenarios/wrapper_module_name_drift_after_rebinding/`
- `fixtures/apple-xcframework-swiftpm-shipkit/scenarios/signed_xcframework_with_privacy_manifest_gap/`

Updated:
- `proposals/apple-xcframework-swiftpm-shipkit.md`
- `INDEX.md`
- `README.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- Swift bindings generation,
- XCFramework slice assembly,
- SwiftPM wrapper/checksum metadata,
- Apple signature/origin verification,
- and privacy-manifest requirements

into one fake “Apple support” story.
