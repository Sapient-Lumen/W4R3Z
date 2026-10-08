# text-input-kit — product plan (2026-03-20)

This note sharpens **P-0027 text-input-kit** one step further into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should still be a **small crate family plus replay-capable CLI**, but it must now publish more than transactions and selection rules.
It should help toolkit maintainers and app teams publish one reviewable answer to:

- what IME transaction sequence the engine actually saw,
- what document/selection mutation the engine applied,
- what grapheme/word/line policy it claims,
- **which edit path is really active** on native versus web,
- whether candidate/selection geometry is synchronized precisely enough for OS composition UI,
- and whether a custom-rendered surface still owes an explicit accessibility mirror.

It should **not** try to become a full editor framework, a browser editing standard, or a generic accessibility platform adapter.
Those are adjacent lanes, not the missing product.

## What the crate should provide other people

For GUI toolkit maintainers, editor builders, QA engineers, and app teams, the crate should provide:

1. **One shared IME transaction model** instead of each toolkit inventing its own preedit/commit/cancel edge cases.
2. **A reusable selection/caret engine** that is explicit about grapheme, word, line, and replacement-range behavior.
3. **Backend adapters with honest receipts** for native `winit`, web hidden-input fallback, and later experimental EditContext paths.
4. **One edit-path receipt** that says what surface actually owns focus/composition state.
5. **One selection-geometry report** that says whether caret/selection/character bounds are synchronized precisely enough for candidate windows and inline composition.
6. **An accessibility-mirror declaration** so a canvas-backed editor cannot quietly claim a11y parity while rendering text off-DOM.
7. **A replayable transcript format** so text-input bugs can travel as evidence instead of folklore.

## Five first-class review objects

### 1. IME transaction report

Named classes for `0.1` should focus on transaction truth such as:
- `preedit_started`
- `preedit_updated`
- `commit_applied`
- `commit_replaces_range`
- `preedit_cancelled`
- `keyboardinput_overlap_detected`
- `leaked_key_release_normalized`
- `manual_review_required`

This object should answer:
- which preedit string and cursor the engine saw,
- whether the commit replaced an explicit range,
- whether leaked key events were deduplicated, ignored, or still need review,
- and whether the adapter had to fall back to approximations.

### 2. Selection contract report

Named classes for `0.1` should focus on selection truth such as:
- `grapheme_delete_safe`
- `word_nav_defined`
- `line_nav_defined`
- `replacement_range_honored`
- `selection_anchor_stable`
- `visual_logical_policy_declared`
- `manual_review_required`

This object should answer:
- how backspace/delete operate across grapheme clusters,
- whether emoji/ZWJ sequences are treated atomically,
- how anchor/head behave across extend/select operations,
- what visual-versus-logical movement policy is claimed,
- and which parts still need manual review for bidi/editor-specific behavior.

### 3. Backend capability receipt

Named classes for `0.1` should focus on honest adapter capabilities such as:
- `native_winit`
- `web_hidden_input_fallback`
- `web_editcontext_experimental`
- `candidate_anchor_precise`
- `candidate_anchor_approximate`
- `ime_events_unsupported`
- `fullscreen_risk`
- `manual_review_required`

Each receipt should also record:
- platform/runtime identity,
- adapter strategy,
- unsupported or emulated surfaces,
- and upstream references where the adapter is constrained by known issues.

### 4. Web edit-path receipt

This should stop the web lane from collapsing into a vague “supports WASM text input” story.

Named classes for `0.1` should focus on path truth such as:
- `hidden_input_proxy`
- `editcontext_experimental`
- `dom_editable_delegate`
- `canvas_direct_not_available`
- `offscreen_mirror_required`
- `manual_review_required`

This object should answer:
- which element actually holds focus and composition state,
- whether the visible surface and the editable surface are the same thing,
- whether selection/candidate geometry is fed through DOM input, EditContext, or emulation,
- and whether the path is stable enough for production or only experimental.

### 5. Selection-geometry report

Named classes for `0.1` should focus on geometry truth such as:
- `caret_rect_precise`
- `selection_bounds_synced`
- `character_bounds_synced`
- `candidate_anchor_detached`
- `inline_preedit_rendered`
- `offscreen_a11y_mirror_present`
- `manual_review_required`

This object should answer:
- whether the OS can place candidate / composition UI near the actual caret,
- whether selection and character bounds are being updated,
- whether provisional text is rendered inline or detached,
- whether fullscreen or transformed surfaces degrade geometry,
- and whether assistive technology can inspect an equivalent text surface.

## Recommended `0.1` command surface

### `cargo textinput replay <transcript>`
Read a normalized transcript and produce engine state snapshots plus mutation history.

### `cargo textinput doctor`
Run invariant checks and emit:
- `ime-transaction.report.json`
- `selection-contract.report.json`
- `backend-capability.receipt.json`
- `selection-geometry.report.json`
- `textinput-doctor.report.json`

### `cargo textinput web-path`
Inspect a web-backed adapter and emit:
- `web-edit-path.receipt.json`
- optional `selection-geometry.report.json`

### `cargo textinput diff <old> <new>`
Compare two runs and classify:
- `transaction_changed`
- `selection_policy_changed`
- `geometry_changed`
- `edit_path_changed`
- `manual_review_boundary_changed`

### `cargo textinput bundle`
Produce one compact `.textinputbundle.zip` containing reports, summaries, and fixture references.

## Recommended crate/workspace split

- `textinput_model`
  - shared types for transactions, selections, edits, and receipts
- `textinput_unicode`
  - grapheme/word/line navigation helpers and replacement-range policy
- `textinput_winit`
  - `winit` event translation plus native-capability receipts
- `textinput_web`
  - hidden-input and EditContext adapters, focus/geometry caveats, and web-path receipts
- `textinput_accesskit`
  - export helpers for value/selection semantics and mirror declarations
- `textinput_replay`
  - transcript import/export and deterministic replay
- `cargo-textinput`
  - user-facing CLI / cargo subcommand

## `0.1` artifact set

Core artifacts should be:
- `textinput.toml`
- `ime-transaction.report.json`
- `selection-contract.report.json`
- `backend-capability.receipt.json`
- `web-edit-path.receipt.json` (when relevant)
- `selection-geometry.report.json`
- `textinput-doctor.report.json`
- `textinput-diff.report.json`
- `notes.md`

The MVP should make these five truths reviewable before it tries to grow into a full editor framework:
- transaction truth,
- selection truth,
- adapter-capability truth,
- web edit-path truth,
- selection-geometry truth.

## Discovery order

1. **Backend capability import**
   - platform/runtime identity
   - adapter strategy
   - unsupported/emulated surfaces
2. **Edit-path classification**
   - native widget vs hidden-input proxy vs EditContext vs DOM delegate
   - focus/composition owner
   - fullscreen/transformed-surface caveats
3. **Transcript replay**
   - key/input/IME sequence
   - selection/caret moves
   - replacement ranges
4. **IME transaction classification**
   - preedit/update/commit/cancel
   - dedup or overlap handling
5. **Selection-contract evaluation**
   - grapheme safety
   - word/line policy
   - anchor/head stability
6. **Selection-geometry evaluation**
   - caret/selection/character bounds
   - inline vs detached preedit rendering
   - a11y mirror presence
7. **Diff + bundle**
   - policy drift
   - compact repro archive

## Ranking discipline

The first implementation should not treat “text eventually appeared in the widget” as the verdict.
A good `0.1` should keep separate:
- `transaction_truth_known`
- `selection_truth_known`
- `backend_capability_known`
- `edit_path_truth_known`
- `selection_geometry_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- `winit` native IME APIs and issue tracker reality
- hidden-input fallback experience on the web
- EditContext experimental support and responsibilities
- AccessKit text position/selection vocabulary
- layout/editing substrate such as `cosmic-text`
- toolkit-native glue such as `bevy_egui` IME handling

### Do not flatten into one fake verdict
- “the toolkit has a text widget”
- “the layout engine shaped the glyphs”
- “the web fallback eventually committed text”
- “the IME candidate box was somewhere on screen”
- “the accessibility tree contains a text node”

## Preferred proving grounds

- a Windows/X11/macOS IME flow where leaked key events must be normalized explicitly
- a hidden-input web flow where candidate anchoring or fullscreen behavior is approximate rather than native
- a Chromium EditContext canvas path where selection and character bounds are available but the text still needs an offscreen accessibility mirror
- an emoji/ZWJ deletion case where naïve scalar deletion corrupts user-visible selection semantics

## Non-goals

- not another text layout engine
- not another full editor widget toolkit
- not a browser-standard editing model implementation
- not a platform accessibility adapter
- not a generic GUI snapshot harness

## MVP API sketch

```rust
pub fn replay_transcript(transcript: &Transcript) -> Result<ReplayRun>;
pub fn summarize_ime_transactions(run: &ReplayRun) -> ImeTransactionReport;
pub fn evaluate_selection_contract(run: &ReplayRun, policy: &SelectionPolicy) -> SelectionContractReport;
pub fn inspect_backend_capabilities(adapter: &AdapterIdentity) -> BackendCapabilityReceipt;
pub fn inspect_web_edit_path(adapter: &WebAdapterIdentity) -> WebEditPathReceipt;
pub fn evaluate_selection_geometry(run: &ReplayRun, geometry: &GeometrySnapshot) -> SelectionGeometryReport;
pub fn write_bundle(bundle: &TextInputBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow `winit` API and backend changes closely.
- Treat hidden-input support as an explicit fallback lane, not as proof that Web IME is solved.
- Treat EditContext as an explicit experimental lane until browser support and toolkit experience are broader.
- Keep layout/shaping, transaction semantics, geometry sync, and a11y mirror claims separate in the repo.
- Preserve `manual_review_required` whenever candidate anchoring, transformed-surface geometry, or accessibility mirrors cannot be inferred honestly.

## Sources

- https://github.com/rust-windowing/winit/issues/4508
- https://github.com/rust-windowing/winit/issues/4525
- https://github.com/rust-windowing/winit/issues/4526
- https://github.com/rust-windowing/winit/issues/4424
- https://developer.mozilla.org/en-US/docs/Web/API/EditContext_API
- https://developer.mozilla.org/en-US/docs/Web/API/EditContext_API/Guide
- https://docs.rs/accesskit/latest/accesskit/
- https://docs.rs/cosmic-text/latest/cosmic_text/struct.Editor.html
- https://docs.rs/bevy_egui/latest/bevy_egui/input/index.html
- https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
- https://github.com/slint-ui/slint/issues/8716
