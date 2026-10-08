# Frontier salience snapshot — 2026-03-21-133

This pass did **not** add another queue, pool, limiter, or cache crate.
It sharpened **P-0521 Crate Resource Surface Pack Kit** into a more implementation-ready topology-aware resource contract.

## Why this frontier moved up

The Rust ecosystem already has serious resource substrate, but the support lie has shifted.
It is no longer only “is there a limit?”
It is also “where does that limit live, and what multiplies it?”

Current docs make that concrete enough to standardize:

- `reqwest::Client` documents one reusable internal connection pool and says the client already uses an `Arc` internally, while `pool_max_idle_per_host` remains a per-host setting with a default of `usize::MAX`;
- `sqlx::Pool` and Deadpool both document cheap clone handles backed by shared inner state;
- Tokio `mpsc::Sender` documents clone as a cheap reference-count increment, meaning many senders can still share one bounded channel budget;
- Moka documents that cloning a shared cache only clones reference-counted pointers to the same internal data structures;
- tonic documents a concurrency limit **per connection**, so an honest local number can still scale with live connections;
- Tower documents that layer order can change the actual total number of in-flight requests.

That combination means the missing crate is not another implementation primitive.
It is a **resource-surface contract** that can publish **budget topology**, **sharing behavior**, **multiplication axes**, and **aggregate-bound posture**.

## Main conclusion

Promote **P-0521** upward again, but keep it narrow.
The next worthy move is not more performance prose and not a generic resource dashboard.

It should stay focused on:

1. freezing resource claims into a topology-aware support surface,
2. making clone-sharing versus budget multiplication explicit,
3. keeping per-host / per-connection / per-instance scope visible,
4. and downgrading process-wide claims when deployment topology makes them unknowable.

## Ranked near-term frontier from this pass

1. **P-0521 Crate Resource Surface Pack Kit** — strengthened because resource posture remains broadly painful while current docs finally make sharing-scope and multiplication truth concrete enough to standardize.
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because background work, barriers, and timeout aftermath remain adjacent to retained-resource incidents.
3. **P-0518 Crate Observability Surface Pack Kit** — still strong because pressure signals are only useful once the resource topology being observed is honest.
4. **P-0530 Request Execution Policy Contract Kit** — still strong because retry/hedge/admission behavior often multiplies resource usage through extra in-flight work.
5. **P-0529 Channel Surface Contract Kit** — still strong because delivery/overflow semantics remain the nearest substrate for many queue-like stories.

## Keep these boundaries sharp

- **P-0521** is the topology-aware support contract for retained resources and their boundaries.
- **P-0517** remains measured performance-envelope work.
- **P-0518** remains telemetry/delivery/completeness work.
- **P-0520** remains lifecycle/drain/teardown work.
- **P-0529** remains channel semantics.

Do not let “resource usage” flatten those lanes into one fake crate.
