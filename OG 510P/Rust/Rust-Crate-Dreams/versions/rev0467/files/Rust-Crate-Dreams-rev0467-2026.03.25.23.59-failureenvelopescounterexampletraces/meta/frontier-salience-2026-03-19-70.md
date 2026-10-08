# Frontier salience snapshot — 2026-03-19 (70)

This pass did **not** promote another generic GUI layer.
It sharpened a neglected but highly leverageable product-engineering substrate:

- **P-0027 text-input-kit** — because Rust now has meaningful layout, editing, and accessibility substrate, but still lacks one shared engine that makes IME transactions, selection truth, adapter capability, and replayable text-input evidence boring.

## Main judgment

The next worthy move here was **not** another layout engine, **not** another accessibility doctor pass, and **not** another generic GUI testing harness.
Those are adjacent lanes with real existing substrate or separate product goals.

The sharper missing layer is the **shared text-input engine and replayable adapter-truth layer** above today’s substrate, especially once three more facts are kept explicit:

- **IME transaction truth** — what preedit, commit, cancel, replacement-range, and overlap behavior the engine actually saw and applied;
- **selection truth** — what grapheme-safe deletion, caret/anchor movement, and replacement semantics the engine actually claims;
- **backend capability truth** — what the active adapter can really support on native versus web, and where fallback/manual-review boundaries begin.

That move is better grounded now because:

- `winit` explicitly documents native IME APIs such as `set_ime_allowed`, `Ime` events, and IME positioning while also documenting **Web as unsupported** for IME events/positioning;
- March 2026 issue traffic shows native behavior still has sharp edges, including leaked `KeyboardInput` during IME use on Windows;
- the active Web/WASM IME issue still describes the hidden-input workaround as a hacky fallback because canvas cannot receive `CompositionEvent` directly;
- `Parley` and `cosmic-text` show that layout/editing substrate is becoming real;
- AccessKit already has text-position / text-selection vocabulary, which means input semantics can feed upward once the lower layer is honest;
- and current field surveying of Rust GUI libraries plus Slint discussion still show text-input and accessibility polish remain uneven.

So the gap is no longer “Rust cannot render or edit text at all”.
The gap is that teams still rarely get a **shared, reviewable text-input correctness workflow** above the substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0027 text-input-kit** — now promoted as one of the clearest end-user product-engineering opportunities because the missing value is no longer a vague text stack, but a shared transaction/selection/capability/replay layer.
8. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane above AccessKit substrate.
9. **P-0197 Text Layout & Shaping Conformance Kit** — still a strong cross-stack correctness lab.
10. **P-0092 GUI Testing & Snapshot Harness Kit** — still a strong shared regression substrate, but less sharply timed than P-0027 right now.
11. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
12. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library-shipping lane.
13. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm contract opportunities.
14. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK contract opportunities.
15. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET contract opportunities.
16. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-native contract opportunities.

## Why this won over adjacent candidates right now

- It beat another **accessibility doctor** pass because the archive had just made P-0087 implementation-ready enough to hold its own lane.
- It beat **P-0197 Text Layout & Shaping Conformance Kit** because the archive already has a stronger handoff shape for layout correctness than for transaction/caret truth.
- It beat **P-0092 GUI Testing & Snapshot Harness Kit** because generic regression substrate is less urgent than making text entry itself honest and replayable.
- It beat another **foreign-package ship contract** because the archive still benefits from deliberate rebalancing toward end-user product engineering.

## What changed in the archive

Added:
- `entries/2026-03-19-250.md`
- `meta/frontier-salience-2026-03-19-70.md`
- `meta/text-input-kit-product-plan-2026-03-19.md`
- `meta/text-input-stack-boundaries-2026-03-19.md`
- `fixtures/text-input-kit/README.md`
- `fixtures/text-input-kit/ime-transaction.report.schema.json`
- `fixtures/text-input-kit/selection-contract.report.schema.json`
- `fixtures/text-input-kit/backend-capability.receipt.schema.json`
- `fixtures/text-input-kit/scenarios/windows_preedit_keyboardinput_overlap_requires_dedup/`
- `fixtures/text-input-kit/scenarios/web_hidden_input_fullscreen_breaks_candidate_anchor/`
- `fixtures/text-input-kit/scenarios/emoji_zwj_backspace_breaks_grapheme_cluster_selection/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/text-input-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`

## What this pass deliberately did not do

It did **not** collapse:

- layout/shaping,
- editor/document behavior,
- IME event handling,
- accessibility export,
- and snapshot/capture tooling

into one fake “text support” story.
