# Concurrency Contract Kit delivery order / gap visibility boundaries — 2026-03-23

This note exists to keep **P-0538 Concurrency Contract Kit** from collapsing too many message-passing questions into one fake “channel ordering” story.

## Delivery order is not delivery memory

A surface may retain:

- one coalesced permit,
- one latest value,
- a bounded queue,
- a bounded retained broadcast history,
- or no buffered memory at all.

That does **not** yet say whether receivers get a meaningful ordered sequence.

## Delivery order is not audience or claim semantics

A surface may reach:

- one waiter,
- one competing consumer,
- all active receivers,
- or each receiver’s own latest-state cursor.

That does **not** yet say what ordered history each observer gets.

## Gap visibility is not backlog pressure

A surface may be bounded, unbounded, backpressured, overwrite-prone, or coalescing.
That still leaves open whether missed units are:

- impossible under the documented route,
- counted,
- cursor-rebased,
- silently collapsed,
- or only manually reviewable.

## Gap visibility is not acceptance or observation evidence

Producer-visible success and later proof-of-observation are different seams.
This seam is only about what a receiver can know about the sequence it saw or failed to see.

## Selection order is not underlying channel FIFO

A channel may preserve FIFO while a selector/combinator picks among multiple ready operations randomly or by bias.
Do not flatten cross-surface choice order into the same claim as per-channel message order.

## What belongs in this seam

Belongs:

- FIFO versus per-receiver FIFO versus latest-snapshot-only posture
- coalesced wake-without-sequence posture
- counted skip signals
- cursor rebasing after lag/loss
- silent intermediate-drop posture
- selection-level random versus biased ready-operation choice

Does **not** belong here:

- reentrancy
- fairness/progress writ large
- cancellation class
- execution-context legality
- recovery posture
- audience / claim semantics
- producer-visible acceptance meaning
- observation evidence

## Anti-patterns this note should stop

Reject wording like:

- “this channel is ordered” when it only exports latest state,
- “messages may be lost” when docs actually expose exact skipped counts,
- “lagged” when the real behavior is silent overwrite or silent coalescing,
- “FIFO” when the only documented order is per receiver,
- “selection preserved order” when a select combinator explicitly chooses randomly among ready operations.
