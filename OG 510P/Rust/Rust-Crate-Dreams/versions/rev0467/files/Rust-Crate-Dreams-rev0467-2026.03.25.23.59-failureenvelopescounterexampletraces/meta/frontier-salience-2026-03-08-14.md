# Frontier salience scan — 2026-03-08 (fourteenth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it made **P-0486 Debuggability Support Contract Kit** much more implementation-ready.
The current Rust/Cargo substrate is now explicit enough that the archive should stop treating debug support as a vague “better debuggers” wish.
The sharper gap is a **portable support bundle** above Cargo profile settings, platform-specific symbol sidecars, stable debugger visualizers, and path-hygiene drift.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
4. **P-0486 Debuggability Support Contract Kit**
5. **P-0046 buildscript-ux-kit**
6. **P-0490 Cargo Lock Contention Witness Kit**
7. **P-0035 cargo-build-insights**
8. **P-0489 Cargo Build-Dir Consumer Transition Kit**
9. **P-0059 buildscript-testkit**
10. **P-0058 native-deps-kit**

## Why P-0486 rose

Five current facts matter here:

- Cargo profiles already define the main raw posture knobs (`debug`, `split-debuginfo`, `strip`).
- Cargo explicitly warns that its `split-debuginfo` defaults can differ from `rustc`’s defaults.
- `rustc` documents platform-specific sidecar outputs (`pdb`, `dSYM`, `dwo`, `dwp`) and warns that `strip=debuginfo` may preserve backtraces while making interactive debugging ineffective.
- stable `#[debugger_visualizer]` means visualizer assets are a real language surface.
- the 2026 debugging survey shows that debugger support quality, visualizers, async debugging, and expression evaluation remain active project concerns.

That means **P-0486** no longer needs to sound like an essay topic.
It can be precise about a 0.1 contract:

- one `debuggability.receipt.json`,
- one `symbol-layout.manifest.json`,
- one `visualizer.manifest.json`,
- one `support-posture.report.json`,
- optionally one `debuggability-drift.diff.json`,
- and one compact `notes.md`.

## What should happen next

The best next passes on this frontier should prefer:

1. scenario bundles for Windows/MSVC `pdb`, macOS `dSYM`, Linux `line-tables-only`, and policy-weaker-than-expected cases,
2. conservative evidence and confidence fields,
3. vocabulary alignment with **P-0493 / P-0491** without merging them,
4. and redaction rules strong enough for real support handoffs.

They should **not** add another generic debugging proposal unless it is clearly distinct from:

- broad debuggability support posture,
- source-path and source-component diagnosis,
- or visualizer compatibility receipts.

## Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo profiles: https://doc.rust-lang.org/cargo/reference/profiles.html
- `rustc` codegen options: https://doc.rust-lang.org/rustc/codegen-options/index.html
- Rust reference: debugger visualizers: https://doc.rust-lang.org/reference/attributes/debugger.html
- Cargo unstable features (`trim-paths`): https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
