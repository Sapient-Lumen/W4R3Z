# Epic Proposal: A11yKit (Accessibility + UI Testing substrate)

## One-sentence pitch
Make Rust GUI stacks production-ready by standardizing accessibility semantics and framework-agnostic UI testing around the accessibility tree, with CI-diffable artifacts.

## Deliverables
- `cargo-a11y` + `cargo-ui-test` reference CLIs
- Schemas:
  - `a11y-report/v0`
  - `a11y-snapshot/v0`
  - `ui-test-report/v0`
- Conformance suite + fixtures (text inputs, focus traversal, menus)
- Integrations:
  - AccessKit + winit adapter path (primary)
  - optional adapters for egui, iced, slint (via AccessKit where possible)
- Docs:
  - how to expose text editing semantics correctly
  - privacy/redaction guidance for snapshots

## Why now
- AccessKit provides reusable cross-platform accessibility infrastructure intended for toolkits, lowering the cost of “do accessibility once.”  
  https://accesskit.dev/
- Multiple major Rust GUI stacks are actively working on accessibility, but gaps persist (text input exposure, stable widget identity).  
  https://github.com/slint-ui/slint/issues/2895  
  https://github.com/iced-rs/iced/issues/552

## Non-goals
- Mandating one GUI framework
- Capturing user content by default (snapshots are redacted)
- Perfect DOM accessibility parity across webviews on day one

## Milestones
1) v0: snapshot + diff + basic conformance checks (winit + AccessKit)
2) v0.2: UI testing query API + adapters for one toolkit (egui first)
3) v0.3: conformance corpus + additional toolkit adapters
4) v1: stable schemas + CI templates + ecosystem “a11y badge” program
