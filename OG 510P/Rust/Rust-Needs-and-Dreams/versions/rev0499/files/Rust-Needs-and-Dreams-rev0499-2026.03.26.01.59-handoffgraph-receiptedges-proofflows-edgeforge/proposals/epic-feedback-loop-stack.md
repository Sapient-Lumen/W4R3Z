# Epic Proposal: Feedback Loop Stack (`cargo innerloop` + `feedback-loop-pack/v0`)

## One-sentence pitch
Make Rust iteration review boring by standardizing a portable boundary that keeps **session identity, build-state evidence, debug evidence, and consumer summaries** distinct instead of forcing every team to reconstruct the developer loop from shell history, editor workarounds, rebuild logs, debugger folklore, and issue-thread archaeology.

## Deliverables
- reference command:
  - `cargo innerloop`
- schemas:
  - `feedback-loop-brief/v0`
  - `feedback-loop-session/v0`
  - `feedback-loop-pack/v0`
  - `feedback-loop-diff/v0`
  - `feedback-loop-handoff/v0`
- adapters/importers for:
  - `build-state-pack/v0`
  - `impact-pack/v0`
  - `build-doctor-pack/v0`
  - `diagnostic-pack/v0`
  - `obs-pack/v0`
  - `debug-pack/v0`
  - `debuggability-pack/v0`
  - optional `change-slice/v0`, `edit-application-report/v0`, `semctx-pack/v0`
  - optional replay / incident / test attachments
- docs:
  - Cargo ↔ rust-analyzer coexistence guide
  - build-dir / target-dir / debug-info tradeoff guide
  - build-session → debugger handoff guide
  - issue/support/assistant consumer-lossiness guide

## Why now (signals)
- The 2025 State of Rust survey still says resource usage remains one of the leading productivity problems and says debugging remains a major problem, while also saying online docs remain canonical and LLM/tool usage is rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2025 build-performance survey says workflow differences matter, says more than 35% of users consider IDE and Cargo blocking one another to be a big problem, and says full debug info makes disk usage and build/link times worse.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Cargo build-analysis goal is explicitly about recording metadata across invocations, linking it with identifiers like `CARGO_RUN_ID`, and eventually unlocking build replay for debugging.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout goal explicitly treats rust-analyzer coexistence, finer-grained locking, target-dir GC, and cross-workspace cache sharing as first-class goals.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- rust-analyzer’s own configuration docs and FAQ say you can avoid Cargo lock contention by using a separate target directory, but only at the cost of duplicated artifacts, which is exactly the kind of inner-loop tradeoff that should become first-class evidence rather than hidden folklore.
  https://rust-analyzer.github.io/book/configuration.html
  https://rust-analyzer.github.io/book/faq.html
- The March 2026 build-dir-layout-v2 testing call says many tools still rely on unspecified Cargo details because some missing features force them to.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The 2026 debugging survey says the ecosystem still lacks strong multi-debugger, multi-OS, async-aware debugging support and that maintaining quality across debugger versions and std-layout changes is hard.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo 1.94 says plugins matter and keeps expanding machine-readable report surfaces with `cargo report rebuild`, `cargo report sessions`, and improved timings.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## The missing seam
This proposal is best read as the concrete product-direction candidate for the archive’s newly promoted **Rust inner-loop contract**. It does **not** claim that the feedback loop is now more important than Build-State Evidence overall; it claims that this is the clearest next bundle-shaped contribution beneath the build/debug band.

Rust is finally getting better raw evidence for the two biggest parts of the iteration loop:
- **build-state evidence** (sessions, timings, rebuild causes, layout/locking/caching facts), and
- **debug evidence** (diagnostics, telemetry, debugger tuple results, side-channel inspection, repro handoffs).

What it still lacks is the thin layer that says:
1. which loop session are we talking about?
2. which build evidence belongs to it?
3. which debug evidence belongs to it?
4. which tradeoffs were intentional?
5. what may a consumer honestly summarize?

Without that, maintainers, support engineers, IDE authors, and assistants still have to reconstruct the answer from partial tools.

## Reference CLI shape
- `cargo innerloop record`
  - emit `feedback-loop-session/v0` for one concrete loop session
- `cargo innerloop attach-build`
  - import build-state evidence and link it to the session
- `cargo innerloop attach-debug`
  - import debug/diagnostic evidence and link it to the session
- `cargo innerloop diff --against <prior-pack|ref|path>`
  - emit `feedback-loop-diff/v0`
- `cargo innerloop render --for <issue|support|docs|ci|assistant|editor>`
  - emit `feedback-loop-handoff/v0`
- `cargo innerloop pack`
  - produce `feedback-loop-pack/v0`
- `cargo innerloop verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace Cargo, rust-analyzer, debuggers, tracing stacks, or assistant tooling.

## What `feedback-loop-pack/v0` should contain
- `manifest.json`
- `feedback-loop-brief.json`
- one or more `feedback-loop-session.json`
- imported build-state evidence pointers or attachments
- imported debug evidence pointers or attachments
- optional change/edit/semantic imports
- optional `feedback-loop-diff.json`
- one or more `feedback-loop-handoff.json` summaries
- checksums, provenance, freshness, and generator identity

## Design principles
- **One session first.** Trend dashboards and organization analytics come later.
- **Build facts are not debug facts.** Do not let diagnosis overwrite Cargo evidence.
- **Runtime-side inspection is not native debugger parity.** Keep the lane identity explicit.
- **Tradeoffs must stay visible.** Separate target dirs, reduced debug info, profile changes, and tuple-specific workarounds are core evidence.
- **Consumers import bounded conclusions.** Issue trackers, docs, support pages, CI systems, assistants, and editors each need their own summaries.
- **Companion-tool posture stays honest.** A plugin/pack layer is already a success.

## Early implementation order
1. session identity lane
2. editor / CLI coexistence lane
3. build → debugger handoff lane
4. issue / support / docs consumer lane
5. assistant/editor consumer lane

That order follows the real pressure in the ecosystem: first make one iteration legible, then connect it to debugging evidence, then make downstream summaries honest.

## Non-goals
- a universal IDE backend;
- a local daemon that owns all builds and debugging;
- a hosted DX portal;
- an assistant that replaces Cargo or debuggers;
- flattening build pain and debugging pain into one badge.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what exact iteration session is under review;
- what changed, if that is known;
- what Cargo/build evidence exists for it;
- what debugger/diagnostic evidence exists for it;
- what tradeoffs were intentional;
- what changed versus the prior session or release;
- and what a given consumer may safely summarize,

without scraping shell history, IDE state, issue threads, or CI logs.

## Read this with
- `design/feedback-loop-stack.md`
- `design/feedback-loop-pilot-program.md`
- `design/build-state-evidence-stack.md`
- `design/debuggability-stack.md`
- `design/edit-workflow-kit.md`
- `design/semantic-context-kit.md`
