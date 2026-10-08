# Concurrency Contract Kit delivery order / gap visibility plan — 2026-03-23

This note exists to make **P-0538 Concurrency Contract Kit** more implementation-ready.

The archive already decided that the missing value is a **receiver-facing support-contract layer** for concurrency semantics scattered across docs and folklore.
This pass sharpens what a plausible next slice should actually ship above the existing memory / pressure / audience / claim / acceptance work.

## Main product judgment

The next lovable slice should **not** try to infer total causality across arbitrary programs.

It should do two smaller things well:

1. say what kind of observable sequence, if any, a receiver is actually promised;
2. say whether missed or collapsed units are visible, counted, cursor-rebased, or silent.

## New reports that now look worth shipping

### 1. `delivery-order.report.json`
Purpose:
- answer what order guarantee a receiver-facing surface actually exports.

Minimum fields:
- `surface`
- `order_class`
- `order_scope`
- `sequence_unit`
- `late_joiner_window`
- `reordering_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `single_consumer_fifo`
- `per_receiver_fifo_broadcast`
- `latest_snapshot_only`
- `coalesced_wake_not_sequence`
- `ready_operation_choice_random`
- `ready_operation_choice_biased`
- `manual_review_required`

### 2. `gap-visibility.report.json`
Purpose:
- answer whether missing or collapsed units are visible to the receiver and how much can be known.

Minimum fields:
- `surface`
- `gap_visibility_class`
- `gap_trigger`
- `gap_signal`
- `gap_cardinality_visibility`
- `cursor_or_state_after_gap`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `no_gap_signal_expected_under_fifo_receipt`
- `skip_count_exposed`
- `silent_intermediate_drop`
- `coalesced_without_count`
- `manual_review_required`

## Why these reports now belong here

Current docs now make these distinctions concrete enough to standardize:

- Tokio bounded `mpsc` explicitly exports in-order single-consumer delivery, but not a skip-count signal;
- Tokio `broadcast` explicitly exports in-order per-receiver delivery plus `Lagged(u64)` skipped-message counts and cursor rebasing to the oldest retained value;
- Tokio `watch` explicitly exports latest-state visibility while dropping intermediate values;
- Tokio `Notify` explicitly exports a single stored permit and coalesces repeated `notify_one` calls;
- Crossbeam `Select` explicitly exports random ready-operation choice unless biased mode is requested.

That is enough substrate for a first portable support-contract layer around order and gaps.

## MVP shape

The first useful cut should:

1. inspect documented order class,
2. inspect documented gap-visibility posture,
3. render compact receipts,
4. join them into the portable concurrency-support bundle,
5. add doctor checks that reject fake equivalence between FIFO queues, latest-value watches, coalesced wake sources, and random selection combinators.

## First doctor rules worth shipping

- `latest_snapshot_is_not_fifo_history`
- `coalesced_permit_is_not_counted_sequence`
- `lagged_count_is_stronger_than_generic_message_loss`
- `single_consumer_fifo_is_not_per_receiver_broadcast_fifo`
- `random_ready_selection_is_not_global_message_order`

## Why this belongs in P-0538 instead of a new lane

This is still concurrency-contract work because the missing value is a **receiver-facing support claim** above existing primitives and combinators.
The lane is still not trying to replace Tokio, Crossbeam, Flume, or async-channel.
It is trying to export honest receipts about what those surfaces already promise.

## What a real crate should provide other people

A real crate should let another engineer answer:

- Is there a meaningful sequence here at all?
- Is the order FIFO globally, FIFO per receiver, or only latest-state visibility?
- Can a slow receiver tell how many units were skipped?
- Does a collapse/loss event move a cursor to a known retained point, or just silently hide history?
- Does a selector/combinator preserve underlying channel order, or introduce random choice across ready operations?

## Suggested artifact inventory

- `delivery-order.report.json`
- `gap-visibility.report.json`
- `concurrency-support-bundle.manifest.json`
- doctor output referencing fake-equivalence failures
- release diffs when order/gap posture changes

## Fixture priorities

1. Tokio `mpsc`
2. Tokio `broadcast`
3. Tokio `watch`
4. Tokio `Notify`
5. Crossbeam `Select`
6. portable bundle join fixture

## Non-goals

This slice should **not** try to prove end-to-end causal order across an application.
It should **not** guess order from benchmarks.
It should **not** collapse fairness, memory, audience, or acceptance into order.
And it should **not** pretend every loss event yields a count.
