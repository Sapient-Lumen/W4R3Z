# Gap: Native-shell mobile products still lack a boring shared-engine default that keeps platform ownership explicit

## Problem
Rust mobile guidance is getting better, but much of the visible discourse still jumps too quickly from:
- “Rust can run on mobile”
- or “Rust can back a Flutter app”

to the implied conclusion that there is already one general “Rust mobile” answer.

That is false for one of the most common serious product classes:
**native-shell Android+iOS products where Swift/Kotlin own the product shell and Rust is the shared engine.**

## Why this gap matters now
The latest Rust challenges framing still says ecosystem navigation is burdened by **choice paralysis** and **tacit knowledge**.
The 2025 survey still says online docs are canonical while editor/LLM mediation rises.

UniFFI is now strong enough to make this lane concrete:
- production-quality Swift support is documented;
- Kotlin/Android integration is documented;
- the generated surface and configuration points are documented;
- resource/lifetime behavior is documented;
- and the project is explicit about its safety-first and mobile-consumer-driven design goals.

At the same time, UniFFI is also explicit that it does **not** solve end-to-end Android/iOS packaging.
That means the ecosystem still lacks a widely shared boring answer for keeping these truths reviewable together:
- which parts of the product remain natively owned;
- what the shared Rust core is actually responsible for;
- what UniFFI generates and what it does not;
- how Android cross-build and packaging are handled;
- how iOS build phases, libraries, modulemaps, or framework packaging are handled;
- and what lifetime/threading/resource obligations still land in platform code.

## Why this deserves a maintained card instead of staying inside the cross-platform mobile card
The existing cross-platform mobile card is about **one shared shell/runtime**.
This gap is about the opposite architectural choice:
- platform-native shell ownership,
- shared Rust engine,
- and a generated bridge that is deliberately not the whole productization story.

Those are different lane truths.
If they stay in one card, the archive will keep under-specifying the actual decision teams face.

## Proposed correction
Publish a maintained defaults-corpus card for **native-shell mobile product** with:
- **native Swift/Kotlin shells + Rust core via UniFFI** as the conservative default;
- explicit Android-build and iOS-build truths;
- explicit lifetime/resource caveats;
- and clear alternatives when the team actually wants a cross-platform shell or Rust-owned UI.

## References
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
- https://mozilla.github.io/uniffi-rs/latest/Motivation.html
- https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html
- https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
- https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- https://mozilla.github.io/uniffi-rs/latest/kotlin/configuration.html
- https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html
- https://mozilla.github.io/uniffi-rs/latest/kotlin/lifetimes.html
- https://docs.rs/crate/cargo-ndk/latest
