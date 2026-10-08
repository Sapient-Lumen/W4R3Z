## Execution addendum (rev0441)
This proposal now has a paired execution answer in `design/async-capability-commons-execution-blueprint-2026Q1.md`.
Read that note first when the question is no longer only “is Async Commons a worthy seam?” but “what concrete artifact family and proving lanes should it actually ship before it turns into another runtime story?”

# Epic proposal: Async Commons Kit

## Thesis
Rust’s async story is now important enough that one of the highest-leverage missing contributions is no longer just another runtime, compatibility shim, or ergonomic wrapper.
The higher-leverage missing piece is a **lane-aware async-commons contract** that lets the ecosystem identify, specify, validate, and ship neutral shared async seams: lane profiles, capability profiles, common traits/types, adapter rules, and readiness reports.

In other words: Rust needs a boring, attachable `async-commons-pack/v0` more than it needs one more claim that “our crate works on every runtime”.
Read [`design/async-commons-lane-map.md`](../design/async-commons-lane-map.md) as the rule for what must stay separate.

## Why now
The signals line up:
- the March 20, 2026 Rust challenges post says async remains one of the sharpest pain points, that runtime lock-in through library choice is real, and that the ecosystem may need more cohesive fundamental async library traits/functions over time;
- the 2025H1 async goal explicitly says runtime choice and runtime interoperability are central pain points;
- the July 2025 goals update says async traits and generators/streams work is meant to unblock the next generation of async libraries in the ecosystem;
- the Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than synchronous Rust;
- `Future` in `std` plus `Spawn` / `LocalSpawn` and `futures-io` in the wider ecosystem prove that some neutral async vocabulary already exists, but only partially;
- Tokio, `tokio-util::compat`, and Embassy prove that runtime-shaped surfaces, adapters, and environment splits are real and need honest review instead of portability theater.

That means the missing substrate is not raw capability.
It is the **reviewable path for creating, classifying, and validating shared async lanes**.

Sources:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- https://doc.rust-lang.org/std/future/trait.Future.html
- https://docs.rs/futures/latest/futures/task/index.html
- https://docs.rs/futures-io/latest/futures_io/
- https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
- https://docs.rs/tokio-util/latest/tokio_util/compat/index.html
- https://docs.rs/embassy-executor/latest/embassy_executor/

## What should be built
A first credible version should ship:
1. `async-lane-profile/v0`, `async-seam/v0`, `async-capability-profile/v0`, `async-common-surface/v0`, `async-adapter-profile/v0`, `async-vector-set/v0`, `async-readiness-report/v0`, `async-interop-check-report/v0`, and `async-commons-pack/v0`
2. one I/O lane pilot with explicit adapter truth and negative cases
3. one spawn/local capability pilot for runtime-portable libraries
4. one timer/deadline capability pilot
5. one explicit `watch` readiness report for stream / async-sequence / borrow-sensitive iteration work
6. one environment contrast pilot proving server-runtime and embedded/no-alloc lanes should stay distinct
7. one Async Lifecycle or Atlas consumer that imports async-commons output
8. diff support showing how async portability claims change across versions

The winning version is small, boring, adapter-heavy, lane-aware, and explicit about what it does **not** own.

## Initial pilots
- one I/O lane pilot centered on `futures-io` style vocabulary plus Tokio adapter truth
- one spawn/local capability pilot for libraries that need generic spawn, local `!Send`, or runtime-specific posture without claiming universal portability
- one timer/deadline capability pilot for crates that only need some timer support
- one explicit watch/wait readiness pilot for stream / async-sequence / borrow-sensitive iteration
- one environment contrast pilot comparing server-runtime versus embedded/no-alloc assumptions
- one downstream consumer pilot proving Async Lifecycle or Atlas can import the resulting artifacts

Treat [`design/async-commons-pilot-program.md`](../design/async-commons-pilot-program.md) as the ranked execution anchor so this work does not jump from abstract schemas straight to premature runtime standardization.

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and worked examples
   - preserve lane identity, capability truth, and adapter honesty
2. **v0.2 adapters + vectors**
   - ship I/O, spawn/local, and timer pilots
   - run explicit negative cases and partial-support paths
3. **v0.3 readiness + environment depth**
   - add watch/defer seam reports and environment-contrast reports
   - support version diffs and migration notes
4. **v1 consumer adoption**
   - at least two materially different downstream consumers use the artifact family without sharing one exact runtime lane

## Success metrics
- libraries can publish honest async capability requirements instead of vague runtime-agnostic claims;
- adapter lossiness becomes easier to see before integration work begins;
- Async Lifecycle and Async Reliability artifacts become sharper because lower-level portability truth exists below them;
- Atlas / Adoption recommendations can describe runtime lock-in and environment fit more honestly;
- and future `std`/language discussions get better evidence about which async seams are genuinely shared, adapter-mediated, or still only `watch` / `defer`.

## Archive fit
This proposal fills a real gap between existing archive kits:
- **Async Lifecycle Kit** handles cancellation, ownership, shutdown, and lifecycle evidence,
- **Async Reliability Stack** handles lifecycle/replay/exploration composition,
- **Interop Commons Kit** handles broader cross-domain neutral seams,
- **Navigation + Atlas** handle guidance and recommendation,
- and **Runtime Capability Kit** handles authority and least privilege.

But none of those is the portable contract for the **lower-level shared async vocabulary and capability layer** between competing runtimes, adapters, and environment families.
Async Commons Kit is the missing substrate that lets Rust reduce gratuitous async fragmentation deliberately instead of by folklore, adapters of uncertain scope, or premature standardization.
