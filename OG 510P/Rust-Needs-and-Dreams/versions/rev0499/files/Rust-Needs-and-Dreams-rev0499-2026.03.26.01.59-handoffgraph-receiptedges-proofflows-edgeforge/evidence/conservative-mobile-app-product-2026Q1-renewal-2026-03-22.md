# Renewal receipt: Conservative mobile app product (2026-03-22)

Card under review:
- `defaults/conservative-mobile-app-product-2026Q1.md`

Review goal:
- decide whether the archive should publish a first maintained **mobile-first app product** card;
- decide whether the clearest boring current default is **Flutter shell + Rust core via `flutter_rust_bridge`**;
- and keep shell/runtime truth, Rust-core truth, native escape truth, permission truth, and store/package/signing truth visibly separate.

## Canon import checked
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tauri 2 and mobile docs:
  https://v2.tauri.app/blog/tauri-20/
  https://v2.tauri.app/develop/
  https://v2.tauri.app/develop/plugins/develop-mobile/
  https://v2.tauri.app/security/capabilities/
  https://v2.tauri.app/learn/security/using-plugin-permissions/
- Dioxus mobile docs:
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/tutorial/bundle/
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
  https://docs.rs/crate/dioxus-mobile/latest
- Slint mobile docs:
  https://docs.slint.dev/latest/docs/slint/
  https://docs.slint.dev/latest/docs/slint/guide/platforms/
  https://slint.dev/blog/slint-1.15-released
- UniFFI guide:
  https://mozilla.github.io/uniffi-rs/
  https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
  https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
  https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
- flutter_rust_bridge docs:
  https://docs.rs/crate/flutter_rust_bridge/latest
  https://cjycode.com/flutter_rust_bridge/quickstart
  https://cjycode.com/flutter_rust_bridge/guides/concurrency/async-rust
- Flutter / Android release docs:
  https://docs.flutter.dev/deployment/android
  https://docs.flutter.dev/deployment/ios
  https://docs.flutter.dev/platform-integration
  https://docs.flutter.dev/packages-and-plugins/developing-packages
  https://developer.android.com/guide/app-bundle
  https://developer.android.com/studio/publish/app-signing

## Fresh observations
1. Official Rust signals still say the ecosystem navigation problem is partly about **choice paralysis** and **tacit knowledge**, which supports publishing a bounded mobile default rather than leaving the lane to folklore.
2. Tauri 2 is unquestionably a real mobile lane now, but its docs still make mobile-specific dev-server setup, capabilities, permissions, and Kotlin/Swift mobile plugin work explicit. That keeps it in the serious-alternative band rather than making it the boring default for the whole lane.
3. Dioxus mobile is substantially stronger than it used to be, but current docs still make setup friction, Android tooling, and store-signing/bundling steps visible enough that it should remain a serious alternative rather than the conservative default.
4. Slint is now a serious mobile lane too, including recent iOS/Android safe-area and virtual-keyboard improvements, but the evidence still reads more like a strong native/declarative alternative than the broadest boring store-first default.
5. UniFFI remains the strongest serious alternative when native Swift/Kotlin shells should own the product, but its own guide still reflects real native integration work rather than one cross-platform app shell.
6. `flutter_rust_bridge` plus Flutter currently gives the clearest combination of:
   - mainstream cross-platform mobile shell/runtime,
   - clear store-release guidance,
   - generated ergonomic Rust bindings,
   - and explicit room for native/plugin escape hatches.

## Slot-by-slot review
### Mobile shell/runtime truth
Defaulting to **Flutter** keeps the shell/runtime in a mainstream mobile product lane with clear Android+iOS deployment docs.
This is more honest for the bounded scope than pretending Rust must also own the widget/runtime layer.

### Rust-core / bridge truth
Defaulting to **`flutter_rust_bridge`** keeps the Rust boundary explicit and ergonomic.
Current docs are strong enough to support arbitrary types, async Rust, and Rust-calls-Dart as real lane features rather than edge claims.

### Native escape truth
The lane still needs explicit native/plugin escape hatches.
This is not a weakness of the card; it is part of the lane truth.
The card should therefore name platform plugins and native code as first-class escapes instead of promising bridge-only purity.

### Permission / device-capability truth
Mobile permissions and device APIs remain product truth.
Neither Flutter nor Rust alone erases that reality, so the card must keep permissions explicit and avoid flattening them into “framework support.”

### Store/package/signing truth
The Android App Bundle and app-signing docs, plus Flutter’s iOS release guide, make clear that package/signing/store behavior is not optional release trivia.
That supports keeping store/package/signing posture as a first-class part of the lane.

## Serious alternatives retained
- **native shell + UniFFI** — strongest alternative when native ownership is strategic.
- **Tauri 2 mobile** — strongest alternative when webview + capability/plugin model fits.
- **Dioxus mobile** — strongest Rust-first app-framework alternative today.
- **Slint mobile** — strongest native/declarative alternative for a narrower app class.

## Judgment
Publish the card as a maintained public default.

Label:
- **default-with-caveats**

Why:
- the project class recurs often;
- the corpus still lacked a maintained mobile-first product answer;
- and the evidence supports a bounded conservative default without pretending the entire mobile lane has converged.

## Replay notes
- renew when Dioxus mobile, Slint mobile, or Tauri mobile changes enough to move the boring default for this scope;
- renew when Flutter or `flutter_rust_bridge` changes enough to alter shell/core boundary guidance;
- split the lane when the archive is ready for a separate **native shell + Rust core** card or a separate **Rust-first mobile UI** card.
