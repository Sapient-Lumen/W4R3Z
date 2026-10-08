# Epic proposal: Native-shell mobile product default lane

## Thesis
Add a maintained defaults-corpus card for **native-shell mobile products** so the archive can answer a common practical question with a bounded current recommendation instead of leaving the lane smeared across cross-platform-mobile guidance and generic polyglot theory.

## Proposed artifact family
- `design/native-shell-mobile-product-default-lane.md`
- `defaults/conservative-native-shell-mobile-product-2026Q1.md`
- `evidence/conservative-native-shell-mobile-product-2026Q1-renewal-2026-03-22.md`
- frontier/meta refresh tying the new card back to `design/mobile-app-product-default-lane.md` and `design/polyglot-productization-stack.md`

## Initial lane judgment
For the narrow native-shell mobile scope, publish:
- **native Swift/Kotlin shells + Rust core via UniFFI-generated bindings** as the conservative default;
- **Flutter + `flutter_rust_bridge`**, **Tauri mobile**, **Dioxus mobile / Slint mobile**, and **hand-written FFI** as serious alternatives for different scopes;
- explicit separation of native-shell truth, Rust-core truth, binding-generation truth, iOS-build truth, Android-build truth, resource/lifetime truth, and support/docs truth.

## Why this deserves a maintained card instead of only a stack note
This project class recurs constantly.
Teams repeatedly ask some variant of:
- should we keep the app shell native and share only the engine?
- should we use UniFFI or write the bridge by hand?
- how much of Android/iOS build reality still belongs to the project after choosing a binding generator?

Without a bounded maintained answer, guidance collapses back into folklore: one Firefox/Mozilla anecdote, one blog post, one proof-of-concept bridge, or one cross-platform framework debate.
That is exactly the kind of tacit-knowledge failure the archive is trying to reduce.

## Why now
- Rust’s latest official framing still names **choice paralysis** and **tacit knowledge** as central adoption issues.
- The survey still says docs are the canonical learning surface.
- UniFFI now has enough explicit Swift/Kotlin/Xcode/Gradle/lifetime documentation to support a reviewable boring default.
- UniFFI is also explicit about what it does **not** solve end-to-end, which keeps the card honest.
- The current cross-platform mobile card already names native shell + UniFFI as a serious alternative, which is a signal that the lane is central enough to deserve first-class treatment.

## Success criteria
A successful first revision of this lane should:
1. keep the app shell native on both platforms;
2. use Rust as a shared core through UniFFI-generated bindings;
3. name Xcode and Gradle/Android Studio integration work explicitly rather than hiding it;
4. keep Android build/package truth and iOS build/package truth separate;
5. and make it obvious when teams should stay on the existing Flutter-first card instead.

## Non-goals
- deciding the best native iOS UI architecture;
- deciding the best native Android UI architecture;
- replacing language-specific build/distribution tooling;
- or turning UniFFI into an end-to-end mobile packaging system.
