# Renewal receipt: Conservative native-shell mobile product (2026-03-22)

Card under review:
- `defaults/conservative-native-shell-mobile-product-2026Q1.md`

Review goal:
- decide whether the archive should publish a first maintained **native-shell mobile product** card;
- decide whether the clearest boring current default for the bounded native-shell mobile lane is **native Swift/Kotlin shells + Rust core via UniFFI-generated bindings**;
- and keep native-shell truth, Rust-core truth, binding-generation truth, Android-build truth, iOS-build truth, lifetime/resource truth, and support/docs truth visibly separate.

## Canon import checked
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- UniFFI getting started / motivation / design principles:
  https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
  https://mozilla.github.io/uniffi-rs/latest/Motivation.html
  https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html
- UniFFI Swift bindings / module / Xcode / Swift bindgen:
  https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
  https://mozilla.github.io/uniffi-rs/latest/swift/module.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  https://mozilla.github.io/uniffi-rs/next/swift/uniffi-bindgen-swift.html
- UniFFI Kotlin configuration / Gradle / lifetimes:
  https://mozilla.github.io/uniffi-rs/latest/kotlin/configuration.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/lifetimes.html
- `cargo-ndk`:
  https://docs.rs/crate/cargo-ndk/latest
- Existing cross-platform mobile card for contrast:
  `defaults/conservative-mobile-app-product-2026Q1.md`

## Fresh observations
1. Official Rust signals still say the ecosystem-navigation problem is partly about **choice paralysis** and **tacit knowledge**, which supports publishing a bounded native-shell-mobile default rather than leaving this lane to “mobile Rust” folklore.
2. UniFFI is now explicit enough about what it is and is not: a tool that automatically generates foreign-language bindings targeting Rust libraries, with real Swift and Kotlin docs, but not an end-to-end Android/iOS packaging system.
3. The Swift side is concrete enough to review: the current docs describe production-quality Swift bindings, generated headers/modulemaps/Swift sources, Xcode build phases, and even an optional Swift-specific bindgen path for XCFramework-compatible modulemaps.
4. The Kotlin/Android side is concrete enough to review: the docs describe configuration knobs, Android-specific options, Gradle integration, and explicit lifetime management via `close()` / `AutoCloseable` for generated wrappers.
5. UniFFI’s design principles still make the lane’s intended posture clear: safety first, idiomatic foreign-language bindings, and generated code that should remain inspectable enough to debug.
6. Android build/setup truth is still separate from binding-generation truth, which keeps `cargo-ndk` useful as a boring helper rather than a hidden whole-lane answer.
7. The existing Flutter-first mobile card is still the better default for “one shared shell/runtime”, which is exactly why native-shell mobile now deserves its own maintained card instead of remaining only an alternative bullet.

## Slot-by-slot review
### Native-shell truth
The product shell should stay explicitly native on both platforms.
That means iOS and Android framework ownership remain first-class truths rather than implementation details.

### Rust-core truth
Rust should own meaningful shared logic in this lane.
The point is not tiny helper functions; it is a shared engine with real value.

### Binding-generation truth
UniFFI is the clearest boring default for exposing one Rust core to both Swift and Kotlin with a generated, reviewable high-level API.
It is stronger here than hand-written FFI as the first answer, but not because it erases the rest of the product.

### Android-build truth
Android cross-build and packaging remain explicit truths.
`cargo-ndk` is a useful helper because it handles environment/configuration and target layout, but it does not replace the native Android app/package story.

### iOS-build truth
The iOS side still requires explicit library and build-phase integration.
That is acceptable in this lane because native shell ownership is the point, not something to hide.

### Lifetime/resource truth
UniFFI’s Kotlin wrappers explicitly require `close()` / `AutoCloseable` handling for exposed interfaces.
That resource-management surface is exactly the kind of truth a boring default should keep visible.

## Serious alternatives retained
- **Flutter shell + `flutter_rust_bridge`** — strongest alternative when one shared cross-platform shell is the point.
- **Tauri 2 mobile** — strongest alternative when a webview shell and existing web frontend assets dominate.
- **Dioxus mobile / Slint mobile** — strongest alternatives when the team wants Rust to own much more of the UI/runtime story.
- **hand-written FFI or language-specific bindings** — strongest alternative when only one foreign language matters or tighter control over the bridge is required.

## Judgment
Publish the card as a maintained public default.

Label:
- **default-with-caveats**

Why:
- the project class recurs often;
- the current cross-platform mobile card already proves this lane matters by naming it as a serious alternative;
- the current UniFFI/Xcode/Gradle/Kotlin-lifetime docs are finally concrete enough to support a bounded boring default;
- and the evidence supports a UniFFI-centered answer without pretending mobile build/package complexity has disappeared.

## Replay notes
- renew when UniFFI changes enough to move the boring default for this bounded scope;
- renew when Android/iOS build-helper tooling changes enough to alter the boring helper posture;
- renew if the native-shell lane becomes clearly better served by narrower platform-specific cards;
- and keep the boundary with the **cross-platform mobile shell** card explicit rather than letting the two lanes drift back together.
