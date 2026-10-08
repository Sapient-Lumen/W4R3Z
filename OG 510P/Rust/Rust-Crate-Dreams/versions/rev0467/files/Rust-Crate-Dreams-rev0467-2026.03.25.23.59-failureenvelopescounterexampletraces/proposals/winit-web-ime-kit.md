---
id: P-0043
title: winit-web-ime-kit — reliable IME/composition for canvas-based WASM apps
status: idea
domains: [gui, wasm, text-input, accessibility]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/rust-windowing/winit/issues/4424
  - https://github.com/rust-windowing/winit/issues/1497
  - https://github.com/rust-windowing/winit/issues/1293
---

# Problem
IME (composition) is a baseline requirement for global text input. On Web/WASM, canvas-based apps often cannot receive CompositionEvent directly, leading to hidden-input hacks that are hard to make reliable (focus, fullscreen, mobile keyboards, selection syncing). This gap blocks serious international text input for Rust GUIs targeting the browser.

# Users & user stories
- **GUI toolkit maintainers** (egui, iced, slint, bespoke WebGPU canvases) want a reusable solution instead of repeating fragile JS glue.
- **App developers** want “text fields just work” across languages and input methods.
- **Accessibility maintainers** want consistent focus/selection behavior that can be surfaced to accessibility layers.

# Prior art (and why it’s insufficient)
- winit has long-running IME tracking issues across platforms. Sources: https://github.com/rust-windowing/winit/issues/1497 and https://github.com/rust-windowing/winit/issues/1293
- A specific Web IME issue documents current limitations and hacky workarounds (hidden input forwarding). Source: https://github.com/rust-windowing/winit/issues/4424
- Individual toolkits implement bespoke bridges; there is no shared conformance/test corpus.

# Design goals
- **Shared “bridge” primitive**: hidden input element + event forwarding with a stable Rust API.
- **Deterministic state machine**: composition start/update/commit/cancel; selection and cursor synchronization.
- **Fullscreen-safe**: handle focus changes, pointer lock/fullscreen transitions, and mobile quirks.
- **Testable**: a replayable event corpus (JSON) for browser integration tests.
- **Composable** with `text-input-kit` (proposal P-0027): this crate can be the WASM adapter backend.

# Non-goals
- Building a full GUI framework.
- Forcing winit to adopt a specific internal design (should work as an external “adapter crate” first).

# Architecture & API sketch
## Components
- `Bridge` (Rust): owns composition state, exposes `on_js_event(...) -> Vec<Event>`.
- `bridge.js`: installs hidden input, listens to `composition*`, `beforeinput`, `input`, `keydown`, and forwards normalized events to Rust.
- Optional “DOM overlay” mode for better IME behavior in some browsers.

## Rust API (sketch)
- `WebImeBridge::new(config) -> Self`
- `WebImeBridge::set_focus(bool)`
- `WebImeBridge::set_surrounding_text(text, cursor, selection)`
- `WebImeBridge::handle(event: JsImeEvent) -> Vec<ImeEvent>`
- `ImeEvent` maps to winit-style events (composition update/commit, received text, key events).

# Security / safety model
- Avoid exposing raw keystrokes unless needed; keep APIs focused on text changes.
- Provide explicit opt-in for logging/replay capture (privacy).

# Maintenance & governance plan
- Maintain a browser matrix (Chrome/Firefox/Safari) with CI via Playwright.
- Keep the JS surface tiny and versioned; prefer feature detection over UA sniffing.
- Store a small replay corpus for regressions.

# Milestones
- **0.1**: hidden-input bridge, composition events, text commit, focus handling (Chrome/Firefox).
- **0.2**: fullscreen + mobile keyboards; selection syncing; replay tests.
- **0.3**: optional integration crate for winit/egui; publish “how to integrate” cookbook.

# Open questions
- Best strategy for fullscreen: input in DOM overlay vs hidden input?
- How to expose accessibility info without coupling tightly to a11y crates?

# Sources
- winit: Add IME support for Web (WASM) — https://github.com/rust-windowing/winit/issues/4424
- winit: Tracking issue for IME / composition support — https://github.com/rust-windowing/winit/issues/1497
- winit: Improve IME event handling — https://github.com/rust-windowing/winit/issues/1293
