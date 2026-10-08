# Design: Client App Surface Kit (`cargo appcheck`, `app-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust project’s supported **client-app surface**: app identities, bridge APIs, platform capabilities and permissions, lifecycle expectations, packaging/store assumptions, and evidence that the declared behavior still matches reality across desktop/mobile shells.

This should **not** replace Tauri, Dioxus, Slint, UniFFI, `flutter_rust_bridge`, `cargo-mobile2`, Xcode, Gradle, or app-store tooling.
It should make them compose better and make support claims reviewable.

## References (signals)
- Tauri’s current docs treat mobile as a first-class workflow with `tauri android dev` / `tauri ios dev`, device selection, IDE opening, and mobile-specific development caveats.
  https://v2.tauri.app/develop/
- Tauri’s plugin/capability docs show that client-app surfaces already span lifecycle hooks, Rust/Swift/Kotlin integration, window-specific capability files, platform-specific capabilities, and a broad official plugin set such as deep linking, notifications, biometrics, geolocation, haptics, NFC, updater, and storage.
  https://v2.tauri.app/develop/plugins/
  https://v2.tauri.app/plugin/
  https://v2.tauri.app/learn/security/capabilities-for-windows-and-platforms/
  https://v2.tauri.app/plugin/notification/
- `cargo-mobile2` explicitly generates Xcode and Android Studio project files, project boilerplate, device-run commands, IDE-opening flows, and template packs for multiple Rust UI/runtime stacks.
  https://docs.rs/crate/cargo-mobile2/latest
- Dioxus now positions itself as one codebase across web, desktop, and mobile and documents iOS/Android prerequisites plus store-distribution guidance.
  https://dioxuslabs.com/
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- Slint positions itself as a native GUI toolkit for embedded, desktop, and mobile with explicit platform docs and support tables.
  https://docs.slint.dev/latest/docs/slint/
  https://docs.slint.dev/latest/docs/slint/guide/platforms/desktop/
- UniFFI is explicitly about writing reusable Rust components once and consuming them from Kotlin/Swift/other languages, and its docs include Xcode integration/build-phase guidance.
  https://mozilla.github.io/uniffi-rs/latest/Motivation.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- `flutter_rust_bridge` is an active high-level Rust↔Flutter/Dart bridge with async Rust support, Rust-calls-Dart support, arbitrary-type handling, and codegen-driven quickstarts.
  https://docs.rs/crate/flutter_rust_bridge/latest

## Core components

### 1) `app-surface/v0`
A design-time declaration of the supported client-app boundary for a binary/workspace/product.

Required ideas:
- application identity
- official app flavors / channels / shells
- supported platforms:
  - windows
  - macos
  - linux
  - ios
  - android
  - web/wasm (optional attached lane, not assumed)
- support classes:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- linked attachments:
  - support envelopes
  - package/store profiles
  - bridge catalogs
  - capability profiles
  - lifecycle profiles
  - runtime settings refs
  - identity / diagnostic / observability refs
  - raw framework and platform manifests

Design rule: preserve **client-app support truth** separate from raw target-triple support truth. “Builds for iOS” is not the same thing as “officially supports iOS app behavior X/Y/Z.”

### 2) `bridge-catalog/v0`
Stable identities for how the shell/UI runtime communicates with Rust.

Each entry should support:
- stable bridge id
- bridge lane:
  - Tauri invoke/event/plugin API
  - direct Rust UI callback surface
  - UniFFI-generated Swift/Kotlin/Python bridge
  - Flutter/Dart bridge
  - custom FFI bridge
  - JS/webview bridge
- raw source artifact refs
- input/output schema refs where known
- threading / async / callback notes
- ownership/lifetime caveats when relevant
- support level
- review owner

Design rule: keep **bridge identity** separate from packaging/runtime identity. A binding generator or JS API surface is not the same thing as the app/package that embeds it.

### 3) `app-capability-profile/v0`
The platform features, permissions, and security/capability posture the app relies on.

Each profile should capture:
- stable capability-profile id
- linked app surface ids
- capability families such as:
  - notifications
  - deeplinks / URL handling
  - filesystem / storage
  - camera / barcode
  - biometrics
  - geolocation
  - haptics
  - NFC
  - background/foreground access
  - shell/process/network access
  - updater / installer actions
- platform-specific enablement/permission refs
- optional per-window / per-view scope
- requested vs required distinction
- user-consent / prompt notes
- unsupported / unchecked lanes

Design rule: keep **capabilities** separate from **bridge APIs** and separate from **store/package metadata**. “Uses notifications” is different from “exports bridge function `send_notification`.”

### 4) `app-lifecycle-profile/v0`
Lifecycle and entry-point assumptions for supported app surfaces.

Each profile should support:
- stable lifecycle-profile id
- startup/init assumptions
- foreground/background/suspend/resume notes
- single-instance or multi-window posture
- deeplink entry points
- push/notification entry points
- activity/scene/document-opening notes
- state restoration / persistence posture
- crash/restart/recovery notes when relevant
- linked capability and bridge ids

Design rule: keep lifecycle truth explicit. Desktop-only windows, mobile scenes/activities, deeplinks, and notification re-entry are not small implementation details.

### 5) `app-package-profile/v0`
Packaging, distribution, and signing posture for the client app.

Each profile should support:
- stable package-profile id
- package/bundle identifiers
- channel / flavor / store identity
- minimum OS/runtime refs where known
- signing/notarization/store-metadata refs
- packaging style:
  - direct bundle
  - installer
  - app store package
  - mobile package
  - side-loaded dev build
- updater posture
- linked release-pipeline attachments

Design rule: keep package/store truth separate from generic release artifacts. A CI release pack is not enough to tell reviewers what store/bundle/signing assumptions the client app needs.

### 6) `app-check-plan/v0`
A plan for validating that the declared client-app surface still behaves as claimed.

A plan should capture:
- selected platforms/devices/simulators/windows exercised
- bridges exercised
- capabilities and permission prompts exercised
- lifecycle transitions exercised
- deeplink / notification / updater scenarios exercised
- package/install smoke lanes when relevant
- illustrative-only or unsupported scenarios

Design rule: distinguish **surface checks** from generic UI screenshot tests or unit tests. This kit cares about supported app behavior and platform posture.

### 7) `app-check-report/v0`
Portable results from running the app checks.

A report should capture:
- app/package/build identity
- platforms/devices/simulators exercised
- capabilities exercised and permission outcomes
- lifecycle/deeplink/notification scenarios exercised
- bridges exercised
- failures and unsupported lanes
- linked raw logs/screenshots/videos/artifacts when appropriate
- verdicts with explicit confidence limits

Design rule: preserve raw platform truth as attachments. Do not flatten Android logs, iOS simulator traces, Tauri capability files, and codegen outputs into one fake generic transcript.

### 8) `app-pack/v0`
A review bundle containing:
- `app-surface/v0`
- zero or more `bridge-catalog/v0`
- zero or more `app-capability-profile/v0`
- zero or more `app-lifecycle-profile/v0`
- zero or more `app-package-profile/v0`
- optional package/install/check plans
- one or more `app-check-report/v0`
- raw attachments:
  - Tauri config/capability refs
  - AndroidManifest / Gradle refs
  - Info.plist / entitlements / Xcode refs
  - generated bindings refs
  - device/simulator logs
  - screenshots/video attachments when relevant

## Out of scope for v0
- inventing a new GUI toolkit
- replacing Xcode/Gradle/store portals
- inventing a universal permissions DSL that erases platform differences
- replacing Release Pipeline Kit, Support Envelope Kit, or Plugin Surface Kit
- pretending all app frameworks use the same lifecycle model

## Why this is high leverage
This kit would make it easier to:
- review mobile/desktop capability creep,
- diff bridge/API changes at the app boundary,
- hand off client apps across teams,
- track what was actually tested on which platforms,
- and survive framework churn because support truth lives above one toolkit.

It also creates a clean convergence point for Rust client-app work without forcing the ecosystem to pick one winner between webview shells, native Rust UIs, generated bindings, or Flutter/native host combinations.
