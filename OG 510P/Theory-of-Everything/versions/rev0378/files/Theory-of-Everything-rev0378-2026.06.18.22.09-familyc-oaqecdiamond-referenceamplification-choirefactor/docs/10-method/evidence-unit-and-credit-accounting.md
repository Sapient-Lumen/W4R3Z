# Evidence-unit and credit-accounting discipline

Purpose: prevent the archive from counting one support chain several times merely because it appears as many papers, repositories, carriers, benchmarks, likelihood tables, proof objects, or route rows.

`EVIDENCE-UNIT-LEDGER.json` defines the unit of support that may be spent by a route. A unit is not a citation, not a dataset, and not a claim. It is the smallest record-bearing support packet whose failure would remove the same kind of route credit from the rows that depend on it.

A unit must declare:

1. which route rows it supports;
2. which public-record carriers and acquisition protocols carry it;
3. which empirical deltas, severity rows, and negative controls it touches;
4. which independence assumptions condition its use;
5. which shared-support cluster it belongs to;
6. the maximum credit it may spend;
7. the rollback rule if it is compromised.

## Counting rule

Multiple presentations of the same support chain do not become independent evidence. A theory paper, proof artifact, benchmark replay, public repository, metadata wrapper, and generated summary may all be necessary for custody, but they may still share one evidence unit or one shared-support cluster.

The archive therefore treats credit as route-local and capped:

```text
support packet + carrier + protocol + independence assumption + credit row
= bounded route credit
```

It does not become:

```text
many surfaces + many citations + many wrappers
= many independent confirmations
```

## Metadata wrapper rule

`EU-0014-METADATA-PROVENANCE-WRAPPER` exists because publicness, provenance, and metadata improve custody. They do not, by themselves, identify a candidate, close an inverse problem, defeat an adversarial quotient, or recover the observed sector. They are enabling evidence, not independent physical evidence.

## Non-promotion rule

Evidence-unit coverage can lower, cap, or audit authority. It cannot promote a route by itself. Route promotion still requires the state machine, promotion gates, observed-sector recovery, public-record carrier closure, acquisition replay, negative controls, defeater handling, severity tests, empirical deltas, and residual-cap discipline.
