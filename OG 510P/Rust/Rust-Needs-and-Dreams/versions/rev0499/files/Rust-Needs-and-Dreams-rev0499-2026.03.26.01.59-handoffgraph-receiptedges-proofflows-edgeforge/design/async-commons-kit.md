# Design: Async Commons Kit (`cargo async-commons`, `async-commons-pack/v0`)

## Goal
Define a portable contract for identifying, specifying, validating, diffing, and reviewing **lane-aware async building blocks** in Rust: capability profiles, common traits/types, adapter truth, readiness reports, and bounded consumer views.

This should help answer questions like:
- what async capabilities does a crate or stack actually require,
- which lane is genuinely shared substrate versus runtime-shaped surface,
- which adapters exist and what semantics or costs they lose,
- which async seams are mature enough for common vocabulary,
- and which seams should stay in explicit `watch` / `defer` posture.

This should **not** replace Tokio, async-std, Smol, Glommio, Embassy, or future runtimes.
It should not pretend `std`, `futures`, runtime crates, and embedded executors already form one finished portability story.
It should make that story reviewable.

Read [`design/async-commons-lane-map.md`](./async-commons-lane-map.md) as the rule for what must stay separate.

## References (signals)
- The March 20, 2026 challenges post says async is a major pain point, that choosing a useful library can lock a project into one runtime family, and that the ecosystem may need more cohesive fundamental async traits/functions over time.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025H1 async goal explicitly says runtime choice and runtime interoperability are central problems in the status quo.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The July 2025 goals update says work on async traits and generators/streams is intended to unblock the next generation of async libraries in the wider ecosystem.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- The Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than sync Rust.
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- `Future` is in the standard library, while the `futures` family continues to provide shared or semi-shared substrate such as `Stream`, `Spawn` / `LocalSpawn`, and `futures-io` traits.
  https://doc.rust-lang.org/std/future/trait.Future.html
  https://docs.rs/futures/latest/futures/task/index.html
  https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
  https://docs.rs/futures-io/latest/futures_io/
- Tokio still owns runtime-shaped surfaces like task spawning, local-task placement, timers, and I/O, while `tokio-util::compat` ships explicit I/O bridges. Embassy shows that embedded async is a materially different environment lane.
  https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  https://docs.rs/tokio/latest/tokio/task/fn.spawn.html
  https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html
  https://docs.rs/tokio/latest/tokio/time/index.html
  https://docs.rs/tokio-util/latest/tokio_util/compat/index.html
  https://docs.rs/embassy-executor/latest/embassy_executor/

## Design principles
1. **Lane map before façade.** Preserve core-future, spawn/local, I/O, time, stream/watch, and environment lanes instead of calling all of it “runtime agnostic”.
2. **Capabilities before slogans.** “Works across runtimes” is not a design. Required capabilities must be explicit.
3. **Neutral core, runtime-shaped edges.** Keep the common layer small and let richer semantics remain adapter- or runtime-specific.
4. **Adapter honesty is first-class.** Boxing, buffering, wake/readiness behavior, cancellation side-effects, `Send`/local constraints, and unsupported paths must be visible.
5. **Language blockers are not crate bugs.** Keep language/compiler blockers distinct from library fragmentation.
6. **Readiness beats wishful standardization.** Some async seams should be marked `watch` or `defer`, not prematurely treated as solved.
7. **Downstream stacks import async commons.** Async Lifecycle, Async Reliability, Atlas, and Adoption should consume this layer rather than silently redefining it.
8. **Std-track is an outcome, not an assumption.** The kit may surface what could belong in `std`, but it must not pretend that decision has already been made.

## Proposed artifact family

### 1) `async-lane-profile/v0`
Declares which async lane is under review and how mature/shared it is.

Fields should include:
- lane id and title
- lane family (`core-future`, `spawn`, `local`, `io`, `time`, `stream-watch`, `environment`, `consumer-import`)
- shared-vs-runtime-shaped classification
- environment posture (`std`, `alloc`, `no_std`, embedded, server-runtime, mixed)
- readiness class (`promote`, `pilot`, `watch`, `defer`)
- imported dependencies on other lanes
- known semantic fault lines

### 2) `async-seam/v0`
Declares the seam under review.

Fields should include:
- seam id and title
- problem scope
- primary lane refs
- candidate adopter families
- known semantic fault lines
- likely downstream consumers

### 3) `async-capability-profile/v0`
Declares what a library, service, or tool actually requires.

Fields should include:
- profile id
- required lane refs
- required capabilities
- optional capabilities
- `Send` / local posture
- no_std / alloc posture
- runtime assumptions
- unsupported environments

### 4) `async-common-surface/v0`
Describes the neutral shared surface actually being claimed.

Fields should include:
- shared traits/types/functions
- semantic invariants
- ownership / pin / poll posture
- explicit exclusions
- extension points

### 5) `async-adapter-profile/v0`
Describes how a runtime or crate maps to the shared surface.

Fields should include:
- adapter id
- source crate/runtime and versions
- source lane and target lane refs
- provided capabilities
- unsupported capabilities
- lossy edges
- allocation / boxing / buffering / pinning costs
- wake/readiness, `Send`/local, and environment assumptions

### 6) `async-vector-set/v0`
Golden vectors and negative cases for the seam.

Fields should include:
- vector id
- scenario description
- expected behavior
- failure expectations
- environment/runtime assumptions
- fixture refs

### 7) `async-readiness-report/v0`
Says whether a seam is actually ready for shared treatment.

Fields should include:
- lane refs and seam id
- evidence summary
- adopter diversity
- unresolved semantic blockers
- language/compiler blockers
- recommendation (`promote`, `pilot`, `watch`, `defer`)

### 8) `async-interop-check-report/v0`
Records what was actually exercised.

Fields should include:
- seam and version ids
- lane refs
- adapter matrix exercised
- vectors run / skipped
- pass/fail/partial status
- environment details
- attached raw outputs/logs

### 9) `async-commons-pack/v0`
Bundle of the above plus human-facing docs, diagrams, and migration notes.

## CLI shape
`cargo async-commons` should be a thin adapter/orchestrator.

Potential commands:
- `cargo async-commons init`
- `cargo async-commons profile`
- `cargo async-commons readiness`
- `cargo async-commons export`
- `cargo async-commons check`
- `cargo async-commons diff`
- `cargo async-commons pack`

The CLI should prefer pointers and normalized reports over giant embedded blobs.

## Initial targets
The first credible version should not start by trying to unify all of async Rust.
It should start where there is already repeated friction and where lane identity clarifies the problem:
1. **I/O lane pilot**
   - neutral `futures-io` style vocabulary
   - Tokio adapter truth via compat layers and explicit unsupported/approximation notes
2. **spawn + local capability pilot**
   - make `Spawn` / `LocalSpawn` / `!Send` posture explicit for libraries and runtimes
3. **time / deadline capability pilot**
   - publish honest timer requirements without pretending timer semantics are universal
4. **stream / async-sequence `watch` pilot**
   - important enough to model
   - not mature enough to flatten today
5. **environment contrast pilot**
   - prove that server-runtime and embedded/no-alloc async lanes do not belong in one fake portability sentence
6. **downstream-consumer pilot**
   - Async Lifecycle imports async-commons output instead of inventing portability claims in place

This matters: a good kit must support both **promotion** and **deferral**.

## What good adoption looks like
A good v1 does not need every runtime in the ecosystem.
It needs a few serious proofs that the artifact family clarifies real portability work.

Success would look like:
- one lane profile plus capability-profile pilot making a library’s runtime needs explicit,
- one I/O seam report plus adapter profile and negative cases,
- one spawn/local or timer capability report showing a nontrivial portability boundary,
- one explicit `watch` async-stream / borrowing readiness report,
- one Async Lifecycle or Adoption consumer that imports async-commons output,
- and one diff showing how portability claims changed across releases.

## Boundaries with other archive proposals
- **Interop Commons Kit** is broader; Async Commons is the async-specialized lower-level seam where language motion and runtime plurality are unusually central.
- **Async Lifecycle Kit** owns cancellation propagation, ownership, shutdown, and lifecycle evidence; it should import portability truth from Async Commons instead of re-inventing it.
- **Async Reliability Stack** owns lifecycle/replay/exploration composition, not the lower-level shared async vocabulary.
- **Runtime Capability Kit** owns authority and least privilege, not executor/timer/I/O portability truth.
- **Adoption Decision / Ecosystem Atlas** recommend async lanes; Async Commons makes their shared substrate reviewable.

## Failure modes to avoid
- a universal async facade that secretly chooses one runtime’s semantics;
- a fake portability badge without lane identity or adapter lossiness;
- letting language/compiler blockers disappear into crate blame;
- treating `Future` in `std` as evidence that the rest of async already has a finished neutral layer;
- or pushing every promising seam into standardization before the ecosystem is ready.

See [`design/async-commons-pilot-program.md`](./async-commons-pilot-program.md) for the ranked rollout. The next credible move is not another runtime wrapper; it is proving that lane profiles, capability declarations, adapter honesty, and watch/defer seam reporting can survive real async-library use.
