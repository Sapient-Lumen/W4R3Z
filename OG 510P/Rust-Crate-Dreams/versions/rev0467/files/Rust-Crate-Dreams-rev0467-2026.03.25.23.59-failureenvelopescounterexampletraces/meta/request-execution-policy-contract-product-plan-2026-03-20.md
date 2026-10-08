# Request Execution Policy Contract Kit — product plan (2026-03-20)

This note sharpens **P-0530 Request Execution Policy Contract Kit** into an implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0530** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace Tower, `reqwest`, `governor`, or server-framework execution controls.
It should provide one boring, reviewable contract layer above existing retry / timeout / quota / hedge / load-shed semantics.

`0.1` should make four things first-class:

1. **idempotency basis** — why replay is safe at all, and whether cloning or rebuilding is required;
2. **attempt budgets** — serial-attempt limits, retry budgets, timeouts, deadlines, backoff, and jitter;
3. **admission path** — where queueing, concurrency limits, keyed quotas, buffering, and shedding happen;
4. **attempt topology** — whether work is single-shot, serially retried, or hedged in parallel.

## What `0.1` should provide other people

- one compact `idempotency-basis.receipt.json`
- one compact `attempt-budget.receipt.json`
- one compact `admission-path.receipt.json`
- one compact `attempt-topology.report.json`
- one rendered `request-execution.summary.md`
- a diff command for release reviewers

## Commands worth shipping first

- `cargo request-execution init`
- `cargo request-execution observe`
- `cargo request-execution check`
- `cargo request-execution doctor`
- `cargo request-execution summary`
- `cargo request-execution diff <old> <new>`
- `cargo request-execution pack`

## What to import, not reinvent

- native `reqwest` retry policy and scope information where available
- `reqwest-retry` policy/middleware declarations
- Tower layer order and retry/timeout/hedge structure
- `governor` quota/state scope choices
- `tonic` server knobs for load shed, timeout, and concurrency
- optional app-authored idempotency-key policy notes

## Suggested `0.1` doctor warnings

- `retryable_without_replay_basis`
- `retry_budget_missing_scope`
- `per_attempt_timeout_without_overall_budget_posture`
- `queue_and_limit_order_not_explicit`
- `hedge_requires_cloneability_but_basis_missing`
- `load_shed_and_buffered_modes_share_same_receipt`
- `rate_limit_scope_missing`
- `serial_and_parallel_attempts_collapsed`

## First proving-ground scenarios

1. **Scoped same-host retry budget for safe transient `reqwest` replay**
2. **Tower buffer-before-limit versus limit-before-buffer ordering**
3. **Hedged parallel attempts that require request cloning**
4. **Tonic load shedding versus default buffering**
5. **Governor keyed quota with wait-and-jitter posture**

## What to leave for later

- full middleware-stack symbolic execution
- hosted dashboards
- automatic policy synthesis from arbitrary app code
- organization policy engines
- cross-language request-policy normalization beyond the shared receipt vocabulary
