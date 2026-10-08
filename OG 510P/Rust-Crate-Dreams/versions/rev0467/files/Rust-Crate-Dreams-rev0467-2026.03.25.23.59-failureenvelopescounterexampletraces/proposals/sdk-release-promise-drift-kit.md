---
id: P-0482
title: SDK Release Promise Drift Kit — Python-wheel/XCFramework promise ledgers, consumer-compat diffs, and cross-ecosystem release review bundles
status: idea
domains: [python, apple, ffi, packaging, release, interoperability, sdk, ci, tooling]
last_reviewed: 2026-03-07
evidence:
  - https://pyo3.rs/main/building-and-distribution
  - https://pyo3.rs/main/building-and-distribution/multiple-python-versions
  - https://www.maturin.rs/distribution.html
  - https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  - https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
  - https://developer.apple.com/documentation/PackageDescription/Target/checksum
  - https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
---

# Problem

Rust now has real foreign-SDK shipping substrate in at least two strategically important ecosystems:

- **Python**: PyO3 documents version-selection and `abi3` tradeoffs, while maturin handles wheel building, manylinux tagging, bundled shared libraries, and optional debug-info sidecars.
- **Apple**: UniFFI documents Swift/Xcode integration, Apple treats XCFramework + SwiftPM binary targets as the normal binary-distribution path, checksums are explicit, and privacy manifests now matter for third-party SDKs.

That means the sharp pain is less often “how do I produce *an* artifact?” and more often:

- what **consumer promise** did this release actually make,
- what changed in that promise since the last release,
- which changes were deliberate versus accidental,
- and how can a reviewer compare Python and Apple release contracts without re-reading build logs and package metadata by hand?

Today’s tools mostly optimize for **building** or **publishing** artifacts. They do not give maintainers one compact, diffable answer to questions like:

- did we drop or add a Python interpreter/platform tag,
- did we accidentally switch from version-specific wheels to `abi3` or vice versa,
- did free-threaded support become separate or disappear,
- did bundled libraries, debug-info posture, or manylinux compatibility drift,
- did an XCFramework lose a simulator slice,
- did the SwiftPM checksum or privacy-manifest posture change,
- and what should downstream consumers expect to break or re-validate?

The missing crate is not another builder and not another uploader.

The missing crate is a **release promise drift kit** that turns foreign-SDK artifact changes into a boring review ritual.

# What it provides

- `sdk-release-policy.toml` — declares supported consumer surfaces, allowed drift classes, manual-review zones, and adapter-specific policy.
- `release-promise.snapshot.json` — normalized promise surface for one release: tags, slices, ABI mode, toolchain facts, sidecars, checksum facts, privacy-manifest facts, and consumer-visible support axes.
- `promise-drift.diff.json` — compares two snapshots and classifies additions, removals, widenings, tightenings, and ambiguous drift.
- `consumer-compat.report.json` — explains likely downstream consequences in plain categories such as `rebuild_required`, `re-pin_checksum`, `manual_review_required`, and `likely_safe`.
- `manual-review-zones.json` — facts that were observed but not conclusively classified automatically.
- `cargo sdk-promise capture` — inspect imported wheels / XCFrameworks and emit one snapshot.
- `cargo sdk-promise diff <old> <new>` — compare releases and classify promise drift.
- `cargo sdk-promise doctor` — flag suspicious gaps such as missing `t` wheels, missing simulator slices, stale checksums, or privacy-manifest mismatch.
- `*.sdkpromise.zip` — portable artifact for release review, downstream integrator handoff, or incident/postmortem use.

# What the crate should provide other people

1. **A stable vocabulary for external promises** instead of ad hoc reading of wheel tags, Info.plists, and package manifests.
2. **A diffable release-review artifact** for what changed in consumer compatibility.
3. **Policy locks** so teams can say which drift is allowed in patch/minor/major releases.
4. **One adapter surface** that can start with Python wheels and Apple SDKs without pretending they are identical.
5. **A downstream-facing explanation layer** that helps app/library consumers know what to re-test.

# Persona / who it’s for

- teams shipping Rust-backed Python extensions or Apple SDKs
- release engineers maintaining cross-language artifact matrices
- downstream integrators who want boring compatibility receipts
- security/compliance reviewers checking release drift
- tooling authors building higher-level release dashboards or bots

# Users & user stories

- **Python maintainer**: “Tell me whether this release changed our wheel promise in a way that forces downstream rebuilds or Python-version revalidation.”
- **Apple SDK maintainer**: “Show me if the XCFramework lost a slice, changed checksum, or drifted on privacy-manifest expectations.”
- **Reviewer**: “Compare old and new release promises without reverse-engineering package formats.”
- **Integrator**: “Give me a concise compatibility summary so I know whether I can update safely.”

# Prior art (and why it’s insufficient)

- PyO3 documents how to choose version-specific versus `abi3` builds and how to cope with multiple Python versions.
- maturin builds and tags wheels, checks manylinux compatibility, bundles shared libraries, and can include separate debug info.
- UniFFI and related Apple-facing tooling help generate Swift bindings and package XCFrameworks.
- Apple documents binary-target distribution, checksums, and privacy manifests.

What remains missing is a **review-first adapter layer** that says: “here is the promise this artifact set makes to consumers, here is how it drifted, and here is which changes are definitely safe, definitely risky, or still manual-review territory.”

# Design goals

1. **Promise-first** — focus on consumer-visible guarantees rather than raw build internals.
2. **Adapter-driven** — one schema family, multiple artifact adapters.
3. **Import-friendly** — useful even when artifacts were built elsewhere.
4. **Diffable and policy-aware** — drift classification matters more than giant inventories.
5. **Conservative with uncertainty** — unclear changes should stay visible, not guessed away.

# MVP surface

- Minimal types: `SdkReleasePolicy`, `PromiseAxis`, `PromiseSnapshot`, `PromiseDrift`, `ConsumerCompatReport`, `ManualReviewZone`, `SdkPromiseBundle`
- Minimal functions:
  - `capture_python_wheel_promise()`
  - `capture_xcframework_promise()`
  - `diff_promise_snapshots()`
  - `classify_consumer_impact()`
  - `write_bundle()`
- Feature flags:
  - `python-wheel`
  - `apple-xcframework`
  - `serde`
  - `zip`
  - `markdown`

# Compatibility story

- Works on **imported artifacts** first; it must not require owning the build pipeline.
- Python mode should normalize wheel tags, ABI mode, free-threading posture, bundled-library posture, and optional debug-info sidecars.
- Apple mode should normalize XCFramework slices, SwiftPM checksum/binary-target facts, and privacy-manifest presence.
- Every field should say whether it was **observed**, **declared**, or **inferred**.
- The crate should remain useful even if builders become more capable, because the review/diff artifact still matters.

# Conformance & fixtures

- One PyO3 wheel pair that changes from version-specific wheels to `abi3`.
- One PyO3 wheel pair where free-threaded support is added or dropped.
- One XCFramework pair with a missing simulator slice.
- One XCFramework pair with checksum drift and stale package metadata.
- Goldens for `promise_widened`, `promise_tightened`, `checksum_drift`, `privacy_review_required`, and `manual_review_required`.

# Path to boring stability

- Stabilize the snapshot/diff vocabulary before adding any release automation.
- Start with read-only capture and drift classification.
- Keep consumer-impact categories coarse and reviewable.
- Treat manual-review zones as a success condition, not as failure to be hidden.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that inspect imported Python wheels or XCFramework bundles, normalize their consumer-visible promise surface, compare two releases, and emit one diffable compatibility bundle.

# De-risk plan

1. Start with imported artifact inspection instead of build-pipeline integration.
2. Keep the first consumer-impact vocabulary very small and auditable.
3. Validate on one PyO3 crate and one UniFFI/XCFramework release flow.
4. Add adapter-specific details only when they clearly affect downstream compatibility.

# Non-goals

- Not a replacement for PyO3, maturin, UniFFI, SwiftPM, or Xcode.
- Not a new uploader or package registry client.
- Not a guarantee that compatibility can always be inferred automatically.
- Not a universal abstraction for every packaging ecosystem.

# Architecture & API sketch

```rust
pub enum DriftKind {
    Added,
    Removed,
    Widened,
    Tightened,
    Ambiguous,
}

pub fn capture_python_wheel_promise(path: &Path) -> Result<PromiseSnapshot>;
pub fn capture_xcframework_promise(path: &Path) -> Result<PromiseSnapshot>;
pub fn diff_promise_snapshots(old: &PromiseSnapshot, new: &PromiseSnapshot) -> PromiseDrift;
pub fn classify_consumer_impact(diff: &PromiseDrift) -> ConsumerCompatReport;
```

Bundle draft: `sdk-release-policy.toml`, `release-promise.snapshot.json`, `promise-drift.diff.json`, `consumer-compat.report.json`, `manual-review-zones.json`, `notes.md`.

# Security / safety model

- Treat wheel metadata, package manifests, and XCFramework contents as untrusted input.
- Never imply that checksums, tags, or privacy manifests alone prove safety.
- Support redaction of internal paths and proprietary module names.
- Preserve exact tool versions and raw adapter observations where known.

# Maintenance & governance plan

- Track PyO3 / maturin changes around `abi3`, interpreter support, free-threading, and wheel tagging.
- Track Apple/SwiftPM changes around binary targets, checksums, and privacy-manifest policy.
- Keep adapter schemas small and versioned.
- Publish adapter-specific fixture corpora so drift classifications can be regression-tested.

# Milestones

## 0.1
- Python wheel snapshot capture
- XCFramework snapshot capture
- promise diff bundle export

## 0.2
- consumer-impact classification
- manual-review zones
- policy locks for allowed drift classes

## 1.0
- stable schema
- curated adapter fixture corpus
- CI/release-bot integration helpers

# Open questions

- What is the smallest cross-ecosystem promise vocabulary that still helps real reviewers?
- Which Python wheel facts are genuinely consumer-facing versus noisy implementation detail?
- How much of Apple privacy-manifest interpretation should stay explicit manual review forever?

# Sources

- https://pyo3.rs/main/building-and-distribution
- https://pyo3.rs/main/building-and-distribution/multiple-python-versions
- https://www.maturin.rs/distribution.html
- https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
- https://developer.apple.com/documentation/PackageDescription/Target/checksum
- https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
