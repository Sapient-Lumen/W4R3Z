# Epic proposal: Mobile app product default lane

## Thesis
Add a maintained defaults-corpus card for **mobile-first Rust-involving app products** so the archive can answer a common practical question with a bounded current recommendation instead of only a broad client-productization theory.

## Proposed artifact family
- `design/mobile-app-product-default-lane.md`
- `defaults/conservative-mobile-app-product-2026Q1.md`
- `evidence/conservative-mobile-app-product-2026Q1-renewal-2026-03-22.md`
- frontier/meta refresh tying the new card back to `design/client-productization-stack.md`

## Initial lane judgment
For the narrow cross-platform mobile-product scope, publish:
- **Flutter shell + Rust core via `flutter_rust_bridge`** as the conservative default;
- **native shell + UniFFI**, **Tauri 2 mobile**, **Dioxus mobile**, and **Slint mobile** as serious alternatives for different scopes;
- explicit separation of shell/runtime truth, Rust-core/bridge truth, native escape hatches, permission/device capability truth, store/package/signing truth, and support/docs posture.

## Why this is epic-worthy
- It turns an older client-productization frontier into a reusable current answer.
- It covers a mainstream recurring adoption lane rather than an edge case.
- It gives the archive a way to talk honestly about mobile productization without forcing a fake “all-Rust UI has already won” story.
- It is exactly the kind of contribution the ecosystem is currently missing: not another toolkit, but a reviewable boring default with the real tradeoffs left visible.

## Non-goals
- declaring one Rust UI framework the universal mobile winner;
- collapsing desktop, mobile, polyglot component, and embedded client work into one card;
- or replacing `design/client-productization-stack.md`.
