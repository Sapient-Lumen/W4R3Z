# Frontier salience scan — 2026-03-17 (crate resource surfaces promoted as the capacity / saturation-truth lane)

This pass added a new top-level proposal: **P-0521 Crate Resource Surface Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a thirteenth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), **P-0516** (configuration/setup scenarios), **P-0517** (performance envelopes), **P-0518** (observability surfaces), **P-0519** (authority surfaces), and **P-0520** (lifecycle surfaces).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another queue crate,
- another cache crate,
- another rate limiter,
- another metrics exporter,
- or another “capacity tuning” blog-in-a-box.

It is the boring crate that can hand other people:

- one **resource pack**,
- one **resource-surface receipt**,
- one **capacity-profile manifest**,
- one **saturation-behavior report**,
- one **reclaim-obligation report**,
- one **resource-budget report**,
- one **resource-check report**,
- and one **resource diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0521 Crate Resource Surface Pack Kit**
9. **P-0520 Crate Lifecycle Surface Pack Kit**
10. **P-0518 Crate Observability Surface Pack Kit**
11. **P-0519 Crate Authority Surface Pack Kit**
12. **P-0512 Crate Guidance Pack Kit**
13. **P-0513 Crate Runtime Handoff Pack Kit**
14. **P-0515 Crate Off-Ramp Pack Kit**
15. **P-0510 Crate Capability Contract & Interop Profile Kit**
16. **P-0511 Crate Interop Profile Pack Kit**
17. **P-0429 rustc_public Analysis Workbench Kit**

## Why P-0521 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, which makes resource truth a plausible crate support surface rather than a tuning afterthought.
- The 2025 survey says **docs and code** remain the main learning surfaces and that **resource usage** remains a recurring productivity problem.
- Tokio’s channel docs already distinguish **bounded** backpressured queues from **unbounded** queues that can buffer arbitrarily.
- Tokio’s runtime and `spawn_blocking` docs already expose worker counts, stack sizes, blocking-thread limits, and queueing once a limit is reached.
- Real ecosystem crates already expose resource-shaping knobs like connection-pool sizes, cache capacities, quotas, and concurrency limits.
- Runtime metrics stacks already observe tasks and queue depths, which means the missing value is increasingly the support artifact, not raw measurability.

That means the lane is both:

- **timely** — because the substrate is real enough to support a contract layer now,
- and **distinct** — because the missing value is a crate-authored resource surface above primitives and below dashboards or framework-specific docs.

## What changed in the archive

Added:
- `proposals/crate-resource-surface-pack-kit.md`
- `meta/crate-resource-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-36.md`
- `fixtures/crate-resource-surface-pack-kit/`
- `entries/2026-03-17-207.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- setup/configuration scenarios,
- performance envelopes,
- observability,
- authority / ambient powers,
- lifecycle / shutdown truth,
- generic queues/caches/limiters,
- and receiver-facing resource contracts

into one fake “better backpressure and tuning” story.

## Sources

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
- https://docs.rs/tokio/latest/tokio/runtime/struct.RuntimeMetrics.html
- https://docs.rs/tokio-metrics/latest/tokio_metrics/
