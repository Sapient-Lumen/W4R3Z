# Frontier salience refresh — 2026-03-22 (196)

## Why P-0491 deserved another pass

The archive already had asset manifests, backend matrices, render goldens, and embed-vs-external routing for **P-0491 Debugger Visualizer Compatibility Kit**.
The remaining weak point was not “can a crate ship visualizers?”.
It was **activation-route and formatter-origin honesty**.

Current official and primary sources make that gap concrete:

1. The Rust Reference keeps `#[debugger_visualizer]` stable, allows multiple visualizer files, and still limits embedded NatVis support to `-windows-msvc` targets.
2. The rustc dev guide now explains that `rust-gdb`, `rust-lldb`, and `rust-windbg.cmd` are support scripts that locate toolchain visualizer scripts and launch debuggers with the right preload arguments.
3. That same dev-guide page says `#![debugger_visualizer]` currently works for GDB and NatVis, while LLDB is **not currently supported** through the Rust-embedded lane and instead points toward separate formatter mechanisms.
4. GDB’s current manual still makes `auto-load safe-path` a first-class security gate and says declined files are not loaded when the path is not trusted.
5. LLDB’s formatter architecture remains its own multi-kind system (formats, summaries, filters, synthetic children) rather than a Rust-embedded visualizer lane.
6. The 2026 Rust debugging survey still calls out multi-debugger support and quality visualizers as active needs, and warns that debugger support can regress across debugger versions and representation changes.

That makes the sharper missing value here less “another pretty-printer tool” and more a **support-contract layer for route truth, formatter origin, and portable bundle completeness**.

## Main ranked takeaway

**P-0491 Debugger Visualizer Compatibility Kit** remains a worthy medium-high lane because it can now offer something adjacent crates still do not:

- an `activation-route.receipt` for *how* a visualizer was expected to become active,
- a `formatter-origin.receipt` for *where* the effective formatter came from,
- and a `visualizer-support-bundle.manifest` that keeps assets, activation facts, formatter origin, backend verdicts, and drift separate.

## Why this beat adjacent ideas this pass

It beat a broader debug-support pass because **P-0486** already owns posture, sidecars, backend observations, and source-material handoff.
What remained missing here was the smaller question: *did the effective visualization come from an embedded crate asset, a toolchain support script, debugger-local formatter config, or not at all?*

It beat another generic debugger survey pass because the official substrate is now explicit enough that the archive should ship artifact vocabulary, not more prose.

It beat a source-path or sidecar pass because the main unresolved ambiguity in this lane was not “are sources available?” or “is debuginfo present?”, but “what formatter route is this verdict actually talking about?”

## Boundaries to keep sharp

P-0491 should now own:

1. asset discovery,
2. activation-route truth,
3. formatter-origin authority,
4. backend support verdicts,
5. tiny render-golden comparisons,
6. release-to-release visualizer drift,
7. and portable visualizer-support bundles.

It should not silently become:

- a universal debugger installer,
- a generic debugger doctor,
- a broad symbol/source/debug-profile support contract,
- or a full debugger-extension platform.
