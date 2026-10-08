# Gap: Mobile app products still lack a reviewable boring default for shell/core/store truth

## The missing thing
Rust now has multiple real mobile stories, but the ecosystem still lacks a **reviewable boring default** for teams asking:
**how should we ship a real Android+iOS product with Rust in the core without turning every project into a custom mobile-toolchain negotiation?**

## Why the gap is real
Current signals all point to the same missing layer:
- Rust’s official challenges framing still names **choice paralysis** and **tacit knowledge** in ecosystem navigation.
- Tauri 2 is real on mobile, but its docs still make mobile dev-server setup, capabilities, permissions, and Kotlin/Swift plugin escape hatches explicit.
- Dioxus has made mobile much more real, but its docs still keep setup and bundling work visible rather than magical.
- Slint is now serious on mobile too, including recent iOS/Android safe-area and virtual-keyboard support.
- UniFFI gives production-quality Swift/Kotlin bindings, but the docs still show real Xcode/Gradle integration work.
- flutter_rust_bridge makes Rust↔Dart much more ergonomic, while Flutter itself still gives one of the clearest boring store-release paths.

The ecosystem therefore does **not** mainly lack “another mobile framework”.
It lacks a portable way to keep the following truths reviewable at once:
- which shell owns the UI/runtime,
- which logic lives in Rust,
- how the bridge is generated and renewed,
- how native/plugin escape hatches are handled,
- what permission/device capability surface exists,
- and how Android/iOS package/signing/store truth is carried.

## Why this deserves a maintained card instead of only a stack note
This project class recurs often.
Teams repeatedly ask some variant of:
- should we use Tauri mobile,
- Dioxus mobile,
- Slint,
- Flutter plus Rust,
- or native shells plus a Rust core?

Without a bounded maintained answer, guidance collapses back into vibes, team familiarity, or one impressive demo.
That is exactly the kind of tacit-knowledge failure the archive is trying to reduce.

## Proposed correction
Publish a maintained defaults-corpus card for **mobile-first app product** with:
- **Flutter shell + `flutter_rust_bridge`** as the conservative default for the narrow cross-platform/store-first scope;
- **native shell + UniFFI**, **Tauri 2 mobile**, **Dioxus mobile**, and **Slint mobile** as explicit serious alternatives;
- a receipt that keeps shell/runtime truth, Rust-core truth, bridge truth, native escape truth, permission truth, and store/package/signing truth visibly separate.

## References
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://v2.tauri.app/blog/tauri-20/
- https://v2.tauri.app/develop/
- https://v2.tauri.app/develop/plugins/develop-mobile/
- https://dioxuslabs.com/learn/0.7/getting_started/
- https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- https://docs.rs/crate/dioxus-mobile/latest
- https://docs.slint.dev/latest/docs/slint/
- https://slint.dev/blog/slint-1.15-released
- https://mozilla.github.io/uniffi-rs/
- https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
- https://cjycode.com/flutter_rust_bridge/quickstart
- https://docs.rs/crate/flutter_rust_bridge/latest
- https://docs.flutter.dev/deployment/android
- https://docs.flutter.dev/deployment/ios
- https://developer.android.com/guide/app-bundle
