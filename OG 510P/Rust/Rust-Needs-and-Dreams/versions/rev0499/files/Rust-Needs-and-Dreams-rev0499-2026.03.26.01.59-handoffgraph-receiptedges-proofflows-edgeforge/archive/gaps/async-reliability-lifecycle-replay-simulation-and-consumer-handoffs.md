# Gap: async reliability still lacks one portable lifecycle → replay → simulation boundary

## Summary
Rust async now has credible building blocks for:
- graceful shutdown and cancellation trees,
- captured failures and replay attempts,
- deterministic or seeded schedule / network / fault exploration,
- and increasingly rich downstream consumers like tests, incidents, debuggers, and support tooling.

What it still lacks is the **portable contract layer** that keeps those truths distinct while letting them compose.

Today, teams can often answer fragments such as:
- “we use `CancellationToken` to request shutdown,”
- “this task set drains before exit,”
- “we captured a flaky failure and can sometimes replay it,”
- “Loom/Shuttle/Turmoil/MadSim found a bad schedule or network world,”
- or “our incident report links to some traces and a reproducer.”

What they still struggle to answer cleanly is:
- what the runtime-shaped lifecycle promise actually was,
- whether cancellation was tree-shaped or flat,
- whether a replay is exact or best-effort,
- what schedule/time/network/fault semantics a simulator approximated,
- how a concrete failure handoff differs from a search campaign,
- and what later consumers may honestly conclude without re-parsing logs, CI glue, and crate-specific folklore.

That missing layer is not another runtime, not another deterministic scheduler, and not another observability dashboard.
It is a **portable async reliability boundary** above lifecycle truth, replay truth, and exploration truth.

## Why now
Current Rust signals make this seam more concrete than it used to be:
- the 2025H1 async flagship explicitly says async remains a multi-year parity effort and calls out runtime choice, runtime interoperability, cancellation sharp edges, and reliability as active ecosystem pain;
- the 2026 flagship themes keep **Just Add Async** active, with milestones around return type notation, `async fn in dyn trait`, immobile types / guaranteed destructors, and ergonomic ref-counting;
- the May 2025 project-goals update says the official Async Book recently gained chapters on concurrency primitives, structured concurrency, and pinning;
- the current Async Book still says async Rust has compatibility constraints across runtimes and a higher maintenance burden than sync Rust;
- Tokio’s own shutdown guidance now teaches `CancellationToken` and `TaskTracker`, and `CancellationToken::child_token` plus `TaskTracker::wait` expose explicit hierarchy/drain semantics rather than vague “cancel everything” folklore;
- concurrency and simulation tools now cover meaningfully different ground: Loom explores executions by permuting valid concurrent interleavings, Shuttle uses randomized testing for scale, Turmoil provides deterministic distributed execution with seeded network hardship, and MadSim provides a deterministic simulator for distributed systems;
- the 2025 State of Rust survey still lists resource usage and debugging among major productivity problems, which is exactly where async hangs, cancellation bugs, and flaky timing failures become painful.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- https://tokio.rs/tokio/topics/shutdown
- https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- https://docs.rs/loom/latest/loom/
- https://docs.rs/shuttle/latest/shuttle/
- https://docs.rs/turmoil/latest/turmoil/
- https://docs.rs/madsim/latest/madsim/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
Today, async reliability truth often gets improvised from incompatible ingredients:
- runtime-specific shutdown code,
- logs and tracing spans,
- test-runner output,
- ad hoc issue repro steps,
- simulator-specific seeds or history dumps,
- debugger screenshots,
- and human memory about which cancellations or timers were “supposed” to work.

That usually leads to five failures:
1. lifecycle policy and observed failures get flattened into one story;
2. replayable failures and exploration campaigns get confused with each other;
3. runtime identity disappears behind fake portability claims;
4. deterministic-testing tools with very different semantics get treated as interchangeable;
5. incident/debug/support consumers quietly become the de facto source of truth.

## Why this matters
This gap affects more than runtime authors.
It matters to:
1. **service maintainers** — because shutdown, draining, and cancellation ownership need reviewable evidence;
2. **library authors** — because runtime portability and shutdown assumptions need to be stated instead of guessed;
3. **test / simulation tool authors** — because interoperability is easier when lifecycle subjects and replay/search artifacts are explicit;
4. **debugging and incident workflows** — because async failures need portable handoff artifacts rather than screenshots and log fragments;
5. **downstream stacks** — because Service Productization, Debuggability, Support Envelope, and Test Execution all benefit from importing one honest async-reliability story.

## What good looks like
A worthy contribution here is a thin composition layer above Async Lifecycle Kit, Replay Kit, and DST Kit, with at least:
- `async-reliability-brief/v0` — why this async reliability subject exists and which runtime/backend lane it covers;
- `async-reliability-pack/v0` — linked lifecycle, replay, and exploration artifacts with explicit caveats;
- `async-reliability-diff/v0` — what changed between two async-reliability review points;
- `async-reliability-handoff/v0` — bounded imports for tests, incidents, debuggers, support, and service/product stacks;
- and a coordinating CLI/layer that validates attachments without absorbing the underlying lifecycle, replay, or simulation tools.

The winning version should keep these distinctions visible:
- **runtime-shaped lifecycle truth** versus **observed failure / replay truth**,
- **exact replay** versus **best-effort replay**,
- **local concurrency exploration** versus **distributed/fault simulation**,
- **declared shutdown/cancellation topology** versus **later incident or debugger conclusions**,
- and **canonical linked packs** versus compressed consumer views.

The bar is not a better async dashboard.
The bar is a durable, explainable, importable evidence boundary for async reliability.
