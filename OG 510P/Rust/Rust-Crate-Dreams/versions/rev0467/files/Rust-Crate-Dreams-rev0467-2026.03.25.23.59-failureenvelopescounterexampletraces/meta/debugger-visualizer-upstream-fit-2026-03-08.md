# Debugger visualizer upstream fit — 2026-03-08

## Main judgment

The archive should now treat **P-0491 Debugger Visualizer Compatibility Kit** as a crate that sits **above real upstream debugger-visualizer substrate**, not as a fantasy debugger platform.

The current upstream story is already concrete enough:

- Rust has stable `#[debugger_visualizer]` support.
- The Rust reference explicitly documents two asset families: **NatVis** and **GDB pretty-printer scripts**.
- The same reference explicitly narrows NatVis embedding to `-windows-msvc` targets.
- The same reference explicitly warns that embedded GDB pretty printers are **not automatically loaded** unless GDB auto-load safe-path trust is configured.
- The 2026 Rust debugging survey makes cross-debugger support, visualizers, async debugging, and evaluator quality an active project concern.
- LLDB’s official formatter model already exposes summaries, filters, synthetic children, and Python-backed routes as real external substrate.

So the sharper missing layer is **not** “Rust needs visualizer syntax” and not “we need one giant debugger product.”
The sharper missing layer is a **receiver-facing compatibility bundle** that can say:

1. which visualizer assets exist,
2. which backend families they intend to support,
3. whether a probe succeeded, failed, or was blocked by debugger trust policy,
4. which backends are intentionally external/manual lanes,
4.5. which backend lanes depend on activation/config rather than asset bytes,
5. and what changed between two releases or toolchain matrices.

## Three upstream truths the crate should encode

### 1. NatVis is not a generic backend lane

The Rust reference is explicit that embedding NatVis via `#[debugger_visualizer]` only supports `-windows-msvc` targets.
That should become a first-class policy fact in the bundle, not a buried note.

The crate should therefore make it easy to say:

- `supported` on the intended MSVC lane,
- `unsupported_by_design` on non-MSVC targets,
- and `manual_review_required` only when the tool cannot classify safely.

### 2. GDB can refuse to load an otherwise-correct embedded printer

The Rust reference already warns that embedded GDB pretty printers are not auto-loaded by default.
The GDB manual makes the trust model more explicit: scripts outside the trusted auto-load safe-path are declined unless the user or environment config changes.

That means a worthy crate should **not** flatten every GDB rendering failure into `asset_failed`.
It should have a dedicated lane such as `safe_path_blocked` or an equivalent conservative diagnosis.

### 3. LLDB should stay an explicit external/manual lane unless evidence gets stronger

The Rust reference does not document an LLDB embedding lane for `#[debugger_visualizer]`.
LLDB’s own docs instead expose type summaries, filters, synthetic children, and Python-backed formatters as command/script-driven formatter substrate.

That means the archive should prefer an explicit `external_formatter_route` or `manual_review_required` lane for LLDB-family support instead of pretending embedded-asset parity exists.

### 4. Visualizer compatibility is narrower than broad debug support

P-0486 should answer: *is this build broadly interactive-debugger-friendly?*
P-0493 should answer: *can the source paths actually be resolved?*
P-0491 should answer: *did the visualizer asset itself work across the intended backend lanes?*

That separation is now easier to keep honest because upstream docs already expose the relevant boundaries.

## What the first boring bundle should contain

The crate’s first useful output should be a small, reviewable bundle:

- `visualizer-policy.toml`
- `visualizer-assets.manifest.json`
- `backend-matrix.receipt.json`
- `render-golden.report.json`
- `embed-vs-external.report.json`
- `visualizer-drift.diff.json`
- `notes.md`

That is enough to make release review and support handoffs much less folklore-driven.

## Recommended 0.1 stance

The first version should be conservative:

- Start with NatVis and GDB only.
- Treat backends not covered by the Rust reference as `external_formatter_route`, `unsupported_by_design`, or `manual_review_required`.
- Model safe-path/autoload refusal explicitly.
- Keep render goldens tiny and fixture-oriented.
- Import broader support facts from P-0486 when available, but do not require them.

## What this proposal should not become

It should not become:

- a full debugger integration suite,
- a new debugger UI,
- a universal pretty-printer pack,
- or a broad support-posture doctor that duplicates P-0486.

## Sources

- Rust reference: `#[debugger_visualizer]`: https://doc.rust-lang.org/reference/attributes/debugger.html
- GDB manual: auto-load safe path: https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html
- Rust release notes: https://doc.rust-lang.org/beta/releases.html
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- LLDB variable formatting: https://lldb.llvm.org/use/variable.html
