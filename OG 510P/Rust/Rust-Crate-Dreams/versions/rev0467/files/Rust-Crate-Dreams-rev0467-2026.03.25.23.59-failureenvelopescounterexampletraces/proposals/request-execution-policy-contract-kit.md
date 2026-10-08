---
id: P-0530
title: Request Execution Policy Contract Kit — idempotency basis, attempt budgets, admission paths, and hedge/retry topology
status: idea
domains: [async, networking, http, tower, reqwest, retries, deadlines, rate-limiting, resilience, dx, supportiveness]
last_reviewed: 2026-03-20
evidence:
  - https://docs.rs/reqwest/latest/src/reqwest/retry.rs.html
  - https://docs.rs/reqwest-retry/latest/reqwest_retry/struct.RetryTransientMiddleware.html
  - https://docs.rs/tower/latest/tower/struct.ServiceBuilder.html
  - https://docs.rs/tower/latest/tower/timeout/
  - https://docs.rs/tower/latest/tower/retry/trait.Policy.html
  - https://docs.rs/tower/latest/tower/retry/budget/index.html
  - https://docs.rs/tower/latest/tower/hedge/index.html
  - https://docs.rs/governor/latest/governor/struct.RateLimiter.html
  - https://docs.rs/governor/latest/governor/_guide/index.html
  - https://docs.rs/tonic/latest/tonic/transport/server/struct.Server.html
---

# Problem

Rust already has serious resilience substrate:

- `reqwest` now ships built-in retry configuration with budgets and scoped policies;
- `reqwest-retry` offers transient-safe middleware above `reqwest_middleware`;
- Tower composes retry, timeout, buffering, concurrency limits, load shedding, and hedging;
- `governor` provides keyed and unkeyed quota enforcement with wait-based APIs and jitter;
- `tonic` exposes server-side timeout, load shedding, and concurrency controls.

What the ecosystem still lacks is one compact, reviewable answer to a downstream question that appears in every client and service integration:

> “What actually happens when this request is slow, duplicated, retried, hedged, rate-limited, or rejected under load?”

Today, library docs often say some subset of:

- “supports retries”
- “has a timeout”
- “uses Tower middleware”
- “rate-limited”
- “safe to retry transient failures”
- “load shedding enabled”

Those are not enough.
Another team still cannot quickly tell:

1. **what makes a replay safe**;
2. **what the total attempt budget is**;
3. **how retries, deadlines, backoff, and jitter interact**;
4. **whether admission waits, buffers, rejects, or sheds**;
5. **whether attempts are serial or parallel**;
6. **and what request cloning or idempotency key assumptions are hiding underneath**.

The missing crate is therefore **not** another retry middleware, **not** another rate limiter, and **not** another Tower bundle.
It is a **Request Execution Policy Contract Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **Why is replay safe here at all?**
   - protocol-level safe method,
   - explicit idempotency key,
   - app-level idempotency contract,
   - request rebuild recipe,
   - or manual-review-only;
2. **What is the attempt budget?**
   - max serial attempts,
   - retry budget fraction,
   - per-attempt timeout,
   - overall deadline,
   - backoff family,
   - jitter posture;
3. **What admission path does one call traverse?**
   - direct call,
   - queue/buffer before limit,
   - limit before queue,
   - rate limit per key,
   - load shed instead of buffering,
   - or manual-review-required;
4. **What attempt topology exists?**
   - single attempt,
   - serial retry,
   - hedged parallel attempts,
   - or a mixed topology;
5. **What does failure to enter or complete actually mean?**
   - immediate reject,
   - wait until ready,
   - timeout-aborted attempt,
   - first-success-cancels-losers,
   - or budget exhausted.

That is more useful than “uses Tower + governor + reqwest”.

# What it provides

- `request-execution.toml` — maintainer-declared execution policy, scope, safety basis, and manual-review zones.
- `idempotency-basis.receipt.json` — how replay safety is justified, whether cloning/rebuilding is required, and where keys or protocol semantics enter.
- `attempt-budget.receipt.json` — serial-attempt ceiling, retry budget, timeout/deadline posture, backoff family, and jitter class.
- `admission-path.receipt.json` — queue/buffer/limit/load-shed order, rate-limit scope, and overload posture.
- `attempt-topology.report.json` — whether attempts are serial, parallel-hedged, or mixed; whether losers are canceled; and whether request cloning is required.
- `request-execution.summary.md` — short human-facing contract for docs and support notes.
- `request-execution-diff.report.json` — release-to-release change report for replay safety, budgets, admission, or topology.
- `cargo request-execution init`
- `cargo request-execution observe`
- `cargo request-execution check`
- `cargo request-execution doctor`
- `cargo request-execution summary`
- `cargo request-execution diff <old> <new>`
- `cargo request-execution pack`

# What the crate should provide other people

1. **Replay-safety truth** so “retryable” stops hiding whether safety came from HTTP semantics, an idempotency key, or an app-specific promise.
2. **Budget truth** so “3 retries” stops hiding retry-budget limits, per-attempt timeouts, overall deadlines, and jitter/backoff posture.
3. **Admission truth** so “rate-limited” or “concurrency-limited” stops hiding whether requests wait, queue, or get rejected.
4. **Topology truth** so teams know whether they are looking at serial retries or parallel hedges.
5. **Layer-order truth** so middleware composition stops sounding commutative when it materially changes in-flight count and timeout scope.
6. **Diffable release review** so execution-policy changes become reviewable like API changes.
7. **Portable vocabulary** for comparing `reqwest`, Tower, `governor`, `tonic`, and app-specific wrappers without pretending they are identical.

# Why now

This lane earns a slot now because the Rust ecosystem finally has enough substrate to make the missing layer precise.

## 1. `reqwest` now treats retries as scoped policy with a budget

The current `reqwest` retry source says the client can retry by sending additional copies, that policies include a retry budget by default, that the default policy only retries requests known to be safe, and that safe classification requires knowledge of destination behavior because requests should not be retried when side effects are unsafe.
That is already a contract-shaped surface, but it is not published as a receiver-facing receipt.

## 2. Tower makes layer order materially change execution semantics

Tower’s `ServiceBuilder` docs explicitly show that `buffer(100)` before `concurrency_limit(10)` allows up to 110 in-flight requests, while reversing the order keeps the total at 10.
That means “uses timeout + retry + limit” is not one stable statement unless order becomes part of the artifact.

## 3. Timeouts and retries are distinct, not interchangeable

Tower’s timeout middleware says a request is aborted when the response does not complete within the timeout.
That is not the same as overall deadline exhaustion, retry-budget exhaustion, or admission rejection.

## 4. Retry and hedge paths both require replay basis, but not the same topology

Tower retry policies can clone or mutate requests before replay, and Tower hedge explicitly pre-emptively retries outstanding requests based on latency percentiles.
A hedged path can therefore require request cloning and parallel outstanding attempts, which is a different support story from serial retry.

## 5. Admission posture is already split across waiting, buffering, and shedding

`governor` can wait asynchronously until quota is available and supports keyed quota state, while `tonic` explicitly says load shedding rejects when the service is not ready whereas the default is to buffer.
That means “rate limited” and “overload protected” are still too vague as crate claims.

# Prior art scan

## `reqwest` retry
Strong native substrate for scoped retry policy and retry budgets.
Insufficient because it does not publish a joined artifact covering safe classifier basis, admission path, and overall attempt topology for downstream review.

## `reqwest-retry`
Useful middleware for transient-safe HTTP retries.
Insufficient because it still centers one middleware implementation rather than a normalized cross-stack contract.

## Tower retry / timeout / hedge / limit
Excellent execution substrate and composition model.
Insufficient because real semantics depend on layer order, request cloneability, and external classification that downstream users still reconstruct by hand.

## `governor`
Serious quota-control substrate with keyed state and wait-based APIs.
Insufficient because it does not publish how those quota decisions join with retries, deadlines, buffers, and load shedding in one call path.

## Server/framework-specific knobs (`tonic`, app wrappers)
Useful server-side controls for timeout, concurrency, and load shedding.
Insufficient because they still do not yield one receiver-facing execution-policy receipt.

## Domain-specific idempotency middleware
Helpful in narrow ecosystems.
Insufficient because replay safety, admission, and topology still need shared vocabulary above any one middleware stack.

# Recommended `0.1` first-class review objects

## `idempotency-basis.receipt.json`

Should record at least:

- `replay_safety`: `safe_by_protocol` | `safe_by_idempotency_key` | `safe_by_app_contract` | `not_safe_without_manual_review` | `manual_review_required`
- `request_cloneability`: `cloneable` | `rebuildable` | `not_cloneable` | `manual_review_required`
- `classifier_scope`: `global` | `same_host` | `same_route` | `same_operation` | `manual_review_required`
- `idempotency_key_posture`: `none` | `caller_supplied` | `generated_stable_across_retries` | `manual_review_required`

## `attempt-budget.receipt.json`

Should record at least:

- `serial_attempts_max`
- `retry_budget_kind`: `none` | `fractional_extra_requests` | `fixed_attempt_cap` | `manual_review_required`
- `retry_budget_value`
- `per_attempt_timeout_ms`
- `overall_deadline_ms`
- `backoff_kind`: `none` | `constant` | `exponential` | `fibonacci` | `manual_review_required`
- `jitter_kind`: `none` | `full` | `bounded` | `manual_review_required`

## `admission-path.receipt.json`

Should record at least:

- `queueing_posture`: `direct` | `buffer_before_limit` | `limit_before_buffer` | `manual_review_required`
- `concurrency_limit`
- `rate_limit_scope`: `none` | `global` | `per_key` | `per_connection` | `manual_review_required`
- `overload_posture`: `wait` | `buffer` | `reject` | `shed` | `manual_review_required`
- `ready_failure_surface`: `not_ready_wait` | `immediate_error` | `resource_exhausted` | `manual_review_required`

## `attempt-topology.report.json`

Should record at least:

- `topology`: `single_attempt` | `serial_retry` | `hedged_parallel` | `retry_then_hedge` | `manual_review_required`
- `max_outstanding_attempts`
- `request_clone_required`
- `loser_cancellation`: `first_success_cancels_others` | `none` | `not_applicable` | `manual_review_required`
- `parallel_trigger_basis`: `none` | `latency_percentile` | `fixed_delay` | `manual_review_required`

# Commands worth shipping first

- `cargo request-execution init`
- `cargo request-execution observe`
- `cargo request-execution check`
- `cargo request-execution doctor`
- `cargo request-execution summary`
- `cargo request-execution diff <old> <new>`
- `cargo request-execution pack`

# Suggested `0.1` doctor warnings

- `retryable_without_replay_basis`
- `retry_budget_missing_scope`
- `timeout_claim_without_overall_deadline_posture`
- `layer_order_changes_admission_without_receipt`
- `load_shed_and_buffered_modes_share_same_contract`
- `hedged_parallel_attempts_missing_cloneability_basis`
- `rate_limit_scope_missing`
- `serial_retry_and_hedge_topology_collapsed`

# First proving-ground scenarios

1. **Scoped same-host retry budget for safe transient `reqwest` replay**
2. **Tower buffer-before-limit versus limit-before-buffer ordering**
3. **Hedged parallel attempts that require request cloning**
4. **Tonic load shedding versus default buffering**
5. **Governor keyed quota with wait-and-jitter posture**

# Scope boundaries

## This proposal is not:

- another retry middleware crate;
- another Tower layer bundle;
- another rate limiter;
- another idempotency-key implementation;
- another circuit-breaker / bulkhead / cache suite;
- or a proof that one middleware order is universally correct.

It is a support contract layer.

# Adoption plan

1. Start with fixture-backed contracts for `reqwest`, Tower, `governor`, and `tonic` combinations.
2. Ship a small Markdown summary format maintainers can embed in docs.
3. Offer import adapters for native `reqwest` retry config, Tower layer stacks, and common rate-limit/load-shed choices.
4. Publish diff reports so downstream teams can review semantic changes across releases.
5. Let higher-level SDKs, API clients, and service frameworks import the contract rather than rewrite resilience prose from scratch.

# Maintenance plan

- Keep the core vocabulary intentionally small.
- Prefer explicit `manual_review_required` over pretending arbitrary middleware stacks can always be normalized.
- Version the JSON schemas conservatively.
- Keep HTTP-specific sugar separate from generic request-execution artifacts.

# Milestones

## `0.1`

- schemas for idempotency basis, attempt budgets, admission path, and attempt topology
- fixture-backed scenarios for `reqwest`, Tower, `governor`, and `tonic`
- summary and diff commands
- basic doctor rules

## `0.2`

- richer import adapters for common Tower and `reqwest` middleware stacks
- optional release-gating checks
- optional rendered support page snippets

## `0.3+`

- organization policy profiles
- richer workload-specific topology witnesses
- optional integration with upgrade/support/pathfinder lanes

# Open questions

- How much generic vocabulary should be shared across HTTP, RPC, and job-execution surfaces before semantics become misleading?
- Which admission-path facts can be safely inferred from middleware type structure, and which require maintainer declaration?
- Should `0.1` treat circuit breakers and bulkheads as adjacent import lanes or leave them fully out of scope?
- How should per-host/per-route/per-operation scoping be rendered in summaries without becoming unreadable?

# Sources

- `reqwest` retry source — scoped policy, safe classification, retry budgets
- `reqwest-retry` docs — transient-safe retry middleware posture
- Tower `ServiceBuilder`, retry, timeout, hedge, and retry-budget docs
- `governor` docs and guide — keyed/direct quota and wait/jitter posture
- `tonic` server docs — load shedding, buffering, timeout, and concurrency knobs
