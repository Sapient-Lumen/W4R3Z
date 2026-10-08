---
id: P-0487
title: Foreign SDK Consumer Doctor Kit — wheel/XCFramework installability audits, environment snapshots, and downstream-use diagnosis bundles
status: idea
domains: [python, apple, ffi, packaging, support, interoperability, sdk, diagnostics, ci]
last_reviewed: 2026-03-07
evidence:
  - https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
  - https://packaging.python.org/en/latest/specifications/binary-distribution-format/
  - https://pyo3.rs/v0.28.2/free-threading
  - https://pyo3.rs/v0.28.2/features
  - https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
  - https://developer.apple.com/support/third-party-SDK-requirements/
  - https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
---

# Problem

The archive already has **P-0482 SDK Release Promise Drift Kit**, which is about what the *producer* promised across releases.

But downstream breakage often happens later, on the **consumer** side:

- `pip` or another installer rejects a wheel because tags do not match the environment.
- a free-threaded Python consumer expects one wheel shape while the producer actually shipped another.
- an app integrator pulls a Swift package whose XCFramework slices do not match the target they are building.
- the binary target checksum is stale or the package metadata no longer matches the actual binary bundle.
- the app team is unsure whether privacy-manifest or signature expectations are satisfied for a binary SDK they just adopted.

There is already a lot of substrate here:

- Python packaging has a formal wheel format and formal compatibility tags.
- PyO3 documents `abi3` behavior and the special free-threaded-Python constraint that there is not yet an equivalent limited API for the free-threaded ABI.
- Apple treats XCFrameworks as the binary-distribution shape for Swift packages and now expects privacy manifests (and, in important cases, signatures) for third-party SDKs.

Yet ordinary support still tends to rely on screenshots, ad hoc environment dumps, and manual guesswork.

The sharper missing crate is not another shipkit and not another release diff tool.

The sharper missing crate is a **consumer doctor** that captures the consumer environment, inspects the foreign SDK artifact, and explains *why this consumer can or cannot use it*.

# What it provides

- `consumer-env.snapshot.json` — normalized consumer-side facts: Python implementation/version/ABI expectations, OS/arch, Apple platform/SDK tuple, package manager context, and policy toggles.
- `artifact-intake.report.json` — normalized facts imported from wheel or XCFramework artifacts.
- `installability.verdict.json` — explains whether the artifact should install or integrate in the captured environment, with cause categories like `tag_mismatch`, `slice_missing`, `checksum_mismatch`, `privacy_manifest_required`, and `manual_review_required`.
- `runtime-risk.report.json` — flags likely post-install surprises such as free-threaded incompatibility, interpreter/version drift, or ambiguous binary-consumer assumptions.
- `sdk-consumer-policy.toml` — allows teams to declare which warnings are blocking, tolerated, or informational.
- `cargo sdk-consumer-doctor capture-env` — capture the consumer-side environment.
- `cargo sdk-consumer-doctor inspect <artifact>` — inspect one wheel or XCFramework.
- `cargo sdk-consumer-doctor verify <env> <artifact>` — produce the verdict and report bundle.
- `cargo sdk-consumer-doctor diff <old> <new>` — compare diagnosis outcomes or environment changes.
- `*.sdkdoctor.zip` — portable issue/support artifact for downstream consumers, SDK maintainers, or release review.

# What the crate should provide other people

1. **A stable diagnosis vocabulary** for “why can’t I use this Rust-built SDK?”
2. **A consumer-side support bundle** that can be shared without sending entire projects or giant logs.
3. **A bridge between release promises and real intake failures**.
4. **A review artifact** for app teams adopting binary SDKs under privacy/signature or checksum constraints.
5. **A practical support tool** for SDK maintainers who need to debug downstream integration failures quickly.

# Persona / who it’s for

- Python users installing Rust-backed wheels
- Apple app teams consuming Rust-built XCFrameworks or Swift packages
- support engineers debugging adoption failures for Rust-built foreign SDKs
- SDK maintainers who need better downstream diagnostics
- CI/release engineers validating that released artifacts remain consumable in intended environments

# Users & user stories

- **Python consumer**: “Tell me whether this wheel is incompatible with my interpreter/platform tags or whether my environment is missing something else.”
- **PyO3 maintainer**: “Explain whether this failure is a free-threaded/`abi3` mismatch, a version-specific wheel expectation, or a packaging metadata issue.”
- **Apple integrator**: “Show me whether this XCFramework actually has the slice I need and whether the package checksum/privacy expectations line up.”
- **Support engineer**: “Give me one bundle I can request from downstream users instead of asking for screenshots and long environment dumps.”

# Prior art (and why it’s insufficient)

- Python packaging specifies wheel structure and compatibility tags, but not a maintainer-grade diagnosis artifact.
- PyO3 documents `abi3` and free-threaded limitations, but not a generic consumer doctor bundle.
- Apple documents binary frameworks, checksums, privacy manifests, and third-party SDK requirements, but not a compact cross-project diagnosis workflow.
- P-0482 in this archive covers **release promise drift**, which is adjacent but not the same as **consumer environment diagnosis**.

What remains missing is a **consumer-side diagnosis layer** that says: “here is the environment, here is what the artifact claims, here is the specific mismatch, and here is what changed from the last successful case.”

# Design goals

1. **Consumer-first** — start from the question downstream users actually have.
2. **Artifact-import-first** — useful even when the producer build pipeline is unavailable.
3. **Cross-ecosystem but not over-abstracted** — share core bundle structure without pretending Python and Apple are identical.
4. **Cause-oriented** — verdicts should name the mismatch, not just fail generally.
5. **Policy-aware** — teams should be able to define which diagnostics block adoption.

# MVP surface

- Minimal types: `ConsumerEnvironment`, `ArtifactIntakeReport`, `InstallabilityVerdict`, `RuntimeRiskReport`, `SdkConsumerPolicy`, `SdkDoctorBundle`
- Minimal functions:
  - `capture_consumer_environment()`
  - `inspect_python_wheel()`
  - `inspect_xcframework()`
  - `verify_installability()`
  - `diff_diagnosis_results()`
- Feature flags:
  - `python-wheel`
  - `apple-xcframework`
  - `serde`
  - `zip`
  - `markdown`

# Compatibility story

- Python mode should normalize wheel filename tags, ABI expectations, distribution metadata, and free-threaded-specific caveats.
- Apple mode should normalize slice/platform facts, Swift-package checksum expectations, and privacy-manifest presence.
- Every verdict must say whether it came from a **spec rule**, an **artifact observation**, or an **ecosystem-policy expectation**.
- The crate should stay useful even if build/publish tools improve, because downstream diagnosis still matters.

# Conformance & fixtures

- wheel with platform-tag mismatch against the captured environment
- wheel where free-threaded Python requires a version-specific wheel instead of the limited API path
- XCFramework missing a simulator or device slice
- Swift-package checksum mismatch fixture
- fixture where privacy-manifest expectations are present but the artifact is incomplete or ambiguous
- Goldens for `tag_mismatch`, `free_threaded_requires_version_specific`, `slice_missing`, `checksum_mismatch`, `privacy_review_required`, and `manual_review_required`

# Path to boring stability

- Freeze the verdict vocabulary before adding more ecosystems.
- Start with static artifact/environment diagnosis rather than attempting to build or install anything.
- Keep policy and ecosystem expectations explicit and versioned.
- Treat ambiguous verdicts as normal and useful.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI/cargo subcommand that capture a consumer environment, inspect a Python wheel or XCFramework, and emit one diagnosis bundle explaining whether the consumer should be able to use that artifact and why.

# De-risk plan

1. Start with read-only inspection and verdict generation.
2. Keep the initial verdict taxonomy small and explicit.
3. Pilot on one PyO3 wheel flow and one UniFFI/XCFramework flow.
4. Add runtime probing only after the static diagnosis model feels stable.

# Non-goals

- Not a replacement for PyO3, maturin, UniFFI, SwiftPM, or package installers.
- Not a general package manager for Python or Apple ecosystems.
- Not a full runtime health-check framework for consumer apps.
- Not a promise that every integration failure can be inferred statically.

# Architecture & API sketch

```rust
pub enum VerdictKind {
    Compatible,
    TagMismatch,
    SliceMissing,
    ChecksumMismatch,
    PrivacyReviewRequired,
    ManualReviewRequired,
}

pub fn capture_consumer_environment(root: &Path) -> Result<ConsumerEnvironment>;
pub fn inspect_python_wheel(path: &Path) -> Result<ArtifactIntakeReport>;
pub fn inspect_xcframework(path: &Path) -> Result<ArtifactIntakeReport>;
pub fn verify_installability(env: &ConsumerEnvironment, artifact: &ArtifactIntakeReport) -> InstallabilityVerdict;
```

Bundle draft: `consumer-env.snapshot.json`, `artifact-intake.report.json`, `installability.verdict.json`, `runtime-risk.report.json`, `sdk-consumer-policy.toml`, `notes.md`.

# Security / safety model

- Treat wheel archives, XCFramework bundles, package manifests, and environment snapshots as untrusted input.
- Support redaction of local paths, internal package names, and app identifiers.
- Keep ecosystem-policy expectations separate from hard spec mismatches.
- Never imply that checksum or signature presence alone proves safety.

# Maintenance & governance plan

- Track Python packaging tag and wheel-spec evolution.
- Track PyO3 changes around free-threaded Python and `abi3` behavior.
- Track Apple binary-target, checksum, privacy-manifest, and third-party SDK requirement changes.
- Maintain fixtures for common downstream failure modes rather than trying to mirror whole ecosystems.

# Milestones

## 0.1
- consumer environment snapshot
- wheel/XCFramework inspection
- initial verdict taxonomy

## 0.2
- policy file
- diagnosis diffing
- privacy/checksum review hooks

## 0.3
- richer redaction support
- more environment adapters
- optional lightweight runtime probes

# Open questions

- Which Python-environment facts are essential for a useful support bundle without becoming intrusive?
- Should Apple signature checks be first-class in MVP or remain an informative review hook at first?
- How much verdict logic should depend on consumer policy rather than hard spec rules?
- Where should the boundary sit between P-0482’s producer-side promise drift and P-0487’s consumer-side diagnosis?

# Sources

- Python packaging compatibility tags: https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
- Python wheel format: https://packaging.python.org/en/latest/specifications/binary-distribution-format/
- PyO3 `abi3` feature docs: https://pyo3.rs/v0.28.2/features
- PyO3 free-threaded Python docs: https://pyo3.rs/v0.28.2/free-threading
- Apple binary frameworks as Swift packages: https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
- Apple third-party SDK requirements (privacy manifests and signatures): https://developer.apple.com/support/third-party-SDK-requirements/
- Apple privacy manifest files docs: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
