# Frontier salience scan — 2026-03-08 (fifteenth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it made **P-0491 Debugger Visualizer Compatibility Kit** much more implementation-ready.
The current Rust/GDB substrate is now explicit enough that the archive should stop treating visualizer compatibility as a vague debugger-automation wish.
The sharper gap is a **portable compatibility bundle** above stable visualizer embedding, backend-specific trust rules, and small render goldens.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
4. **P-0486 Debuggability Support Contract Kit**
5. **P-0046 buildscript-ux-kit**
6. **P-0490 Cargo Lock Contention Witness Kit**
7. **P-0035 cargo-build-insights**
8. **P-0491 Debugger Visualizer Compatibility Kit**
9. **P-0489 Cargo Build-Dir Consumer Transition Kit**
10. **P-0059 buildscript-testkit**

## Why P-0491 improved

Five current facts matter here:

- stable `#[debugger_visualizer]` means visualizer assets are now real mainstream substrate,
- the Rust reference explicitly documents NatVis and GDB pretty-printer assets,
- the same reference explicitly says NatVis embedding only supports `-windows-msvc` targets,
- the same reference explicitly says embedded GDB pretty printers are not auto-loaded by default,
- and the GDB manual makes the trust model visible through `auto-load safe-path`, including declined-script warnings when trust is missing.

That means **P-0491** no longer needs to talk like a generic debugger tooling idea.
It can be precise about a 0.1 contract:

- one `visualizer-policy.toml`,
- one `visualizer-assets.manifest.json`,
- one `backend-matrix.receipt.json`,
- one `render-golden.report.json`,
- one `embed-vs-external.report.json`,
- optionally one `visualizer-drift.diff.json`,
- and one compact `notes.md`.

## What should happen next

The best next passes on this frontier should prefer:

1. scenario bundles for MSVC NatVis success, GDB safe-path refusal, external/manual backend routing, and malformed assets,
2. conservative verdict vocabulary (`supported`, `unsupported_by_design`, `safe_path_blocked`, `asset_failed`, `backend_failed`, `manual_review_required`),
3. vocabulary alignment with **P-0486 / P-0493** without merging them,
4. and redaction/provenance rules strong enough for real support handoffs.

They should **not** add another generic debugger proposal unless it is clearly distinct from:

- broad debuggability support posture,
- source-path/source-component diagnosis,
- or visualizer compatibility receipts.

## Sources

- Rust reference: debugger visualizers: https://doc.rust-lang.org/reference/attributes/debugger.html
- GDB manual: auto-load safe path: https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html
- Rust release notes: https://doc.rust-lang.org/beta/releases.html
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
