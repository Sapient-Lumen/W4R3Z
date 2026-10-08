# Design: Mobile app product default lane (shell/core boundary + store/package truth + permission/native-escape truth)

## Goal
Add the first maintained **mobile-first app-product** defaults-corpus card so the archive can answer a recurring practical question:
**what should a serious Rust-involving mobile product normalize around right now if the team wants the clearest boring default?**

This lane should not replace the broader `design/client-productization-stack.md`.
It should give that stack one bounded maintained answer for a very common project class.

## Why this note is needed now
The archive already had a desktop-product card and a polyglot-component card, but it still lacked a maintained answer for **real Android+iOS app products**.
That omission is harder to justify now because:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated workflows rise;
- Tauri 2 is now stable across desktop and mobile, but its mobile docs still make explicit that the app shell, plugin boundary, capabilities/permissions, and dev-server/device posture are real moving parts rather than one invisible “works everywhere” button;
- Dioxus now has first-party mobile tooling and a stronger one-codebase story, but its current docs still make clear that mobile setup and bundling remain non-trivial, especially on Android;
- Slint is a serious native/declarative lane and continues to improve mobile-specific behavior, but that does not yet make it the obvious boring default for general store-first cross-platform mobile products;
- UniFFI explicitly gives production-quality Swift and Kotlin bindings, but its own docs still show that native-shell integration means handoff work in Xcode and Gradle rather than one unified mobile-product toolchain;
- flutter_rust_bridge now exposes a much more ergonomic Rust↔Dart bridge, including arbitrary types, async Rust, and Rust-calls-Dart support;
- and Flutter’s own mobile deployment docs still provide one of the clearest boring app-store paths for Android and iOS.

Together those signals say the next worthy move is **not** another framework shootout or a generic “Rust on mobile” essay.
It is a bounded boring default card.

## Chosen project class
The first mobile card should cover:
- mobile-first products intended for real Android and iOS users;
- teams that want one cross-platform mobile shell and a reviewable way to put serious core logic in Rust;
- products where store packaging, signing, native plugin escape hatches, async/device APIs, and long-lived support posture matter alongside UI code;
- teams willing to keep the mobile UI/runtime in a mainstream mobile shell if that buys clearer productization.

It should **not** try to cover in one card:
- native-shell-per-platform products where Swift/Kotlin ownership is the whole point;
- pure-Rust UI ambition as a first principle;
- desktop-first client products that only later sprout mobile ambitions;
- narrow shared-library/component lanes with no product shell;
- or game/graphics-intensive lanes where neither Flutter nor the current Rust UI stacks are the real center.

## Default thesis
For this bounded project class, the conservative default should currently be:

**Flutter for the mobile shell and distribution path + Rust core via `flutter_rust_bridge`**, with explicit shell/core boundaries, explicit native escape hatches, explicit store/package truth, and explicit ownership of what remains in Dart or platform code.

Why this is the right first card:
- Flutter’s docs give a very legible, boring release path for Android and iOS.
- `flutter_rust_bridge` gives the clearest currently maintained high-level binding story for pairing that shell with Rust logic.
- This lane stays honest about reality: the UI/runtime, plugin ecosystem, store packaging, and many platform integrations still live primarily outside Rust.
- It also keeps the archive from pretending that “Rust mobile” has already converged on one all-Rust UI story.

## Serious alternatives that must stay visible
### 1. Native shell + UniFFI
This wins when native platform look-and-feel, OS framework access, or Swift/Kotlin team ownership is central.
It should remain the strongest serious alternative for teams that want Rust to be the shared core but do **not** want a cross-platform UI shell.

### 2. Tauri 2 mobile
This wins when a webview-hosted shell is acceptable, the team already has a strong web frontend, and the product benefits from Tauri’s capability/plugin model.
It should stay a serious alternative, but not the boring default for the whole mobile lane.

### 3. Dioxus mobile
This wins when the team wants a Rust-first UI/application framework and accepts current mobile setup/bundling/tooling realities.

### 4. Slint mobile
This wins when native/declarative UI and shared embedded/desktop/mobile continuity are central enough to drive the lane.

## What the card must keep separate
The maintained card should visibly preserve:
- **mobile shell/runtime truth**;
- **Rust core / bridge truth**;
- **native escape-hatch truth**;
- **permission / device-capability truth**;
- **store/package/signing truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Non-goals
- picking one Rust-only mobile UI framework for all products;
- pretending mobile-first app productization is the same as a generic polyglot component;
- pretending store release, signing, permissions, and device APIs are merely a footnote to widget code;
- or turning the corpus into a cross-ecosystem mobile-framework scoreboard.

## Archive implications
- Add a first maintained mobile-product card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **mobile-first app product** as a maintained public lane distinct from both **desktop app product** and **polyglot workspace component**.
- Keep future narrower cards available, especially **native-shell mobile with UniFFI** and **Rust-first mobile UI** if the evidence warrants them later.

## Archive implication
The archive should therefore keep this lane distinct from the now-maintained **native-shell mobile product** card rather than treating UniFFI/native shells as only an alternative bullet.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tauri 2 stable release:
  https://v2.tauri.app/blog/tauri-20/
- Tauri mobile develop guide:
  https://v2.tauri.app/develop/
- Tauri mobile plugin development:
  https://v2.tauri.app/develop/plugins/develop-mobile/
- Tauri capabilities / permissions:
  https://v2.tauri.app/security/capabilities/
  https://v2.tauri.app/learn/security/using-plugin-permissions/
- Dioxus getting started / mobile setup / bundle/deploy:
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/tutorial/bundle/
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
  https://docs.rs/crate/dioxus-mobile/latest
- Slint overview / mobile docs / recent mobile release work:
  https://docs.slint.dev/latest/docs/slint/
  https://docs.slint.dev/latest/docs/slint/guide/platforms/
  https://slint.dev/blog/slint-1.15-released
- UniFFI overview / Swift / Kotlin integration:
  https://mozilla.github.io/uniffi-rs/
  https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
- flutter_rust_bridge docs / quickstart / crate docs:
  https://cjycode.com/flutter_rust_bridge/quickstart
  https://cjycode.com/flutter_rust_bridge/guides/concurrency/async-rust
  https://docs.rs/crate/flutter_rust_bridge/latest
- Flutter mobile deployment / plugin docs:
  https://docs.flutter.dev/deployment/android
  https://docs.flutter.dev/deployment/ios
  https://docs.flutter.dev/platform-integration
  https://docs.flutter.dev/packages-and-plugins/developing-packages
- Android app bundle / signing docs:
  https://developer.android.com/guide/app-bundle
  https://developer.android.com/studio/publish/app-signing
