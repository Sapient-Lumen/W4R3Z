# Frontier salience snapshot — 2026-03-18 (59)

This pass did **not** promote a new cross-cutting ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0168 Rust Android Mobile Kit** — because the archive still lacked a believable answer to “how do ordinary teams ship Rust-built Android libraries or SDK cores in a boring, reviewable way?”

## Main judgment

The next worthy move here was **not** another mobile UI framework, another full-stack project generator, or another claim that Rust-on-Android is unsolved from scratch.
Those either already exist in partial form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Android library shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **ABI coverage** — what was actually built and for which Android slices,
- **load-doctor / collision policy** — what might fail or become unsafe when the artifact is packaged into a real app or SDK,
- **16 KB page-size readiness** — whether the native output is even plausibly ready for the modern Android release surface.

That move is better grounded now because:

- `cargo-ndk` already handles a real part of Android target and `jniLibs` plumbing; citeturn709402search1turn458687view0
- UniFFI already solves a real Kotlin-binding slice without becoming a full Android shipping story; citeturn709402search2turn458687view1
- `cargo-apk` and `cargo-mobile2` prove ongoing Android/mobile workflow demand; citeturn388957view0turn388957view1
- Android’s NDK documentation already makes native-library packaging/collision policy a concrete problem; citeturn709402search3turn458687view2
- Android’s 16 KB page-size requirement makes native-library readiness newly visible in release review; citeturn559103search1turn458687view3
- and Rust’s own release notes show the Android NDK floor still moves underneath projects. citeturn709402search0turn458687view5

So the gap is no longer “Rust cannot target Android.”
The gap is that teams still rarely get a **reviewable cargo-native Android shipping artifact** above NDK scripts, JNI glue, AAR packaging, and store-policy drift.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0168 Rust Android Mobile Kit** — now one of the clearest **Band B shipping-kit** opportunities because the substrate exists but the boring contract still does not.
7. **P-0451 Cfg Availability Ledger Kit** — still the sharpest item-level conditional-support truth lane.
8. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
9. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
10. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.

## Why this won over adjacent candidates right now

- It beat **another generic foreign-package contract** because Android’s current combination of NDK substrate, JNI/AAR policy, and page-size requirements makes this lane especially concrete.
- It beat **broader mobile-toolchain ambitions** because a review-first library-shipping contract is more believable than a giant mobile platform bet.
- It beat **more diagnostics-only follow-ons** because the missing value here is a combined build/package/doctor artifact rather than one more isolated error explainer.
- It beat **more app-generation ideas** because the sharp pain is often not project scaffolding but repeatable native-library shipping.

## What changed in the archive

Added:
- `entries/2026-03-18-239.md`
- `meta/frontier-salience-2026-03-18-59.md`
- `meta/rust-android-mobile-kit-product-plan-2026-03-18.md`
- `fixtures/rust-android-mobile-kit/abi-coverage.report.schema.json`
- `fixtures/rust-android-mobile-kit/load-doctor.report.schema.json`
- `fixtures/rust-android-mobile-kit/page-size-compat.report.schema.json`
- `fixtures/rust-android-mobile-kit/scenarios/aar_native_library_collision_requires_policy/`
- `fixtures/rust-android-mobile-kit/scenarios/page_size_16kb_release_gate/`
- `fixtures/rust-android-mobile-kit/scenarios/uniffi_kotlin_bindings_need_packaging_honesty/`

Updated:
- `proposals/rust-android-mobile-kit.md`
- `fixtures/rust-android-mobile-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`

## What this pass deliberately did not do

It did **not** collapse:

- target/NDK plumbing,
- binding generation,
- AAR assembly,
- final app-packaging graph behavior,
- runtime loading policy,
- and release-policy readiness

into one fake “Android support” story.

## Sources

- https://github.com/bbqsrc/cargo-ndk
- https://mozilla.github.io/uniffi-rs/latest/kotlin/overview.html
- https://github.com/rust-mobile/cargo-apk
- https://github.com/tauri-apps/cargo-mobile2
- https://developer.android.com/ndk/guides/libs
- https://developer.android.com/guide/practices/page-sizes
- https://developer.android.com/training/articles/perf-jni
- https://doc.rust-lang.org/beta/releases.html
