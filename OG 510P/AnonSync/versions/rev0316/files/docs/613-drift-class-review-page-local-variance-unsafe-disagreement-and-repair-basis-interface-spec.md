# Drift-class review page — local variance, unsafe disagreement, and repair-basis interface spec

## Purpose

The archive already has receipts and policy pages.
What it still lacked was one explicit review surface for the moment an operator asks:

> these rule ledgers differ; is that okay, risky, or already an unsafe shared-meaning split?

## Core decision

AnonSync must expose one first-class **Drift-class review** page whenever relevant peers carry non-identical exclusion or omit ledgers.

## Fixed page order

1. **Current drift verdict**
2. **Difference decomposition**
3. **Interpretation risk**
4. **Repair basis**
5. **Receipt**

### 1) Current drift verdict

Show:

- peer set under review
- verdict (`harmless local variance`, `compatible divergence`, `ambiguous mismatch`, `unsafe disagreement`, `unknown`)
- strongest safe sentence
- confidence class

### 2) Difference decomposition

Show the differences the product is actively classifying, such as:

- text mismatch with same semantics
- same text with OS-semantic mismatch risk
- future-only rule on one side
- counting-only exclusion on one side
- already-synced residue still present on one or more peers

### 3) Interpretation risk

Show:

- likely user-visible symptoms
- whether counts, search/index, or future intake will diverge
- whether the divergence can make one peer think material is absent while another still treats it as in-scope

### 4) Repair basis

Verdicts may include:

- `no repair needed`
- `align selector text only`
- `align semantics and reclassify future intake`
- `disconnect / deeper cleanup required`
- `unsafe to assume agreement before review`

### 5) Receipt

The receipt must preserve:

- peer set reviewed
- drift verdict adopted
- stronger rejected sentence
- next repair page chosen

## Public object

### Drift-class review page

Fields:

- `drift_class_review_id`
- `comparison_peer_set_ref`
- `drift_verdict`
- `safe_sentence`
- `rejected_sentence`
- `difference_rows[]`
- `risk_rows[]`
- `repair_basis_rows[]`
- `next_pages[]`
- `generated_at`
