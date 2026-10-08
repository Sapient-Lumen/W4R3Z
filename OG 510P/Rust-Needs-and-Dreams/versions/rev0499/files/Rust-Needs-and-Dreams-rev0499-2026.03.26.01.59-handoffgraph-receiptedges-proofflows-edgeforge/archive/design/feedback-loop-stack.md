# Design: Feedback Loop Stack (Build-State Evidence + Debuggability + bounded edit/semantic imports)

## Goal
Treat **Build-State Evidence Stack** and **Debuggability Stack** as one shared **Feedback Loop Stack**.

The missing contribution is not another IDE integration, another background daemon, another “why is Rust slow?” dashboard, another debugger wrapper, or another assistant that guesses at local state.
It is a portable, reviewable stack that keeps four truths distinct while letting them compose:
- **change / session truth** — what edit, change slice, workflow, and tool tuple is actually under review;
- **build-state truth** — what Cargo/build/cache/rebuild evidence actually says;
- **debug / diagnosis truth** — what diagnostic, telemetry, debugger-tuple, or side-channel inspection lane actually ran;
- **consumer handoff truth** — what issue/docs/support/CI/assistant consumers may honestly conclude.

That separation matters because Rust feedback-loop pain is rarely one thing:
- sometimes the problem is lock contention or rebuild scope,
- sometimes it is debug-info or target-dir policy,
- sometimes it is debugger tuple quality,
- sometimes it is async/runtime visibility,
- and sometimes it is all of those in one iteration.

## Why this seam matters now
Current official Rust/Cargo signals are unusually aligned here:
- The 2025 State of Rust survey still says resource usage (slow compile times and storage usage) remains one of the main non-trivial productivity problems, debugging is still a major problem, and online docs remain the preferred canonical reference while LLM/tool usage rises.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2025 build-performance survey says build pain differs by workflow, says more than 35% of users consider IDE and Cargo blocking one another to be a big problem, and says full debug info in the default dev profile increases disk usage and slows compilation and linking.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Cargo build-analysis goal explicitly aims to record metadata across invocations, associate it with build identifiers like `CARGO_RUN_ID`, explain rebuild reasons, and eventually enable build replay for debugging and CI reproducibility.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout goal explicitly targets fine-grained locking, rust-analyzer coexistence, target-dir GC, and a cross-workspace shared build cache.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The March 2026 build-dir-layout-v2 call for testing says many projects still rely on unspecified build-dir details because Cargo lacks some missing features. That is direct evidence that the loop boundary is still too implicit.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The 2026 debugging survey says truly strong support would require multiple debugger versions across OSes, quality visualizers, first-class async debugging, and Rust expression evaluation, and it explicitly says this still takes a lot of work.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo’s 1.94 development-cycle report says `cargo report rebuild`, `cargo report sessions`, and better timing support are landing, and it also reiterates that Cargo cannot be everything to everyone and that plugins matter.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

Taken together, ideal Rust needs a more executable story for the **developer feedback loop** than the archive had previously written down.

## What each stack should own
### Build-State Evidence Stack
[`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md) owns:
- build-state topology and reuse truth,
- change classification and rebuild-scope truth,
- workflow-aware diagnosis and suggestion truth.

Its question is:
> what happened in the build, and what part of that is fact versus diagnosis?

### Debuggability Stack
[`design/debuggability-stack.md`](./debuggability-stack.md) owns:
- failure-identity truth,
- runtime-correlation truth,
- debugger-tuple truth,
- repro/escalation handoff truth.

Its question is:
> once the build or run failed or slowed down, what observation/debugging lanes actually produced evidence?

### Edit Workflow + Semantic Context imports
[`design/edit-workflow-kit.md`](./edit-workflow-kit.md) and [`design/semantic-context-kit.md`](./semantic-context-kit.md) remain **imports**, not absorbed subfields.

Their question is:
> what changed, and what semantic or applied-edit context may be attached when available?

That boundary matters.
The stack should improve feedback loops without pretending every loop starts from a fully tracked edit plan or complete semantic snapshot.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without spelunking shell history, IDE state, ad hoc issue threads, and CI logs:
1. Which session/workflow/subject is being discussed?
2. What changed, if that is known?
3. What build-state evidence exists for that session?
4. Which debug/diagnostic lane was actually exercised after or during that session?
5. Which tradeoffs were intentional (for example separate target dirs or reduced debug info) versus accidental?
6. What issue/docs/support/assistant consumer may safely summarize the result?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs both a ranked execution layer and an explicit epic candidate, captured in:
- [`design/feedback-loop-pilot-program.md`](./feedback-loop-pilot-program.md)
- [`proposals/epic-feedback-loop-stack.md`](../proposals/epic-feedback-loop-stack.md)

That pilot program should prove the stack in this order:
1. **session identity lane**
2. **editor / CLI coexistence lane**
3. **build → debugger handoff lane**
4. **issue / support / docs consumer lane**
5. **assistant/editor consumer lane**

That ordering is intentional.
The archive should not jump straight to a giant IDE platform, a universal local daemon, or a fake single score for developer experience.
It should first prove that Rust projects can publish enough feedback-loop truth to make ordinary iteration problems legible and portable.

## Design principles
1. **One session comes before trend stories.** Session identity should exist before cross-session analytics.
2. **Build facts and debug facts stay distinct.** A debugger conclusion must not silently redefine rebuild evidence, and vice versa.
3. **Native debugger support and runtime-side inspection stay distinct.** Tokio Console, tracing, or side-channel inspection can complement debuggers without claiming equivalence.
4. **Edit/semantic imports stay optional and bounded.** Absence of full edit provenance must remain explicit.
5. **Consumer summaries come after core packs.** Docs, support, CI, and assistants should import bounded conclusions.
6. **Tradeoffs must stay visible.** Separate target dirs, reduced debug info, alternate profiles, or tuple-specific debugger workarounds are part of the story, not embarrassing details to hide.

## What an epic contribution would look like in practice
A serious contribution here now looks like a thin `cargo innerloop` / `feedback-loop-pack/v0` layer that links build-state evidence, debuggability evidence, and bounded session/change context without flattening them.

Concretely, it should:
- let `cargo report sessions` / rebuild / timing evidence attach to one loop subject without silently widening one selected slice into whole-workspace truth;
- let build-dir / target-dir / debug-info tradeoffs remain explicit;
- link debugger-tuple or runtime-side inspection evidence to the same session instead of forcing separate issue archaeology;
- create durable handoff artifacts for issue trackers, support pages, release docs, and assistants, while preserving which Cargo-derived pieces are merely the latest operational pack versus the current frozen shared head;
- and make Rust’s build/debug loop more explainable without waiting for Cargo, rust-analyzer, or debugger parity to finish.

## Anti-goals
Do not turn this stack into:
- one universal IDE backend,
- one always-on local daemon,
- one hosted build/debug portal,
- one “AI dev loop” wrapper,
- or one fake developer-experience score.

The stack is a **review boundary**, not a replacement for Cargo, rust-analyzer, debuggers, tracing, or assistants.
