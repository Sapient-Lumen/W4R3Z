# Frontier salience refresh — 2026-03-23 (217)

## Current top frontier

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## Why this refresh mattered

The concurrency lane remains top-five because the ecosystem still publishes crucial semantics in fragmented crate-specific prose, while current Rust challenges still describe async complexity as a live pain. The sharper remaining gap is now not another primitive or wrapper, but a portable support-contract layer for **what wake/value/message state is remembered** and **what pressure/loss mode appears when producers outrun consumers**.

## Sharper frontier judgment

**P-0538** is stronger after this pass because it now covers nine distinct receiver-facing lanes without collapsing them:

1. reentrancy scope,
2. progress/fairness class,
3. wait-cancellation behavior,
4. execution-context legality,
5. recovery posture,
6. mobility/affinity,
7. driver-liveness,
8. delivery memory,
9. backlog pressure / lag / loss posture.

That is increasingly close to an epic crate contribution because adopters routinely need these truths together, but today they have to reconstruct them by reading several incompatible docs vocabularies.

## Why this lane stayed below the top four

Compile iteration, pathfinder, dependency transition, and crate-knowledge still rank above it because those lanes touch broader day-to-day workflow pain and still look more immediately adoptable across the ecosystem.

But the concurrency lane is now more implementation-ready than it was one pass ago because it has a clearer answer to:

- what gets remembered,
- what gets overwritten,
- what blocks,
- what can grow without bound,
- and what only rendezvous-delivers when both sides are present.

## What a worthy crate should provide now

A worthy **P-0538** crate should now provide:

- one `delivery-memory.report.json`,
- one `backlog-pressure.report.json`,
- one bundle manifest that keeps those truths separate from fairness / cancellation / recovery / context / locality / liveness,
- and doctor checks that reject fake “channel-like” equivalence between coalesced signals, latest-value watches, bounded queues, per-receiver broadcast history, and rendezvous channels.
