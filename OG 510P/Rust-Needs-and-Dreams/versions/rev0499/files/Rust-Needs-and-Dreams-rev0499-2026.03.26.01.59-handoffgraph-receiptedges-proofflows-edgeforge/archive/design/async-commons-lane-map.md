# Design: Async Commons lane map (core futures, spawn/local capability, I/O traits, time/deadlines, stream/watch posture, environment lanes, and consumer imports)

## Goal
Sharpen **Async Commons Kit** so the archive stops treating “async portability” or “runtime agnostic” as one bucket.
Rust already has some real shared async substrate, some adapter-bridged substrate, some runtime-shaped surfaces, and some still-watch-worthy language/library seams.
Those differ in **what is actually shared**, **what depends on a runtime family**, **what depends on environment (`std`, `alloc`, `no_std`, embedded, OS-backed drivers)**, and **what downstream stacks may safely compress into adoption or lifecycle claims**.

The archive should therefore keep async-commons work grounded in a lane map instead of one flattened runtime-neutrality story.

## Signals from the current ecosystem
- The March 2026 Rust challenges writeup says async remains a major pain point, that library choice can lock projects into one runtime family, and that the ecosystem may need more cohesive async library traits/functions over time.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025H1 async flagship says runtime choice and runtime interoperability are central pain points, while the July 2025 goals update says progress on async traits and generators/streams is intended to unblock the next generation of async libraries.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- The Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than sync Rust.
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- `std::future::Future` is already in the standard library, which is proof that some async vocabulary is truly shared.
  https://doc.rust-lang.org/std/future/trait.Future.html
- The `futures` family still provides neutral or semi-neutral substrate such as `Stream`, `Spawn` / `LocalSpawn`, and `futures-io`’s `AsyncRead` / `AsyncWrite` traits.
  https://docs.rs/futures/latest/futures/task/index.html
  https://docs.rs/futures/latest/futures/io/index.html
  https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- Tokio still makes runtime-shaped surfaces explicit: its runtime provides an I/O driver, scheduler, timer, and blocking pool; `spawn` behavior depends on runtime configuration; `LocalSet` exists for `!Send` futures; and `tokio::time` types require runtime context.
  https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  https://docs.rs/tokio/latest/tokio/task/fn.spawn.html
  https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html
  https://docs.rs/tokio/latest/tokio/time/index.html
- `tokio-util::compat` explicitly bridges Tokio I/O traits and `futures-io`, which is strong evidence that one important async lane is adapter-mediated rather than natively unified.
  https://docs.rs/tokio-util/latest/tokio_util/compat/index.html
- Embassy’s executor is explicit that embedded async is a distinct environment lane: no `alloc`, no heap, statically allocated tasks, and compile-time RAM-fit checking.
  https://docs.rs/embassy-executor/latest/embassy_executor/
  https://embassy.dev/book/
- The async-iterator RFC and the 2025 async goals update together show that stream / async-sequence ergonomics remain live language-and-library motion rather than finished neutral substrate.
  https://rust-lang.github.io/rfcs/2996-async-iterator.html
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

## The lanes

### 1) Core future / poll / wake lane
This is the lane where the question is: what async substrate is already truly shared across the ecosystem today?

What defines it:
- `Future` / poll / wake vocabulary
- pin / poll contract assumptions
- task-wake mechanics and base executor-facing vocabulary
- the minimum surface downstream crates can reasonably assume without choosing a runtime family

Why it deserves its own lane:
- this is the strongest genuinely shared async substrate today
- it is smaller than “async portability” rhetoric usually implies
- downstream stacks should import this lane carefully rather than pretend timers, spawn, I/O, or streams are equally shared already

Design rule:
- keep core future/poll/wake truth distinct from richer runtime-shaped facilities

### 2) Spawn / executor capability lane
This is the lane where the question is: what task-spawning capability is required or provided, and under what `Send` / local / shutdown assumptions?

What defines it:
- `Spawn` / `LocalSpawn` style capability
- executor family and runtime identity
- blocking-spawn posture where relevant
- task lifetime and shutdown-availability assumptions

Why it deserves its own lane:
- there is neutral executor vocabulary, but real runtime behavior and guarantees still vary materially
- the `Send` versus local split is strategically important for library portability
- many libraries only need a capability profile, not a universal executor API

Design rule:
- keep executor capability truth distinct from core future substrate and from lifecycle/shutdown evidence above it

### 3) Local / `!Send` placement lane
This is the lane where the question is: can non-`Send` futures run, where do they live, and what thread/placement constraints apply?

What defines it:
- local-task support (`LocalSpawn`, `LocalSet`, local executors)
- same-thread or thread-affine execution posture
- task-local or thread-local assumptions when intentionally required
- unsupported local-task scenarios

Why it deserves its own lane:
- “supports async” often hides the decisive `Send` versus local boundary
- many adapters flatten this as a footnote even though it changes crate design materially
- embedded, GUI, and some runtime-specific designs depend on this lane sharply

Design rule:
- keep local-task placement truth distinct from generic spawn claims

### 4) I/O trait and adapter lane
This is the lane where the question is: what asynchronous I/O vocabulary is being claimed, and is it native or adapter-mediated?

What defines it:
- `futures-io` or runtime-native I/O trait family
- compat adapters and conversion direction
- lossy edges, buffering, pinning, wake/readiness assumptions
- which operations or transports remain runtime-specific

Why it deserves its own lane:
- one of the clearest practical async-fragmentation seams is Tokio I/O versus `futures-io`
- adapters are useful, but adapter existence is not the same as one native shared I/O contract
- downstream libraries need to know whether a portability claim is native or bridged

Design rule:
- keep I/O trait truth and adapter truth distinct instead of narrating one fake universal async I/O surface

### 5) Time / deadline lane
This is the lane where the question is: what timer, timeout, interval, or deadline semantics are required, and from which runtime/environment do they come?

What defines it:
- runtime-owned timer identity
- timeout / sleep / interval semantics
- clock granularity and environment assumptions
- cancellation or timeout behavior that affects upper layers

Why it deserves its own lane:
- there is no finished `std` async timer substrate analogous to `Future`
- timer behavior is often runtime-bound and environment-sensitive
- crates that only need “some timer capability” should be able to say that without pretending timer semantics are universal

Design rule:
- keep timer/deadline capability truth distinct from both core future substrate and lifecycle shutdown policy

### 6) Stream / async-sequence lane
This is the lane where the question is: what is the status of asynchronous multi-item sequences, and is the claim stable shared substrate, adapter lore, or watch-worthy language motion?

What defines it:
- `Stream` / async-iterator / generator posture
- borrow-sensitive or lending sequence assumptions
- boxing/buffering/adapter costs
- readiness class such as `pilot`, `watch`, or `defer`

Why it deserves its own lane:
- this seam matters a lot, but it is not as settled as `Future`
- goals work explicitly links generators/streams to the next generation of async libraries
- the archive needs a place to publish disciplined `watch` verdicts instead of faking maturity

Design rule:
- keep stream/async-sequence truth explicit and graded rather than laundering it into a mature portability badge

### 7) Environment / runtime-family lane
This is the lane where the question is: in what environment is the async system expected to run, and what that means for memory model, drivers, and available capabilities?

What defines it:
- server/runtime-with-drivers posture
- embedded / `no_std` / no-alloc posture
- OS-backed versus custom-driver/runtime posture
- imported assumptions about blocking pools, I/O drivers, and timers

Why it deserves its own lane:
- Tokio-style runtimes and Embassy-style executors are not just different libraries; they inhabit different capability environments
- environment posture often decides what a crate can honestly promise before any adapter enters the story
- this lane prevents “runtime agnostic” from silently meaning “agnostic inside one OS/server world only”

Design rule:
- keep environment truth explicit and upstream of any compressed portability claim

### 8) Consumer-import lane
This is the lane where async-commons truth is compressed for lifecycle, reliability, atlas/adoption, docs, CI, or assistants.

What defines it:
- consumer class
- imported lane refs and readiness classes
- permitted claims and mandatory caveats
- forbidden automatic conclusions

Why it deserves its own lane:
- this is where the archive is most tempted to flatten lane truth into one sentence like “supports multiple runtimes”
- different consumers need different compression and caveat rules
- honest consumer views remain downstream and bounded rather than becoming the source of semantic truth

Design rule:
- keep consumer renderings thin, explainable, and explicitly downstream of canonical async lanes

## Cross-lane adapter risks
The archive should make at least these risks explicit:
1. **core future ↔ spawn/executor**
   - shared `Future` vocabulary does not imply shared executor or spawn semantics.
2. **spawn ↔ local placement**
   - generic spawning and `!Send` same-thread placement are not interchangeable capabilities.
3. **I/O lane ↔ adapter lane**
   - a compat adapter is not proof that the two I/O surfaces are semantically identical.
4. **time lane ↔ lifecycle lane**
   - timer availability or timeout helpers do not by themselves define shutdown/cancellation policy.
5. **stream/watch lane ↔ mature shared substrate**
   - active language motion should not be narrated as already-settled portable API truth.
6. **environment lane ↔ portability sentence**
   - server-runtime portability does not imply embedded or no-alloc portability.
7. **any canonical lane ↔ consumer summary**
   - lifecycle/reliability/adoption/docs summaries must not silently replace lane evidence with one badge.

## What should change elsewhere in the archive
- **Async Commons Kit** should cite this lane map as the rule for what must stay separate.
- **Async Lifecycle Kit** should remain the owner of cancellation propagation, shutdown policy, task topology, and lifecycle evidence, but it should now import spawn/time/local/environment lane truth from Async Commons instead of narrating lower-level portability from scratch.
- **Async Reliability Stack** should remain the owner of lifecycle + replay + simulation composition above this substrate.
- **Interop Commons**, **Tooling Contract**, **Atlas**, **Adoption Decision**, and **support/docs consumers** should import bounded async-commons views rather than each carrying a hidden model of async portability.

## Worthy contribution, sharpened
The worthy contribution here is **not** another universal runtime facade, compatibility badge, or marketing claim that one crate “works on all runtimes.”
It is a thin `cargo async-commons` / `async-commons-pack/v0` layer whose lane profiles, capability declarations, adapter-lossiness reports, readiness classes, and bounded consumer summaries let Rust teams compare async claims honestly across core future substrate, spawn/local capability, I/O adapters, time/deadline requirements, stream/watch posture, and environment families without semantic collapse.
