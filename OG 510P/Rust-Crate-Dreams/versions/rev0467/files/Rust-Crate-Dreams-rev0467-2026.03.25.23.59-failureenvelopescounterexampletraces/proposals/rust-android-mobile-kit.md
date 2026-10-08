---
id: P-0168
title: Rust Android Mobile Kit — cargo-native Android library shipping, AAR packaging, and load-readiness evidence
status: idea
domains: [mobile, android, build, ffi, tooling, packaging, release]
last_reviewed: 2026-03-18
evidence:
  - https://github.com/bbqsrc/cargo-ndk
  - https://mozilla.github.io/uniffi-rs/latest/kotlin/overview.html
  - https://github.com/rust-mobile/cargo-apk
  - https://github.com/tauri-apps/cargo-mobile2
  - https://developer.android.com/ndk/guides/libs
  - https://developer.android.com/guide/practices/page-sizes
  - https://developer.android.com/training/articles/perf-jni
  - https://doc.rust-lang.org/beta/releases.html
---

## Main judgment

The worthy missing crate here is **not** “make Rust compile for Android.”
That substrate already exists.
The sharper missing layer is a **cargo-native Android shipping contract** for teams who need to build, package, inspect, and diagnose Rust-produced Android libraries in a boring, reviewable way.

What is missing is a stable answer to questions like:

- Which ABIs, API levels, and binding modes are actually covered by this build?
- What exactly went into the produced `jniLibs/` or AAR?
- Will this artifact collide with other packaged native libraries in a real app?
- Is the output plausibly ready for modern Android requirements like **16 KB page-size support** on 64-bit devices?
- Which claims are local observation versus imported substrate facts versus manual-review-only?

## Why this moved now

This lane is stronger now because the Android/Rust substrate is real but still fragmented:

- `cargo-ndk` already solves a real part of the target/NDK plumbing and can place outputs in `jniLibs`-shaped layouts.
- UniFFI can generate Kotlin bindings when the Rust interface fits UniFFI’s object model.
- `cargo-apk` and `cargo-mobile2` show that Rust-on-Android packaging and mobile workflows are active enough to support a higher coordination layer.
- Android’s NDK guidance makes AAR-native-library packaging, collision risk, and runtime-library policy concrete.
- Google Play’s 16 KB page-size requirement for modern Android device targets makes “native library readiness” a more explicit release concern than it used to be.
- Rust itself now expects **Android NDK 25 or newer**, so toolchain assumptions already drift under long-lived project scripts.

That combination means the ecosystem now has **enough substrate to build on**, but still lacks one boring crate that turns scattered Android/Rust build knowledge into a reviewable shipping workflow.

## What it should provide other people

For Android app teams, SDK authors, and Rust-core-library maintainers, the crate should provide:

1. **One cargo-native golden path** for building Android-ready Rust libraries without re-assembling NDK env, ABI targets, and packaging layouts from scratch.
2. **ABI coverage truth** so the produced artifact says exactly which ABIs, API levels, symbol modes, and binding modes were built.
3. **Binding-mode honesty** so a project can say “this is raw JNI”, “this is UniFFI-generated Kotlin”, or “manual glue is still required.”
4. **AAR / `jniLibs` load-readiness diagnostics** so teams can catch native-library collisions, bad packaging layout, missing entrypoints, or misleading metadata before Gradle/app integration time.
5. **16 KB page-size readiness checks** because modern Android release policy now makes that a real receiver-facing native-library concern.
6. **Versioned evidence bundles** that can be attached to CI, release review, SDK publication, or support threads.
7. **A short human summary** that Android and Rust engineers can both read without spelunking shell scripts.

For maintainers, it should provide:

1. a compact checked config instead of a private pile of shell/Gradle snippets,
2. receipts and reports instead of opaque build directories,
3. reuse of `cargo-ndk`, UniFFI, and standard Android packaging rules instead of replacing them,
4. conservative `manual_review_required` fallbacks for app-specific policy,
5. and release diffs that make shipping drift loud.

## Product boundaries

### In scope

- Rust **libraries** and shared-core components shipped into Android apps or SDKs
- JNI mode and UniFFI/Kotlin mode as explicit binding modes
- `jniLibs/` layout capture, optional AAR packaging, symbol/debug sidecar handling
- ABI/API-level coverage reporting
- load-readiness / packaging-collision doctoring
- 16 KB page-size readiness checks and receipts
- CI/release artifacts for downstream support

### Out of scope

- a full Android UI framework
- replacing Gradle, AGP, or Android Studio
- replacing `cargo-ndk`, `cargo-apk`, or UniFFI
- general mobile project generation
- app-store publishing automation as the center of gravity
- pretending a library-only check can fully prove behavior inside every final app packaging graph

## Design principles

- **Cargo-native first.** Optional Gradle/plugin helpers can exist later, but `0.1` should succeed from Cargo.
- **Build on existing substrate.** Wrap `cargo-ndk`, respect UniFFI where it fits, and reuse Android packaging rules.
- **Review artifacts over wizardry.** The output should be something another engineer can inspect and diff.
- **Library-shipping scope first.** The first win is “ship a Rust library into Android reliably,” not “replace the Android toolchain.”
- **Conservative diagnosis.** The doctor should say `manual_review_required` rather than invent certainty about app-specific merges.

## Recommended `0.1` command surface

### `cargo android-kit init`
Create a starter `android-kit.toml` from workspace metadata plus selected Android targets, binding mode, and packaging intent.

### `cargo android-kit build`
Build configured Android library artifacts through the selected target set, capturing toolchain, target, API-level, and output layout facts.

### `cargo android-kit aar`
Produce an AAR-oriented output bundle when the project intends to ship via AAR rather than a copied `jniLibs/` directory.

### `cargo android-kit doctor`
Render the human-facing risk summary for suspicious situations such as:

- `abi_declared_but_not_built`
- `binding_mode_ambiguous`
- `uniffi_bindings_present_but_packaging_missing`
- `jni_entrypoint_missing_or_unchecked`
- `aar_native_library_collision_risk`
- `shared_runtime_policy_unclear`
- `page_size_16kb_readiness_unknown`
- `manual_review_required`

### `cargo android-kit summary`
Emit a compact summary for release review, README snippets, or support tickets.

### `cargo android-kit diff <old> <new>`
Compare two bundles and classify:

- `abi_set_changed`
- `api_level_changed`
- `binding_mode_changed`
- `symbol_surface_changed`
- `jni_layout_changed`
- `aar_contents_changed`
- `page_size_readiness_changed`
- `load_doctor_changed`
- `manual_review_required`

### `cargo android-kit pack`
Emit one compact `androidbundle.zip` for CI artifacts, release review, Maven/SDK publication review, or downstream debugging.

## Recommended crate/workspace split

- `android_kit_model`
  - shared Rust types for config, manifests, receipts, reports, and diffs
- `android_kit_discovery`
  - workspace import, target discovery, binding-mode import, UniFFI/JNI intent import
- `android_kit_build`
  - `cargo-ndk` orchestration, ABI/API selection, output collection, symbol/debug sidecars
- `android_kit_check`
  - ABI coverage, load-doctor rules, JNI surface checks, page-size checks, AAR/jniLibs policy checks
- `android_kit_pack`
  - summary rendering, diffing, and bundle emission
- `cargo-android-kit`
  - user-facing cargo subcommand

Optional adapters should remain optional until the core format is trusted:

- `android_kit_uniffi`
- `android_kit_gradle`
- `android_kit_cargo_apk_import`
- `android_kit_mobile2_import`

## `0.1` artifact set

The first release should revolve around:

- `android-kit.toml`
- `android-build.manifest.json`
- `abi-coverage.report.json`
- `binding-mode.report.json`
- `jni-surface.report.json`
- `load-doctor.report.json`
- `page-size-compat.report.json`
- `android-summary.md`
- `androidbundle.zip`

The center of gravity is now explicit:

- **ABI coverage** keeps “we build Android” from blurring together unsupported and actually-built slices.
- **load doctor** keeps packaging/layout/runtime-collision risks from surfacing only after Gradle/app integration.
- **page-size compatibility** keeps modern Android release-policy drift from remaining hidden in native-library folklore.

## MVP

A believable `0.1` should prove itself on three boring but common situations:

1. **JNI library copied into an Android app**
   - produces `jniLibs` layout plus ABI coverage and load-doctor output.
2. **UniFFI-based Kotlin bindings with Rust core**
   - captures that bindings were generated but does not pretend packaging happened automatically.
3. **AAR-oriented SDK distribution**
   - checks native-library contents and flags likely packaging/runtime-collision risks.

## Adoption staircase

1. **Single-project local use** — replace a fragile internal script pile.
2. **CI artifact use** — attach `androidbundle.zip` to every release candidate.
3. **SDK/library publication use** — ship summaries and receipts with Android-facing releases.
4. **Org standardization** — make Android Rust packaging drift visible across repositories.

## Risks / open questions

- AAR collision diagnosis can only be conservative unless the final app packaging graph is imported.
- JNI-surface checking must avoid overclaiming semantic correctness when it only has symbol/layout evidence.
- UniFFI mode must stay explicit so the crate does not promise arbitrary Kotlin/Java interop generation.
- The first release must resist becoming another monolithic mobile toolchain.
