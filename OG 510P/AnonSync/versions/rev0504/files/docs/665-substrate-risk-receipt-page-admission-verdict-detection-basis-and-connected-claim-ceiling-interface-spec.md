# Substrate-risk receipt page — admission verdict, detection basis, and connected-claim ceiling interface spec

## Purpose

This receipt preserves what substrate facts and claim ceilings were true when the operator admitted, resumed, migrated, or kept a share on a given path.

It exists because later operators must be able to prove whether the product had already warned that the share was ordinary, degraded, guarded, unsafe, or blocked on that substrate.

## Emission events

Emit this receipt after any event that:

- admits or re-admits a share on a new substrate
- changes the connected claim ceiling because notifications or lock behavior changed
- detects mixed-writer topology strongly enough to change verdict
- moves a share from ordinary to degraded/guarded/unsafe language
- records a remediation that keeps the share on the same substrate temporarily

## Fixed page order

1. event summary
2. substrate facts in force
3. winning admission verdict
4. connected claim ceiling
5. operator obligations and remedies
6. reopening conditions

### 1) Event summary

Show:

- share
- path
- event type
- time
- operator intent in plain language

### 2) Substrate facts in force

Show:

- substrate class
- protocol family
- discovery basis
- lock grade
- mixed-writer risk grade
- strongest evidence source that anchored the verdict

### 3) Winning admission verdict

Show:

- winning verdict (`ordinary-admit`, `guarded-admit`, `quarantine-admit`, `block-until-migrated`, `block-until-topology-cleaned`)
- why it won
- any rejected stronger sentence that explains what did not happen

### 4) Connected claim ceiling

Show:

- strongest safe connected sentence after the event
- strongest safe freshness sentence after the event
- stronger unsupported sentence after the event
- whether later share rows must carry degradation marking

### 5) Operator obligations and remedies

Show:

- whether editing is allowed, guarded, or discouraged
- whether other access channels must stop touching the same bytes
- whether migration is recommended or required
- whether external lock diagnosis remains necessary for some failures

### 6) Reopening conditions

Show:

- what evidence could upgrade the claim ceiling later
- what evidence would force a harsher verdict later
- whether this substrate can ever graduate to ordinary without path change

## Public object

### `substrate_risk_receipt`

Fields:

- `substrate_risk_receipt_id`
- `share_ref`
- `path_ref`
- `event_type`
- `operator_intent`
- `substrate_class`
- `protocol_family`
- `detection_basis`
- `lock_grade`
- `mixed_writer_risk_grade`
- `winning_verdict`
- `connected_claim_ceiling`
- `freshness_claim_ceiling`
- `operator_obligations[]`
- `reopen_conditions[]`
- `issued_at`

## Honest outputs

The receipt may conclude:

- `Winning verdict: guarded admit. Connected claim ceiling: this share is available here, but prompt change discovery is not guaranteed on this mounted substrate.`
- `Mixed-writer risk: likely. Stronger unsupported sentence: safe for ordinary concurrent NAS editing from unmanaged channels.`
- `Upgrade path: prove managed-only topology and restored notification support on this seat.`

It may not reduce the event to `share connected`, `folder added`, or `path changed`.
