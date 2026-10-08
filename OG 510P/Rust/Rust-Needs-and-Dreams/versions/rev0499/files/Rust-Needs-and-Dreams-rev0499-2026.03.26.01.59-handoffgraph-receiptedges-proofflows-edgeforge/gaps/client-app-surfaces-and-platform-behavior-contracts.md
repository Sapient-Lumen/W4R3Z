# Gap: client-app surfaces, platform capabilities, and reviewable app behavior contracts

## What is missing
Rust now has credible ways to power **desktop and mobile applications**:
- webview-based app shells with Rust backends,
- pure-Rust UI frameworks that target desktop and mobile,
- bridge generators for Swift/Kotlin and Flutter/Dart,
- project generators that open Xcode and Android Studio,
- and increasingly rich plugin/capability ecosystems for device features.

What it still lacks is a **boring, reviewable contract** for the supported client-app surface itself.

Today teams can separately:
- build an app shell with Tauri, Dioxus, Slint, or a native host,
- expose Rust functionality to JavaScript, Swift, Kotlin, or Dart,
- declare capabilities and permissions in platform-specific files,
- wire notifications, deeplinks, biometrics, geolocation, NFC, and storage,
- and package or sign binaries for stores or direct distribution.

But they still do not have one portable artifact saying:
- which client surfaces are officially supported,
- which platform capabilities and permissions are required,
- which bridge APIs the shell depends on,
- which lifecycle/deeplink/notification entry points are expected,
- what packaging/store/signing assumptions apply,
- and which parts were actually checked on which platforms/devices.

That means support truth still leaks across:
- `tauri.conf.json`, plugin capability files, and frontend glue,
- Android manifests, Gradle settings, and IDE project state,
- Info.plist / entitlements / Xcode build phases,
- codegen outputs from UniFFI or `flutter_rust_bridge`,
- README prose and release notes,
- and maintainer memory.

## Why this matters
Client apps are where Rust has to survive contact with the messy platform world:
- app-store packaging,
- code signing and notarization,
- lifecycle transitions,
- permissions and capability prompts,
- deeplinks and external intents,
- native notifications,
- bridge APIs between Rust and the shell/UI runtime,
- multi-window or multi-view surface differences,
- and device-specific development/debug flows.

Rust has tools for many of these pieces, but not yet a **shared review/evidence layer** above them.

That missing layer hurts in predictable ways:
- teams cannot easily diff what changed in the supported app surface,
- permission creep hides inside manifests or plugin additions,
- mobile/desktop behavior diverges silently,
- bridge APIs drift without one stable review artifact,
- and release archaeology becomes painful because app-store/package assumptions were never captured in one place.

## Evidence that the ecosystem is real enough
The point is no longer “Rust cannot do client apps.” The point is “Rust client-app support has enough moving parts that it now needs reviewable contracts.”

- Tauri’s current docs treat mobile development as a first-class flow (`tauri android dev`, `tauri ios dev`), support opening Xcode/Android Studio directly, and expose a large official plugin surface including deep links, notifications, biometrics, geolocation, haptics, NFC, storage, updater, and more.
  https://v2.tauri.app/develop/
  https://v2.tauri.app/plugin/
  https://v2.tauri.app/plugin/notification/
- Tauri’s security docs also make capabilities explicit and window/platform-specific, which is a strong signal that “what this app can do” is already a serious support boundary.
  https://v2.tauri.app/learn/security/capabilities-for-windows-and-platforms/
- `cargo-mobile2` explicitly positions itself as “the answer to how do I use Rust on iOS and Android?”, generates Xcode/Android Studio projects, and ships template packs for `wry`, `dioxus`, `egui`, `wgpu`, `winit`, and `bevy`.
  https://docs.rs/crate/cargo-mobile2/latest
- Dioxus now positions itself as a Rust framework for web, desktop, and mobile apps, with dedicated iOS/Android setup guidance and deployment guidance that reaches direct App Store / Play Store publication.
  https://dioxuslabs.com/
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- Slint’s current docs and site position it as a native GUI toolkit for embedded, desktop, and mobile, with explicit platform guides and tested desktop support tables.
  https://docs.slint.dev/latest/docs/slint/
  https://docs.slint.dev/latest/docs/slint/guide/platforms/desktop/
- UniFFI is explicitly motivated by writing reusable Rust components once and consuming them from Kotlin on Android and Swift on iOS; its guide includes Xcode integration steps for generated Swift bindings.
  https://mozilla.github.io/uniffi-rs/latest/Motivation.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- `flutter_rust_bridge` continues to evolve as a feature-rich Rust↔Flutter/Dart bridge with async Rust support, Rust-calls-Dart support, arbitrary-type handling, and a generated project quickstart.
  https://docs.rs/crate/flutter_rust_bridge/latest

## Why existing tools are not yet the whole answer
The ecosystem has **frameworks, bridges, generators, and plugins**, but not the **shared contract / capability / evidence layer**.

Tauri solves one class of application shell.
Dioxus and Slint solve other UI/runtime lanes.
UniFFI and `flutter_rust_bridge` solve different bridge/codegen lanes.
`cargo-mobile2` helps bootstrap device/IDE flows.
Store/signing guidance and OS permission systems remain external realities.

But teams still have to invent their own answers for:
- stable app-surface identities,
- stable bridge API identities,
- stable capability/permission profiles,
- explicit lifecycle/deeplink/notification assumptions,
- package/store/signing/channel truth,
- and diffable check reports proving what was actually exercised on which platform.

That is exactly the kind of missing substrate this archive is trying to identify.

## Target outcome
A project should be able to say:
- “these are the desktop/mobile app surfaces we officially support,”
- “these are the capabilities, permissions, and bridge APIs they rely on,”
- “these are the lifecycle and packaging assumptions,”
- and “this is the portable pack CI, release review, later archaeology, and platform migration work can consume.”

That is bigger than one bridge generator and smaller than a full new app framework.
