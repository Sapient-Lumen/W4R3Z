---
id: P-0467
title: Apple XCFramework & SwiftPM ShipKit — slice coverage, package alignment, and trust posture for Rust-built Apple SDKs
status: idea
domains: [apple, ios, macos, swift, ffi, packaging, release, mobile, sdk]
last_reviewed: 2026-03-18
evidence:
  - https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  - https://docs.rs/crate/uniffi/latest
  - https://github.com/antoniusnaumann/cargo-swift/blob/main/README.md
  - https://docs.rs/xcframework/latest/xcframework/
  - https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html
  - https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
  - https://developer.apple.com/documentation/xcode/verifying-the-origin-of-your-xcframeworks
  - https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk
  - https://developer.apple.com/support/third-party-SDK-requirements/
---

# Problem

Rust already has meaningful Apple-platform substrate:

- UniFFI has production-quality Swift bindings and documents Xcode integration.
- the UniFFI ecosystem now points to `cargo swift` as a package-building helper.
- Rust now has crates like `xcframework` for building Apple XCFramework bundles.

Apple also has a much sharper binary-distribution contract than many Rust maintainers realize:

- XCFrameworks are the canonical multiplatform binary bundle for Swift-package binary distribution.
- Swift Package Manager keeps binary targets explicit through URL/path + checksum boundaries.
- Xcode now treats XCFramework origin verification as a real downstream review surface.
- Apple’s privacy-manifest and third-party-SDK requirement surfaces keep release trust posture visible enough that “the zip published” is not the whole story anymore.

That means today’s gap is not “there is no way to call Rust from Swift.”

The sharper gap is that SDK teams still hand-roll too much of the release contract:

- which slices are actually present,
- whether the wrapper package and binary target still match the XCFramework,
- whether the checksum/module identity/deployment claims stayed aligned,
- whether trust posture around signatures, origin verification, and privacy manifests is even reviewable,
- and how an app team can verify the bundle without reverse-engineering a bespoke CI pipeline.

The missing crate is not another binding generator and not another one-off Xcode script.

The missing crate is a **shipkit** that turns Rust → Apple artifacts into a boring, reviewable release bundle.

# What it provides

- `apple-ship-contract.toml` — declares platforms, packaging mode, wrapper mode, trust-policy expectations, and manual-review boundaries.
- `slice-coverage.report.json` — exact Apple slices present, declared platform matrix, linkage kind, and named gaps.
- `package-alignment.report.json` — normalized SwiftPM binary-target metadata, checksum route, wrapper/module identity, and support-claim drift.
- `trust-posture.report.json` — signature route, origin-verification expectation, privacy-manifest posture, and unresolved manual checks.
- `cargo apple-ship inspect` — import XCFramework + wrapper facts into a normalized release view.
- `cargo apple-ship check` — validate slice coverage, wrapper alignment, checksum posture, and trust-policy boundaries.
- `cargo apple-ship diff` — compare two release bundles and classify what materially changed.
- `cargo apple-ship bundle` — emit one shareable `.applebundle.zip` for maintainers and consumers.

# What the crate should provide other people

1. **A boring release contract** for Rust libraries shipped as Apple SDKs.
2. **A slice-coverage report** that makes “what Apple targets are actually inside this XCFramework?” obvious.
3. **A package-alignment report** that helps consumers trust the wrapper/checksum/module boundary.
4. **A trust-posture report** that keeps signature/origin and privacy-manifest realities reviewable.
5. **A bridge** from Rust binding generators to Apple-native distribution norms.
6. **A diffable release bundle** another person can inspect without reproducing the whole Xcode pipeline.

# Persona / who it’s for

- teams shipping Rust-backed Apple SDKs
- mobile and desktop app teams consuming third-party Rust-built binaries
- release engineers maintaining SwiftPM binary targets
- reviewers checking Apple bundle integrity and packaging drift

# Users & user stories

- **SDK maintainer**: “Show me the exact slices, wrapper identity, checksum route, and trust posture we are publishing.”
- **App integrator**: “Tell me whether this XCFramework really matches the Swift package wrapper and what manual review I still inherit.”
- **Security reviewer**: “Give me one receipt covering signature/origin expectations, privacy-manifest posture, and binary-wrapper drift.”
- **Cross-platform team**: “Compare this release against the previous one and flag slice, wrapper, or trust drift.”

# Prior art (and why it’s insufficient)

- UniFFI provides production-quality Swift bindings and documents Xcode integration.
- `cargo swift` exists as a helper for building Swift packages from Rust code.
- the `xcframework` crate shows there is already packaging substrate.
- SwiftPM documents binary-target URL/path + checksum boundaries.
- Apple documents XCFramework bundles, Swift-package binary distribution, origin verification, privacy manifests, and third-party-SDK requirements.

What remains missing is a **maintainer-facing coordination layer**: the thing that says “these are the slices, this is the wrapper/checksum/module contract, and this is the release trust posture.”

# Design goals

1. **Bundle-first** — publish one artifact humans can review before release.
2. **Apple-contract-aware** — respect XCFramework, SwiftPM, checksum, privacy, and origin-verification seams explicitly.
3. **Binding-generator-neutral** — work with UniFFI first, but avoid hard-coding one FFI generator forever.
4. **Consumer-verifiable** — make app-team verification part of the story, not an afterthought.
5. **Narrow and boring** — stay on packaging/integrity/review, not full mobile app orchestration.

# MVP surface

- Minimal types: `AppleShipContract`, `SliceCoverageReport`, `PackageAlignmentReport`, `TrustPostureReport`, `AppleBundle`
- Minimal functions:
  - `inspect_release()`
  - `evaluate_slice_coverage()`
  - `evaluate_package_alignment()`
  - `evaluate_trust_posture()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `uniffi`
  - `swiftpm`
  - `codesign`

# Compatibility story

- Must be useful with hand-written Swift wrappers, UniFFI-generated bindings, or future generator stacks.
- Should work when the XCFramework is built elsewhere and merely imported for audit.
- Must tolerate partial platform coverage while making absences explicit.
- Should preserve manual-review markers for cases where Xcode, SwiftPM, or codesign behavior cannot be fully inferred.

# Conformance & fixtures

- One checksum-valid-but-simulator-missing fixture.
- One wrapper/module-name drift fixture.
- One signed-but-privacy-gap fixture.
- Goldens for `simulator_gap`, `module_identity_drift`, `checksum_or_zip_mismatch`, and `signed_but_privacy_gap`.

# Path to boring stability

- Stabilize the slice/package/trust vocabulary before any fancy publishing automation.
- Start with audit + bundle export.
- Treat signatures, origin verification, and privacy manifests as evidence, not magic safety proofs.
- Add deeper consumer-side verification helpers only after the core receipt schema settles.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that inspect an XCFramework release, normalize its slice coverage, wrapper/checksum alignment, and trust posture, and emit one shareable release bundle.

# De-risk plan

1. Start with read-only audits and imported XCFrameworks.
2. Validate first on UniFFI + SwiftPM binary-target workflows.
3. Keep trust checks explicit but conservative.
4. Only add build/publish automation after the review artifact is trusted.

# Non-goals

- Not a replacement for UniFFI, `cargo swift`, or `xcframework`.
- Not a full Xcode project generator.
- Not a generic mobile CI platform.
- Not a promise that checksums, signatures, or privacy manifests alone imply safety.

# Architecture & API sketch

```rust
pub enum SliceCoverageClass {
    CompleteDeclaredMatrix,
    DeclaredPlatformGap,
    SimulatorGap,
    WrapperClaimExceedsBundle,
    ManualReviewRequired,
}

pub fn inspect_release(root: &Path) -> Result<ReleaseInspection>;
pub fn evaluate_slice_coverage(release: &ReleaseInspection) -> Result<SliceCoverageReport>;
pub fn evaluate_package_alignment(release: &ReleaseInspection) -> Result<PackageAlignmentReport>;
pub fn evaluate_trust_posture(release: &ReleaseInspection) -> Result<TrustPostureReport>;
pub fn write_bundle(bundle: &AppleBundle, out: &Path) -> Result<()>;
```

Bundle draft: `apple-ship-contract.toml`, `slice-coverage.report.json`, `package-alignment.report.json`, `trust-posture.report.json`, `notes.md`.

# Security / safety model

- Never imply that signatures, checksums, or manifest presence alone make a dependency trustworthy.
- Record exact generator, Xcode, Cargo, SwiftPM, and platform-tool versions when known.
- Support redaction of proprietary file names and internal paths.
- Preserve explicit manual-review zones for privacy-manifest interpretation, signer changes, and downstream packaging policy.

# Maintenance & governance plan

- Track UniFFI / `cargo swift` / XCFramework ecosystem churn.
- Track Apple distribution guidance around XCFramework origin verification, privacy manifests, and third-party SDK requirements.
- Keep the receipt schema small and explanation-heavy.
- Maintain fixtures spanning device/simulator/macOS package variants.

# Milestones

## 0.1
- slice scan
- wrapper/checksum normalization
- bundle export

## 0.2
- trust-posture receipts
- privacy-manifest audit
- release diffing

## 1.0
- stable receipt schema
- consumer verification adapters
- curated release fixtures

# Open questions

- What is the smallest useful slice vocabulary that still helps reviewers catch platform drift?
- How much privacy-manifest checking can be automated without overclaiming Apple policy knowledge?
- Should the first version focus only on XCFramework + SwiftPM, or also permit CocoaPods/Carthage-facing export receipts later?

# Sources

- UniFFI Swift Xcode integration: https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- UniFFI docs.rs (`cargo swift` adjacency): https://docs.rs/crate/uniffi/latest
- `cargo swift` README: https://github.com/antoniusnaumann/cargo-swift/blob/main/README.md
- `xcframework` crate docs: https://docs.rs/xcframework/latest/xcframework/
- SwiftPM package description / binary targets: https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html
- Apple Swift-package binary distribution docs: https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
- Apple XCFramework origin verification docs: https://developer.apple.com/documentation/xcode/verifying-the-origin-of-your-xcframeworks
- Apple privacy manifest docs for apps and third-party SDKs: https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk
- Apple third-party SDK requirements: https://developer.apple.com/support/third-party-SDK-requirements/
