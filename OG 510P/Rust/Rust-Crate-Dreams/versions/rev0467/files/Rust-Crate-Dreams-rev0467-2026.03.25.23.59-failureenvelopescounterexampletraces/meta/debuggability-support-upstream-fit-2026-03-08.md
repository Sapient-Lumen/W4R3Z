# Debuggability support upstream fit — 2026-03-08

## Main judgment

**P-0486 Debuggability Support Contract Kit** is now a better next non-Cargo incubation target than it was even a few days ago.

The reason is not that Rust suddenly lacks debuggers less.
The reason is that the official substrate is now explicit enough that the missing crate can be much smaller and more honest.

## Current upstream substrate that matters

### Cargo profiles already define most of the raw posture knobs

Cargo documents:

- `debug` levels ranging from `none` to `full`, with `line-tables-only` explicitly called out as enough for filename/line-number backtraces but not variable inspection,
- `split-debuginfo`, including the warning that Cargo and `rustc` may use different defaults,
- and `strip`, including the `debuginfo` and `symbols` modes.

That means the crate does not need to invent a settings vocabulary from scratch.
It needs to **normalize those settings into one support posture another human can review**.

### rustc already documents platform-specific sidecar realities

`rustc`’s codegen docs already say:

- Windows MSVC typically uses `*.pdb`,
- macOS typically uses `*.dSYM`,
- other Unix platforms may use `*.dwo` / `*.dwp`,
- and `strip=debuginfo` can leave backtraces mostly intact while making interactive debugging ineffective.

That means the crate does not need to promise universal debugger automation.
It needs to provide an **artifact manifest plus conservative classification**.

### Stable debugger visualizers are real substrate

The stable `#[debugger_visualizer]` attribute means NatVis and GDB-script assets are now a real part of Rust’s official debugging surface.
That matters because builds can be “debuggable” in meaningfully different ways depending on whether these assets are present, embedded, missing, or targeted at the wrong backend family.

### Path hygiene is becoming more explicit, not less

Cargo’s unstable `trim-paths` support and Rust’s source remapping surfaces mean path privacy and source lookup are now first-class enough to record in receipts.
P-0486 should record conservative path-hygiene hints, while deeper source diagnosis remains the narrower follow-on of P-0493.

### Official Cargo behavior shifts can silently change support posture

Cargo’s changelog note that disabling debuginfo now implies `strip = "debuginfo"` when `strip` is not set is exactly the kind of subtle shift that a human maintainer can miss and a support-contract receipt should catch.

## What the crate should provide other people

A good 0.1 should hand other people:

1. one `debuggability.receipt.json`,
2. one `symbol-layout.manifest.json`,
3. one `visualizer.manifest.json` when applicable,
4. one `support-posture.report.json`,
5. optionally one `debuggability-drift.diff.json`,
6. and one tiny `notes.md`.

That is enough to answer most support/release questions without becoming another debugger platform.

## What this crate should not try to own

It should not try to own:

- debugger session orchestration,
- crash collection backends,
- full source remapping diagnosis,
- or cross-debugger golden rendering.

Those are adjacent seams, not the center of gravity.

## Relationship to the rest of the stack

- **P-0486** should answer: *what debugging posture did this build actually ship?*
- **P-0493** should answer: *why can or can’t the debugger find the expected sources?*
- **P-0491** should answer: *did the visualizer asset work across the intended debugger families?*

If a future pass blurs these back together, that is a repo regression.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://doc.rust-lang.org/rustc/codegen-options/index.html
- https://doc.rust-lang.org/reference/attributes/debugger.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
- https://doc.rust-lang.org/cargo/CHANGELOG.html
