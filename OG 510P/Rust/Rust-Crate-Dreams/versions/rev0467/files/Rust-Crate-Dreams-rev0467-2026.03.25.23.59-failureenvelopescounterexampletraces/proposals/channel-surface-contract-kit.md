---
id: P-0529
title: Channel Surface Contract Kit — capacity posture, overflow policy, delivery obligation, and shutdown/drain witnesses
status: idea
domains: [async, concurrency, channels, backpressure, queues, shutdown, dx, supportiveness]
last_reviewed: 2026-03-20
evidence:
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html
  - https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html
  - https://docs.rs/tokio/latest/tokio/sync/watch/index.html
  - https://docs.rs/tokio/latest/tokio/sync/watch/fn.channel.html
  - https://docs.rs/futures/latest/futures/channel/mpsc/index.html
  - https://docs.rs/async-channel/latest/async_channel/struct.Sender.html
  - https://docs.rs/crossbeam/latest/crossbeam/channel/fn.bounded.html
  - https://docs.rs/embassy-sync/latest/embassy_sync/priority_channel/struct.PriorityChannel.html
  - https://docs.rs/commonware-utils/latest/commonware_utils/channel/index.html
  - https://docs.rs/flume/latest/flume/struct.Sender.html
---

# Problem

Rust already has many good channel crates and synchronization primitives.
What it still lacks is one boring, reviewable answer to a downstream question that appears in almost every real system:

> “What does this channel actually promise when senders outrun receivers, multiple consumers subscribe, shutdown starts, or a task gives up waiting?”

Today’s substrate is rich enough that this gap is now precise rather than speculative.

Current channel families differ along several receiver-facing axes:

- Tokio `mpsc` bounded channels apply backpressure, while Tokio `mpsc` unbounded channels buffer arbitrarily.
- Tokio `broadcast` has explicit slow-receiver / lagging behavior.
- Tokio `watch` intentionally keeps only the most recent value and drops intermediate updates.
- `crossbeam` supports zero-capacity rendezvous channels.
- `embassy-sync` priority channels can reorder delivery based on priority.
- `commonware_utils::channel::ring` drops the oldest item instead of applying backpressure.
- `flume`, `async-channel`, and `futures::channel::mpsc` expose still-different send/timeout/blocking/close surfaces.

Those are not merely API trivia.
They are support promises another team has to live with.

The missing crate is therefore **not** another channel implementation.
It is a **Channel Surface Contract Kit**.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What kind of capacity surface does this channel expose?**
   - bounded,
   - unbounded,
   - rendezvous / zero-capacity,
   - latest-value-only,
   - overwrite ring,
   - or priority-bounded;
2. **What happens when producers outrun consumers?**
   - wait / backpressure,
   - immediate rejection,
   - drop oldest,
   - drop intermediate values,
   - lag error with skipped-count signal,
   - or manual-review-required;
3. **What does a successful send actually mean?**
   - value enqueued,
   - value received by one consumer,
   - value cloned for all current subscribers,
   - value visible as the latest state,
   - or some narrower claim;
4. **What history and ordering surface does the receiver actually get?**
   - FIFO,
   - per-receiver future-only,
   - latest-only,
   - or priority-reordered;
5. **What does close / drop / clean shutdown really do to buffered work?**

That is more useful than “uses channel X.”

# What it provides

- `channel-surface.toml` — maintainer-declared channel support contract, named lanes, and manual-review zones.
- `capacity-posture.receipt.json` — bounded/unbounded/rendezvous/latest-only/overwrite/priority surface with capacity and completion-point notes.
- `overflow-policy.receipt.json` — wait/reject/drop-oldest/drop-intermediate/lag-error policy and what signal a sender or receiver sees.
- `delivery-obligation.report.json` — whether send completion means enqueued, delivered to one, cloned to all current subscribers, or merely visible as latest state.
- `shutdown-drain.receipt.json` — close/drop behavior, clean-shutdown recipe, buffered-value fate, and sender-side closed/interest signals.
- `channel-surface.summary.md` — compact human-facing summary for docs, support pages, and crate selection notes.
- `channel-surface-diff.report.json` — release-to-release changes in capacity, overflow, delivery, ordering, or shutdown semantics.
- `cargo channel-surface init`
- `cargo channel-surface observe`
- `cargo channel-surface check`
- `cargo channel-surface doctor`
- `cargo channel-surface summary`
- `cargo channel-surface diff <old> <new>`
- `cargo channel-surface pack`

# What the crate should provide other people

1. **A compact choice artifact** above crate docs and folklore.
2. **Honest backpressure / overflow truth** so “bounded” stops sounding like a complete answer.
3. **Delivery-obligation truth** so teams know whether “send succeeded” means enqueued, observed, or merely latest-state replacement.
4. **History-surface truth** so consumers know whether they will see every message, only future messages, or only the latest value.
5. **Shutdown/drain truth** so channel close semantics can be planned instead of guessed.
6. **Diffs across releases** so support-sensitive semantic changes become visible.
7. **Portable review vocabulary** that can compare Tokio, futures, async-channel, crossbeam, Embassy, and other ecosystems without pretending they are identical.

# Why now

This lane earns a slot now because Rust already has enough channel substrate to make the gap concrete:

- Tokio explicitly distinguishes bounded backpressure from unbounded arbitrary buffering.
- Tokio `broadcast` documents lagging slow receivers.
- Tokio `watch` documents latest-only semantics and dropped intermediates.
- Tokio `Sender::reserve` documents queue-order and cancel-safety implications.
- `futures::channel::mpsc` already talks in terms of FIFO + backpressure + clean shutdown.
- `async-channel` exposes bounded/unbounded plus blocking and async send surfaces.
- `crossbeam` keeps synchronous rendezvous / zero-capacity channels alive as a first-class option.
- `embassy-sync` exposes async embedded channels with backpressure and even priority reordering.
- `commonware_utils` already demonstrates a drop-oldest ring channel, proving overflow policy is not one-size-fits-all.

That means the missing layer is not more raw primitives.
It is the shared contract above them.

# Prior art scan

## Tokio
Strong substrate for async channels, permits, clean shutdown, broadcast lagging, watch latest-only semantics, and sender-closed signals.
What it does **not** provide is a normalized support contract another library can publish to say which semantics it relies on or exports.

## futures::channel::mpsc
Good FIFO + backpressure + clean-shutdown substrate.
Still not a cross-crate receipt layer.

## async-channel / flume / crossbeam
Strong implementations with different sync/async tradeoffs, blocking APIs, timeouts, MPMC shapes, and capacity semantics.
Still no shared receiver-facing contract vocabulary.

## Embassy
Important proof that no-std / embedded async channels need the same honesty around capacity, enqueue vs receive, and ordering.
Still not a cross-ecosystem receipt layer.

## Domain-specific wrappers
Many crates wrap channels for events, rings, workers, and observables.
Those wrappers often add even more semantic policy, which makes a portable contract layer more valuable, not less.

# Recommended `0.1` first-class review objects

## `capacity-posture.receipt.json`

Should record at least:

- `topology`: `mpsc` | `mpmc` | `broadcast` | `watch` | `priority_channel` | `rendezvous`
- `capacity_kind`: `bounded` | `unbounded` | `zero_capacity` | `latest_only` | `overwrite_ring`
- `capacity_bound`
- `send_completion_point`: `enqueued` | `handed_off` | `latest_state_visible`
- `ordering_class`: `fifo` | `per_receiver_fifo` | `priority_reordered` | `manual_review_required`

## `overflow-policy.receipt.json`

Should record at least:

- `when_full`: `wait_backpressure` | `reject_immediately` | `drop_oldest` | `drop_newest` | `retain_latest_only` | `lag_error`
- `sender_signal`
- `receiver_signal`
- `skipped_count_available`
- `manual_review_required`

## `delivery-obligation.report.json`

Should record at least:

- `visibility_scope`: `one_consumer` | `one_of_many_consumers` | `all_current_subscribers` | `latest_value_only`
- `subscription_history`: `full_buffered_history` | `future_only` | `latest_only`
- `message_clone_model`: `move_once` | `clone_per_receiver` | `shared_latest_state`
- `delivery_claim_strength`: `enqueued_only` | `enqueued_and_receivable` | `visible_as_latest` | `manual_review_required`

## `shutdown-drain.receipt.json`

Should record at least:

- `receiver_close_supported`
- `clean_shutdown_recipe`
- `buffered_messages_after_receiver_drop`: `dropped` | `drained_to_completion` | `manual_review_required`
- `sender_closed_signal`
- `reserved_capacity_after_close`: `may_still_send` | `rejected` | `not_applicable`

# Commands worth shipping first

- `cargo channel-surface init`
- `cargo channel-surface observe`
- `cargo channel-surface check`
- `cargo channel-surface doctor`
- `cargo channel-surface summary`
- `cargo channel-surface diff <old> <new>`
- `cargo channel-surface pack`

# Suggested `0.1` doctor warnings

- `bounded_without_overflow_receipt`
- `send_success_meaning_not_explicit`
- `latest_only_channel_documented_as_event_stream`
- `broadcast_lag_policy_missing`
- `shutdown_recipe_missing`
- `queue_order_or_priority_not_explicit`
- `clean_shutdown_supported_but_not_witnessed`

# First proving-ground scenarios

1. **Tokio bounded mpsc with backpressure and close-then-drain**
2. **Tokio broadcast with lagging receivers and skipped-count signals**
3. **Tokio watch for latest-state propagation rather than event history**
4. **Crossbeam zero-capacity rendezvous**
5. **Embassy priority channel with priority-based reorder**
6. **Drop-oldest ring channel that refuses to claim backpressure**

# Scope boundaries

## This proposal is not:

- another channel implementation crate;
- another actor framework;
- another stream-processing framework;
- another queue metrics dashboard;
- another generalized resource-saturation pack;
- or a proof that one channel type should replace all others.

It is a support contract layer.

# Adoption plan

1. Start with fixture-backed example contracts for well-known channel families.
2. Ship a tiny summary format maintainers can embed in crate docs.
3. Offer adapters for Tokio / futures / crossbeam / async-channel / Embassy imports.
4. Publish diff reports so downstream users can review semantic changes across releases.
5. Let adjacent crates (worker pools, event buses, watchers, queue wrappers) import the contract rather than rewrite prose from scratch.

# Maintenance plan

- Keep the core vocabulary intentionally small.
- Prefer explicit `manual_review_required` over pretending ambiguous semantics are solved.
- Version the JSON schemas conservatively.
- Track ecosystem evolution, but treat new channel variants as additive taxonomy work rather than breaking rewrites.

# Why this could matter

This is the crate that would let maintainers say:

- “This channel backpressures rather than dropping.”
- “This watcher keeps only the latest state; it is not a replayable event stream.”
- “This broadcast surface can lag and skip, and here is how that is signaled.”
- “This rendezvous channel has no buffer; send and receive must pair.”
- “This close path drains buffered work to completion, and here is the actual recipe.”

That is a real missing support layer in Rust today.
