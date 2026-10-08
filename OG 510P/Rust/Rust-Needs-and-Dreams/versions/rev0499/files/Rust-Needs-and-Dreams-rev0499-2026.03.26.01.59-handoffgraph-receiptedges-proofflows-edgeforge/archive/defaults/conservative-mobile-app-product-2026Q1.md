# Default card: Conservative mobile app product (2026 Q1)

Latest renewal receipt: `evidence/conservative-mobile-app-product-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- mobile-first app products intended for real Android and iOS users;
- teams that want one cross-platform mobile UI shell plus a reviewable way to put serious logic in Rust;
- products where store packaging, signing, permissions, plugins, device APIs, and support posture matter alongside widget code;
- teams willing to keep the mobile shell outside Rust when that buys a clearer boring product path.

Assumptions:
- stable Rust;
- Android + iOS are both first-class supported targets;
- the team wants the clearest boring default rather than a pure-Rust UI as a first principle;
- the Rust core is expected to own meaningful business logic, data/model logic, protocol logic, or performance-sensitive work;
- native escape hatches are acceptable and should stay explicit.

This is **not** the default for:
- teams that want native Swift/Kotlin shells as a first principle — see `defaults/conservative-native-shell-mobile-product-2026Q1.md`;
- teams that want Rust to own the UI layer itself;
- desktop-first products with only a future mobile ambition;
- narrow shared-library/component work with no product shell;
- or graphics/game-style products where this lane is not the real center.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Tauri 2 is real on mobile and explicitly targets iOS and Android, but its own docs keep mobile development, device-host networking, capabilities, permissions, and Kotlin/Swift mobile plugin work visible rather than magical.
https://v2.tauri.app/blog/tauri-20/
https://v2.tauri.app/develop/
https://v2.tauri.app/develop/plugins/develop-mobile/
https://v2.tauri.app/security/capabilities/
https://v2.tauri.app/learn/security/using-plugin-permissions/

Dioxus is now much stronger on mobile, with first-party CLI support and one-codebase ambition, but its docs still keep platform setup, Android toolchain friction, and store-signing steps explicit enough that this lane should remain cautious about calling it the boring default for general mobile products.
https://dioxuslabs.com/learn/0.7/getting_started/
https://dioxuslabs.com/learn/0.7/tutorial/bundle/
https://dioxuslabs.com/learn/0.7/tutorial/deploy/
https://docs.rs/crate/dioxus-mobile/latest

Slint is a serious native/declarative alternative and continues to improve mobile-specific behavior, but that still does not automatically make it the boring default for general store-first cross-platform mobile products.
https://docs.slint.dev/latest/docs/slint/
https://docs.slint.dev/latest/docs/slint/guide/platforms/
https://slint.dev/blog/slint-1.15-released

UniFFI gives production-quality Swift and Kotlin bindings and remains the strongest route when native shells should own the product, but its own guide still shows real Xcode and Gradle integration work rather than one unified app-product story.
https://mozilla.github.io/uniffi-rs/
https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html

`flutter_rust_bridge` now gives the clearest high-level Rust↔Dart binding story for a cross-platform mobile shell: arbitrary Rust/Dart types, async Rust, and Rust-calls-Dart support are all explicit in current docs.
Flutter itself still provides one of the clearest boring mobile deployment stories to Google Play and the App Store.
https://docs.rs/crate/flutter_rust_bridge/latest
https://cjycode.com/flutter_rust_bridge/quickstart
https://cjycode.com/flutter_rust_bridge/guides/concurrency/async-rust
https://docs.flutter.dev/deployment/android
https://docs.flutter.dev/deployment/ios
https://docs.flutter.dev/platform-integration
https://developer.android.com/guide/app-bundle
https://developer.android.com/studio/publish/app-signing

For this exact project class, the archive’s current answer is:
**use Flutter as the conservative mobile shell/distribution path and put serious Rust logic behind `flutter_rust_bridge`; keep the shell/core boundary explicit; and escalate to native shell + UniFFI, Tauri mobile, Dioxus mobile, or Slint mobile when the product wants a meaningfully different runtime contract.**

## Decision label
**default-with-caveats**

It is the clearest boring default for this narrow scope, but the mobile ecosystem is plural enough — and app-store reality concrete enough — that the default must stay explicit about what it is *not* covering.

## Default lane summary
### Default lane
- mobile shell/runtime: **Flutter**
- Rust boundary posture: **Rust core via `flutter_rust_bridge`**
- native escape posture: **explicit platform plugins/channels when needed; do not pretend every device API should flow through the bridge first**
- packaging/distribution posture: **Android App Bundle / Play signing path + iOS App Store/TestFlight path remain first-class truths, not afterthoughts**
- permission posture: **treat Android/iOS permissions plus any shell/plugin-specific capabilities as part of the product contract**
- support posture: **ship only the OS versions, device classes, and plugin/device features the team is willing to support explicitly**

### Serious alternatives
- **native shell + UniFFI** when native platform fidelity, OS-framework depth, or Swift/Kotlin ownership dominates; see `defaults/conservative-native-shell-mobile-product-2026Q1.md`.
- **Tauri 2 mobile** when a webview-hosted shell is acceptable and the team already has a strong web frontend.
- **Dioxus mobile** when the team wants a Rust-first app framework and accepts current tooling/setup realities.
- **Slint mobile** when native/declarative UI or embedded/desktop/mobile continuity drives the lane.

### Watch / not-default here
- **pure-Rust mobile UI** as a universal answer.
- **desktop-first Tauri or Dioxus guidance** silently reused for mobile-first products.
- **polyglot component guidance** mistaken for full productization guidance.

## Slot guidance
### Shell/runtime slot
Prefer **Flutter** when the team wants the clearest boring path for one cross-platform mobile shell, release tooling, and mainstream plugin/distribution posture.
Do not hide this choice under “Rust mobile”; the shell ownership should be explicit.

### Rust-core slot
Prefer **`flutter_rust_bridge`** when the Rust core should expose an ergonomic boundary to Dart without hand-writing low-level FFI glue.
Keep the boundary narrow and meaningful: domain logic, protocol logic, parsing/crypto/search/data work, or other logic that benefits from Rust.
Do not start by piping every tiny widget concern through Rust.

### Native escape slot
Keep platform plugins and native code as explicit escape hatches.
If the product depends heavily on platform frameworks, background services, or device-specific integrations, name that early.
Do not pretend the bridge erases native ownership.

### Package/store slot
Treat Android/iOS packaging and signing as part of the lane contract.
The Android App Bundle, Play signing/update rules, Xcode/App Store/TestFlight flow, and store-review constraints are real product truths.
Do not reduce them to “later release engineering.”

### Permission/device-capability slot
Permissions and device APIs are product truth.
Track what is handled by Flutter plugins, what is owned by Rust, and what needs explicit native implementation.
Avoid turning capability posture into scattered comments or tribal memory.

## Serious alternatives and when they win
### Native shell + UniFFI wins when
- the team wants true native platform ownership;
- deep OS-framework integration or native look-and-feel dominates;
- or the org already has strong Swift/Kotlin ownership and wants Rust only as a shared core.

### Tauri 2 mobile wins when
- a webview shell is acceptable;
- the team already has strong web frontend assets or expertise;
- and Tauri’s capability/plugin model fits the product better than a Flutter shell.

### Dioxus mobile wins when
- the team wants a Rust-first app framework;
- one-codebase identity matters enough to accept current setup/bundling friction;
- and the product can live with the current renderer/runtime contract.

### Slint mobile wins when
- native/declarative UI is central;
- embedded/desktop/mobile continuity matters;
- or the team specifically wants Slint’s UI language/runtime shape.

## Escalate to a project-specific brief when
- native platform ownership is strategic enough to beat the cross-platform shell default;
- accessibility, offline/background execution, or device-framework depth becomes the main driver;
- the team is deciding among Flutter+Rust, native shell+UniFFI, Tauri mobile, Dioxus mobile, and Slint because the product genuinely spans more than one lane assumption;
- or store/review/enterprise distribution constraints dominate the architecture.

## Canonical references
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
- Dioxus getting started / bundle / deploy / mobile crate docs:
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/tutorial/bundle/
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
  https://docs.rs/crate/dioxus-mobile/latest
- Slint overview / platforms / release notes:
  https://docs.slint.dev/latest/docs/slint/
  https://docs.slint.dev/latest/docs/slint/guide/platforms/
  https://slint.dev/blog/slint-1.15-released
- UniFFI overview / Swift / Kotlin:
  https://mozilla.github.io/uniffi-rs/
  https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
- flutter_rust_bridge docs:
  https://docs.rs/crate/flutter_rust_bridge/latest
  https://cjycode.com/flutter_rust_bridge/quickstart
  https://cjycode.com/flutter_rust_bridge/guides/concurrency/async-rust
- Flutter deployment / platform integration / plugins:
  https://docs.flutter.dev/deployment/android
  https://docs.flutter.dev/deployment/ios
  https://docs.flutter.dev/platform-integration
  https://docs.flutter.dev/packages-and-plugins/developing-packages
- Android app bundle / signing docs:
  https://developer.android.com/guide/app-bundle
  https://developer.android.com/studio/publish/app-signing

## Renewal inputs
Recheck before renewal:
- whether Flutter+`flutter_rust_bridge` remains the clearest boring cross-platform/store-first mobile default;
- whether native shell + UniFFI should become the conservative default for a narrower but more central mobile-first scope;
- whether Dioxus mobile or Slint mobile changes enough to justify a narrower Rust-first mobile card;
- whether Tauri mobile’s productization story becomes strong enough to challenge this card for webview-acceptable products;
- whether store/distribution/signing guidance materially shifts on Android or iOS;
- whether the card should split into **cross-platform mobile shell + Rust core** versus **native shell + Rust core**.

## Non-goals
This card is not:
- a universal mobile-framework verdict;
- a claim that Flutter is “the Rust mobile ecosystem”;
- a replacement for project-specific accessibility/store/distribution review;
- or permission to smuggle huge product-specific native/plugin complexity into a public default.
