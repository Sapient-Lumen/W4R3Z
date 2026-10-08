# Formal proof obligation and assumption discharge discipline

This surface owns the `OQ-0072` rule for proof, theorem, derivation, no-go, uniqueness, consistency, recovery, and formal-verification language.

## Rule

A route may not spend proof or derivation language until it declares:

1. the exact target statement and target grain;
2. the quotient or equivalence relation under which the statement is true;
3. the assumptions required;
4. which assumptions are discharged, merely named, imported, or left open;
5. the proof object, derivation trace, proof certificate, or reviewer/checker fallback;
6. the maximum authority effect and rollback handle.

## Non-promotion

A formal theorem is not a public-record bridge. A proof assistant transcript is not observed-sector recovery. A no-go theorem is not candidate identity. A clean derivation is not assumption discharge unless the assumption-discharge row says what was actually removed.

## Executable owners

- `PROOF-OBLIGATION-LEDGER.json`
- `ASSUMPTION-DISCHARGE-LEDGER.json`
- `FORMALIZATION-COVERAGE-LEDGER.json`
- `CLAIM-ROUTE-BINDING-LEDGER.json`
- `AUTHORITY-DEPENDENCY-GRAPH.json`

## Stop rule

When a proof row and an assumption row disagree, the assumption row wins. When a formalized fragment and a route claim disagree, the formalized fragment is the upper bound. When public-record, measurement, validity, semantic, or language-permission rows are weaker than the proof row, the weakest row controls.
