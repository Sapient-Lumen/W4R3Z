# Rust Android Mobile Kit — product plan (2026-03-18)

This note sharpens **P-0168 Rust Android Mobile Kit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps project maintainers publish one reviewable answer to:

- which Android ABIs and API levels they actually build,
- which binding mode the crate expects downstream users to rely on,
- what exactly is being shipped in `jniLibs/` or AAR form,
- what known native-library collision or loading risks remain,
- whether the build is plausibly ready for modern Android page-size policy,
- and what changed between releases.

It should **not** try to become a full Android framework, a full mobile project generator, or a replacement for Gradle/AGP/Android Studio.
Those are adjacent imports, not the core product.

## Why this lane is finally believable

The substrate is now real enough to build on:

- `cargo-ndk` already handles target/NDK env setup and `jniLibs` placement. citeturn709402search1turn458687view0
- UniFFI already generates Kotlin bindings for a real slice of Rust interfaces, but it does not by itself solve packaging/distribution. citeturn709402search2turn458687view1
- `cargo-apk` and `cargo-mobile2` prove active demand for Rust/mobile packaging workflows. citeturn388957view0turn388957view1
- Android’s own docs already define the AAR/native-library packaging surface and its collision hazards. citeturn709402search3turn458687view2
- Android’s JNI guidance already makes thread/env/marshalling constraints explicit enough to treat them as part of a reviewable shipping surface. citeturn709402search6turn458687view4
- Android’s 16 KB page-size rule turns one formerly-implicit native detail into an explicit release concern. citeturn559103search1turn458687view3

That means the problem has shifted from “Can Rust reach Android?” to “Can teams ship Rust-built Android libraries predictably enough to share one boring workflow?”

## What the crate should provide other people

For downstream consumers and app teams, the crate should provide:

1. **One compact Android shipping contract** instead of a scavenger hunt across shell scripts, Gradle glue, NDK variables, and CI YAML.
2. **ABI coverage truth** so “Android support” does not blur together declared and actually-built slices.
3. **Binding-mode truth** so downstream teams know whether they are integrating raw JNI, UniFFI-generated Kotlin bindings, or manual glue.
4. **Load-doctor output** that warns about layout, collision, runtime-library, and obvious loading risks before the app build.
5. **Page-size readiness receipts** so release review can tell whether a native library still needs Android-policy work.
6. **Release diffs** so ABI, API-level, packaging, and readiness drift become visible.
7. **A short human summary** that Android and Rust engineers can use in the same thread.

For maintainers, the crate should provide:

1. a compact config file that is cheap to review,
2. small receipts/reports rather than a giant generated Android project,
3. reuse of upstream substrate instead of a second mobile stack,
4. conservative `manual_review_required` escape hatches,
5. and artifact bundles that fit CI/release review.

## Recommended `0.1` command surface

### `cargo android-kit init`
Create `android-kit.toml` by importing obvious candidates from:

- workspace `Cargo.toml`,
- selected Android targets,
- crate type / library outputs,
- optional UniFFI config,
- optional packaging intent (`jnilibs`, `aar`).

The generated contract should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` instead of guessed.

### `cargo android-kit build`
Run the Android library build and capture:

- target triples,
- minimum / selected Android API level,
- NDK version / Rust version,
- output library locations,
- hashes, sizes, and debug-sidecar locations,
- declared binding mode.

### `cargo android-kit check`
Run the local validation pass:

- do declared Android targets parse,
- do expected outputs exist for each ABI,
- does the packaging layout match the declared intent,
- are JNI/UniFFI expectations aligned with declared binding mode,
- is the page-size check class satisfied or unknown,
- and which parts remain manual-review-only?

### `cargo android-kit doctor`
Render the receiver-facing warnings for suspicious situations such as:

- `abi_declared_but_missing`
- `binding_mode_ambiguous`
- `uniffi_generated_but_packaging_not_declared`
- `jni_surface_unchecked`
- `aar_collision_risk`
- `shared_runtime_policy_unclear`
- `page_size_16kb_unknown`
- `manual_review_required`

`doctor` should be a human-first renderer over the checked artifacts, not a separate magical inference engine.

### `cargo android-kit summary`
Render a short Android shipping summary.
This should be boring enough to paste into release notes, SDK docs, or support threads.

### `cargo android-kit diff <old> <new>`
Compare two receipts or bundles and classify:

- `abi_added`
- `abi_removed`
- `api_level_changed`
- `binding_mode_changed`
- `jni_layout_changed`
- `aar_contents_changed`
- `load_risk_changed`
- `page_size_readiness_changed`
- `manual_review_required`

### `cargo android-kit pack`
Emit one compact `androidbundle.zip` for CI artifacts, downstream support, or release review.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `android_kit_model`
  - shared Rust types for config, manifests, receipts, reports, evidence classes, and diffs
- `android_kit_discovery`
  - import logic for workspace/build intent, UniFFI usage, ABI targets, and Android metadata
- `android_kit_build`
  - orchestration of `cargo-ndk` and collection of produced outputs
- `android_kit_check`
  - ABI coverage, binding-mode checking, load-doctor logic, page-size checks, and packaging validation
- `android_kit_pack`
  - summary rendering, diffing, and bundle emission
- `cargo-android-kit`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core format is trusted:

- `android_kit_uniffi`
- `android_kit_gradle`
- `android_kit_cargo_apk_import`
- `android_kit_mobile2_import`

## `0.1` artifact set

`0.1` should revolve around these files:

- `android-kit.toml`
- `android-build.manifest.json`
- `abi-coverage.report.json`
- `binding-mode.report.json`
- `jni-surface.report.json`
- `load-doctor.report.json`
- `page-size-compat.report.json`
- `android-summary.md`
- `androidbundle.zip`

The center of gravity is now clearer than before:

- **abi-coverage** keeps build claims honest,
- **load-doctor** keeps packaging/load failure modes from staying script folklore,
- **page-size-compat** keeps modern Android release-policy drift visible instead of implicit.

## First-class review objects

### ABI coverage

This artifact should say:

- which Android ABIs were declared,
- which were actually built,
- whether each slice has a loadable shared library,
- whether symbol/debug sidecars exist,
- and whether any slice is build-only / unreviewed / missing.

### Binding mode

The crate should not hide whether a consumer must integrate:

- raw JNI entrypoints,
- UniFFI-generated Kotlin bindings,
- or manual adapter code.

A build that emits Kotlin bindings but no AAR or packaging instructions should remain explicit about that gap.

### Load doctor

The doctor should stay conservative and focus on reviewable facts such as:

- multiple packaged JNI libraries in one AAR,
- likely `libc++_shared.so` collision risks,
- surprising runtime-library dependencies,
- absent or unclear entrypoint surfaces,
- packaging intent mismatches,
- and unresolved manual-review requirements.

### Page-size compatibility

The first version does not need to become a full ELF analyzer platform.
But it should have a stable receipt/report surface for:

- which native outputs were checked,
- what page-size posture was declared or observed,
- what Android-policy class applies,
- and whether the result is `ready`, `unknown`, `needs_rebuild`, or `manual_review_required`.

## Discovery order

A disciplined import order helps prevent false confidence.

1. **Workspace/library intent**
   - crate type, package metadata, selected library outputs
2. **Target/ABI intent**
   - configured Android targets and API level
3. **Binding-mode intent**
   - UniFFI config or declared JNI mode
4. **Observed build outputs**
   - produced `.so` files, layouts, hashes, debug sidecars
5. **Packaging intent**
   - `jniLibs` copy versus AAR assembly
6. **Policy checks**
   - collision rules, runtime-library posture, page-size status
7. **Manual notes**
   - what still requires final-app review

The importer should prefer surfacing uncertainty over synthesizing false confidence.

## Proving-ground scenarios

The first proving grounds should be boring and common:

1. **A small JNI-based Rust core copied into `app/src/main/jniLibs/`**
2. **A UniFFI-generated Kotlin binding flow where packaging still needs explicit handling**
3. **An AAR-shipped Rust library where native-library collision policy must be made visible**
4. **A release gate where 16 KB page-size support changed from unknown to ready or blocked**

## Adoption staircase

1. **Local wrapper replacement** — one repo replaces fragile private scripts.
2. **CI artifact use** — every Android build produces `androidbundle.zip`.
3. **SDK release review** — AAR / native-library publication includes summary + receipts.
4. **Org-wide standardization** — Android Rust packaging drift becomes diffable across teams.

## What to leave for later

Later versions can add:

- deeper Gradle imports,
- app-packaging graph imports,
- symbolication/minidump handoff,
- Maven publication helpers,
- and device/emulator exercise receipts.

But `0.1` does not need any of those to be worthwhile.
It only needs to make Android Rust library shipping **boring, inspectable, and conservative**.
