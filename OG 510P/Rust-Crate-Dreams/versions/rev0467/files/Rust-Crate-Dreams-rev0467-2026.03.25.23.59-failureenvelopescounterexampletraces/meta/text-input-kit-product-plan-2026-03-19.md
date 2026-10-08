# text-input-kit — product plan (2026-03-19)

This note sharpens **P-0027 text-input-kit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small crate family plus replay-capable CLI** that helps toolkit maintainers and app teams publish one reviewable answer to:

- what IME transaction sequence the engine actually saw,
- which document/selection mutation the engine applied,
- what grapheme-safe deletion and cursor movement it claims,
- what the current backend can and cannot support,
- and how text-selection/value semantics are exported upward to accessibility layers.

It should **not** try to become a full layout engine, a GUI framework, a browser editing standard, or a platform backend.
Those are substrate or adjacent lanes, not the missing product.

## What the crate should provide other people

For GUI toolkit maintainers, editor builders, QA engineers, and app teams, the crate should provide:

1. **One shared IME transaction model** instead of each toolkit inventing its own preedit/commit/cancel edge cases.
2. **A reusable selection/caret engine** that is explicit about grapheme, word, line, and replacement-range behavior.
3. **Backend adapters** for native (`winit`) and web hidden-input flows that report what is truly supported versus emulated.
4. **A replayable transcript format** so text-input bugs can travel as evidence rather than folklore.
5. **An accessibility export lane** so value/selection semantics can be handed to AccessKit-shaped trees honestly.
6. **A compact bundle** that another maintainer can inspect without attaching a debugger to the toolkit.

## Three first-class review objects

### 1. IME transaction report

Named classes for `0.1` should focus on transaction truth such as:
- `preedit_started`
- `preedit_updated`
- `commit_applied`
- `commit_replaces_range`
- `preedit_cancelled`
- `keyboardinput_overlap_detected`
- `manual_review_required`

This object should answer:
- which preedit string and cursor the engine saw,
- whether the commit replaced an explicit range,
- whether leaked key events were deduplicated or ignored,
- whether candidate-anchor updates were requested,
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

This should stop the product from flattening every adapter into “supports text input”.

Named classes for `0.1`:
- `native_winit`
- `web_hidden_input`
- `candidate_anchor_precise`
- `candidate_anchor_approximate`
- `dead_keys_supported`
- `ime_events_unsupported`
- `fullscreen_risk`
- `manual_review_required`

Each receipt should also record:
- platform/runtime identity,
- adapter strategy,
- unsupported or emulated surfaces,
- and links to upstream constraints or open issues when relevant.

## Recommended `0.1` command surface

### `cargo textinput replay <transcript>`
Read a normalized transcript and produce engine state snapshots plus mutation history.

### `cargo textinput doctor`
Run invariant checks and emit:
- `ime-transaction.report.json`
- `selection-contract.report.json`
- `textinput-doctor.report.json`

### `cargo textinput diff <old> <new>`
Compare two runs and classify:
- `transaction_changed`
- `selection_policy_changed`
- `replacement_range_changed`
- `capability_receipt_changed`
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
  - hidden-input adapter, focus/fullscreen/candidate-anchor caveats, and web receipts
- `textinput_accesskit`
  - export helpers for value/selection semantics
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
- `textinput-doctor.report.json`
- `textinput-diff.report.json`
- `notes.md`

The MVP should make these three truths reviewable before it tries to grow into a full editor framework:
- transaction truth,
- selection truth,
- adapter-capability truth.

## Discovery order

1. **Backend capability import**
   - platform/runtime identity
   - adapter strategy
   - unsupported/emulated surfaces
2. **Transcript replay**
   - key/input/IME sequence
   - selection/caret moves
   - replacement ranges
3. **IME transaction classification**
   - preedit/update/commit/cancel
   - dedup or overlap handling
4. **Selection-contract evaluation**
   - grapheme safety
   - word/line policy
   - anchor/head stability
5. **Accessibility export**
   - value/selection semantics
   - manual-review boundaries
6. **Diff + bundle**
   - policy drift
   - compact repro archive

## Ranking discipline

The first implementation should not treat “text appeared in the widget” as the verdict.
A good `0.1` should keep separate:
- `transaction_truth_known`
- `selection_truth_known`
- `backend_capability_known`
- `accessibility_export_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- `winit` native IME APIs and event model
- `winit` platform limitations and current issue tracker reality
- `Parley` / `cosmic-text` layout and editing substrate
- AccessKit text position/selection vocabulary
- toolkit-native adapter work and field bug reports

### Do not flatten into one fake verdict
- “the toolkit has a text widget”
- “the layout engine shaped the glyphs”
- “the windowing layer has IME APIs”
- “the web fallback inserted text somehow”
- “the accessibility tree contains a text node”

## Preferred proving grounds

- a Windows preedit flow where `KeyboardInput` leaks during IME usage and needs explicit dedup or conflict handling
- a web hidden-input flow where candidate anchoring or fullscreen behavior is approximate rather than native
- an emoji/ZWJ deletion case where naïve scalar deletion corrupts user-visible selection semantics
- a custom text widget that can focus but still loses value/selection export unless the adapter is honest

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
pub fn export_accesskit_semantics(run: &ReplayRun) -> AccesskitTextExport;
pub fn write_bundle(bundle: &TextInputBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow `winit` API and backend changes closely.
- Treat web hidden-input support as an explicit fallback lane, not as proof that Web IME is solved.
- Keep layout/shaping and text-input semantics separate in the repo.
- Preserve `manual_review_required` whenever candidate anchoring, bidi cursor policy, or accessibility export cannot be inferred honestly.

## Sources

- https://docs.rs/winit/latest/winit/window/struct.Window.html
- https://docs.rs/winit/latest/winit/event/enum.WindowEvent.html
- https://github.com/rust-windowing/winit/issues/4508
- https://github.com/rust-windowing/winit/issues/4424
- https://docs.rs/parley/latest/parley/
- https://docs.rs/cosmic-text/latest/cosmic_text/
- https://docs.rs/accesskit/latest/accesskit/
- https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
- https://github.com/slint-ui/slint/issues/2895
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
