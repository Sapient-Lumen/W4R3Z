# Frontier salience refresh — 2026-03-23 (221)

## Current top frontier

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## Why this refresh mattered

The concurrency lane remains top-five because the ecosystem still publishes crucial async/message-passing lifecycle semantics in fragmented crate-specific prose, while current Rust challenges still describe async complexity as a live pain. The sharper remaining gap is now not another primitive or shutdown helper, but a portable support-contract layer for **what closure actually finalizes** and **what remains observable after close/disconnect**.

## Sharper frontier judgment

**P-0538** is stronger after this pass because it now covers seventeen distinct receiver-facing lanes without collapsing them:

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
15. gap visibility,
16. closure finality,
17. post-close availability.

That is increasingly close to an epic crate contribution because adopters routinely need these truths together, but today they still have to reconstruct them by reading several incompatible docs vocabularies and then guessing whether “closed” means empty, drained, reopenable, or still carrying a retained tail.

## Why this lane stayed below the top four

Compile iteration, pathfinder, dependency transition, and crate-knowledge still rank above it because those lanes touch broader day-to-day workflow pain and still look more immediately adoptable across the ecosystem.

But the concurrency lane is now more implementation-ready than it was one pass ago because it has a clearer answer to:

- whether closure is immediate terminal or only terminal after residual state is drained,
- whether the surface can be reopened after a closed interval,
- whether a last snapshot or already-sent value remains observable after close,
- and when “closed” says only “no future sends” rather than “nothing more can be read.”

## What a worthy crate should provide now

A worthy **P-0538** crate should now provide:

- one `closure-finality.report.json`,
- one `post-close-availability.report.json`,
- one bundle manifest that keeps those truths separate from memory / pressure / audience / claim / acceptance / evidence / order / gaps / fairness / cancellation / recovery / context / locality / liveness,
- and doctor checks that reject fake equivalence between immediate terminal closure, drain-then-terminal closure, reopenable closed states, retained broadcast tails, latest-state access after close, and in-flight value races around close.
