# Frontier salience refresh — 2026-03-23 (219)

## Current top frontier

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## Why this refresh mattered

The concurrency lane remains top-five because the ecosystem still publishes crucial async/message-passing semantics in fragmented crate-specific prose, while current Rust challenges still describe async complexity as a live pain. The sharper remaining gap is now not another primitive or wrapper, but a portable support-contract layer for **what producer-visible success actually certifies** and **what evidence of downstream observation exists later, if any**.

## Sharper frontier judgment

**P-0538** is stronger after this pass because it now covers thirteen distinct receiver-facing lanes without collapsing them:

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
13. observation-evidence ceiling.

That is increasingly close to an epic crate contribution because adopters routinely need these truths together, but today they still have to reconstruct them by reading several incompatible docs vocabularies and then guessing what `Ok` from `send` was actually worth.

## Why this lane stayed below the top four

Compile iteration, pathfinder, dependency transition, and crate-knowledge still rank above it because those lanes touch broader day-to-day workflow pain and still look more immediately adoptable across the ecosystem.

But the concurrency lane is now more implementation-ready than it was one pass ago because it has a clearer answer to:

- what producer-side success actually means,
- whether success only proves an endpoint was live or a unit was admitted,
- whether any later signal is proof, only a hint, or merely a closure notification,
- and when application-level acknowledgment is still required.

## What a worthy crate should provide now

A worthy **P-0538** crate should now provide:

- one `delivery-acceptance.report.json`,
- one `observation-evidence.report.json`,
- one bundle manifest that keeps those truths separate from audience / claim / memory / pressure / fairness / cancellation / recovery / context / locality / liveness,
- and doctor checks that reject fake equivalence between `Ok` from `send`, receiver-count hints, close notifications, and actual proof that a value was received or processed.
