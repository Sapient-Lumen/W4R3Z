# Gap: async runtime neutrality still collapses too many non-equivalent lanes

## Summary
Rust has enough async substrate now that the next missing contribution is **not** obviously another runtime, reactor, or convenience facade.
The more strategic missing piece is a way to publish and review **which async lane a crate actually depends on**.

Today projects regularly collapse together:
- shared `Future` / poll / wake substrate,
- spawn versus local-`!Send` execution,
- `futures-io` versus Tokio I/O,
- timer / timeout capabilities,
- stream / async-sequence posture,
- server-runtime versus embedded / `no_std` environment assumptions,
- and higher-level lifecycle/reliability conclusions.

That collapse makes portability claims sound stronger than they are and forces downstream adopters to rediscover the real boundaries crate by crate.

## Ecosystem signals
- The March 2026 Rust challenges writeup says async remains a major pain point and that library choice can lock projects into one runtime family.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025H1 async flagship says runtime choice and interoperability are central problems, and the July 2025 goals update says async traits and generators/streams are meant to unblock the next generation of async libraries.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- The Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than sync Rust.
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- `Future` is in `std`, but key adjacent surfaces remain plural: `futures-task` exposes `Spawn` / `LocalSpawn`, `futures-io` exposes async I/O traits, Tokio keeps its own runtime/task/time/I/O surfaces, `tokio-util::compat` bridges but does not erase those differences, and Embassy shows that embedded async occupies a materially different capability environment.
  https://doc.rust-lang.org/std/future/trait.Future.html
  https://docs.rs/futures/latest/futures/task/index.html
  https://docs.rs/futures/latest/futures/io/index.html
  https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html
  https://docs.rs/tokio/latest/tokio/time/index.html
  https://docs.rs/tokio-util/latest/tokio_util/compat/index.html
  https://docs.rs/embassy-executor/latest/embassy_executor/
- The async-iterator RFC is still the right reminder that stream / async-sequence work is important but not fully settled shared substrate.
  https://rust-lang.github.io/rfcs/2996-async-iterator.html

## What is awkward today
Rust already has serious async tools, but the review boundary is poor.
Teams still have to reverse-engineer questions like:
- is this crate only promising `Future` compatibility or also spawn/time/I/O assumptions,
- does “runtime agnostic” really mean `Send`-friendly and local-`!Send`-safe,
- are Tokio I/O claims native or compat-adapted,
- is timeout behavior part of the crate’s API contract,
- is stream support mature substrate or watch-worthy ecosystem motion,
- and does a portability sentence still hold outside one OS/server runtime family.

Without a portable async-commons contract, those answers get reconstructed from:
- feature lists,
- scattered README prose,
- examples written for one runtime,
- adapter crates of unclear lossiness,
- issue threads about `Send`, timers, or local tasks,
- and downstream folklore.

## Why it matters
A lane-aware async substrate would improve:
1. **library design** — crates could publish exact async capability requirements instead of hand-wavy runtime-neutrality claims;
2. **adoption decisions** — teams could compare runtime lock-in and environment fit before integration work starts;
3. **lifecycle tooling** — Async Lifecycle could import lower-level spawn/time/local/environment truth instead of narrating it itself;
4. **interop and docs** — downstream consumers could compress async posture without laundering it into one badge;
5. **future standardization debates** — discussions about `std` or broader common async vocabulary would have better evidence about what is already shared, what is adapter-only, and what is still `watch` or `defer`.

## What “good” looks like
A worthy contribution here is **not** another runtime wrapper.
It is a thin async-commons layer with artifacts like:
- `async-lane-profile/v0` — which lane is being claimed (`core-future`, `spawn`, `local`, `io`, `time`, `stream-watch`, `environment`, `consumer-import`);
- `async-capability-profile/v0` — what a crate actually requires;
- `async-adapter-profile/v0` — what is native versus compat-bridged and what is lossy;
- `async-readiness-report/v0` — whether a seam is `promote`, `pilot`, `watch`, or `defer`;
- `async-commons-pack/v0` — one attachable bundle for lifecycle, reliability, atlas, docs, and assistants.

That would let Rust teams talk about async portability honestly without pretending the ecosystem has already converged on one universal async surface.
