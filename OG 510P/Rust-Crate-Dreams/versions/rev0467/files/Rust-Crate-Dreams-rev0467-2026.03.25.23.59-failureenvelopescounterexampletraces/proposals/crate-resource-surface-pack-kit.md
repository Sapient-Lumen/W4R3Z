---
id: P-0521
title: Crate Resource Surface Pack Kit — queue/pool/cache/thread maps, saturation receipts, and budget diffs for library authors
status: idea
domains: [crates, dx, performance, async, resource-management, backpressure, capacity-planning, supportiveness]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.channel.html
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.unbounded_channel.html
  - https://docs.rs/tokio/latest/tokio/runtime/struct.Builder.html
  - https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
  - https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html
  - https://docs.rs/reqwest/latest/reqwest/struct.Client.html
  - https://docs.rs/tower/latest/tower/limit/index.html
  - https://docs.rs/moka/latest/moka/future/struct.CacheBuilder.html
  - https://docs.rs/moka/latest/moka/future/struct.Cache.html
  - https://docs.rs/governor/latest/governor/struct.Quota.html
  - https://docs.rs/governor/latest/governor/struct.RateLimiter.html
  - https://docs.rs/tokio/latest/tokio/runtime/struct.RuntimeMetrics.html
  - https://docs.rs/tokio-metrics/latest/tokio_metrics/
  - https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html
  - https://docs.rs/tokio/latest/tokio/sync/struct.SemaphorePermit.html
  - https://docs.rs/tower/latest/tower/buffer/index.html
  - https://docs.rs/tower/latest/tower/struct.ServiceBuilder.html
  - https://docs.rs/sqlx/latest/sqlx/struct.Pool.html
  - https://docs.rs/sqlx/latest/sqlx/pool/struct.PoolOptions.html
  - https://docs.rs/deadpool/latest/deadpool/managed/struct.Pool.html
---

# Problem

The archive now has much better receiver-facing lanes for:

- choosing crates,
- understanding support claims,
- fitting interop profiles,
- getting compile-time guidance,
- handling runtime failure handoff,
- upgrading,
- leaving a crate,
- choosing setup scenarios,
- reasoning about performance posture,
- understanding observability surfaces,
- reviewing authority / determinism posture,
- and reviewing lifecycle / shutdown behavior.

It still lacks a good answer to a different but extremely common downstream question:

> “If I adopt this crate in production, how much stuff can it accumulate or keep around — queues, buffers, threads, tasks, permits, connections, cache entries — and what happens when that stuff fills up?”

That gap matters because current Rust substrate already makes resource posture real but scattered.

The December 2025 Rust vision-doc work explicitly recommends more **supportive interfaces from crates**.
The 2025 State of Rust survey says online docs remain the preferred canonical reference, followed by studying code itself, and it also says resource usage is still among the recurring productivity problems.
That makes resource truth a crate-support surface, not merely a benchmark footnote.

Today’s ecosystem already exposes many sharp resource knobs and failure modes:

- Tokio `mpsc` distinguishes **bounded** channels with backpressure from **unbounded** channels that can buffer arbitrarily if a receiver falls behind.
- Tokio runtime builders expose worker-thread and stack-size configuration.
- `spawn_blocking` can keep spawning blocking threads until the configured upper limit is reached and then queue work.
- `reqwest::ClientBuilder` exposes pool idle timeout and max idle connections per host.
- `tower::limit` exposes explicit concurrency and rate limiting layers.
- Moka exposes cache `max_capacity` and weighted sizing.
- Governor exposes quotas with replenishment intervals and burst size.
- Tokio runtime metrics and `tokio-metrics` expose task counts, queue depths, worker counts, and related observations.

But today that substrate still does **not** give maintainers one boring workflow for questions like:

- which public scenarios allocate bounded versus effectively unbounded queues,
- which pools, caches, or worker sets exist by default,
- whether saturation blocks, waits, drops, evicts, errors, spills to disk, or keeps growing,
- what knobs actually bound memory, concurrency, backlog, or connection counts,
- which defaults are safe only for small loads or local tools,
- which metrics should be watched to see pressure building,
- and how that resource surface changed across releases.

The worthy crate is therefore **not** another queue, **not** another cache, **not** another rate limiter, and **not** another metrics reporter by itself.
It is a **Crate Resource Surface Pack Kit**: a crate that helps maintainers author, test, diff, and export the receiver-facing resource contract their crate gives other people.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What resources can this crate accumulate, retain, or keep alive?**
2. **Which of those resources are bounded, effectively unbounded, or externally bounded?**
3. **What happens at saturation — block, wait, reject, evict, backpressure, degrade, or panic?**
4. **Which knobs actually control memory, concurrency, backlog, pool size, or burst?**
5. **Which metrics or receipts can prove the resource posture under a named scenario?**
6. **How did that resource surface change across releases?**

That is more valuable than leaving users to reconstruct capacity and pressure behavior from README snippets, builder docs, issues, and production incidents.

# What it provides

- `resource-pack.toml` — versioned declaration of queues, pools, caches, worker classes, resource knobs, default bounds, and saturation promises.
- `resource-surface.receipt.json` — observed receipt for queue classes, thread pools, runtime workers, cache bounds, pool settings, and selected scenario wiring.
- `capacity-profile.manifest.json` — named profiles such as `tiny_cli`, `default_service`, `high_fanout_client`, `bounded_memory`, or `manual_review_required`.
- `saturation-behavior.report.json` — explicit classification such as `backpressure_wait`, `reject_with_error`, `drop_oldest`, `evict_lru`, `queue_until_limit`, `unbounded_growth_risk`, or `manual_review_required`.
- `reclaim-obligation.report.json` — what frees capacity: receiver drain, explicit close, idle timeout, eviction, task completion, shutdown, or process exit.
- `resource-budget.report.json` — declared ceilings or representative budgets for queue depth, worker count, cache capacity, pool size, burst, or open-connection counts.
- `resource-check.report.json` — verifies fixtures still match declared bounds and saturation semantics.
- `resource-diff.report.json` — compares two releases and classifies `bound_added`, `bound_removed`, `default_increased`, `default_decreased`, `saturation_semantics_changed`, `resource_class_added`, and `manual_review_required`.
- `resource.summary.md` — short human-facing explanation of what a downstream integrator is actually buying.
- `boundedness-class.policy.json` — explicit meaning for `bounded`, `configurable`, `burst_bounded`, `externally_bounded`, `effectively_unbounded`, and `manual_review_required`.
- `pressure-signal.profile.json` — named signals to watch for queue pressure, blocking-thread fanout, pool growth, cache pressure, or budget exhaustion.
- `saturation-evidence.receipt.json` — observed evidence for wait/reject/queue/evict/continued-buffering behavior under a named scenario.
- `admission-path.report.json` — which layer, permit gate, queue, or pool admits work first and what effective in-flight budget that creates.
- `backlog-ownership.receipt.json` — whether backlog lives inside the crate, upstream, downstream, or in an external/shared service.
- `capacity-shrink.report.json` — what can reduce effective capacity over time, including forgotten permits, closed pools, resized pools, or other support-relevant shrink paths.
- `acquire-fate.report.json` — whether callers wait, time out, error, or wake closed when the resource boundary is hit.
- `cargo resource-pack check` — run resource fixtures and verify receipts against the pack.
- `cargo resource-pack diff <old> <new>` — show how resource promises changed.
- `cargo resource-pack summary` — render a concise operator/integrator summary.

# What the crate should provide other people

1. **A receiver-facing resource contract** above scattered builder docs and issue-thread folklore.
2. **A boundedness map** so integrators can see what is capped, what is bursty, and what can grow without a hard stop.
3. **A saturation-behavior matrix** so teams know whether overload waits, sheds, errors, evicts, or silently accumulates.
4. **Named capacity profiles** for real scenarios instead of one vague “defaults are fine” story.
5. **Checked receipts** that prove which resource knobs and defaults were actually active in a scenario.
6. **An admission-order explanation** so teams can see whether queueing happens before or after the visible limit.
7. **A backlog-ownership receipt** so teams know whether the waiting room is actually owned by the crate.
8. **A capacity-shrink report** so effective limits are not confused with constructor-time limits only.
9. **An acquire-fate report** so callers know whether they wait, time out, fail closed, or need manual review at the boundary.
10. **A diffable resource surface** so release reviewers can spot hidden default growth, new unbounded paths, or changed admission order.
11. **Importable vocabulary** for docs portals, support bots, pathfinder crates, org review tooling, and incident playbooks.

# Persona / who it’s for

- library authors with queues, pools, caches, runtimes, background workers, or rate limits
- SDK/client maintainers whose defaults imply connection pooling or request backlog
- framework teams that expose concurrency, worker, buffer, or cache knobs
- downstream integrators trying to make memory / concurrency / queue posture reviewable
- docs/tool authors who want stable artifacts instead of scraping prose

# Users & user stories

- **HTTP client maintainer**: “Publish exactly how many idle connections I may keep, which defaults are effectively unlimited, and which knob changes that.”
- **Async library author**: “Prove whether my request queue is bounded, what happens when it fills, and which metrics show pressure building.”
- **Cache maintainer**: “Tell users whether I bound by entries or weighted size, how eviction works, and which workloads need manual review.”
- **Platform engineer**: “Diff two releases and see whether the crate added a new unbounded queue, larger thread pool, or changed shedding behavior.”
- **Support engineer**: “When someone says memory climbed all night, show whether the crate promised eviction, backpressure, explicit close/drain, or no hard cap at all.”

# Prior art (and why it’s insufficient)

- Tokio `mpsc` documents bounded versus unbounded channels and backpressure behavior.
- Tokio runtime builders expose worker-thread and stack-size knobs.
- `spawn_blocking` documents a large default upper limit and queueing after the limit is reached.
- `reqwest` documents connection-pool configuration.
- `tower::limit` documents concurrency and rate limiting layers.
- Moka documents max-capacity and weighted-size cache bounds.
- Governor documents quotas, burst size, and replenishment behavior.
- Tokio runtime metrics and `tokio-metrics` expose observation substrate.

What remains missing is a **crate-authored resource contract workflow** above those pieces:

- author one resource support contract,
- verify it against fixtures,
- classify boundedness and saturation semantics,
- export stable receipts,
- and diff the resource surface over time.

That is a different lane from:

- **P-0516** configuration scenarios,
- **P-0517** performance envelopes,
- **P-0518** observability surfaces,
- **P-0519** authority surfaces,
- **P-0520** lifecycle surfaces,
- generic limiter/cache/queue crates,
- or runtime metrics stacks.

# Design goals

1. **Receiver-facing resource truth first** — optimize for the integrator adopting a crate, not only the maintainer tuning internals.
2. **Boundedness honesty** — let maintainers say “this path is effectively unbounded unless you opt in to a cap.”
3. **Saturation clarity** — every important resource class should state what happens when demand exceeds supply.
4. **Join, don’t replace** — import existing queue/cache/limit/runtime settings where possible.
5. **Scenario relevance** — support profiles like `small_local_tool`, `latency_sensitive_service`, `offline_batch`, and `manual_review_required`.
6. **Diffability** — support release-to-release review of resource posture.
7. **Wide-scope usefulness** — remain relevant across async, sync, embedded-ish, data, client, server, and CLI crates.

# MVP surface

- Minimal `resource-pack.toml` schema with named resource classes, bounds, and saturation semantics.
- Import lane for selected builder/config/runtime defaults.
- A `resource-check.report.json` that records whether advertised bounds were actually observed.
- `resource-budget.report.json` for declared or representative ceilings.
- `resource-diff.report.json` to compare two resource surfaces.
- `cargo resource-pack summary` to render a short, reviewable Markdown summary.

# Artifact vocabulary

## `resource-pack.toml`

```toml
schema_version = "0.1"
crate = "example-crate"

[[resource]]
name = "request_queue"
kind = "queue"
boundedness = "bounded"
default_bound = 1024
saturation = "backpressure_wait"
profile = "default_service"

[[resource]]
name = "idle_http_connections"
kind = "connection_pool"
boundedness = "configurable"
default_bound = "usize::MAX"
saturation = "manual_review_required"
profile = "high_fanout_client"
```

## `saturation-behavior.report.json`

```json
{
  "schema_version": "0.1",
  "crate": "example-crate",
  "resources": [
    {
      "name": "request_queue",
      "kind": "queue",
      "boundedness": "bounded",
      "saturation": "backpressure_wait",
      "evidence": ["tokio::sync::mpsc::channel(1024)"],
      "manual_review_boundary": null
    },
    {
      "name": "idle_http_connections",
      "kind": "connection_pool",
      "boundedness": "configurable",
      "saturation": "manual_review_required",
      "evidence": ["reqwest::ClientBuilder::pool_max_idle_per_host default usize::MAX"],
      "manual_review_boundary": "bound exists only if integrator overrides the default"
    }
  ]
}
```

# Distinctive implementation shape

## Crates

- `resourcepack-core` — schemas, pack/diff logic, boundedness vocabulary, summary rendering.
- `resourcepack-capture` — importers for selected builder/runtime/queue/cache observations.
- `resourcepack-tokio` — adapters for Tokio queues, runtime builders, runtime metrics, and `spawn_blocking` surfaces.
- `resourcepack-http` — adapters for common client/service pool/limit surfaces.
- `cargo-resource-pack` — CLI.

## Boundedness vocabulary

The crate should make boundedness explicit instead of forcing fake certainty:

- `bounded`
- `configurable`
- `burst_bounded`
- `externally_bounded`
- `effectively_unbounded`
- `manual_review_required`

## Saturation vocabulary

The crate should classify overload behavior directly:

- `backpressure_wait`
- `reject_with_error`
- `drop_newest`
- `drop_oldest`
- `evict`
- `queue_until_limit`
- `spill_or_degrade`
- `unbounded_growth_risk`
- `panic_or_abort`
- `manual_review_required`

# Example scenario families

1. **HTTP client pool** — idle sockets, connect timeout posture, max-idle-per-host default, request concurrency interaction.
2. **Bounded async work queue** — queue depth, backpressure semantics, receiver drain, saturation metrics.
3. **Cache with eviction** — entry or weighted bounds, eviction posture, TTL/TTI interaction.
4. **Blocking worker bridge** — worker-thread upper bound, queueing once saturated, recommended caps for CPU-heavy work.
5. **Rate-limited service boundary** — burst, replenish interval, backpressure versus reject semantics.
6. **Unbounded queue under slow receiver** — “send always succeeds” should become explicit `effectively_unbounded` posture rather than hidden convenience.
7. **Blocking queue after worker-thread cap** — thread caps may still hide a second queue that deserves its own pressure signal.
8. **Inflight limit with external backlog** — concurrency limits can bound in-flight work without owning or documenting the upstream waiting room.

For an implementation-ready `0.1` shape, see `meta/crate-resource-surface-product-plan-2026-03-19.md`.

# Early implementation plan

## 0.1
- Stabilize the pack/report schemas.
- Add `boundedness-class.policy`, `pressure-signal.profile`, `saturation-evidence.receipt`, `admission-path.report`, `backlog-ownership.receipt`, `capacity-shrink.report`, and `acquire-fate.report` as first-class review artifacts.
- Implement summary + diff logic.
- Ship three scenario packs:
  - `http_client_pool`
  - `bounded_async_queue`
  - `evicting_cache`
- Ship three hard-edge scenario families:
  - `unbounded_channel_receiver_falls_behind`
  - `spawn_blocking_queue_after_thread_cap`
  - `tower_concurrency_limit_upstream_backlog_external`

## 0.2
- Add Tokio runtime and `spawn_blocking` importers.
- Add `reqwest`, Tokio `mpsc`, and Moka capture helpers.
- Add `resource-check` fixture runner for selected scenarios.

## 0.3
- Add limit-adapter imports for `tower::limit` and `governor`.
- Add budget-class heuristics and explicit `manual_review_required` output.
- Publish docs showing how to derive receiver-facing summaries from packs.

## 0.4
- Add release-to-release diff classification for hidden default changes.
- Add import/export hooks for docs portals and pathfinder/selection tools.

## 1.0
- Freeze the pack/report schema.
- Publish a conservative glossary for boundedness, saturation, reclaim, and manual-review boundaries.

# Adoption strategy

- Start with crates that already expose resource knobs but document them only piecemeal.
- Make the 0.1 value mostly documentation + fixture honesty, not deep runtime instrumentation.
- Produce summaries that are useful even when only part of the surface is automatically captured.
- Integrate with docs generation and release review so the resource pack becomes part of normal maintenance, not a special audit ritual.

# Why this could be epic

Because many painful Rust production questions are really resource-contract questions hiding behind other labels:

- “Why did memory climb?”
- “Why did latency spike?”
- “Why did the service stop accepting work?”
- “Why did this client keep so many sockets open?”
- “Why did the queue explode when the consumer slowed down?”

Today teams answer those with source dives, dashboards, and incidents.
A crate that makes the **resource surface** reviewable, exportable, and diffable would turn a wide class of vague operational folklore into one boring support artifact.

# Non-goals

- building a new runtime, queue, cache, limiter, or service framework
- promising exact memory usage in every environment
- replacing profilers, metrics stacks, or observability backends
- proving absence of leaks or pathological behavior by itself
- pretending every resource surface can be inferred automatically without maintainer input

# Open questions

- Which resource classes deserve first-class vocabulary in 0.1: threads, tasks, queue depth, pool size, cache size, permits, descriptors, burst, or others?
- How should the crate represent defaults like `usize::MAX` honestly without overfitting to one library’s API wording?
- Which parts of the resource surface can be captured mechanically and which should always remain declared-by-maintainer plus fixture-checked?
- How much should the crate try to connect resource packs to observability packs without collapsing the lanes?
- Which lane should own cross-release “capacity got larger” warnings when the change is performance-relevant but not obviously breaking?

# Sources

- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces; resource usage remains visible pain): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio `mpsc` module docs (bounded vs unbounded, backpressure, clean shutdown, allocation behavior): https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
- Tokio bounded channel docs: https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.channel.html
- Tokio unbounded channel docs: https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.unbounded_channel.html
- Tokio runtime builder docs: https://docs.rs/tokio/latest/tokio/runtime/struct.Builder.html
- Tokio `spawn_blocking` docs: https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- Reqwest client builder and connection-pool docs: https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html
- Reqwest client connection-pooling docs: https://docs.rs/reqwest/latest/reqwest/struct.Client.html
- Tower limit module docs: https://docs.rs/tower/latest/tower/limit/index.html
- Tower buffer docs: https://docs.rs/tower/latest/tower/buffer/index.html
- Tower `ServiceBuilder` docs: https://docs.rs/tower/latest/tower/struct.ServiceBuilder.html
- Moka cache builder and cache capacity docs: https://docs.rs/moka/latest/moka/future/struct.CacheBuilder.html
- Moka cache weighted-size / max-capacity docs: https://docs.rs/moka/latest/moka/future/struct.Cache.html
- Governor quota and rate-limiter docs: https://docs.rs/governor/latest/governor/struct.Quota.html
- Tokio runtime metrics docs: https://docs.rs/tokio/latest/tokio/runtime/struct.RuntimeMetrics.html
- tokio-metrics docs: https://docs.rs/tokio-metrics/latest/tokio_metrics/
- Tokio `Semaphore` docs: https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html
- Tokio `SemaphorePermit` docs: https://docs.rs/tokio/latest/tokio/sync/struct.SemaphorePermit.html
- SQLx pool docs: https://docs.rs/sqlx/latest/sqlx/struct.Pool.html
- SQLx `PoolOptions` docs: https://docs.rs/sqlx/latest/sqlx/pool/struct.PoolOptions.html
- Deadpool managed-pool docs: https://docs.rs/deadpool/latest/deadpool/managed/struct.Pool.html
