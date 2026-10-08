# Conservation law versus gauge constraint audit

Conservation laws, Ward identities, constraints, and gauge redundancies are related but not interchangeable. A route must identify whether a relation is a physical conservation law, a gauge identity, a constraint-propagation rule, a soft charge, a continuity equation, a catalog convention, or a metadata bookkeeping invariant.

The audit blocks this move:

```text
Ward-looking identity + gauge-fixed calculation + clean package = physical conserved current
```

The allowed move is narrower:

```text
route-local conserved object + anomaly control + gauge/quotient object + leakage budget + rollback handle = bounded conservation language
```
