# Design: Native-shell mobile product default lane (native OS shell truth + Rust-core truth + binding-generation truth + build/package truth)

## Goal
Add the first maintained **native-shell mobile product** defaults-corpus card so the archive can answer a recurring practical question:
**what should a serious Android+iOS product normalize around right now if Swift/Kotlin should own the app shell and Rust should be the shared engine?**

This lane should not replace the broader `design/client-productization-stack.md` or `design/polyglot-productization-stack.md`.
It should give the corpus one bounded maintained answer for a common project class that the existing cross-platform mobile card explicitly excluded.

## Why this note is needed now
The archive already has a maintained **mobile app product** card.
But that card is intentionally scoped to the “one cross-platform shell plus Rust core” shape and currently picks **Flutter + `flutter_rust_bridge`** as the conservative answer for that narrower scope.

That leaves a still-central practical question unanswered:
- what should teams do when they want **real native Swift / SwiftUI / UIKit ownership on iOS**,
- **real native Kotlin / Jetpack Compose / Android-framework ownership on Android**,
- and **shared Rust domain/protocol/engine code** underneath?

That omission is harder to justify now because:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises;
- UniFFI now has mature, explicit Swift and Kotlin guidance rather than only vague “mobile bindings are possible” folklore;
- UniFFI’s own design principles still reflect real mobile consumers, safety-first posture, and generated code that should remain readable and debuggable rather than magical;
- the Swift lane is now concrete enough to review: generated Swift API surface, modulemap/header split, Xcode integration, and even `uniffi-bindgen-swift` support for XCFramework-compatible modulemaps are all explicit;
- the Kotlin lane is also concrete enough to review: current configuration, Android-specific options, Gradle integration, and explicit lifetime/`close()` behavior are all documented;
- UniFFI itself is explicit that it is **not** an end-to-end Android/iOS packaging story, which is actually a strength for a bounded default card because it keeps build/package truth visible;
- `cargo-ndk` gives Android cross-build/setup a more reviewable boring path than hand-managed NDK environment folklore;
- and the archive’s mobile map is now mature enough that “cross-platform shell” and “native shell” are clearly different lanes rather than one umbrella story.

Together these signals say the next worthy move is **not** another generic mobile-framework comparison.
It is a bounded boring default card for the native-shell mobile lane.

## Chosen project class
The first native-shell mobile card should cover:
- mobile-first products where **iOS and Android are both first-class**;
- teams that want the app shell to be **owned natively per platform** rather than forced through one cross-platform UI runtime;
- teams that want a **shared Rust core** for meaningful logic: protocol, parsing, sync, storage, crypto, search, model, media, offline, or performance-sensitive work;
- products where platform-framework depth, native feel, or existing Swift/Kotlin ownership matters enough to reject a shared-shell default.

It should **not** try to cover in one card:
- one-shell cross-platform app products where Flutter or another shared UI runtime is the actual center;
- Rust-owned UI on mobile;
- narrow internal library/component work with no app-shell ownership;
- or native-ABI-only interop where hand-written C FFI is deliberately the point.

## Default thesis
For this bounded project class, the conservative default should currently be:

**native Swift/Kotlin shells + Rust core via UniFFI-generated bindings**

with explicit acceptance that:
- the iOS and Android app shells remain first-class owned products;
- Rust is the shared engine, not the UI ideology;
- UniFFI owns the high-level binding surface, but not the whole packaging story;
- Xcode and Gradle/Android Studio integration remain part of the lane truth;
- and Android/iOS build/distribution details must stay visible rather than hidden behind “mobile Rust” branding.

Why this is the right first card:
- UniFFI is the clearest documented path for one Rust core exposed to both Swift and Kotlin.
- Its docs are explicit about the generated-language surface, integration steps, and safety/ownership tradeoffs.
- It keeps the shell/core split honest: generated bindings are separate from native app/package setup.
- It leaves room for platform-native UX, OS framework integration, background execution, and policy/compliance differences without pretending one runtime erases them.
- It complements rather than displaces the existing Flutter-first mobile card.

## Serious alternatives that must stay visible
### 1. Flutter shell + `flutter_rust_bridge`
This wins when one shared cross-platform shell and plugin/runtime story is the point.

### 2. Tauri mobile
This wins when a webview shell is acceptable and the team already has strong web frontend assets.

### 3. Dioxus mobile or Slint mobile
These win when the team wants Rust to own far more of the app/UI layer and accepts the current runtime/tooling tradeoffs.

### 4. Hand-written FFI or language-specific binding layers
This wins when only one foreign language matters, when tighter control/performance over the bridge is strategic, or when UniFFI’s generated surface is the wrong abstraction.

## What the card must keep separate
The maintained card should visibly preserve:
- **native app-shell truth**;
- **Rust-core ownership truth**;
- **binding-generation truth**;
- **iOS build/package truth**;
- **Android build/package truth**;
- **resource/lifetime/threading truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Non-goals
- declaring UniFFI the universal best Rust FFI tool;
- pretending native-shell mobile has converged into one build/package command;
- hiding Xcode/Gradle/build-signing reality behind binding generation;
- or flattening native-shell mobile back into the cross-platform-shell mobile lane.

## Archive implications
- Add a first maintained native-shell-mobile card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **cross-platform mobile shell** and **native-shell mobile product** as distinct maintained client lanes.
- Keep future narrower cards available, especially **Android-first native Rust shell**, **iOS-first native Rust framework**, or **hand-written mobile FFI** if later evidence warrants them.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- UniFFI getting started / motivation / design principles:
  https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
  https://mozilla.github.io/uniffi-rs/latest/Motivation.html
  https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html
- UniFFI Swift bindings / Xcode / Swift module / Swift bindgen:
  https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  https://mozilla.github.io/uniffi-rs/latest/swift/module.html
  https://mozilla.github.io/uniffi-rs/next/swift/uniffi-bindgen-swift.html
- UniFFI Kotlin configuration / Gradle / lifetimes:
  https://mozilla.github.io/uniffi-rs/latest/kotlin/configuration.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/lifetimes.html
- `cargo-ndk`:
  https://docs.rs/crate/cargo-ndk/latest
- Existing cross-platform mobile card for contrast:
  ./mobile-app-product-default-lane.md
