# Frontier salience scan — 2026-03-08 (sixteenth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it sharpened **P-0491 Debugger Visualizer Compatibility Kit** one step further by making the backend story more honest.
The important distinction is now explicit: **embedded asset presence**, **backend activation/trust**, and **actual compatibility** are not the same thing.
That keeps the crate small and makes the support artifact more believable.

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

## Why P-0491 got sharper

Six current facts matter here:

- stable `#[debugger_visualizer]` means visualizer assets are real mainstream Rust substrate,
- the Rust reference explicitly documents NatVis and GDB pretty-printer assets,
- the same reference explicitly says NatVis embedding only supports `-windows-msvc` targets,
- the same reference explicitly says embedded GDB pretty printers are not auto-loaded by default,
- the GDB manual makes trust/activation rules visible through `auto-load safe-path`,
- and LLDB’s official formatter docs expose summaries, filters, synthetic children, and Python-backed formatters as real **external formatter substrate** rather than a Rust-embedded lane.

That means **P-0491** should now be read as a crate that can say, separately:

- the asset is present,
- the backend lane is intended,
- activation or trust was missing,
- or the backend is intentionally external/manual rather than embedded.

## What should happen next

The best next passes on this frontier should prefer:

1. more scenario bundles where activation/config differs from asset quality,
2. explicit provenance and confidence fields on backend verdicts,
3. reuse of **P-0486** support-posture facts without collapsing into that crate,
4. and conservative LLDB handling until there is better official Rust-side embedding evidence.

They should **not** drift into:

- a universal debugger-integration suite,
- a giant formatter pack,
- or fake “all backends are equal” parity claims.

## Sources

- Rust reference: debugger visualizers: https://doc.rust-lang.org/reference/attributes/debugger.html
- GDB manual: auto-load safe path: https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html
- LLDB variable formatting: https://lldb.llvm.org/use/variable.html
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
