# Apple XCFramework & SwiftPM ShipKit — product plan (2026-03-18)

This note sharpens **P-0467 Apple XCFramework & SwiftPM ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which Apple platform/arch/simulator slices they actually shipped,
- whether the SwiftPM wrapper and binary-target metadata really match the XCFramework bundle,
- whether the package checksum and module naming still align with the shipped zip,
- what privacy-manifest and signature/origin posture the release really has,
- and whether important trust or coverage gaps are honest unsupported boundaries or merely hidden packaging drift.

It should **not** try to become a replacement for UniFFI, `cargo swift`, `xcframework`, Xcode, Swift Package Manager, codesign, or notarization tooling.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For SDK maintainers, release engineers, app integrators, and reviewers, the crate should provide:

1. **One compact support contract** instead of release truth spread across CI YAML, shell scripts, XCFramework metadata, and `Package.swift` fragments.
2. **A slice-coverage report** that states which Apple target slices actually shipped.
3. **A package-alignment report** that keeps wrapper metadata, checksum, module name, and deployment claims visibly aligned or visibly drifted.
4. **A trust-posture report** that records signature/origin expectations and privacy-manifest posture without pretending those settle all safety questions.
5. **A conservative downstream summary** for app teams explaining what binary they are actually consuming, what platform gaps remain, and what still needs manual review.
6. **A diffable release bundle** another person can inspect without recreating the full Xcode or release pipeline.

## Three first-class review objects

### 1. Slice coverage
This should stay separate from “the XCFramework exists.”

Named classes for `0.1`:
- `complete_declared_matrix`
- `declared_platform_gap`
- `simulator_gap`
- `wrapper_claim_exceeds_bundle`
- `manual_review_required`

### 2. Package alignment
This should answer questions like:
- does the SwiftPM binary-target checksum correspond to the actual artifact that shipped?
- do the wrapper package and the XCFramework agree on module/framework naming?
- are local-path and remote-URL distribution modes being confused?
- do declared supported platforms or minimum deployment targets exceed what the bundle actually carries?
- did a rebinding or modulemap change leave the wrapper stale?

### 3. Trust posture
This should stop the product from treating release trust as invisible.
It should say explicitly:
- whether the XCFramework is signed and whether origin verification is expected,
- whether the signature route is stable, changed, absent, or manual-review territory,
- whether privacy manifests are present for the supported platform slices,
- and whether listed third-party-SDK requirements or other policy-sensitive checks still require manual review.

## Recommended `0.1` command surface

### `cargo apple-ship inspect`
Read project facts from `Cargo.toml`, `Package.swift`, wrapper directories, built XCFramework bundles, modulemaps/headers, and imported artifact zips if present.
Emit early observations without pretending the release is valid yet.

### `cargo apple-ship check`
Run policy checks for:
- missing device/simulator/macOS slices,
- wrapper module-name drift,
- stale SwiftPM checksum or zip mismatch,
- wrapper deployment claims exceeding bundle reality,
- missing privacy manifests for supported slices,
- signature/origin review gaps,
- and manual-review warnings.

### `cargo apple-ship diff <old> <new>`
Compare release bundles and classify:
- `slice_matrix_changed`
- `package_alignment_changed`
- `checksum_route_changed`
- `module_identity_changed`
- `trust_posture_changed`
- `manual_review_boundary_changed`

### `cargo apple-ship bundle`
Produce one compact `.applebundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `apple_ship_model`
  - shared types for policies, slice inventories, receipts, and diffs
- `apple_ship_import`
  - XCFramework inspection, wrapper import, metadata parsing
- `apple_ship_check`
  - policy checking and conservative classification
- `apple_ship_render`
  - markdown summaries and zip bundle export
- `cargo-apple-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `apple_ship_uniffi`
- `apple_ship_swiftpm`
- `apple_ship_codesign`

## `0.1` artifact set

Core artifacts should be:
- `apple-ship-contract.toml`
- `artifact-inventory.json`
- `release.receipt.json`
- `notes.md`

This pass says `0.1` also needs three sharper review artifacts:
- `slice-coverage.report.json`
- `package-alignment.report.json`
- `trust-posture.report.json`

Those matter because the shipkit gets vague again if it only records “an XCFramework exists” without making clear:
- which slices were really shipped,
- whether the wrapper/checksum/module identity still match,
- and what trust-policy facts a reviewer should inherit.

## Discovery order

1. **Artifact inspection**
   - XCFramework slices
   - module name / headers / modulemap
   - wrapper package structure
   - zip/checksum posture
2. **Slice classification**
   - device/simulator/macOS coverage
   - declared versus actual platform support
   - missing or unexpected slices
3. **Package-alignment receipt**
   - `Package.swift` binary target facts
   - checksum route
   - module naming
   - deployment/support claim alignment
4. **Trust-posture receipt**
   - signature/origin expectations
   - privacy-manifest inclusion
   - policy-sensitive review markers
5. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “Xcode imported it” as the verdict.
A good `0.1` should keep separate:
- `artifact_exists`
- `slice_matrix_complete`
- `wrapper_aligned`
- `checksum_matches`
- `trust_posture_strong`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- UniFFI Swift/Xcode integration
- `cargo swift` package assembly workflows
- `xcframework` bundle generation substrate
- SwiftPM binary-target rules and checksums
- Apple signature/origin verification guidance
- Apple privacy-manifest and third-party-SDK requirement surfaces

### Do not flatten into one fake verdict
- “bindings were generated”
- “an XCFramework zip exists”
- “the wrapper imports locally”
- “the checksum matches”
- “the artifact is signed”
- “the privacy manifest exists somewhere”

## Preferred proving grounds

- a Rust SDK shipping iOS device plus simulator slices through a remote SwiftPM binary target
- a package whose wrapper remained stale after a module/modulemap or rebinding change
- a signed XCFramework whose privacy-manifest posture is incomplete for one supported platform
- a release where local Xcode import works but the published wrapper/checksum contract drifted

## Non-goals

- not a replacement for UniFFI
- not a full Xcode project generator
- not a full codesign/notarization/origin-verification platform
- not a generic mobile CI service
- not a promise that checksum or signature presence alone makes a dependency safe

## MVP API sketch

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

## Maintenance posture

- Follow SwiftPM binary-target and checksum behavior closely.
- Follow Apple origin-verification and third-party-SDK policy changes closely.
- Follow `cargo swift`, UniFFI, and `xcframework` conventions closely.
- Preserve `manual review required` whenever the crate cannot safely infer trust or platform-support truth.
