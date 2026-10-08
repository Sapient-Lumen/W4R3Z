# P-0521 — Crate Resource Surface Pack Kit: product plan refresh (2026-03-19)

## Why this lane deserves another pass

The March 17 plan got the lane to a believable `0.1`.
The sharper move now is to make **resource support** answer a more concrete downstream question:

> “Where does work actually wait, who owns that backlog, what can shrink effective capacity, and what happens to callers at the boundary?”

That question is now unusually buildable because the Rust ecosystem already has real substrate for it:

- Tokio documents the difference between bounded and unbounded `mpsc`, including the risk that unbounded buffering can exhaust memory.
- Tokio documents that `spawn_blocking` reaches a configured thread cap and then queues more work.
- Tokio `Semaphore` documents permit waiting, and `SemaphorePermit::forget` makes capacity shrink a real surface.
- Tower documents that `buffer` versus `concurrency_limit` ordering changes effective in-flight capacity.
- SQLx and Deadpool document pool waiting, timeout, closure, and wake-up semantics.

The missing value is therefore **not** another queue/pool/cache crate.
It is the support layer that turns those scattered facts into one compact contract another maintainer can inspect.

## Main judgment

A worthy `0.1` should treat five review objects as first-class:

1. **admission path** — which queue, permit gate, pool, or layer decides first,
2. **backlog ownership** — whether waiting work is inside the crate, upstream, downstream, or external,
3. **capacity shrink** — what can reduce effective capacity permanently or until reset,
4. **acquire fate** — wait, timeout, error, closed, or manual review,
5. **pressure evidence** — which metrics or scenario receipts actually support the claim.

Those objects sit naturally above the archive’s earlier boundedness / saturation / pressure-signal work.
They do not replace it.
They make it reviewable in the places where production support usually gets murky.

## What the crate should provide other people

For downstream integrators, operators, and maintainers, the crate should provide:

1. **a resource contract they can read quickly**
   - what can accumulate,
   - what is bounded,
   - where waiting happens,
   - what happens at the edge.

2. **an admission-order explanation**
   - whether queueing happens before or after concurrency limits,
   - whether limits bound in-flight work only,
   - whether backlog still exists somewhere else.

3. **a backlog-ownership receipt**
   - crate-owned queue,
   - upstream caller waiting room,
   - downstream service bottleneck,
   - external/shared resource.

4. **a capacity-shrink report**
   - forgotten permits,
   - resized pools,
   - closed pools,
   - dynamic feature toggles,
   - fallback-to-manual-review when capacity cannot be stated honestly.

5. **an acquire-fate report**
   - wait forever,
   - wait with timeout,
   - return closed/error immediately,
   - fairness or ordering note,
   - manual-review boundary.

6. **pressure-evidence guidance**
   - which metrics or counters actually support the support claim,
   - which are optional or only advisory,
   - and which claims have no good generic signal.

7. **release-to-release diffs**
   - hidden default growth,
   - changed admission order,
   - new externally-owned backlog,
   - capacity-shrink behavior added,
   - closure behavior changed.

## Recommended `0.1` artifact set

Keep the earlier artifact set, but promote four more files into first-class review objects:

- `admission-path.report.json`
- `backlog-ownership.receipt.json`
- `capacity-shrink.report.json`
- `acquire-fate.report.json`

The complete compact bundle should revolve around:

- `resource-pack.toml`
- `resource-surface.receipt.json`
- `capacity-profile.manifest.json`
- `saturation-behavior.report.json`
- `resource-budget.report.json`
- `boundedness-class.policy.json`
- `pressure-signal.profile.json`
- `saturation-evidence.receipt.json`
- `admission-path.report.json`
- `backlog-ownership.receipt.json`
- `capacity-shrink.report.json`
- `acquire-fate.report.json`
- `resource-diff.report.json`
- `resource.summary.md`

## Suggested command surface

### `cargo resource-surface init`
Create a starter `resource-pack.toml` plus empty review-object stubs.
Anything uncertain should begin as `manual_review_required`, not guessed.

### `cargo resource-surface capture`
Emit a normalized receipt bundle from a named scenario.
In `0.1`, this should support imported evidence and fixture-driven capture, not heavy universal runtime instrumentation.

### `cargo resource-surface check`
Validate that:
- resource classes parse,
- boundedness classes parse,
- admission-path claims have named resources,
- backlog ownership is explicit,
- capacity shrink is either explained or marked `none`,
- acquire fate is explicit,
- pressure signals are either attached or explicitly unavailable.

### `cargo resource-surface doctor`
Render human-first warnings such as:
- `unbounded_queue_default`
- `buffer_order_changes_total_inflight`
- `permit_forget_can_reduce_capacity`
- `pool_waits_but_timeout_not_summarized`
- `close_wakes_waiters_not_recorded`
- `backlog_owner_not_declared`
- `manual_review_required`

### `cargo resource-surface diff <old> <new>`
Compare two packs or receipts and classify:
- `admission_path_changed`
- `backlog_owner_changed`
- `capacity_shrink_added`
- `capacity_shrink_removed`
- `acquire_fate_changed`
- `default_bound_changed`
- `new_unbounded_path`
- `manual_review_required`

### `cargo resource-surface summary`
Render a short support note answering:
- what accumulates,
- what bounds it,
- where waiting occurs,
- how callers experience the boundary,
- and what to watch.

### `cargo resource-surface pack`
Emit one compact `.resourcesurface.zip` bundle for CI artifacts, release review, support handoff, or pathfinder imports.

## Scenario families that should anchor `0.1`

1. **service builder ordering**
   - `buffer` before `concurrency_limit`
   - `concurrency_limit` before `buffer`
   - why the in-flight budget differs

2. **unbounded channel under slow receiver**
   - explicit `effectively_unbounded`
   - honest memory-risk language

3. **blocking pool after thread cap**
   - worker cap exists,
   - but queued backlog still exists

4. **semaphore permit shrink**
   - capacity is not just the constructor argument,
   - lost permits are a support fact

5. **database or object pool acquire semantics**
   - wait behavior,
   - timeout behavior,
   - close-wakes-waiters behavior,
   - fairness note when documented

6. **externally-owned backlog**
   - concurrency limit bounds in-flight work,
   - but backlog still lives elsewhere

## Recommended workspace split

- `resource_surface_model`
  - schema types and diff classes
- `resource_surface_check`
  - validation and doctor warnings
- `resource_surface_summary`
  - markdown and support-bundle rendering
- `resource_surface_capture`
  - imported-evidence adapters and fixture harness
- `cargo-resource-surface`
  - CLI

Optional adapters can stay optional in `0.1`:
- `resource_surface_tokio`
- `resource_surface_tower`
- `resource_surface_sqlx`
- `resource_surface_deadpool`
- `resource_surface_reqwest`
- `resource_surface_moka`

## Adoption strategy

- Start with crates whose defaults already create real operational questions.
- Prefer fixture-backed scenario evidence over ambitious automatic instrumentation.
- Make the first value mostly about **honest support truth**, not exact telemetry.
- Optimize for release-review and downstream support bundles rather than dashboards.

## What to keep separate

Do **not** let future revisions collapse these lanes:

- **P-0517 performance envelopes** — measured speed/throughput/latency claims,
- **P-0518 observability surfaces** — signal activation/stability/export surfaces,
- **P-0519 authority surfaces** — ambient power and policy-constrained execution,
- **P-0520 lifecycle surfaces** — start/stop/drain/teardown semantics,
- **P-0521 resource surfaces** — what can accumulate, where waiting occurs, and how the boundary behaves.

## Bottom line

The best `0.1` for **P-0521** is not a profiler and not a new queue primitive.
It is a compact support contract that lets another team answer, without source diving:

- where work waits,
- who owns that waiting room,
- what can shrink capacity,
- what callers experience at the boundary,
- and which signals or receipts actually support those claims.
