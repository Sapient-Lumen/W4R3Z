# Epic Proposal: Debuggability Stack (`cargo debuggability` + `debuggability-pack/v0`)

## Why this is worthy
Rust projects increasingly need to publish **debuggability claims that can be reviewed like contracts instead of reconstructed from folklore**.

The current signals are unusually aligned:
- The 2025 State of Rust survey still lists debugging among the leading productivity problems, says online documentation remains the preferred canonical reference, and notes that many users do find compiler error explanations useful.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 Rust debugging survey says first-class support would require multiple debugger versions across operating systems, high-quality visualizers, first-class async debugging, and Rust expression evaluation. It also says keeping those working across debugger releases and std-layout changes is hard.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The Rust Reference exposes `#[debugger_visualizer]`, which means debugger-facing presentation artifacts are part of Rust’s public ergonomics surface, not just debugger-specific trivia.
  https://doc.rust-lang.org/reference/attributes/debugger.html
- The rustc dev guide documents debug info as a real compiler output path and documents debuginfo tests with debugger-specific commands and checks across families such as GDB, LLDB, and CDB. That is strong evidence that debugger support is tuple-specific and testable rather than one generic “works in the debugger” claim.
  https://rustc-dev-guide.rust-lang.org/debuginfo/intro.html
  https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
- Tokio’s tracing guidance explicitly positions `tracing` as a way to emit distributed traces, logs, and Tokio Console debugging signals, while Tokio Console itself is explicit that it is a diagnostics/debugging tool for async Rust built on runtime instrumentation. That is a valuable lane, but it is not the same thing as native debugger parity.
  https://tokio.rs/tokio/topics/tracing
  https://tokio.rs/blog/2021-12-announcing-tokio-console
- Cargo 1.94 continues expanding structured reports (`cargo report timings`, `cargo report rebuild`, `cargo report sessions`), which means debugging workflows can increasingly import machine-readable build/run context rather than relying only on screenshots and issue-thread archaeology.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

But the ecosystem still has no single honest handoff for **debuggability truth**.
That means maintainers, support engineers, release reviewers, docs authors, compatibility systems, and assistants still have to reconstruct the answer from:
- failure docs and compiler/application diagnostics,
- tracing/logging configuration,
- Tokio Console or runtime-specific inspection setup,
- debugger setup pages and visualizer files,
- ad hoc repro projects,
- and scattered incident or issue artifacts.

The missing contribution is a thin composition layer above those pieces, not another debugger, another telemetry backend, another pretty-error crate, or another IDE plugin.

## Proposal
Define a **Debuggability Stack** with:
- a reference companion CLI, `cargo debuggability`;
- a thin linked bundle, `debuggability-pack/v0`;
- imported evidence from:
  - `diagnostic-pack/v0` attachments,
  - `obs-pack/v0` attachments,
  - `debug-pack/v0` and debugger capability artifacts,
  - optional replay / incident / support / compatibility attachments;
- stable debuggability-facing artifacts:
  - `debug-subject/v0`
  - `debug-lane-register/v0`
  - `debug-evidence-register/v0`
  - `debug-escalation-report/v0`
  - `debug-change-report/v0`
  - `debug-consumer-summary/v0`
  - `debuggability-pack/v0`

## Reference CLI shape
- `cargo debuggability export`
  - emit `debug-subject/v0` and `debug-lane-register/v0` for one binary / service / crate / workspace subject
- `cargo debuggability check`
  - import diagnostic / observability / debugger attachments and emit `debug-evidence-register/v0`
- `cargo debuggability diff --against <prior-pack|ref|path>`
  - emit `debug-change-report/v0` comparing failure identity, runtime-correlation posture, debugger tuple posture, and handoff posture
- `cargo debuggability render --for <docs|support|release|compat|assistant|incident>`
  - emit `debug-consumer-summary/v0`
- `cargo debuggability pack`
  - produce `debuggability-pack/v0`
- `cargo debuggability verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace Diagnostic Surface Kit, Observability Kit, Debugger Experience Kit, Replay Kit, Incident Kit, or native debugger/runtime-specific tools.

## What `debuggability-pack/v0` should contain
- `manifest.json`
- `debug-subject.json`
- `debug-lane-register.json`
- `debug-evidence-register.json`
- `debug-escalation-report.json`
- optional `debug-change-report.json`
- one or more `debug-consumer-summary.json` attachments
- imported diagnostic / observability / debugger / replay attachments or pointers
- checksums, provenance, freshness, and generator identity
- optional support / compatibility / release / incident pointers

## Design principles
- **Failure identity comes before runtime fishing.** Many issues should stop at checked diagnostics and clear help/docs.
- **Runtime evidence is not debugger evidence.** Logs, traces, and runtime inspection are not native stepping/evaluation claims.
- **Async side-channel inspection is not native debugger parity.** Tokio Console-style lanes are real and useful, but they stay distinct.
- **Debugger support is tuple-scoped.** Family, version, OS, target, toolchain, and visualizer posture all matter.
- **Consumers import bounded conclusions.** Docs, support pages, compatibility notes, release notes, incident packs, and assistants each need their own summaries.
- **Cargo-merger fantasies stay out of scope.** A useful companion layer is already a success.

## Early implementation order
1. failure-identity lane
2. debugger tuple-truth lane
3. runtime-correlation lane
4. repro / replay handoff lane
5. support / compatibility consumer lane

That order follows the real ecosystem pressure: first prove better everyday failure understanding, then honest debugger tuple truth, then telemetry correlation, then escalated repro handoff, and only after that broader downstream consumers.

## Non-goals
- a universal debugger abstraction layer;
- a new telemetry SDK or hosted backend;
- a replacement for `tracing`, Tokio Console, or debugger wrappers;
- a new error-handling framework;
- a giant hosted debugging portal;
- flattening diagnostics, observability, debugger support, and replay into one badge.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what failure identities are actually declared and checked;
- what runtime evidence should exist and how it correlates;
- what debugger tuples are really supported, partial, watch-only, or unsupported;
- what async/runtime inspection is side-channel rather than native debugger support;
- what escalation/handoff artifacts exist for harder failures;
- what changed since the prior release or support statement;
- and what a given consumer may safely say,

without scraping wiki pages, ad hoc issue templates, debugger folklore, and production dashboards.

## Read this with
- `design/debuggability-stack.md`
- `design/debuggability-pilot-program.md`
- `design/diagnostic-surface-kit.md`
- `design/observability-kit.md`
- `design/debugger-experience-kit.md`
- `design/debugger-pilot-program.md`
- `design/replay-kit.md`
- `design/incident-kit.md`
