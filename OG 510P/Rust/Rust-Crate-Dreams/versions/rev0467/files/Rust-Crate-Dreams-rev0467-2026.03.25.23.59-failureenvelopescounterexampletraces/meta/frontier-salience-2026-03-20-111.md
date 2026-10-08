# Frontier salience snapshot — 2026-03-20 (111)

This pass did **not** add another generic GUI toolkit, another canvas editor prototype, or another accessibility checker.
It deepened **P-0027 text-input-kit** by making one more product-critical truth explicit:

- **text input is only reviewable when edit path, geometry sync, and accessibility mirror truth stay separate from “characters were committed”.**

## Main judgment

The sharper missing layer is no longer merely “a shared IME transaction engine.”
The sharper missing layer is a **shared transaction/selection engine plus edit-path and geometry receipts**.

The current Rust/web/gui substrate has changed enough to make that specific:

1. `winit` already gives native IME enablement and events, but fresh March 2026 issues still show leaked or inconsistent key-event behavior across Windows, X11, and macOS;
2. the Web/WASM lane in `winit` still relies on hidden-input bridging because canvas-based composition is not natively boring there yet;
3. the same issue now points to the EditContext API as the promising long-term route, but only once broader support exists;
4. MDN’s EditContext docs now spell out that custom editable regions owe selection updates, character/selection bounds, and accessibility representation explicitly;
5. AccessKit already has text-position and text-selection vocabulary, so custom editors can no longer hand-wave the export layer away;
6. current field reporting on Rust GUI libraries still shows IME provisional-state rendering, candidate placement, and screen-reader-visible text varying widely.

That means the next worthy move is not “another text widget.”
It is one conservative crate family that can publish:

- **IME transaction truth**,
- **selection-contract truth**,
- **backend-capability truth**,
- **web-edit-path truth**,
- **selection-geometry truth**,
- and **a11y-mirror truth**.

## Why this beat nearby work

The archive already has adjacent lanes for:

- layout/shaping correctness,
- authoring-side accessibility doctoring,
- observer-side accessibility capture,
- generic GUI regression harnessing,
- and desktop shipping.

What it still lacked was one compact way to say:

- “this web editor is still on hidden-input fallback rather than a first-class edit path,”
- “the OS candidate UI is anchored precisely / approximately / detached,”
- and “assistive technology can or cannot inspect the same text surface the user sees.”

That is a real product boundary, not just “more GUI polish.”

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still strongest among release-support lanes because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still rising because the 2026 registry/advisory substrate makes reviewable trust posture more buildable.
4. **P-0027 text-input-kit** — materially stronger after this pass because edit-path, geometry, and a11y-mirror truth make the lane feel like a real cross-toolkit product instead of a vague “GUI text support” wish.
5. **P-0011 Crate Health Contract Kit** — still very strong because maintainer/support posture remains distinct from trust/risk posture.
6. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown/drain truth remains under-served and broadly useful.
7. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
8. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.

## What changed in the archive

Added:
- `entries/2026-03-20-291.md`
- `meta/frontier-salience-2026-03-20-111.md`
- `meta/text-input-kit-product-plan-2026-03-20.md`
- `meta/text-input-web-path-boundaries-2026-03-20.md`
- `fixtures/text-input-kit/web-edit-path.receipt.schema.json`
- `fixtures/text-input-kit/selection-geometry.report.schema.json`
- `fixtures/text-input-kit/scenarios/chromium_editcontext_canvas_needs_bounds_and_offscreen_mirror/`
- `fixtures/text-input-kit/scenarios/x11_fcitx5_key_release_leaks_need_normalization_and_receipt/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/text-input-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- `fixtures/text-input-kit/README.md`
