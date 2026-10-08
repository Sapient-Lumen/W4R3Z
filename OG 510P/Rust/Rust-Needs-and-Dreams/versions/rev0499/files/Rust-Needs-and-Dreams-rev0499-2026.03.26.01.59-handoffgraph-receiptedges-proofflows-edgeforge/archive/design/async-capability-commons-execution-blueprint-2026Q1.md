# Design: Async Capability Commons execution blueprint (2026 Q1)

## Goal
Turn one of the archive's clearest **outside-the-box / program-shaped worthy contributions** into a sharper **buildable program**.

The missing contribution is not another runtime, another tutorial stack, another universal async facade, or another portability badge.
It is a disciplined companion layer that makes Rust's async reality **lane-aware, capability-aware, adapter-aware, and reviewable** across libraries, runtimes, embedded/server environments, adoption guidance, lifecycle/reliability stacks, and future tooling.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team wants to build the archive's current best async commons contribution, what should that project actually ship in theory and practice?

Read with:
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/async-commons-kit.md`
- `design/async-commons-lane-map.md`
- `design/async-commons-pilot-program.md`
- `design/async-lifecycle-kit.md`
- `design/async-reliability-stack.md`
- `proposals/epic-async-commons-kit.md`

## Why this note is needed now
The archive already knew that **Async Capability Commons** mattered.
What it still lacked was a crisper answer to **what the worthy contribution should actually become**.

Fresh official and primary signals sharpen that answer:
- Rust's March 20, 2026 challenges writeup says async remains a major pain point, that library choices can lock projects into one runtime family, and that the ecosystem may need more cohesive foundational async traits/functions over time.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2026 flagships page keeps **Just Add Async** active and lists milestones like return type notation, `async fn in dyn Trait`, immobile types / guaranteed destructors, and ergonomic ref-counting. That is roadmap evidence that async ergonomics and capability boundaries are still active project terrain rather than solved background plumbing.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H1 async flagship explicitly says runtime choice and runtime interoperability are central pain points, calls async Rust “Rust on hard mode”, and frames parity with sync Rust as a **multi-year** effort aimed at interoperable and thriving ecosystem substrate.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The January 2026 program-management update says async features and ergonomics will likely take multiple years to complete, which strengthens the case for a thin commons layer that can stabilize expectations while the language frontier keeps moving.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than sync Rust; it also notes that execution, I/O, and task spawning are still runtime-provided and that async traits still have dynamic-dispatch limitations even after stabilization.
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- Rust 1.85 stabilized async closures and the `AsyncFn` / `AsyncFnMut` / `AsyncFnOnce` traits, which is evidence that language support is improving — but not yet the same thing as cross-runtime capability truth.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- The `futures` task vocabulary (`Spawn`, `LocalSpawn`) and `futures-io` ecosystem traits show that some substrate is already shared; `tokio-util::compat` shows adapters exist because the seam is real; and `embassy-executor` shows embedded/no-alloc async is a materially different environment lane with static task allocation and compile-time memory-fit checks.
  https://docs.rs/futures/latest/futures/task/index.html
  https://docs.rs/futures-io/latest/futures_io/
  https://docs.rs/tokio-util/latest/tokio_util/compat/index.html
  https://docs.rs/embassy-executor/latest/embassy_executor/

Taken together, those signals say the archive should stop describing the async opportunity only as a theme.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest async commons contribution, the answer should now be:

> Build an **Async Capability Commons layer** that preserves async lane identity, records library/runtime/environment capability truth, makes adapter lossiness and watch/defer seams explicit, and emits reviewable packs and handoffs for humans, downstream stacks, and future tooling.

That answer is deliberately narrower than “fix async Rust”.
It is also deliberately stronger than “write runtime-agnostic APIs”.

## What this contribution should be in theory

### Core thesis
An async-commons system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what async seam or subject is under review;**
2. **which lane or lanes that subject actually depends on;**
3. **which capabilities are genuinely required, optional, or unsupported;**
4. **which adapters or bridges make the claim possible, and what semantics or costs they lose;**
5. **which areas are still `watch`, `defer`, blocked on language/compiler work, or only environment-specific;**
6. **what downstream consumers may honestly conclude about portability, adoption, lifecycle, reliability, or debugging.**

If a project cannot answer those questions without README folklore, adapter archaeology, and maintainer guesswork, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable async capability review**.

It should include:
- lane identity;
- capability profiles;
- common-surface claims;
- adapter and bridge receipts;
- environment contrast;
- readiness / `watch` / `defer` judgments;
- consumer-specific handoffs.

It should not become:
- a replacement runtime;
- a universal async facade;
- a new blessed runtime list;
- a hosted compatibility dashboard first;
- or an assistant that invents portability claims from docs.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **lane truth** — what async lane is being discussed (`core-future`, `spawn`, `local`, `io`, `time`, `stream-watch`, `environment`, `consumer-import`);
- **capability truth** — what a library or runtime actually requires, optionally uses, or forbids;
- **common-surface truth** — what traits/types/functions are being claimed as genuinely shared substrate;
- **adapter truth** — what bridge exists, what it maps, and what semantics or costs it loses;
- **environment truth** — what changes between server-runtime, desktop, embedded, `no_std`, `alloc`, or mixed targets;
- **consumer truth** — what adoption, lifecycle, reliability, docs, or tooling layers may safely reuse.

This is the largest theory/practice guardrail in the design.
Without it, every async summary becomes runtime-portability theater.

### Shape rule
This contribution should begin as a **reference layer + capability commons + adapter/acceptance corpus + report/pack command**.
That means:
- a **reference layer** for lane and capability vocabulary;
- a **commons** for reusable profile and readiness artifacts;
- an **adapter/acceptance corpus** for real bridges, negative cases, and scenario coverage;
- and a thin **command / pack layer** that imports evidence instead of replacing runtimes.

It should not begin as a service, ranking site, new runtime brand, or giant abstraction crate.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo async-commons lane`
- `cargo async-commons capability`
- `cargo async-commons adapter`
- `cargo async-commons readiness`
- `cargo async-commons diff`
- `cargo async-commons export --consumer <adoption|lifecycle|reliability|debug|docs|assistant>`
- `cargo async-commons pack`

The tool should **import** established crate/runtime evidence where possible rather than pretending it owns execution.

### Public artifact spine

#### Imported/internal families
- `async-lane-profile/v0`
- `async-seam/v0`
- `async-capability-profile/v0`
- `async-common-surface/v0`
- `async-adapter-profile/v0`
- `async-vector-set/v0`
- `async-readiness-report/v0`
- optional lifecycle / reliability / debug / incident attachments

#### Public review families
- `async-capability-brief/v0`
- `async-adapter-acceptance-report/v0`
- `async-capability-diff/v0`
- `async-commons-pack/v0`
- `async-commons-handoff/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — crate/workspace/runtime/adapter family, versions, target, environment class, workflow lane, and intent;
- **authority posture** — observed locally, imported from crate/runtime docs, imported from adapter tests, imported from downstream consumer packs, or inferred;
- **coverage / completeness** — exact, partial, adapter-mediated, environment-limited, watch-only, defer-only, stale, or mixed;
- **lane anchors** — named lane IDs, imported lane dependencies, and known fault lines;
- **capability anchors** — `Send`/local posture, spawn model, I/O traits, timer/deadline assumptions, cancellation assumptions, allocation posture, and unsupported environments;
- **adapter anchors** — source lane, target lane, required crate features, lossy semantics, allocation/boxing/buffering costs, wake/readiness caveats, and negative cases;
- **consumer limits** — what adoption/docs/lifecycle/reliability/debug consumers may and may not claim.

## Commands and what they should emit

### `cargo async-commons lane`
Purpose:
- declare or inspect lane identity;
- record lane family, readiness class, environment posture, and imported dependencies;
- emit `async-lane-profile/v0`.

Important rule:
- if a seam spans multiple lanes, say so explicitly instead of forcing one fake “runtime-agnostic” label.

### `cargo async-commons capability`
Purpose:
- capture what a library or stack actually requires;
- emit `async-capability-profile/v0` and optional `async-capability-brief/v0`.

Important rule:
- capabilities should be phrased as requirements and exclusions, not marketing promises.

### `cargo async-commons adapter`
Purpose:
- record how one ecosystem surface maps to another;
- emit `async-adapter-profile/v0` and `async-adapter-acceptance-report/v0`.

Important rule:
- unsupported and lossy paths must stay visible; adapters do not magically collapse semantic differences.

### `cargo async-commons readiness`
Purpose:
- publish `promote` / `pilot` / `watch` / `defer` judgments for a seam or lane;
- cite language/compiler blockers separately from ecosystem fragmentation;
- emit `async-readiness-report/v0`.

Important rule:
- `watch` is a successful answer when the seam is important but not yet mature enough for a common layer.

### `cargo async-commons diff`
Purpose:
- compare two capability or readiness packs while preserving the difference between:
  - newly shared substrate,
  - newly explicit capability requirements,
  - newly available adapters,
  - newly discovered lossiness,
  - and newly downgraded or deferred claims.

### `cargo async-commons export`
Purpose:
- emit smaller consumer handoffs for adoption briefs, lifecycle reviews, reliability packs, docs, assistants, or debugger-oriented notes without making those consumer slices canonical by themselves.

## Ranked feature set

### P0 — required for a worthy v0
- preserve lane identity explicitly;
- support capability profiles for at least spawn/local, I/O, and time/deadline seams;
- support adapter truth with negative/lossy edges;
- support one explicit `watch` or `defer` lane for stream / async-sequence / borrowing-sensitive work;
- support one environment-contrast report (server-runtime vs embedded/no-alloc is the clearest first proof);
- emit one portable brief plus one portable pack;
- surface `partial`, `unsupported`, `watch`, and `defer` honestly.

### P1 — strong near-term extensions
- import language-feature posture (`async fn in dyn Trait`, generators/streams, immobile types / guaranteed destructors) as blockers or readiness caveats;
- import Async Lifecycle / Async Reliability packs so they can reuse lane and capability truth instead of re-describing runtimes ad hoc;
- import debugging/visualizer acceptance facts where async inspection depends on runtime/task-model posture;
- add version-aware diffs for portability claim changes across releases.

### P2 — do later or fold elsewhere
- runtime rankings;
- hosted dashboards;
- universal convenience facades;
- ecosystem-wide scorecards;
- automatic “best runtime for you” recommendation engines.

## Pilot lanes that best prove the idea

### 1) I/O lane pilot
Prove:
- what is genuinely shared between `futures-io`-style vocabulary and runtime-native I/O;
- which adapter paths exist;
- what compatibility costs or unsupported cases remain.

This is the best first proof because `tokio-util::compat` already shows the seam is real rather than theoretical.

### 2) Spawn + local capability pilot
Prove:
- what a library means when it needs spawning;
- whether it needs generic spawn, local `!Send`, blocking escape hatches, or a specific runtime family;
- how to publish that requirement without pretending universal portability.

This lane matters because `Spawn` vs `LocalSpawn` is one of the highest-value async truths to make explicit early.

### 3) Time / deadline capability pilot
Prove:
- what timer/deadline support a crate actually needs;
- what environments are excluded;
- which semantics are common enough to share and which are not.

This lane matters because many portability claims secretly depend on timer posture without naming it.

### 4) Stream / async-sequence `watch` pilot
Prove:
- that the commons can publish a disciplined `watch` verdict instead of faking a solved substrate;
- which blockers are language/compiler-shaped versus crate-shaped;
- what downstream consumers may say today.

This lane matters because the ecosystem visibly wants better async sequences, but a worthy commons must know when not to flatten.

### 5) Environment contrast pilot
Prove:
- that server-runtime and embedded/no-alloc async do not belong in one portability sentence;
- which assumptions break when the environment changes;
- and what the commons still helps compare.

This lane matters because Embassy is not just Tokio-with-different-branding.

### 6) Async Lifecycle / Reliability import pilot
Prove:
- that downstream stacks become sharper because the commons exists beneath them;
- that lifecycle/reliability notes can import capability truth instead of repeating runtime folklore.

This is the point where the contribution stops being a nice theory note and starts multiplying the rest of the repo.

## Theory-of-practice framework for judging proposals in this seam
A proposed async contribution is closer to the archive's target when it answers “yes” to most of these questions:
1. does it name the lane or capability it is talking about;
2. does it keep shared substrate separate from runtime-shaped APIs;
3. does it preserve adapter lossiness instead of hiding it;
4. does it let `watch` / `defer` be real outcomes;
5. does it improve downstream decisions without requiring a universal runtime story;
6. can it ship as a thin local/reportable layer before asking for ecosystem standardization.

A proposal should be folded or downgraded when:
- it treats runtime portability as a slogan;
- it erases environment differences;
- it substitutes a convenience API for capability truth;
- or it implies that one runtime or wrapper already solves the whole async story.

## Relationship to nearby seams
- **Async Lifecycle Kit** owns ownership, shutdown, cancellation, and supervised task truth; it should import capability and adapter posture from this commons.
- **Async Reliability Stack** owns lifecycle/replay/exploration composition; it should not quietly redefine runtime capability truth.
- **Feedback Loop / Debuggability Acceptance** owns debugger and inspection acceptance; it may import async capability or task-model posture, but it should not replace the commons.
- **Adoption Navigation** may import async capability commons to improve recommendations; it should not invent portability claims from taste.
- **Native Edge Contract** and **Safety-Critical Readiness** may import environment-specific async caveats, especially where embedded, mixed-language, or qualification settings care about executor and timer posture.

## What this contribution should not become
Do **not** let this seam turn into:
- a “best runtime” leaderboard;
- a replacement runtime;
- a runtime-neutral facade that secretly bakes in one runtime's semantics;
- a compatibility badge without negative cases;
- a documentation mirror that never emits reviewable packs.

The archive's target is a **commons with honesty**, not a new center of gravity for async branding.

## What success should look like
The contribution is working when:
- libraries can publish honest async capability requirements instead of vague runtime-agnostic claims;
- adapter lossiness becomes easier to review before integration work starts;
- `watch` and `defer` seams become explicit rather than folklore;
- lifecycle/reliability/adoption/debugging layers import the same async truth instead of restating it inconsistently;
- and future language/runtime progress can narrow the gap without forcing everyone to relearn the map from scratch.

## Immediate archive decision
Treat this note as the canonical answer for:
**what should Async Capability Commons actually ship before it turns into another runtime story?**

That means:
- keep the broad ladder intact;
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle;
- keep **Native Edge Contract** as the active specialist frontier;
- and treat **Async Capability Commons** as the archive's clearest next **program-shaped execution blueprint** for reducing async fragmentation without pretending runtimes, environments, or language progress are already converged.
