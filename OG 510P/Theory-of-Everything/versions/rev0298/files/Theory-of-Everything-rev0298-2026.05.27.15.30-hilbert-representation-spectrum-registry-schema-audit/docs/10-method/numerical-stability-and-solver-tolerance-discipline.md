# Numerical stability and solver-tolerance discipline

`NUMERICAL-STABILITY-LEDGER.json` records when a route-local computation is stable enough to support update language.

A row must name the numerical object, tolerance, precision, solver or convergence checks, stochastic variability, platform sensitivity, maximum authority effect, and rollback handles.

## Stop rule

A likelihood, benchmark score, catalog statistic, reconstruction output, simulation result, proof-assistant boundary calculation, or optimizer product is not portable support when it is sensitive to seed, tolerance, floating-point behavior, solver settings, truncation, event ordering, hardware, or library versions beyond the declared equivalence relation.

## Stability dimensions

| Dimension | Required question | Typical rollback pressure |
|---|---|---|
| floating-point order | Does summation, reduction, or parallel scheduling change the result class? | lower to custody/replay-only |
| solver tolerance | Does convergence threshold or stopping rule change the route decision? | cap update language |
| discretization / truncation | Does grid size, cutoff, RG truncation, or finite-size choice change the claimed invariant? | trigger regulator/truncation rollback |
| stochasticity | Do seed, sampling schedule, optimizer initialization, or training split change the outcome? | selection / multiplicity rollback |
| hardware / platform | Do CPU/GPU, compiler, BLAS, container, or OS choices change the output class? | supply-chain and replay rollback |
| symbolic-numeric boundary | Does a proof, algebraic reduction, or exact/approximate conversion hide numerical assumptions? | proof-gap or benchmark rollback |
| posterior / likelihood stability | Does a small numerical perturbation change model ranking, Bayes factor, anomaly status, or route language? | contrast/update rollback |

## Authority ceilings

Numerical stability can license only the computational object that was stress-tested. It cannot by itself license:

- a new evidence unit,
- an independent replication claim,
- a causal mechanism claim,
- a global transport claim,
- a candidate ontology claim,
- an `S4`/`S5` promotion.

## Non-promotion rule

Numerical stability is a condition for spending computational evidence, not an additional evidence unit by itself.

- Additional numerical-stability anchors: `REF-0286`, `REF-0287`.
