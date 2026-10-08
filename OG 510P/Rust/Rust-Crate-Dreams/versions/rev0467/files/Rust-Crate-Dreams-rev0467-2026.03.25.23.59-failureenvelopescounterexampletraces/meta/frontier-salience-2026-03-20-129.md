# Frontier salience snapshot — 2026-03-20 (129)

This pass did **not** promote another actor framework, another queue benchmark suite, or another “better channels” implementation.
It added **P-0529 Channel Surface Contract Kit** because the archive still lacked one receiver-facing layer above Rust’s rich but semantically divergent channel substrate.

## Main judgment

The sharper missing layer is not “how do channels work?” and not “which channel is fastest?”.
The sharper missing layer is a **channel support contract** that publishes:

- what capacity surface a channel actually has,
- what happens when it fills or receivers fall behind,
- what a successful send means,
- what receiver history and ordering exist,
- and what close/drop/clean shutdown do to buffered work.

## Why this moved now

Current Rust channel substrate already makes the problem precise:

1. Tokio `mpsc` explicitly distinguishes bounded backpressure from unbounded arbitrary buffering.
2. Tokio `broadcast` explicitly documents lagging slow receivers and skipped-count signals.
3. Tokio `watch` explicitly documents latest-only visibility with dropped intermediate updates.
4. Tokio `Sender::reserve` documents queue-order / cancel-safety implications, which shows how much send semantics can matter.
5. `futures::channel::mpsc` already frames itself in terms of FIFO + backpressure + clean shutdown.
6. `crossbeam` keeps zero-capacity rendezvous alive as a first-class surface.
7. `embassy-sync` shows that async embedded channels can have backpressure while also reordering by priority.
8. `commonware_utils::channel::ring` proves that a bounded channel may choose drop-oldest instead of backpressure.
9. `flume` and `async-channel` keep sync/async/blocking/time-bounded variations alive, which makes a shared receipt layer more valuable rather than less necessary.

## Why this beat nearby work

The archive already had adjacent lanes for:

- resource saturation,
- lifecycle/shutdown aftermath,
- observability delivery truth,
- persistence,
- and general capability contracts.

What it still lacked was one compact way to say:

- “this is a latest-state watcher, not an event-history channel,”
- “this bounded channel blocks on fullness rather than dropping,”
- “this broadcast surface can lag and skip,”
- “this rendezvous channel has no buffer at all,”
- and “this close path drains buffered messages instead of silently dropping them.”

That is a real crate contribution, not just another concurrency tutorial.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0514 Crate Upgrade Pack Kit**
3. **P-0520 Crate Lifecycle Surface Pack Kit**
4. **P-0529 Channel Surface Contract Kit**
5. **P-0523 Crate Test Surface Pack Kit**
6. **P-0518 Crate Observability Surface Pack Kit**
7. **P-0528 Cargo Feature Surface Contract Kit**
8. **P-0474 cargo-config-layer-receipt-kit**
9. **P-0124 schema-compatibility-workbench-kit**
10. **P-0017 Trust Lens**

## What changed in the archive

Added:
- `entries/2026-03-20-309.md`
- `meta/frontier-salience-2026-03-20-129.md`
- `meta/channel-surface-contract-product-plan-2026-03-20.md`
- `meta/channel-surface-contract-lane-boundaries-2026-03-20.md`
- `proposals/channel-surface-contract-kit.md`
- `fixtures/channel-surface-contract-kit/README.md`
- capacity-posture / overflow-policy / delivery-obligation / shutdown-drain schemas
- six scenario families covering Tokio bounded, Tokio broadcast, Tokio watch, zero-capacity rendezvous, priority reorder, and drop-oldest overwrite semantics

Updated:
- `README.md`
- `INDEX.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Freshness anchors

- Tokio `mpsc` docs — https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
- Tokio `Sender` docs — https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html
- Tokio `broadcast` docs — https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html
- Tokio `watch` docs — https://docs.rs/tokio/latest/tokio/sync/watch/index.html
- Tokio `watch::channel` docs — https://docs.rs/tokio/latest/tokio/sync/watch/fn.channel.html
- `futures::channel::mpsc` docs — https://docs.rs/futures/latest/futures/channel/mpsc/index.html
- `async-channel::Sender` docs — https://docs.rs/async-channel/latest/async_channel/struct.Sender.html
- `crossbeam::channel::bounded` docs — https://docs.rs/crossbeam/latest/crossbeam/channel/fn.bounded.html
- `embassy-sync::priority_channel::PriorityChannel` docs — https://docs.rs/embassy-sync/latest/embassy_sync/priority_channel/struct.PriorityChannel.html
- `commonware_utils::channel` docs — https://docs.rs/commonware-utils/latest/commonware_utils/channel/index.html
- `flume::Sender` docs — https://docs.rs/flume/latest/flume/struct.Sender.html
