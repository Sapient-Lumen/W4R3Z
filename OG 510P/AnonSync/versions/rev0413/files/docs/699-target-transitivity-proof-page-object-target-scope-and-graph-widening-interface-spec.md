# Target transitivity proof page: object, target scope, and graph widening interface spec

## Purpose

This page exists to prove whether target bytes are already in scope, still out of scope, or only obtainable through a new admission act.

## Core rule

A product must never let `symlink preserved` or `junction found` stand in for a target-inclusion answer.
Target transitivity must be proven separately.

## Fixed page order

1. entry proof strip
2. target resolution card
3. in-scope / out-of-scope verdict
4. graph-widening proof
5. receipts and counterfactuals

### 1) Entry proof strip

Show:

- entry path
- entry kind
- proof confidence for the entry classification
- whether the object currently survives on this seat

### 2) Target resolution card

Show:

- target path or unresolved state
- target scope relative to current subject
- whether target resolution is stable, broken, or ambiguous
- whether the target can be inspected safely now

### 3) In-scope / out-of-scope verdict

Show exactly one verdict:

- `target already in scope`
- `target outside current scope`
- `target requires separate admission`
- `cannot prove target scope yet`
- `not applicable`

Also show the strongest sentence explaining why.

### 4) Graph-widening proof

Show:

- whether follow-target changes the set of governed bytes
- whether the change is merely coupling within current scope or a true outward widening
- what new subject or approval object would be minted if widening occurs
- what later receipt proves that widening did or did not happen

### 5) Receipts and counterfactuals

Show:

- last target transitivity proof receipt
- counterfactual sentence for `preserve object only`
- counterfactual sentence for `follow target`
- counterfactual sentence for `branch ordinary bytes`

## Public objects

### Target transitivity proof

Fields:

- `target_transitivity_proof_id`
- `entry_ref`
- `target_path` nullable
- `target_scope`
- `target_transitivity_verdict`
- `graph_widening_risk`
- `proof_confidence`
- `counterfactual_rows[]`
- `receipt_refs[]`

## Guardrails

The page must never:

- claim target inclusion because the object itself is visible
- claim no graph widening when the target is outside current scope
- bury target ambiguity behind `unsupported` alone
- force operators to infer counterfactual outcomes from troubleshooting prose
