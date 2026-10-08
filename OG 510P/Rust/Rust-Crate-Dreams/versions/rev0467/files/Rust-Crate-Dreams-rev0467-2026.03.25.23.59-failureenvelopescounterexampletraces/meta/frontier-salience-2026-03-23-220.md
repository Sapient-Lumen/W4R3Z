# Frontier salience refresh — 2026-03-23 (220)

## Current top frontier

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## Why this refresh mattered

The concurrency lane remains top-five because the ecosystem still publishes crucial async/message-passing semantics in fragmented crate-specific prose, while current Rust challenges still describe async complexity as a live pain. The sharper remaining gap is now not another primitive or wrapper, but a portable support-contract layer for **what delivery order a receiver is actually promised** and **whether missed or collapsed units are visible, countable, or silent**.

## Sharper frontier judgment

**P-0538** is stronger after this pass because it now covers fifteen distinct receiver-facing lanes without collapsing them:

1. reentrancy scope,
2. progress/fairness class,
3. wait-cancellation behavior,
4. execution-context legality,
5. recovery posture,
6. mobility/affinity,
7. driver-liveness,
8. delivery memory,
9. backlog pressure / lag / loss posture,
10. delivery audience,
11. consumption-claim semantics,
12. delivery acceptance,
13. observation-evidence ceiling,
14. delivery order,
15. gap visibility.

That is increasingly close to an epic crate contribution because adopters routinely need these truths together, but today they still have to reconstruct them by reading several incompatible docs vocabularies and then guessing whether they are looking at a queue, a snapshot stream, a coalesced wake source, or a surface with counted gaps.

## Why this lane stayed below the top four

Compile iteration, pathfinder, dependency transition, and crate-knowledge still rank above it because those lanes touch broader day-to-day workflow pain and still look more immediately adoptable across the ecosystem.

But the concurrency lane is now more implementation-ready than it was one pass ago because it has a clearer answer to:

- whether sequence order is defined per receiver, per queue, or not meaningfully exported at all,
- whether missed units are impossible, counted, cursor-rebased, or silent,
- whether “lag” means quantified skips versus merely learning about the latest state,
- and when cross-surface selection destroys any simple global order story.

## What a worthy crate should provide now

A worthy **P-0538** crate should now provide:

- one `delivery-order.report.json`,
- one `gap-visibility.report.json`,
- one bundle manifest that keeps those truths separate from memory / pressure / audience / claim / acceptance / evidence / fairness / cancellation / recovery / context / locality / liveness,
- and doctor checks that reject fake equivalence between FIFO queues, per-receiver broadcast order, latest-snapshot watches, coalesced wake sources, and random selection among simultaneously ready operations.
