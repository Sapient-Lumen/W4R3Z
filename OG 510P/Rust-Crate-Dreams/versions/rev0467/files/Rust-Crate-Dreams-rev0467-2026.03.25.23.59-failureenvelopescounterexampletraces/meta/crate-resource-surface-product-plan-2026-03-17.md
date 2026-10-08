# Crate resource-surface product plan — 2026-03-17

This note exists to keep **P-0521 Crate Resource Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing queue / pool / cache / worker / budget contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0521** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- what resource classes their crate can accumulate or keep alive,
- which of those classes are bounded, effectively unbounded, burst-bounded, or only externally bounded,
- what happens when demand outruns supply,
- which knobs actually control queue depth, worker count, cache capacity, pool size, or burst,
- which pressure signals are worth watching,
- and what changed between releases.

It should **not** try to become a new runtime, a new metrics backend, a new queue/cache/rate-limiter library, or a precise memory profiler.
Those are imports and proving grounds, not the product.

## What the crate should provide other people

For downstream users, operators, and release reviewers, the crate should provide:

1. **One compact resource contract** instead of folklore scattered across README prose, builder docs, examples, support tickets, and incident dashboards.
2. **A boundedness map** so users can see which paths are hard-capped, configurable, burst-limited, externally bounded, or effectively unbounded by default.
3. **A saturation receipt** so overload stops being vague: wait, reject, evict, queue, spill, or keep growing.
4. **Pressure-signal guidance** so teams know which metrics or counters actually indicate backlog, thread fanout, cache pressure, or pool growth.
5. **Named capacity profiles** for scenarios like `small_local_tool`, `default_service`, `high_fanout_client`, `bounded_memory`, and `manual_review_required`.
6. **A short human summary** that can be pasted into integration docs, ops runbooks, or release notes.
7. **A release diff** that makes hidden default growth or new unbounded paths loud.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. adapters for common Tokio / reqwest / tower / cache / limiter substrate instead of bespoke reinvention,
4. one place to record resource posture that is narrower than performance and more honest than generic observability,
5. and a CI gate for “this release changed resource promises”.

## Recommended `0.1` command surface

### `cargo resource-surface init`
Create a starter `resource-pack.toml` by importing obvious candidates from:

- maintainer-declared public components,
- selected builder defaults,
- known queue / cache / pool / worker classes,
- selected Tokio runtime settings and metrics names,
- and existing scenario/profile declarations.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo resource-surface capture`
Emit one normalized receipt bundle from a declared resource scenario.
This should capture:

- resource classes,
- boundedness classes,
- saturation behavior,
- pressure signals,
- reclaim obligations,
- and imported evidence sources.

`capture` should work on imported artifacts too.
It must not require deep runtime instrumentation to be useful.

### `cargo resource-surface check`
Run the local validation pass:

- do declared resource classes and bounds parse,
- do boundedness classes and saturation classes parse,
- do scenario fixtures still match the declared posture,
- are “watch these metrics” claims connected to named signals,
- are externally-bounded or manual-review-only cases clearly labeled,
- and which parts remain uncertain?

### `cargo resource-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `effectively_unbounded_default`
- `thread_cap_exists_but_queue_not_summarized`
- `inflight_limit_claim_without_backlog_boundary`
- `cache_capacity_claim_without_weighting_mode`
- `pool_default_no_limit`
- `pressure_signal_missing`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo resource-surface summary`
Render a short receiver-facing note for integration docs or operator runbooks.
A good summary answers:

- what can accumulate,
- which of those things are actually bounded,
- what happens at saturation,
- which knobs matter,
- which pressure signals to watch,
- and where the caveats are.

### `cargo resource-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `resource_class_added`
- `resource_class_removed`
- `boundedness_changed`
- `default_bound_changed`
- `saturation_changed`
- `pressure_signal_changed`
- `reclaim_obligation_changed`
- `manual_review_required`

### `cargo resource-surface pack`
Emit one compact `.resourcesurface.zip` bundle for CI artifacts, release review, downstream support, or integration handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `resource_surface_model`
  - shared Rust types for packs, receipts, reports, manifests, evidence classes, and diffs
- `resource_surface_discovery`
  - import logic for queues, pools, caches, worker classes, bounds, and adapter hints
- `resource_surface_check`
  - policy validation, drift checks, and doctor warnings
- `resource_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-resource-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `resource_surface_tokio`
- `resource_surface_reqwest`
- `resource_surface_tower`
- `resource_surface_moka`
- `resource_surface_governor`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `resource-pack.toml`
- `resource-surface.receipt.json`
- `capacity-profile.manifest.json`
- `saturation-behavior.report.json`
- `reclaim-obligation.report.json`
- `resource-budget.report.json`
- `resource-check.report.json`
- `resource-diff.report.json`
- `resource.summary.md`

This pass adds three more important artifacts:

- `boundedness-class.policy.json` — what `bounded`, `configurable`, `burst_bounded`, `externally_bounded`, `effectively_unbounded`, and `manual_review_required` actually mean for downstream support.
- `pressure-signal.profile.json` — which queue / thread / pool / cache / rate-budget signals should be watched for a given resource class or scenario.
- `saturation-evidence.receipt.json` — what was actually observed at the boundary: wait, reject, queue-after-cap, evict, or keep-buffering.

Those files matter because resource support gets vague again if the archive only records “there is a queue or pool” without making clear:

- whether the default is really bounded,
- which signal proves pressure is building,
- and what counts as evidence that saturation behavior matched the documentation.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared public surface**
   - `resource-pack.toml`
   - maintainer-declared resource classes and knobs
2. **Boundedness classes**
   - hard caps
   - configurable caps
   - burst budgets
   - external/backlog boundaries
3. **Saturation behavior**
   - wait / reject / evict / queue / keep-growing / manual review
4. **Reclaim obligations**
   - receiver drain
   - explicit close
   - idle timeout
   - eviction
   - task completion
   - process exit
5. **Pressure signals**
   - queue depth
   - worker counts
   - blocking queue depth
   - idle connections
   - cache entry/weight counts
   - rate budget signals
6. **Manual review zones**
   - anything backend-specific, topology-specific, or not directly observed

The importer should prefer visible uncertainty over synthesis.

## Boundedness-class policy

The first implementation should treat **boundedness meaning as first-class review material** and keep it separate from raw numeric defaults.

### What should count as boundedness classes in `0.1`

- `bounded`
- `configurable`
- `burst_bounded`
- `externally_bounded`
- `effectively_unbounded`
- `manual_review_required`

### What should *not* be encoded as boundedness classes in `0.1`

- “there is probably some practical limit because the machine has finite RAM”
- “the runtime has a limit somewhere internally, so the scenario is bounded enough”
- “the crate docs mention concurrency so backlog must be solved too”

The boundedness policy should be versioned and diffable.
If a maintainer cannot explain whether a path is capped by the crate itself, the class should fall back to `manual_review_required`.

## Pressure-signal policy

The first implementation should treat **pressure signals as support promises**, not just optional telemetry nice-to-haves.
A good `0.1` should model:

- `queue_depth`
- `blocking_queue_depth`
- `num_workers`
- `num_blocking_threads`
- `global_runtime_queue_depth`
- `idle_connection_count`
- `cache_entry_count`
- `cache_weight`
- `rate_budget_remaining`
- `manual_review_required`

with optional source hints such as:

- `tokio::runtime::RuntimeMetrics::global_queue_depth`
- `tokio::runtime::RuntimeMetrics::num_workers`
- `tokio::runtime::RuntimeMetrics::num_blocking_threads`
- `reqwest::ClientBuilder::pool_max_idle_per_host`
- `moka::future::Cache::entry_count`
- application-specific counters imported by name

The policy should allow “no good generic signal” only when that caveat is itself explicit.

## Saturation-evidence policy

The first implementation should treat **what happened at the boundary** as distinct from declared intent.
A useful `0.1` evidence vocabulary should include:

- `send_waited_for_capacity`
- `send_rejected`
- `task_queued_after_thread_cap`
- `connection_reused`
- `connection_opened`
- `entry_evicted`
- `budget_exhausted`
- `continued_buffering`
- `manual_review_required`

with the reminder that “limit exists” is not enough evidence.
The receipt should record:

- what resource class was under stress,
- what class of bound was claimed,
- what saturation behavior was claimed,
- what was observed,
- and which imported source or fixture supports the observation.

## Recommended proving grounds

The first `0.1` proving grounds should stay close to substrate that already has sharp resource semantics:

1. **Tokio bounded vs unbounded channels**
   - explicit backpressure versus arbitrary buffering
2. **Tokio `spawn_blocking` bridges**
   - large default blocking-thread limits, queueing after the cap, and non-abortability after start
3. **Reqwest connection pools**
   - internal reuse plus pool-idle timeout and max-idle-per-host defaults
4. **Moka caches**
   - entry-count bounds versus weighted-size bounds and eviction posture
5. **Tower / governor limits**
   - inflight/rate bounds that still leave surrounding backlog or composition questions explicit

A strong `0.1` does not need to solve all of those deeply.
It needs enough adapters and fixtures to prove the vocabulary is real.

## Three fixture families this pass makes especially important

1. **`unbounded_channel_receiver_falls_behind`**
   - prove that “send always succeeds” and “arbitrarily buffered” means `effectively_unbounded` + `unbounded_growth_risk`
2. **`spawn_blocking_queue_after_thread_cap`**
   - prove that a thread cap may still imply queue growth, not rejection, and that shutdown semantics are adjacent but separate
3. **`tower_concurrency_limit_upstream_backlog_external`**
   - prove that bounding inflight service work does not automatically bound upstream waiting, buffering, or admission

## Out of scope for `0.1`

- exact memory accounting across all allocators and environments
- automatic inference of every hidden internal queue or pool
- replacing profiler, dashboard, or tracing stacks
- proving leak-freedom or fairness properties
- becoming a full performance lab or autoscaling advisor

## Adoption strategy

Start with crates that already expose resource knobs but document them only piecemeal.
Make the first release mostly about **resource truth and reviewability**, not heavy instrumentation.
The easiest win is a summary that answers “what can build up, what stops it, and what should I watch?”
Then make diffing part of normal release review so hidden default growth gets caught early.

## Why this looks buildable now

The substrate is unusually concrete:

- Tokio `mpsc` already distinguishes bounded backpressure from arbitrarily buffered unbounded channels.
- Tokio runtime builders and runtime metrics already expose worker counts, queue depth, and blocking-thread posture.
- `spawn_blocking` already documents queueing after the configured upper limit.
- Reqwest already documents internal connection pooling and an unlimited-by-default max-idle-per-host setting.
- Moka already documents entry-count and weighted-size bounds.
- Tower and governor already document concurrency and burst/rate primitives.

That means the missing value is no longer “invent resource controls”.
It is the **boring contract layer** above them.
