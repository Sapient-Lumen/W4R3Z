---
id: P-0027
title: text-input-kit — reusable IME/composition + selection engine for Rust GUIs
status: idea
domains: [gui, accessibility, wasm, text, desktop]
last_reviewed: 2026-03-20
evidence:
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
---

# P-0027 — text-input-kit

**Codename:** `textinput`

**Primary surface:** a crate family plus `cargo textinput` replay/doctor tooling.

**Canonical artifact:** `*.textinputbundle.zip`.

## Problem

Rust now has real text substrate, but it still lacks one shared layer that makes text entry boring.

Today’s situation is better than it used to be, but also more specific:

- `winit` now has real native IME controls and event surfaces, but fresh March 2026 issues still show leaked or inconsistent key-event behavior across Windows, X11, and macOS.
- the active Web/WASM IME issue in `winit` still says canvas-based composition is not natively boring there yet, so hidden-input forwarding remains the practical workaround.
- the same issue now points to the **EditContext API** as a cleaner long-term route, but only once browser support is broader and the responsibilities are clearer.
- MDN’s EditContext docs now make explicit that custom editable regions owe the OS text service **selection changes**, **text/character bounds**, and — for canvas-backed text — a separate accessibility representation.
- `cosmic-text` shows that Rust now has real editing/layout substrate.
- AccessKit already has text-position and text-selection vocabulary, which means the export lane is no longer imaginary.
- `bevy_egui` still contains explicit IME glue, which is useful evidence that the integration layer remains ad hoc.
- current field reporting on Rust GUI libraries still shows that “ordinary text input that feels production-ready” is not a solved boring default.

That means the missing crate is not another layout engine and not another vague widget toolkit.
The sharper missing crate is a **shared text-input engine plus adapter/replay/receipt layer** with explicit web-path and geometry honesty.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> “Given this event stream and backend, what preedit/commit/cancel sequence did we actually see, what document/selection mutation did we apply, which edit path is really active, and how precisely are candidate/selection/accessibility surfaces synchronized?”

That answer should travel as one replayable bundle, with explicit receipts rather than folklore.

## What the crate should provide other people

### 1. A toolkit-neutral input engine
The crate should define a reusable core for:
- preedit/update/commit/cancel,
- selection and replacement ranges,
- grapheme-safe delete/backspace,
- word/line navigation policy,
- and dedup/conflict handling when backend events overlap.

### 2. Backend adapters with honest receipts
The crate should ship adapters at least for:
- native `winit` flows,
- web hidden-input fallback flows,
- experimental web EditContext flows,
- and imported toolkit-native event streams later.

The sharp idea is that adapters should emit **capability receipts**, not just “support text input” badges.

### 3. Web edit-path receipts
The crate should say explicitly whether the active web route is:
- hidden-input proxy,
- experimental EditContext,
- delegated DOM editable,
- or something else.

It should also say which surface truly owns focus/composition state and whether the visible text surface is the editable one.

### 4. Selection-geometry reports
Text input is not reviewable if the OS candidate UI and the visible caret drift apart.
The crate should define a compact report for:
- caret rect updates,
- selection bounds updates,
- character bounds updates,
- candidate-anchor precision,
- inline versus detached provisional rendering,
- and fullscreen/transformed-surface caveats.

### 5. Accessibility export and mirror helpers
This proposal should help toolkits export:
- value semantics,
- text selection semantics,
- text-position facts,
- and when needed an explicit **offscreen / parallel accessibility mirror** declaration

into AccessKit-shaped trees without each toolkit inventing the contract from scratch.

### 6. Replayable transcripts and bundles
The receiver-facing artifact should be `*.textinputbundle.zip` carrying:
- transcript,
- IME transaction report,
- selection contract report,
- backend capability receipt,
- web edit-path receipt when relevant,
- selection geometry report,
- diff summary,
- and notes/manual-review markers.

## Users & user stories

- **GUI toolkit maintainer:** “I do not want to re-implement IME/composition/selection logic for every backend.”
- **App team:** “I need Japanese/Chinese/Korean IME, emoji, dead keys, and clipboard-like replacement flows to behave consistently.”
- **Editor builder:** “I need explicit grapheme/word/line policy instead of accidental selection behavior.”
- **QA engineer:** “I need a replayable transcript and geometry receipt for a bug that only appears on Windows or Web.”
- **Accessibility maintainer:** “I need text selection/value semantics exported honestly, and I need to know when a canvas-backed editor still owes a mirror.”

## Prior art scan (and why it’s insufficient)

### `winit` proves event substrate, not the whole product
`winit` now has native IME APIs and event surfaces.
That is necessary substrate.
It is not the missing crate.
The missing layer is the **shared transaction/selection engine and adapter-truth layer above it**.

### Web fallback and EditContext prove demand, not boring support
The current Web/WASM issue is especially useful as a reality check.
It shows hidden-input forwarding is still a practical fallback, while EditContext is the plausible future route.
Neither by itself gives Rust toolkits one boring contract for path truth, geometry sync, or mirror honesty.

### `cosmic-text` proves editing/layout substrate, not shared input semantics
That crate makes the ecosystem meaningfully stronger.
But it does not by itself settle IME transaction truth, edit-path receipts, or replayable cross-toolkit text-input evidence.

### AccessKit proves the upward export vocabulary exists
AccessKit already has text position/selection concepts.
That makes the missing crate more specific: a reusable lower layer that can export honest text semantics upward and declare when a mirror is still required.

### Existing toolkit glue proves the gap is operational, not theoretical
`bevy_egui` handling around `Window::set_ime_allowed` and wrapped IME messages is a good example of useful but toolkit-specific glue.
The missing crate is the **shared product layer** above such one-off integrations.

## Design goals

1. **Toolkit-neutral core** — works for immediate-mode and retained-mode stacks.
2. **Transaction honesty** — preedit/commit/cancel/replacement truth is first-class.
3. **Selection honesty** — grapheme/word/line/caret policy is explicit.
4. **Backend honesty** — adapters emit capability receipts instead of fake support claims.
5. **Edit-path honesty** — native, hidden-input, EditContext, and delegated editable surfaces stay distinguishable.
6. **Geometry honesty** — candidate-anchor and bounds synchronization are reviewable.
7. **Accessibility-ready** — export enough value/selection semantics to feed authoring-side accessibility work.
8. **Replayability** — failures travel as transcripts and bundles.

## Explicit non-goals

- becoming a layout/shaping engine,
- becoming a full widget toolkit,
- replacing platform APIs,
- pretending Web IME is already native-equivalent,
- pretending canvas text is automatically accessible,
- or flattening all text behavior into one “supports text” checkbox.

## Proposed architecture

```text
textinput-model/        # transactions, selections, edit policies
textinput-unicode/      # grapheme/word/line helpers
textinput-winit/        # native adapter + capability receipts
textinput-web/          # hidden-input + EditContext adapters + web-path receipts
textinput-accesskit/    # value/selection export helpers + mirror declarations
textinput-replay/       # transcript import/export + deterministic replay
cargo-textinput/        # replay, doctor, diff, bundle
```

## Core artifacts

### `ime-transaction.report.json`
Captures:
- preedit/update/commit/cancel classes,
- replacement ranges,
- overlap/dedup handling,
- leaked key-release normalization where relevant,
- and manual-review boundaries.

### `selection-contract.report.json`
Captures:
- grapheme-safe deletion,
- word/line navigation policy,
- anchor/head stability,
- replacement-range truth,
- and visual-vs-logical policy declaration.

### `backend-capability.receipt.json`
Captures:
- backend/runtime identity,
- adapter strategy,
- supported versus approximate versus unsupported surfaces,
- and upstream references where the adapter is constrained by known issues.

### `web-edit-path.receipt.json`
Captures:
- focus/composition owner,
- visible versus editable surface identity,
- hidden-input versus EditContext versus DOM delegate,
- and whether an offscreen/parallel a11y mirror is required.

### `selection-geometry.report.json`
Captures:
- caret/selection/character-bounds updates,
- candidate-anchor precision,
- inline versus detached preedit rendering,
- fullscreen/transformed-surface drift,
- and mirror/a11y reflection truth.

## Minimum lovable MVP

A lovable `0.1` should ship:

- one reusable engine for transactions + selection,
- one native `winit` adapter,
- one web hidden-input adapter,
- one experimental EditContext adapter behind an explicit unstable flag,
- one replay format,
- one bundle format,
- and four proving-ground scenarios:
  - native IME/key-event overlap,
  - native leaked key-release normalization,
  - web candidate-anchor/fullscreen fallback honesty,
  - EditContext canvas path with explicit bounds + mirror declaration.

## De-risk plan

1. Start with transcript replay and the engine model before building a full widget demo.
2. Prove that leaked-key and replacement-range flows can be classified without toolkit-specific code.
3. Keep word/line movement policy explicit rather than pretending there is one universal behavior.
4. Keep hidden-input and EditContext web paths visibly separate.
5. Export minimal AccessKit-facing text semantics early, but label unsupported/manual-review zones clearly.

## Scorecard

- **Impact:** 5/5 — every serious Rust GUI/editor stack touches this seam.
- **Neglectedness:** 5/5 — there is still no shared boring default for IME/composition/selection across native and web.
- **Feasibility:** 4/5 — a focused engine + receipts + replay MVP is buildable without solving all of editing.
- **Adoptability:** 4/5 — adapters can meet toolkits where they are.
- **Sustainability:** 3/5 — platform churn is real, but the core can stay small if receipts remain explicit.
- **Differentiation:** 5/5 — the sharp idea is not “text editing in Rust”, but **transaction truth + selection truth + edit-path truth + geometry truth + replayable evidence**.

## Open questions

- Which parts of word/line navigation should be engine-owned versus layout-owned?
- How much of bidi cursor movement belongs in `0.1`, and how much should stay manual-review territory?
- What is the narrowest AccessKit export contract that still helps toolkits avoid bespoke text-selection semantics?
- How should clipboard/paste/undo flows be represented without growing into a full editor framework too early?
- Which parts of EditContext integration belong in stable `0.1`, and which should stay explicit experimental receipts only?

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
