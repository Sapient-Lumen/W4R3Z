# Policy effect verification page: reread witness, non-retroactivity, and residual drift interface spec

## Purpose

When an operator wants to know whether a changed rule has actually taken effect, they need one page that answers:

> what fresh witness proves the rule is live, what exactly did that witness cover, and what surviving old material still prevents a stronger claim?

AnonSync should require a **Policy effect verification** page whenever policy activation depends on reread, rescan, restart, or future-only semantics.

## Page contract

Render the same sections in the same order:

1. verification target
2. witness set
3. coverage and blind spots
4. non-retroactivity and drift summary
5. resulting sentence and receipt

### 1) Verification target

Show:

- policy or setting under test
- target scope
- expected activation class
- expected effect class (`future-only`, `retroactive-with-reconcile`, `runtime-only`, `diagnostic-only`, `mixed`)

### 2) Witness set

Allow multiple witness kinds, such as:

- runtime reread observed
- manual rescan observed
- restart observed
- targeted example matched new policy
- targeted example remained old because policy is future-only
- external dependency witness imported
- unknown / insufficient

Each witness shows freshness, scope, and confidence.

### 3) Coverage and blind spots

The page must say what the proof does and does not cover.
Examples:

- `Future arrivals now follow the new exclusion rule.`
- `Already-synced files remain present and were not expected to disappear.`
- `Already-indexed structure still remains visible until disconnect or deeper reconcile.`

### 4) Non-retroactivity and drift summary

Show:

- whether surviving old material is expected
- whether any remaining difference is honest residue or unexpected drift
- cheapest next step to reduce drift if desired
- stronger rejected sentence

### 5) Resulting sentence and receipt

The page emits only sentence forms consistent with the evidence, such as:

- `The rule is live for future arrivals; historical material remains outside its retroactive scope.`
- `Runtime has reread the change, but no named-example proof has been recorded yet.`
- `Verification is incomplete because the expected trigger has not occurred.`

## Required data object

### `policy_effect_verification`

Suggested fields:

- `policy_effect_verification_id`
- `policy_ref`
- `target_scope`
- `witnesses[]`
- `coverage_summary`
- `blind_spots[]`
- `retroactivity_boundary`
- `residual_drift_class`
- `safe_sentence`
- `rejected_stronger_sentence`
- `receipt_ref`

## Rules

### Rule 1 — live-for-future and fixed-the-past are different outcomes

The page must preserve that distinction in both prose and receipts.

### Rule 2 — expected residue is not silent success

Residual old state must remain visible until the operator accepts it or runs a deeper reconcile path.

### Rule 3 — verification must name its examples

A page may not overclaim broad effect from one narrow witness without stating the coverage limit.

## Acceptance criteria

A cautious operator can:

- prove the rule is live or not yet live
- tell what witness class carried that proof
- tell what historical residue is still expected
- avoid overstating one witness into full historical correction
