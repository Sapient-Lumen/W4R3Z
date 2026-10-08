# Frontier salience snapshot — 2026-03-20 (130)

This pass did **not** promote another channel lane, another generalized resilience toolkit, or another middleware bundle.
It added **P-0530 Request Execution Policy Contract Kit** because the archive still lacked one receiver-facing layer above Rust’s retry / timeout / quota / hedge / load-shed substrate.

## Main judgment

The sharper missing layer is not “how do I add retries?” and not “which resilience crate should I install?”.
The sharper missing layer is a **request execution support contract** that publishes:

- what makes replay safe,
- what the real attempt budget is,
- how admission and overload are handled,
- and whether work is retried serially or hedged in parallel.

## Why this moved now

Current Rust substrate already makes the problem precise:

1. `reqwest` now treats retries as scoped policy with a retry budget and explicit classifier responsibility.
2. `reqwest-retry` frames retries in terms of transient-safe execution rather than generic replay.
3. Tower documents that layer order materially changes in-flight totals and therefore execution semantics.
4. Tower timeout, retry, and hedge are separate surfaces with different meanings.
5. `governor` shows that quotas can be global or keyed and can wait with jitter rather than only reject.
6. `tonic` explicitly distinguishes load shedding from the default buffering path.

## Why this beat nearby work

The archive already had adjacent lanes for:

- channel semantics,
- lifecycle/shutdown aftermath,
- observability delivery truth,
- resource saturation,
- and capability/support contracts.

What it still lacked was one compact way to say:

- “this request is only safe to replay because the method/classifier/idempotency key says so,”
- “this budget permits extra attempts but only within these deadline/timeout limits,”
- “this path queues before limiting, so the in-flight story differs from limit-first,”
- “this server sheds overload rather than buffering it,”
- and “this policy hedges with parallel clones instead of performing serial retries.”

That is a real crate contribution, not just another resilience article.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0514 Crate Upgrade Pack Kit**
3. **P-0520 Crate Lifecycle Surface Pack Kit**
4. **P-0529 Channel Surface Contract Kit**
5. **P-0530 Request Execution Policy Contract Kit**
6. **P-0523 Crate Test Surface Pack Kit**
7. **P-0518 Crate Observability Surface Pack Kit**
8. **P-0528 Cargo Feature Surface Contract Kit**
9. **P-0474 cargo-config-layer-receipt-kit**
10. **P-0124 schema-compatibility-workbench-kit**

## What changed in the archive

Added:
- `entries/2026-03-20-310.md`
- `meta/frontier-salience-2026-03-20-130.md`
- `meta/request-execution-policy-contract-product-plan-2026-03-20.md`
- `meta/request-execution-policy-contract-lane-boundaries-2026-03-20.md`
- `proposals/request-execution-policy-contract-kit.md`
- `fixtures/request-execution-policy-contract-kit/README.md`
- `idempotency-basis` / `attempt-budget` / `admission-path` / `attempt-topology` schemas
- scenario families for scoped `reqwest` retry budgets, Tower layer-order drift, hedged parallel attempts, tonic load-shed versus buffer behavior, and keyed quota waiting

Updated:
- `README.md`
- `INDEX.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Freshness anchors

- `reqwest` retry source — https://docs.rs/reqwest/latest/src/reqwest/retry.rs.html
- `reqwest-retry` docs — https://docs.rs/reqwest-retry/latest/reqwest_retry/struct.RetryTransientMiddleware.html
- Tower `ServiceBuilder` docs — https://docs.rs/tower/latest/tower/struct.ServiceBuilder.html
- Tower timeout docs — https://docs.rs/tower/latest/tower/timeout/
- Tower retry policy docs — https://docs.rs/tower/latest/tower/retry/trait.Policy.html
- Tower retry budget docs — https://docs.rs/tower/latest/tower/retry/budget/index.html
- Tower hedge docs — https://docs.rs/tower/latest/tower/hedge/index.html
- `governor` docs — https://docs.rs/governor/latest/governor/struct.RateLimiter.html
- `governor` guide — https://docs.rs/governor/latest/governor/_guide/index.html
- `tonic` server docs — https://docs.rs/tonic/latest/tonic/transport/server/struct.Server.html
