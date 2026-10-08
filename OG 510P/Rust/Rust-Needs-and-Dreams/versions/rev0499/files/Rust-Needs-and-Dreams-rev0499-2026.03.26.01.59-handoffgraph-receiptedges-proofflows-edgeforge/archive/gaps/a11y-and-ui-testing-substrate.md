# Gap: Accessibility + UI Testing as First-Class Ecosystem Substrate (A11yKit)

## Summary
Rust has multiple promising GUI stacks (native and webview-based), but production readiness often hinges on:
- **Accessibility (a11y)**: screen readers, keyboard navigation, semantic roles, text editing semantics.
- **Testability**: framework-agnostic UI testing (query by role/label), deterministic input playback, and CI-ready artifacts.

There is now strong foundational work in **AccessKit**—a cross-platform accessibility abstraction meant to be reused across toolkits.
However, the ecosystem is missing an *adoption-ready* “kit” that:
1) standardizes the a11y contract for Rust UI toolkits (including text inputs),
2) provides a shared UI-testing query model built on the a11y tree,
3) emits portable reports so accessibility regressions are diffable in CI.

## Ecosystem signals
- AccessKit positions itself as “accessibility infrastructure for UI toolkits,” providing a cross-platform abstraction over platform accessibility APIs.  
  https://accesskit.dev/
- AccessKit has a `winit` adapter crate (`accesskit_winit`) for exposing an accessibility tree via native APIs on supported platforms.  
  https://crates.io/crates/accesskit_winit
- egui includes optional AccessKit support (native accessibility APIs; enabled by default in eframe per repo docs).  
  https://docs.rs/egui  
  https://github.com/emilk/egui
- Slint has open issues highlighting missing/complex accessibility features (e.g., text input exposure in a11y).  
  https://github.com/slint-ui/slint/issues/2895
- Iced has a long-running accessibility issue describing the need for stable widget identity and hierarchy for proper a11y integration.  
  https://github.com/iced-rs/iced/issues/552

## What “good” looks like
- A shared vocabulary and conformance tests for a11y trees (roles, states, text semantics).
- A framework-agnostic UI testing layer that queries by a11y role/label (like Testing Library on the web).
- CI artifacts: `a11y-report/v0` and `ui-test-report/v0` that can be diffed and gated.
