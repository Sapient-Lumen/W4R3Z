# Frontier salience scan — 2026-03-08 (thirteenth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it made **P-0046 buildscript-ux-kit** more implementation-ready.
The current Cargo substrate is now explicit enough that the archive should stop treating build-script UX as a vague “logs are noisy” complaint.
The missing layer is a **portable support bundle** above Cargo’s directives, JSON output, visibility rules, and still-noisy real-world failure presentation.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
4. **P-0046 buildscript-ux-kit**
5. **P-0490 Cargo Lock Contention Witness Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0035 cargo-build-insights**
8. **P-0489 Cargo Build-Dir Consumer Transition Kit**
9. **P-0059 buildscript-testkit**
10. **P-0058 native-deps-kit**

## Why P-0046 improved

Five current facts matter here:

- the build-script docs explicitly say `cargo::warning` is hidden by default for non-path dependencies unless the build fails or the user uses `-vv`,
- Cargo JSON already includes `build-script-executed` output,
- those JSON messages may reflect cached build-script results even when the script did not run,
- `cargo::error` exists but real Cargo issues still report noisy output when scripts exit non-zero,
- and unstable Cargo already has `metabuild` plus `multiple-build-scripts`, which means downstream tooling should model units/observations rather than a forever-single-file worldview.

That means **P-0046** does not need to invent a new build-script protocol.
It can be precise about its 0.1 contract:

- one redaction-aware `buildscript-report.json`,
- one human-first `buildscript-summary.txt`,
- one workspace-focused `policy-gate.report.json`,
- optionally one `notes.md`,
- plus explicit capture-origin and message-visibility semantics.

## What should happen next

The best next passes on this frontier should prefer:

1. fixture scenarios for hidden warnings, `cargo::error` + non-zero exit, rerun-noise overload, cached-output import, and redaction,
2. conservative capture-origin vocabulary,
3. explicit visibility semantics for messages,
4. and alignment with **P-0059 / P-0058** without merging them.

They should **not** add another generic build-script/native-build idea unless it is clearly distinct from:

- support/report bundles,
- fixture-driven build-script testing,
- or native dependency contracts.

## Sources

- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo external-tools JSON: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo unstable features (`metabuild`, `multiple-build-scripts`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue #10159: https://github.com/rust-lang/cargo/issues/10159
- Cargo issue #15038: https://github.com/rust-lang/cargo/issues/15038
- Cargo issue #15792: https://github.com/rust-lang/cargo/issues/15792
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
