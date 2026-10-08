# Design: Debuggability Stack (Diagnostic Surface + Observability + Debugger Experience)

## Goal
Treat **Diagnostic Surface Kit**, **Observability Kit**, and **Debugger Experience Kit** as one shared **Debuggability Stack**.

The missing contribution is not another debugger, another tracing bootstrap crate, another pretty-error layer, or another issue template.
It is a portable, reviewable stack that keeps four distinct truths separate while letting them compose:
- **failure-identity truth** — what stable diagnostics, help/docs pointers, redaction rules, and public renderings a program claims to expose;
- **runtime-correlation truth** — what logs/traces/metrics/runtime-diagnostic signals were actually emitted, under what config, with what schema and privacy posture;
- **debugger-tuple truth** — what debugger family/version/OS/target/toolchain tuple was actually tested, with what visualizers, async inspection, and expression-evaluation posture;
- **repro/handoff truth** — what transcripts, minimized repros, issue packs, replay imports, or support/compatibility consumers may legitimately conclude.

That separation matters because Rust debugging pain is almost never one missing tool:
- many failures should stop at a stable diagnostic with good help and a reproducible fixture;
- some need logs, traces, runtime metadata, or Tokio-Console-style async inspection;
- some need native debugger tuple truth with explicit visualizer and expression-eval caveats;
- and some need replay or incident packs, but only after the earlier lanes proved insufficient.

## Why this seam matters now
Current Rust signals are unusually aligned around a real debuggability substrate:
- The 2025 State of Rust survey still says debugging is one of the leading non-trivial productivity problems, says online docs remain the preferred canonical reference, and says many users do find compiler error-code explanations useful. That means supportive failure surfaces and trustworthy debug evidence matter at the language-ecosystem level rather than as local polish.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 debugging survey makes the missing contract explicit: truly strong support means multiple debugger versions across operating systems, high-quality visualizers, first-class async debugging, and Rust expression evaluation. It also says keeping that support working across debugger releases and std-layout changes is a real challenge.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust’s vision work explicitly recommends doubling down on extensibility for **supportive interfaces** and compilation workflow. That is direct support for investing in diagnostics, guidance, and debugging-support substrates rather than only more expressive type-level abstraction.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Cargo is actively making machine-facing reporting more real through `cargo report timings`, `cargo report rebuild`, and `cargo report sessions`. That does not solve debugging by itself, but it means the surrounding evidence story can now import more trustworthy build/run context instead of relying only on screenshots and tribal lore.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

Taken together, ideal Rust needs a debuggability layer that is broader than one debugger plugin but narrower than “one mega observability platform.”

## What each kit should own
### Diagnostic Surface Kit
[`design/diagnostic-surface-kit.md`](./diagnostic-surface-kit.md) owns:
- stable/public diagnostic identity,
- help/docs metadata,
- redaction/exposure policy,
- checked CLI/JSON/HTTP renderings,
- failure-surface drift.

Its question is:
> what failure did the program say happened, and how was that exposed safely and consistently?

### Observability Kit
[`design/observability-kit.md`](./observability-kit.md) owns:
- telemetry intent and profile,
- exporter/runtime/config truth,
- correlation policy,
- validation vectors,
- explainable report artifacts.

Its question is:
> what runtime evidence was actually emitted, with what schema, pipeline, and privacy posture?

### Debugger Experience Kit
[`design/debugger-experience-kit.md`](./debugger-experience-kit.md) owns:
- debugger tuple identity,
- capability reports,
- visualizer packs,
- async-inspection profiles,
- expression-evaluation posture,
- regression packs.

Its question is:
> what can this debugger tuple actually observe and do for this subject?

### Replay / incident / async-reliability consumers
[`design/replay-kit.md`](./replay-kit.md), [`design/incident-kit.md`](./incident-kit.md), and the async-reliability stack remain **imports**, not absorbed subfields.

Their question is:
> once normal diagnostic / telemetry / debugger lanes are insufficient, what reproducible or operational handoff should happen next?

That boundary matters. The stack should improve debugging without pretending every debugging problem already deserves a replay engine or an incident process.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without spelunking CI logs, IDE folklore, debugger setup wikis, and production dashboards:
1. Which stable diagnostic or failure family actually fired?
2. Which logs/traces/runtime signals correlate with that failure, and were they configured intentionally?
3. Which debugger tuple was actually tested, and what remained partial or unsupported?
4. Was the relevant async/runtime state natively visible, side-channel visible, or not visible at all?
5. What minimized repro or handoff artifact now exists?
6. What support, docs, release, or compatibility consumers may safely import?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs both a ranked execution layer and an explicit epic candidate, captured in:
- [`design/debuggability-pilot-program.md`](./debuggability-pilot-program.md)
- [`proposals/epic-debuggability-stack.md`](../proposals/epic-debuggability-stack.md)

That pilot program should prove the stack in this order:
1. **failure-identity lane**
2. **debugger tuple-truth lane**
3. **runtime-correlation lane**
4. **repro / replay handoff lane**
5. **support / compatibility consumer lane**

That ordering is intentional.
The archive should not jump straight to a giant debugger compatibility lab, a full hosted observability service, or one universal “debugging health” score.
It should first prove that Rust projects can publish enough debuggability truth to make ordinary failures easier to understand and escalate honestly.

## Design principles
1. **Failure identity comes before forensics.** Many debug sessions should end at clear diagnostics rather than escalating into tracing or debugger spelunking.
2. **Runtime evidence is not debugger evidence.** Logs/traces/runtime inspection and native stepping/evaluation are related, but they are not interchangeable.
3. **Debugger support is tuple-scoped.** Support is a property of debugger version + OS + target + toolchain + visualizer/adapter setup, not a brand name.
4. **Replay is downstream of ordinary evidence.** Reproduction engines and incident packs should import prior truth instead of becoming the first and only debugging surface.
5. **Partial support must stay explicit.** `partial`, `watch`, `unsupported`, and `inconclusive` are legitimate outcomes.
6. **Consumers come after evidence.** Docs, support pages, release notes, compatibility claims, and assistants should import stack artifacts instead of paraphrasing them from memory.

## What an epic contribution would look like in practice
A serious contribution here now looks like a thin `cargo debuggability` / `debuggability-pack/v0` layer that imports diagnostic, observability, debugger, and replay/incident artifacts without flattening them.

Concretely, it should:
- make declared diagnostics, emitted telemetry, debugger capabilities, and repro packs reference the same subject identity;
- let CI and release review diff debugging-support posture instead of burying it in screenshots or broken wiki pages;
- make async inspection and native debugger support comparable but non-equivalent;
- let support and compatibility docs say exactly what is observable on which tuples;
- and create durable handoff artifacts for later replay, incident response, or archaeology.

## Anti-goals
Do not turn this stack into:
- one universal debugger abstraction crate,
- one giant telemetry SDK or hosted backend,
- one new error-handling framework,
- or one fake “debugging works” badge.

The stack is a **review boundary**, not a replacement for all debugging tools.
