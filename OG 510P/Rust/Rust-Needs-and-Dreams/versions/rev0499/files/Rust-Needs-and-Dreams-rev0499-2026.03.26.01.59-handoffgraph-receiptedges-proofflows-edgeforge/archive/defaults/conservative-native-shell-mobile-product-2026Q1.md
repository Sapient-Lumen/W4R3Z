# Default card: Conservative native-shell mobile product (2026 Q1)

Latest renewal receipt: `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- mobile-first app products intended for real Android and iOS users;
- teams that want **native app shells on both platforms** rather than one shared cross-platform UI runtime;
- teams that want a **shared Rust core** for meaningful logic, not just tiny helper functions;
- products where OS-framework depth, native look-and-feel, or existing Swift/Kotlin ownership matters enough to keep the shell native.

Assumptions:
- stable Rust;
- Android + iOS are both first-class supported targets;
- the team wants the clearest boring default for a **native-shell** mobile architecture;
- Rust is expected to own meaningful business/domain/protocol/data/media/crypto/sync logic;
- platform-native code remains acceptable and should stay explicit.

This is **not** the default for:
- teams that want one shared cross-platform shell/runtime;
- teams that want Rust to own the UI layer itself;
- narrow internal library/component work with no full product shell;
- or products where webview, Flutter, or pure-Rust UI ownership is the actual center.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

UniFFI is now explicit enough to support a real native-mobile lane rather than vague “bindings are possible” folklore:
- the guide says UniFFI generates foreign-language bindings targeting Rust libraries;
- Swift bindings are documented as production-quality and have a concrete generated-surface story;
- Xcode integration is documented as real build-phase work;
- Kotlin/Android integration is documented as real Gradle/build-source integration work;
- Kotlin lifetime/resource behavior is documented and explicitly requires `close()`/`AutoCloseable` handling for exposed interfaces;
- and UniFFI’s motivation docs are explicit that it is **not** an end-to-end Android/iOS packaging solution.
https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
https://mozilla.github.io/uniffi-rs/latest/kotlin/lifetimes.html
https://mozilla.github.io/uniffi-rs/latest/Motivation.html

UniFFI’s design principles also make the lane’s philosophy legible: safety first, idiomatic foreign-language bindings, and generated code that should remain debuggable rather than magical. That is a good fit for a boring default card.
https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html

On Android, `cargo-ndk` now gives a clearer boring build helper for Rust→NDK cross compilation and `jniLibs` layout than hand-managed NDK environment folklore.
https://docs.rs/crate/cargo-ndk/latest

For this exact project class, the archive’s current answer is:
**use native Swift/Kotlin shells and put serious shared logic in Rust behind UniFFI-generated bindings; keep Xcode and Gradle/build truth explicit; and escalate to the cross-platform mobile card, Tauri mobile, Dioxus mobile, Slint mobile, or hand-written FFI when the architecture wants a different runtime contract.**

## Decision label
**default-with-caveats**

It is the clearest boring default for this narrow scope, but the lane stays honest only if it keeps Android/iOS build/package work, native-shell ownership, and resource/lifetime caveats visible.

## Default lane summary
### Default lane
- mobile shell/runtime: **native platform shells (Swift/SwiftUI/UIKit on iOS; Kotlin/Android-native UI on Android)**
- Rust boundary posture: **Rust core via UniFFI-generated Swift and Kotlin bindings**
- Android build posture: **cross-build Rust artifacts explicitly, with `cargo-ndk` as the boring helper when appropriate**
- iOS build posture: **compile Rust as a library and integrate it into Xcode with generated bindings/modulemap/header truth kept explicit**
- lifetime/resource posture: **treat generated object/resource ownership as part of the product contract, not as invisible GC magic**
- support posture: **ship only the OS versions, frameworks, device classes, and background/capability behaviors the team is willing to support explicitly**

### Serious alternatives
- **Flutter shell + `flutter_rust_bridge`** when one shared cross-platform shell is the real point.
- **Tauri 2 mobile** when a webview-hosted shell is acceptable and the team already has strong web assets.
- **Dioxus mobile** or **Slint mobile** when the team wants Rust to own much more of the UI/runtime layer.
- **hand-written FFI or language-specific bindings** when only one foreign language matters or tighter bridge control is strategic.

### Watch / not-default here
- **the existing cross-platform mobile card** (`defaults/conservative-mobile-app-product-2026Q1.md`) reused as if it also answered the native-shell question.
- **polyglot component guidance** mistaken for full productization guidance.
- **Rust mobile** treated as one architecture rather than several materially different lanes.

## Slot guidance
### Native-shell slot
Prefer **real native shells on both platforms** when OS-framework depth, native UX, or existing platform-team ownership is central.
Do not hide this under “mobile Rust”; the shell ownership should stay explicit.

### Rust-core slot
Prefer **UniFFI** when one Rust core should be exposed to both Swift and Kotlin with a higher-level generated surface rather than hand-written low-level FFI glue.
Keep the boundary narrow and meaningful: domain logic, protocol logic, parsing, storage, search, media, crypto, sync, or other logic that benefits from Rust.
Do not start by dragging every UI concern through Rust.

### Android-build slot
Treat Android build/package truth as first-class.
Cross-compilation, ABI targets, artifact placement, and app packaging are real product truths.
Use `cargo-ndk` as the boring helper when it fits, but do not pretend it solves the whole Android app story.

### iOS-build slot
Treat iOS build/package truth as first-class.
The Rust library artifact, generated headers/modulemaps/Swift sources, and Xcode build phases are part of the lane contract.
Do not reduce them to “later release engineering.”

### Lifetime/resource slot
Keep UniFFI-generated resource/lifetime behavior explicit.
In Kotlin especially, generated wrappers expose `close()` / `AutoCloseable` rather than pretending finalizers solve ownership.
Do not let resource cleanup become tribal knowledge.

## Serious alternatives and when they win
### Flutter shell + `flutter_rust_bridge` wins when
- one shared cross-platform shell/runtime is the point;
- the team wants one main UI codebase;
- and plugin/runtime/distribution simplicity beats native-shell fidelity.

### Tauri 2 mobile wins when
- a webview shell is acceptable;
- the team already has strong web frontend assets or expertise;
- and Tauri’s capability/plugin model fits the product better than a native shell.

### Dioxus mobile or Slint mobile wins when
- the team wants Rust to own much more of the UI/runtime layer;
- one-codebase identity matters enough to accept the current runtime/tooling tradeoffs;
- or the product specifically wants those frameworks’ renderer/runtime contracts.

### Hand-written FFI wins when
- only one foreign language matters;
- tighter performance or boundary control is strategic;
- or UniFFI’s generated surface is the wrong abstraction for the app.

## Escalate to a project-specific brief when
- only one platform is strategically central and the other is secondary;
- deep background execution, device-framework integration, or OS-policy constraints dominate architecture;
- the team is deciding among native shell + UniFFI, Flutter + `flutter_rust_bridge`, Tauri mobile, Dioxus mobile, or Slint because the product genuinely spans more than one lane assumption;
- or signing/store/compliance constraints dominate the architecture.

## Canonical references
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
