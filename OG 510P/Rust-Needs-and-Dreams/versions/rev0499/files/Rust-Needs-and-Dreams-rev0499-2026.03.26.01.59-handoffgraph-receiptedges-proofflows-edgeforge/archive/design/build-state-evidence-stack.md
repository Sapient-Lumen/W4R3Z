# Design: Build-State Evidence Stack (Build Cache + Change Impact + Build Doctor)

## Goal
Treat **Build Cache Kit**, **Change Impact Kit**, and **Build Doctor Kit** as one shared **Build-State Evidence Stack**.

The missing contribution is not another cache wrapper, another timings dashboard, another “why did Cargo rebuild?” FAQ answer, or another blog-post checklist for slow builds.
It is a portable, reviewable stack that keeps three truths distinct while letting them compose:
- **build-state topology and reuse truth**,
- **change classification and rebuild-scope truth**,
- **workflow-aware diagnosis and suggestion truth**.

That separation matters because Rust build pain is rarely one thing:
- sometimes the problem is **layout and locking**,
- sometimes it is **conservative invalidation**,
- sometimes it is **workflow mismatch**,
- and sometimes it is all three at once.

## Why this seam matters now
Current official Rust/Cargo signals are unusually aligned here:
- The 2025 State of Rust survey still lists resource usage, especially slow compile times and storage usage, among the biggest productivity problems.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2025 compiler-performance survey says users need better explanations of slow builds and explicitly calls out editor latency and rust-analyzer performance as meaningful blockers.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Cargo build-analysis goal is explicitly about recording build metadata across invocations and exposing rebuild reasons and timing history through `cargo report`.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The **Relink don’t Rebuild** goal is explicitly about avoiding reverse-dependency rebuilds when public interfaces do not change.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- The build-dir-layout goal explicitly targets finer-grained locking, reduced rust-analyzer contention, GC, and a cross-workspace shared build cache.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo’s build-cache docs now explicitly separate **final build artifacts** in `target-dir` from **intermediate build artifacts** in `build-dir`, which makes it easier to reason about build-state lanes without pretending all artifacts are the same thing.
  https://doc.rust-lang.org/cargo/reference/build-cache.html

Taken together, that means ideal Rust needs a more executable story for build-state evidence than the archive had previously written down.

## What each kit owns
### Build Cache Kit
[`design/build-cache-kit.md`](./build-cache-kit.md) owns:
- build-state units,
- layout/topology,
- lock domains,
- reuse and duplication verdicts,
- retention and exchange policy.

Its question is:
> what persisted build state existed, where did it live, and why was it reused, duplicated, blocked, or pruned?

### Change Impact Kit
[`design/change-impact-kit.md`](./change-impact-kit.md) owns:
- concrete change slices,
- semantic/interface classifications,
- observed rebuild scope,
- relink opportunities,
- observed-versus-required work.

Its question is:
> what changed, what boundary did it cross, and what work was actually or ideally required?

### Build Doctor Kit
[`design/build-doctor-kit.md`](./build-doctor-kit.md) owns:
- workflow profiles,
- bottleneck classes,
- ranked diagnoses,
- tradeoff-aware suggestions,
- human-usable explanations.

Its question is:
> given the evidence we have, what is the likely bottleneck and what should a user do next?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without spelunking raw logs or bespoke CI glue:
1. Which workflow/lane was being analyzed?
2. What changed between builds?
3. What build-state units were available or reused?
4. What blocked reuse or concurrency?
5. Which rebuilds were semantically required, merely conservative, or only policy-driven?
6. Which diagnosis or suggestion is actually justified by the evidence?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs a shared execution layer, captured in:
- [`design/build-state-evidence-pilot-program.md`](./build-state-evidence-pilot-program.md)

That pilot program should prove the stack in the following order:
1. **editor/CLI coexistence and lock-scope lane**
2. **private-change / relink-opportunity lane**
3. **workspace / CI cache-exchange lane**
4. **workflow-aware diagnosis lane**
5. **federated consumer lane**

That ordering is intentional.
The archive should not jump straight to giant dashboards, remote-cache standardization, or universal scheduling policy.
It should first prove that the stack can explain everyday local build pain honestly.

## Design principles
1. **Observed facts come before suggestions.** Diagnosis must not silently redefine cache or impact facts.
2. **Intermediate and final artifact lanes stay separate.** `build-dir` and `target-dir` are related, not interchangeable.
3. **Rebuild cause and optimization opportunity stay separate.** “Could relink” is not the same as “Cargo reused”.
4. **Duplication by policy is not failure.** rust-analyzer isolation or CI policy may be intentional and should stay explicit.
5. **Workflow identity is first-class.** `check`, `build`, `clippy`, docs, editor background runs, and CI release lanes are not one build.
6. **Large raw attachments stay optional.** Portable reports should summarize, not absorb, timing HTML, traces, self-profile data, or cache blobs.

## What an epic contribution would look like in practice
A serious contribution here would:
- import stable `cargo report future-incompat` and unstable build-analysis sessions through **Cargo Report Kit** instead of competing with or scraping Cargo-native report lanes directly, and keep authoritative-basis, coverage-slice, currentness, and frozen-head warnings visible whenever shared examples or current-active claims move above local review;
- preserve exact build-state and impact boundaries instead of flattening them into one score;
- make rust-analyzer / CLI contention and duplication explainable;
- attach relink-sensitive opportunity reports to ordinary PR/build review;
- and let Build Doctor ground its suggestions in evidence rather than prose heuristics alone.

## Anti-goals
Do not turn this stack into:
- one giant build-health score,
- one universal cache hit ratio,
- one monolithic remote-cache product,
- or a premature replacement for Cargo internals.

The stack is a **review boundary**, not a replacement build system.
