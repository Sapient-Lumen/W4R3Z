# Epic proposal: Client App Surface Kit

## Thesis
Rust’s client-app ecosystem is now strong enough that the missing contribution is no longer “yet another desktop/mobile UI framework” or “yet another bridge generator.”
The higher-leverage missing piece is a **portable client-app contract** that lets teams declare, diff, validate, and ship what a Rust-powered desktop/mobile application actually promises: app identities, bridge APIs, platform capabilities/permissions, lifecycle assumptions, packaging/store posture, and checked per-platform behavior.

In other words: Rust needs a boring, attachable `app-pack/v0` more than it needs one more app shell novelty crate.

## Why now
The ecosystem signals line up:
- Tauri has real desktop/mobile development flows, plugin ecosystems, capability files, and distribution guidance.
- Dioxus now explicitly spans web/desktop/mobile and is trying to make native distribution easier.
- Slint is now a serious native GUI lane across embedded/desktop/mobile.
- UniFFI and `flutter_rust_bridge` show that “Rust core + native/Flutter shell” is a real production pattern, not a thought experiment.
- `cargo-mobile2` already bridges Rust projects into Xcode/Android Studio/device flows.

The hard part is increasingly not “can Rust reach Android/iOS/desktop?” but “what exactly does this app officially support on each platform, and what evidence do we have?”

Sources:
- https://v2.tauri.app/develop/
- https://v2.tauri.app/develop/plugins/
- https://v2.tauri.app/plugin/
- https://v2.tauri.app/learn/security/capabilities-for-windows-and-platforms/
- https://docs.rs/crate/cargo-mobile2/latest
- https://dioxuslabs.com/
- https://dioxuslabs.com/learn/0.7/getting_started/
- https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- https://docs.slint.dev/latest/docs/slint/
- https://docs.slint.dev/latest/docs/slint/guide/platforms/desktop/
- https://mozilla.github.io/uniffi-rs/latest/Motivation.html
- https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- https://docs.rs/crate/flutter_rust_bridge/latest

## What should be built
A first credible version should ship:
1. `app-surface/v0`, `bridge-catalog/v0`, `app-capability-profile/v0`, `app-lifecycle-profile/v0`, `app-package-profile/v0`, `app-check-plan/v0`, `app-check-report/v0`, and `app-pack/v0`
2. adapters for at least:
   - one Tauri lane
   - one native-Rust UI lane (`dioxus` or `slint`)
   - one generated-bridge lane (`uniffi` or `flutter_rust_bridge`)
3. docs/reference generation for supported platforms, capabilities, permissions, deeplinks, notifications, bridge APIs, and package/store assumptions
4. validation/reporting for capability drift, package-identifier drift, lifecycle regressions, missing permission handling, and unchecked platform lanes
5. examples showing packs attached to:
   - a desktop+mobile Tauri app
   - a Dioxus or Slint app
   - a Rust core consumed by Swift/Kotlin via UniFFI
   - a Flutter app backed by Rust through `flutter_rust_bridge`

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one Tauri pilot proving capability files, plugin inventory, and window/platform scope need durable review artifacts above `tauri.conf.json`
- one Dioxus or Slint pilot proving cross-platform app/package/lifecycle truth is worth exporting even when the UI is “mostly Rust”
- one UniFFI pilot proving generated bridge APIs and Xcode/Android host assumptions belong in explicit app-boundary artifacts
- one `flutter_rust_bridge` pilot proving Rust↔Dart API drift and async/threading assumptions deserve reviewable contracts
- one release pilot proving package/store/signing/channel truth must stay attached to the client app instead of living only in release notes or CI secrets

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve app surfaces, bridges, capabilities, lifecycle, and package/store posture as separate artifacts
2. **v0.2 adapters**
   - support one Tauri adapter, one native-Rust UI adapter, one generated-bridge adapter, and one manual/static lane
3. **v0.3 cross-kit integration**
   - integrate with Support Envelope, Release Pipeline, Runtime Settings, Identity Surface, Diagnostic Surface, Observability, and Plugin Surface workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact framework stack

## Success metrics
- Teams can review client-app changes as explicit artifacts instead of Android/iOS configs, generated bindings, framework glue, and tribal memory.
- Capability/permission creep becomes easier to detect before release.
- Platform support drift becomes easier to explain because app behavior lives above target triples.
- Bridge/API changes become easier to audit across Swift/Kotlin/JS/Dart/native shells.
- Rust client apps become easier to hand off because package/store/lifecycle/deeplink/notification truth stops living only in people’s heads.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Support Envelope Kit covers targets, build-hosts, docs surfaces, and runtime baselines,
- Plugin Surface Kit covers host/extension ecosystems,
- Runtime Settings Kit covers declared settings and precedence,
- Release Pipeline Kit covers publishing/installers/signatures/provenance,
- Identity Surface Kit covers auth/session/access behavior,
- and Command/Service/Event kits cover other interface classes.

But none of those is the portable contract for the **client app boundary itself**.
Client App Surface Kit is the missing substrate that keeps platform capabilities, lifecycle assumptions, bridge APIs, package/store posture, and checked device/platform evidence attached to one reviewable interface without absorbing the rest of the stack into one mega-format.
