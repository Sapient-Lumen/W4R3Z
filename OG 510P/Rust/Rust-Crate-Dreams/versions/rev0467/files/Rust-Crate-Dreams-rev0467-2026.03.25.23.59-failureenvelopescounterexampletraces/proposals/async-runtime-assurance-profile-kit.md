---
id: P-0532
title: Async Runtime Assurance Profile Kit — runtime profiles, service-topology receipts, capability routes, and bridge-debt evidence for async runtime choice under scrutiny
status: idea
domains: [async, runtime, safety-critical, embedded, backend, assurance, diagnostics, supportiveness, selection]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
  - https://docs.rs/tokio/latest/tokio/runtime/
  - https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  - https://docs.rs/tokio-metrics/latest/tokio_metrics/
  - https://docs.embassy.dev/embassy-executor/0.9.1/cortex-m/index.html
  - https://github.com/rtic-rs/rtic
  - https://docs.rs/tokio/latest/tokio/runtime/index.html
  - https://docs.rs/tokio/latest/tokio/runtime/struct.Handle.html
  - https://docs.rs/tokio/latest/tokio/io/
  - https://docs.rs/tokio/latest/tokio/signal/
  - https://docs.rs/tokio/latest/tokio/signal/unix/
  - https://docs.rs/tokio/latest/tokio/signal/windows/
  - https://docs.rs/tokio/latest/tokio/io/unix/struct.AsyncFd.html
  - https://docs.embassy.dev/embassy-time-queue-driver
  - https://embassy.dev/book/
  - https://rtic.rs/2/book/en/by-example/app.html
  - https://rtic.rs/2/book/en/by-example/software_tasks.html
  - https://docs.rs/async-compat/latest/async_compat/
  - https://docs.rs/async_executors/latest/async_executors/
  - https://docs.rs/async-std/latest/async_std/
---

# Problem

Rust's async story is getting stronger at the language level, but runtime choice is still one of the ecosystem's sharpest hidden contracts.

The current challenge reports make that gap unusually explicit:

- the March 2026 Rust challenges post says async remains a pain point, that many developers avoid it, and that runtime lock-in is still a real ecosystem problem;
- the January 2026 safety-critical post says async is appealing for event-driven systems, but the runtime and qualification story is not settled for higher-criticality work;
- that same post quotes teams saying that if they want to use async Rust in ISO 26262 contexts, they need a runtime with the right quality and process artifacts;
- the 2026 project flagships put safety-critical evidence and functional-safety tooling on the main Rust agenda;
- and the async project-goal updates keep framing current language work as an attempt to unblock the next generation of async libraries rather than as the whole story.

Meanwhile, today's runtime substrate is real but materially different:

- Tokio bundles an I/O driver, scheduler, timer, and blocking pool, and its shutdown docs make clear that spawned async tasks, blocking work, and timeout aftermath do not all behave the same way;
- `tokio-metrics` shows that runtime/task metrics are real enough to instrument, but still require deliberate capture choices;
- Embassy documents no-`alloc`, statically allocated tasks, compile-time RAM fit, fair polling, integrated timers, and optional multi-priority executors;
- RTIC documents an interrupt-priority scheduler, message passing, a timer queue, compile-time deadlock freedom, no hard dependency on a dynamic allocator, and WCET/scheduling-analysis-friendly structure.
- Tokio signal and `AsyncFd` docs additionally show that some capabilities are platform-scoped rather than global runtime-family guarantees.
- Embassy’s book shows that one ecosystem can span PC `std` examples and MCU deployment targets without one uniform capability story.

That means the missing crate is **not** another runtime.
It is also **not** a generic benchmark suite, another shutdown helper, or another async tutorial.

The missing crate is a **reviewable runtime-choice and runtime-support contract**:

> what runtime family is actually in play, what allocation/scheduling/preemption assumptions it imports, what shutdown and panic behavior it really has, and what evidence exists if a team needs to justify that choice to others.

# Main judgment

A worthy crate here should give maintainers, reviewers, and downstream users one compact answer to:

1. **Which runtime model is actually being relied on?**
   - work-stealing I/O runtime,
   - cooperative embedded executor,
   - interrupt-priority scheduler,
   - or a custom/manual-review runtime family;
2. **What memory/allocation posture does that runtime assume?**
   - heap required,
   - heap optional,
   - static task allocation,
   - single shared stack,
   - or mixed/manual-review;
3. **What does shutdown really mean?**
   - when async tasks stop,
   - what happens to blocking work,
   - what timeout does or does not guarantee,
   - and what becomes unusable after shutdown;
4. **What preemption and timing story exists?**
   - cooperative only,
   - multi-priority / interrupt preemption,
   - integrated timer queue,
   - hardware timer dependence,
   - or external/manual-review;
5. **What evidence backs the support claim?**
   - docs only,
   - observed metrics,
   - on-target measurements,
   - imported assurance note,
   - or still manual review.
6. **Which deployment lanes are actually in scope?**
   - local host examples,
   - CI hosts,
   - production hosts,
   - simulator lanes,
   - or target boards.
7. **Which capabilities are lane-scoped or guard-scoped?**
   - Unix-only signals,
   - Windows console signals,
   - reactor-bound file-descriptor support,
   - runtime-context-sensitive time/I/O surfaces,
   - or target-only scheduler routes.

That is more useful than “uses Tokio”, “supports Embassy”, or “RTIC-friendly”.

# What it provides

- `async-runtime-profile.toml` — maintainer-declared runtime/support contract, evidence classes, and manual-review zones.
- `runtime-profile.receipt.json` — runtime family, scheduler model, allocation posture, preemption posture, timer authority, and blocking posture.
- `shutdown-behavior.report.json` — task-cancellation behavior, blocking-work shutdown posture, timeout aftermath, panic visibility, and post-drop I/O/resource caveats.
- `qualification-basis.receipt.json` — which claims are docs-derived, metrics-derived, target-measured, imported from external assurance work, or still manual review.
- `runtime-service-topology.receipt.json` — per lane, records where spawn, time, I/O, blocking, and other async services actually come from.
- `capability-route.receipt.json` — for one claimed capability, records provider kind, activation requirement, evidence class, and unmet-route honesty.
- `compatibility-bridge.report.json` — records what an adapter bridges, what provider/context constraints remain, and what review debt survives the bridge.
- `runtime-deployment-topology.receipt.json` — records which host, CI, simulator, console, and target lanes exist and what runtime family/support level each lane actually uses.
- `capability-availability.matrix.json` — records which runtime-sensitive capabilities are supported, unsupported, or guarded in each lane.
- `surface-guard.report.json` — records cfg/feature/runtime-context/provider guards that fence public support claims.
- `runtime-choice.summary.md` — compact human-facing summary suitable for README, architecture docs, or review packets.
- `runtime-profile-diff.report.json` — release-to-release or profile-to-profile drift in runtime family, shutdown behavior, allocation posture, or evidence basis.
- `cargo runtime-assurance init`
- `cargo runtime-assurance capture`
- `cargo runtime-assurance check`
- `cargo runtime-assurance doctor`
- `cargo runtime-assurance summary`
- `cargo runtime-assurance diff <old> <new>`
- `cargo runtime-assurance pack`

# What the crate should provide other people

1. **A compact runtime-choice artifact** instead of forcing downstream users to infer support claims from framework names and scattered docs.
2. **Allocation-posture honesty** so “embedded-friendly” or “no_std-compatible” stops hiding whether the runtime still expects dynamic allocation, fixed arenas, or purely static tasks.
3. **Shutdown truth** so “graceful shutdown” stops hiding whether async tasks are dropped at yield points, whether blocking work can outlive the shutdown call, and what timeout actually guarantees.
4. **Preemption/scheduling truth** so “supports priorities” or “fair scheduling” stops hiding whether the system is cooperative, interrupt-driven, multi-priority, or mixed.
5. **Qualification-basis honesty** so “safe/suitable for regulated use” cannot be claimed without saying whether that is based on vendor docs, local test evidence, imported assurance notes, or real on-target measurement.
6. **Deployment-lane honesty** so host examples, CI hosts, production hosts, and target boards do not get flattened into one runtime-support claim.
7. **Guarded capability matrices** so Unix-only, Windows-only, runtime-context-sensitive, or provider-sensitive surfaces are explicit.
8. **A portable vocabulary** for comparing backend, embedded, robotics, and safety-critical runtime lanes without pretending that Tokio, Embassy, and RTIC are the same class of thing.
9. **A bridge into broader assurance work** without requiring every team to start with a full assurance-case platform.

# Why now

This lane earns a slot now because the official ecosystem signals finally line up.

## 1. Async remains a broad ecosystem pain, not just a language-design discussion

The March 2026 Rust challenges post says async complexity is still a real pain point, and explicitly calls out runtime lock-in as a distinctive ecosystem problem.
That means a runtime-choice contract is not a niche regulated-industry concern.
It is also ordinary ecosystem navigation infrastructure.

## 2. Safety-critical Rust now names the runtime question directly

The January 2026 safety-critical post does not merely say “async is hard”.
It says teams immediately ask for runtime quality and process artifacts, and it explicitly recommends defining requirements for a safety-case-friendly async runtime.
That upgrades this from speculation to a documented ecosystem need.

## 3. The language roadmap is unblocking async libraries, not solving runtime support on its own

The async project-goal updates and 2026 flagships focus on `async fn` in dyn trait, RTN, generators, pin ergonomics, and related language blockers.
Those are important, but they do not by themselves tell a downstream reviewer what runtime assumptions a shipped system actually makes.

## 4. Runtime substrate is now concrete enough to compare honestly

Tokio, Embassy, and RTIC all have mature enough docs to expose materially different support surfaces:

- Tokio: I/O driver + scheduler + timer + blocking pool + runtime/task metrics + shutdown caveats.
- Embassy: no-`alloc`, static tasks, compile-time memory fit, fair polling, integrated timers, optional multi-priority executors.
- RTIC: interrupt-priority concurrency, timer queue, zero-hard-dependency on dynamic allocator, compile-time deadlock-freedom claims, and scheduling-analysis-friendly structure.

The missing value is therefore the joined contract above those facts.

# Prior art scan

## Tokio
Tokio is strong runtime substrate for backend and systems work.
It already documents runtime structure, shutdown semantics, and metrics surfaces.
What it does **not** provide is a normalized artifact another library or product team can publish to explain its runtime assumptions to downstream users or reviewers.

## Embassy
Embassy is serious embedded async substrate and already exposes a much more qualification-shaped story than many general-purpose runtimes.
What it still does **not** provide is a portable, cross-runtime contract vocabulary that lets another team compare an Embassy profile against a Tokio or RTIC profile without flattening them into one vague “async runtime” label.

## RTIC
RTIC is strong proof that Rust concurrency for embedded/safety-adjacent systems can have compile-time and scheduling-analysis-oriented properties.
But RTIC is also not the same thing as an async I/O runtime, which is exactly why a runtime-profile kit is useful: it can compare and classify instead of pretending all runtimes are one lane.

## Existing lifecycle, resource, and channel crates in the archive
Those adjacent proposals are important proving grounds.
But none of them publish one compact artifact for **runtime family + allocation posture + preemption/timer model + shutdown/qualification basis** as a joined support surface.

# Recommended `0.1` first-class review objects

## `runtime-profile.receipt.json`

Should record at least:

- `runtime_family`: `tokio` | `embassy_executor` | `rtic` | `custom` | `manual_review_required`
- `scheduler_model`: `io_driver_and_task_scheduler` | `cooperative_executor` | `interrupt_priority_scheduler` | `mixed` | `manual_review_required`
- `allocation_posture`: `requires_alloc` | `can_run_without_alloc` | `shared_stack_no_dynamic_allocator` | `mixed` | `manual_review_required`
- `preemption_posture`: `cooperative_only` | `priority_preemptive` | `mixed` | `manual_review_required`
- `timer_authority`: `runtime_timer_driver` | `integrated_timer_queue` | `hardware_timer_queue` | `external_or_board_specific` | `manual_review_required`
- `blocking_posture`: `dedicated_blocking_pool` | `forbidden_or_discouraged` | `board_or_app_specific` | `manual_review_required`

## `shutdown-behavior.report.json`

Should record at least:

- `async_task_shutdown_posture`: `dropped_after_next_yield` | `cooperative_until_framework_stop` | `manual_review_required`
- `blocking_shutdown_posture`: `waits_for_blocking_tasks` | `no_blocking_pool` | `manual_review_required`
- `timeout_aftermath`: `work_may_continue_after_timeout` | `no_timeout_surface` | `manual_review_required`
- `panic_visibility`: `join_handle_or_user_observed` | `framework_or_policy_defined` | `manual_review_required`
- `post_shutdown_resource_posture`: `bound_resources_fail_after_drop` | `manual_review_required`

## `qualification-basis.receipt.json`

Should record at least:

- `claim_basis`: `documentation_only` | `documentation_plus_metrics` | `documentation_plus_on_target_measurement` | `imported_assurance_artifact` | `manual_review_required`
- `target_scope`: `host_only` | `board_or_rtos_specific` | `mixed` | `manual_review_required`
- `analysis_notes`
- `open_assumptions`

# Persona / who it’s for

- maintainers of libraries that currently lock users into one runtime family without clearly publishing what that implies
- backend/product teams choosing among Tokio-shaped runtime stacks
- embedded teams deciding whether Embassy/RTIC-style concurrency assumptions are compatible with their product constraints
- safety-critical and robotics teams that need runtime evidence without first building a full assurance program
- reviewers, auditors, and platform leads who need one portable runtime-choice artifact

# Users & user stories

- **Backend team:** “Tell us what we really committed to when we adopted Tokio — especially shutdown and blocking behavior — before we promise support guarantees to customers.”
- **Embedded team:** “Record that this executor runs without `alloc`, that tasks are statically allocated, and that this profile should not be compared to a threadpool runtime.”
- **Safety engineer:** “Show me exactly which runtime claims are docs-derived versus target-measured, and where manual review still remains.”
- **Library maintainer:** “Publish our runtime assumptions without forcing downstream users to reverse-engineer them from examples and issue threads.”
- **Reviewer:** “Diff the old runtime-support pack against the new one and tell me whether we changed shutdown, priority, or allocation posture.”

# Design goals

1. **Contract-first, not runtime-first** — the missing value is the support/selection artifact above today's runtimes.
2. **Useful outside regulated domains** — safety-case-friendly structure should still help ordinary teams choose and document runtime assumptions.
3. **Evidence-honest** — separate docs-derived claims from measured or externally reviewed ones.
4. **Runtime-neutral but not runtime-blind** — preserve real semantic differences instead of collapsing everything into generic async language.
5. **Joined, not bloated** — runtime family, allocation, shutdown, preemption, and evidence should be visible together without becoming a dashboard platform.
6. **Diffable** — runtime-support drift should be reviewable across branches and releases.

# Non-goals

- Not a new async runtime.
- Not a universal abstraction layer that makes Tokio, Embassy, and RTIC interchangeable.
- Not a benchmark suite pretending performance equals qualification.
- Not a replacement for broader assurance-case tooling.
- Not another lifecycle/channel/resource contract lane with a runtime label pasted on top.

# Architecture & API sketch

```rust
pub struct RuntimeProfileReceipt {
    pub runtime_family: RuntimeFamily,
    pub scheduler_model: SchedulerModel,
    pub allocation_posture: AllocationPosture,
    pub preemption_posture: PreemptionPosture,
    pub timer_authority: TimerAuthority,
    pub blocking_posture: BlockingPosture,
}

pub struct ShutdownBehaviorReport {
    pub async_task_shutdown_posture: AsyncTaskShutdownPosture,
    pub blocking_shutdown_posture: BlockingShutdownPosture,
    pub timeout_aftermath: TimeoutAftermath,
    pub panic_visibility: PanicVisibility,
}

pub fn capture_runtime_profile(root: &Path) -> Result<RuntimeProfileReceipt>;
pub fn assess_shutdown_behavior(root: &Path) -> Result<ShutdownBehaviorReport>;
pub fn diff_profiles(old: &RuntimeProfileReceipt, new: &RuntimeProfileReceipt) -> RuntimeProfileDiff;
pub fn export_pack(out: &Path) -> Result<()>;
```

Suggested workspace shape:

- `runtime_assurance_model`
- `runtime_assurance_discovery`
- `runtime_assurance_check`
- `runtime_assurance_pack`
- `cargo-runtime-assurance`

Optional adapters later:

- `runtime_assurance_tokio`
- `runtime_assurance_embassy`
- `runtime_assurance_rtic`

# Security / safety model

- Never let a runtime label stand in for a qualification claim.
- Preserve open assumptions explicitly whenever shutdown, panic, timing, or allocation posture cannot be proven from imported evidence.
- Support redaction of internal paths, board identifiers, or target details when exporting packs externally.
- Treat “documentation only” as a real but weaker evidence class, not as proof of verified behavior on a product target.

# Maintenance & governance plan

- Keep the core schema small and runtime-neutral.
- Add adapters only when the imported runtime docs and behaviors are concrete enough to classify conservatively.
- Prefer a handful of high-signal scenario fixtures over broad fake completeness.
- Coordinate conceptually with adjacent lanes such as lifecycle, resource, channel, and toolchain support, while keeping runtime choice as its own contract.

# Milestones

## 0.1
- profile schema
- shutdown-behavior schema
- qualification-basis schema
- Tokio / Embassy / RTIC example imports
- `capture`, `check`, `doctor`, `summary`, `diff`, `pack`

## 0.2
- richer evidence adapters
- target-specific notes and board/RTOS qualifiers
- import bridge to assurance-case tooling
- release-review runtime drift summaries

# Open questions

- Which minimum vocabulary is shared cleanly across Tokio, Embassy, RTIC, and future runtimes without becoming meaningless?
- Should runtime metrics instrumentation count as a distinct evidence class from generic runtime docs?
- How much target/board specificity belongs in the core schema versus an adapter-specific extension?
- What is the clean boundary between runtime-support drift and broader system lifecycle/shutdown evidence?


# 2026-03-22 artifact-completeness refresh — evidence class, drift, and bundle shape must stay explicit

This proposal is stronger now because the next useful move was **not** another runtime-specific helper crate.
It was to make **P-0532** look more like the archive’s strongest support-contract lanes.

Three details needed to become first-class:

1. **qualification basis** — another reviewer needs to know whether a runtime claim is docs-derived, metrics-backed, target-measured, imported from external assurance work, or still manual-review-only.
2. **runtime drift meaning** — a change from Tokio to RTIC or Embassy is not the same kind of change as “same runtime, better metrics exports”.
3. **bundle shape** — mixed host/runtime and target/runtime stacks should export one bundle with multiple lanes, not one flattened runtime label.

That yields three new `0.1` artifacts worth promoting now:

- `qualification-basis.receipt.json`
- `runtime-profile-diff.report.json`
- `runtime-assurance-bundle.manifest.json`

The sharper receiver-facing contract is therefore:

- what runtime model is in play,
- what shutdown/blocking behavior matters,
- what evidence class backs the claim,
- what changed across revisions,
- and how the exported bundle keeps host/test/runtime lanes separate from shipped target/runtime lanes.

If a crate in this territory cannot export those objects, it is still probably substrate or instrumentation rather than the missing support-contract layer.

# Sources

- Rust challenges and async/runtime lock-in: https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Safety-critical Rust and runtime-quality/process-artifact requirement: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- 2025 async goal update: https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- Tokio runtime docs: https://docs.rs/tokio/latest/tokio/runtime/
- Tokio shutdown/metrics docs: https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
- Tokio metrics: https://docs.rs/tokio-metrics/latest/tokio_metrics/
- Embassy executor docs: https://docs.embassy.dev/embassy-executor/0.9.1/cortex-m/index.html
- RTIC repository/readme: https://github.com/rtic-rs/rtic

# 2026-03-23 capability-topology refresh — runtime family alone is not enough

This proposal is stronger now because the next useful move was **not** another runtime abstraction layer.
It was to make **P-0532** explicit about **service topology**, **capability routes**, and **compatibility-bridge debt**.

Three details needed to become first-class:

1. **service topology** — a runtime dependency alone does not say where spawn, time, I/O, process, signal, or blocking services actually come from;
2. **capability route** — a claimed capability like `sleep` or `TcpStream` often depends on a builder flag, runtime context, HAL feature, or dispatcher setup that should be reviewable directly;
3. **bridge debt** — adapter crates such as `async-compat` and `async_executors` prove real demand, but they also preserve hidden provider/context constraints that should stay explicit.

That yields three more `0.1` artifacts worth promoting now:

- `runtime-service-topology.receipt.json`
- `capability-route.receipt.json`
- `compatibility-bridge.report.json`

The sharper receiver-facing contract is therefore:

- what runtime family is in play,
- which async services are actually present in each lane,
- what exact provider/activation route makes each claimed capability available,
- what adapters are used and what they do **not** erase,
- and how the exported bundle keeps profile, topology, capability, and bridge debt separate.

If a crate in this territory cannot export those objects, it is still probably runtime substrate or adapter glue rather than the missing support-contract layer.

