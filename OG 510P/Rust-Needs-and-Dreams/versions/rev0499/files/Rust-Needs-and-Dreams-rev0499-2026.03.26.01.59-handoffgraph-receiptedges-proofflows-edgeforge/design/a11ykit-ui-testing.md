# Design: A11yKit (`cargo a11y`, `cargo ui-test`, a11y-report/v0)

## Goal
Turn accessibility and UI testing into a shared substrate for Rust UI toolkits by:
- defining portable artifacts (`a11y-report/v0`, `a11y-snapshot/v0`, `ui-test-report/v0`),
- providing conformance checks and diffing workflows,
- offering a framework-agnostic UI testing query model grounded in accessibility semantics.

This kit does *not* replace AccessKit; it operationalizes it for toolkits, apps, and CI.

## References (signals)
- AccessKit overview: https://accesskit.dev/
- accesskit_winit adapter: https://crates.io/crates/accesskit_winit
- egui AccessKit flag + repo a11y notes: https://docs.rs/egui ; https://github.com/emilk/egui
- Slint accessibility text-input issue: https://github.com/slint-ui/slint/issues/2895
- Iced accessibility issue (stable widget identity): https://github.com/iced-rs/iced/issues/552

## Core UX
### `cargo a11y`
- `cargo a11y check`
  - run accessibility conformance checks (roles, focus order, labels, text fields)
  - emits `a11y-report/v0`
- `cargo a11y snapshot`
  - captures a stable `a11y-snapshot/v0` (tree + semantics) for diffing
- `cargo a11y diff <A> <B>`
  - highlights semantic changes (role changes, unlabeled controls, focus traps)

### `cargo ui-test`
- `cargo ui-test run`
  - execute tests that query elements by role/label (like web testing libraries)
  - stores `ui-test-report/v0` + optional input traces for replay
- `cargo ui-test record` / `replay`
  - deterministic input playback (ties into Replay Kit concepts, but UI-specific)

## Query model (framework-agnostic)
Expose selectors:
- `get_by_role("button", name="Save")`
- `get_by_label("Username")`
- `get_by_text("Error")` (discouraged unless semantically justified)

Implementation:
- For frameworks using AccessKit, query the AccessKit tree.
- For webview apps (Tauri), optionally map DOM accessibility tree to the same schema where possible (best-effort).

## Artifacts
### `a11y-report/v0`
- platform + backend (winit/accesskit/etc.)
- violations with reason codes:
  - `MISSING_LABEL`
  - `FOCUS_TRAP`
  - `NO_KEYBOARD_NAV`
  - `TEXT_INPUT_NOT_EXPOSED`
  - `ROLE_MISMATCH`
- “fix hints” and links to relevant nodes in snapshot

### `a11y-snapshot/v0`
- stable accessibility tree representation
- redaction rules (avoid capturing sensitive text)
- node ids + roles + names + states + relationships

### `ui-test-report/v0`
- test results + timings
- references to snapshots used
- optional recorded input script hashes

## Conformance suite
Ship a cross-framework fixture corpus:
- standard widgets (buttons, menus, lists, text inputs)
- complex text editing semantics
- focus traversal expectations
- IME / accessibility actions

Toolkits can run the suite and publish a “conformance badge” in their docs.

## Integration points
- Policy Kit: require `a11y-report/v0` pass for releases.
- Replay Kit: attach UI input traces to replay packs.
- Incident Kit: capture a11y state for UI security incidents involving spoofing/phishing.

## Evaluation plan
- Start with winit-based toolkits (AccessKit easiest path).
- Validate on Windows/macOS first (where AccessKit native backends are mature), then expand.
- UX bar: “CI can detect an unlabeled control regression in one screen of diff output.”
