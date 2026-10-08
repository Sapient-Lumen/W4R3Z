# text input stack boundaries — 2026-03-19

This note exists to stop future passes from collapsing multiple adjacent problems into one fake “Rust text support” story.

## Keep these lanes separate

1. **Event ingress**
   - OS/browser/windowing events
   - IME enablement and candidate positioning
   - hidden-input or platform fallback strategies

2. **Transaction semantics**
   - preedit/update/commit/cancel
   - replacement ranges
   - dedup/conflict handling when key events leak alongside IME events

3. **Document and selection semantics**
   - insertion/replacement/delete
   - grapheme-safe movement and deletion
   - anchor/head stability
   - visual-versus-logical navigation policy

4. **Layout and shaping**
   - bidi resolution
   - segmentation and shaping
   - line breaking and measurement
   - font discovery and fallback

5. **Accessibility export**
   - value semantics
   - selection semantics
   - text-span representation in accessibility trees

6. **Regression/capture tooling**
   - transcript replay
   - render snapshots
   - observer-side platform capture
   - end-user bug bundles

## Why this matters

The current Rust ecosystem already has meaningful substrate in several of these lanes.
That makes it dangerous for the archive to say “text input is missing” without specifying **which layer** is actually missing.

The sharper current gap is not another layout engine and not another platform adapter.
It is a **shared transaction/selection engine plus backend-capability receipts and replay artifacts** above existing substrate.

## Archive homes

- **P-0027 text-input-kit** — transaction/selection engine + adapter receipts + replay bundle
- **P-0197 Text Layout & Shaping Conformance Kit** — layout/shaping correctness and backend/profile truth
- **P-0087 UI Accessibility Doctor Kit** — authoring-side semantic doctoring and release gating
- **P-0202 Accessibility Capture & Interop Lab** — observer-side platform capture and semantic diff
- **P-0092 GUI Testing & Snapshot Harness Kit** — broader GUI regression and snapshot workflows
