# Indirection action review page: preserve, follow target, branch, or block interface spec

## Purpose

This page exists to stop indirection repair from being treated as a casual path tweak.

The operator should be able to review one exact choice:

> do I preserve the object, follow its target, branch ordinary bytes, or block this row on this seat?

## Allowed reviewed actions

- `preserve-object`
- `follow-target-inside-subject`
- `follow-target-as-separate-subject`
- `branch-ordinary-bytes`
- `keep-local-only`
- `block-on-this-seat`

## Required review columns

Every action row must preview:

- object fate after apply
- target transitivity after apply
- graph widening delta
- expected parity across seat families
- conflict hazard delta
- reversibility class

## Fixed page order

1. current posture strip
2. proposed action rows
3. widening and coupling review
4. parity and conflict review
5. commit guardrail language

### 1) Current posture strip

Show:

- current entry kind
- current object fate
- current target-scope verdict
- current conflict hazard

### 2) Proposed action rows

Each row must show:

- action label
- one-sentence effect
- whether the entry object survives
- whether target bytes become in scope
- whether a new subject admission is minted
- whether bytes are branched into ordinary content

### 3) Widening and coupling review

Show:

- whether the action widens the current subject graph
- whether target drift remains coupled later
- whether inside-subject following merely formalizes existing scope or changes it
- what evidence is missing if proof is incomplete

### 4) Parity and conflict review

Show:

- cross-seat parity delta
- unsupported-seat fallout still expected after apply
- whether current or future `.Conflict` residue remains possible
- whether the action improves clarity at the cost of semantic fidelity

### 5) Commit guardrail language

Before commit, publish:

- strongest safe sentence
- strongest forbidden sentence
- exact receipt that will be generated

## Public objects

### Indirection action review

Fields:

- `indirection_action_review_id`
- `indirection_posture_ref`
- `candidate_actions[]`
- `selected_action`
- `graph_widening_delta`
- `parity_delta`
- `conflict_delta`
- `reversibility_grade`
- `receipt_preview`

## Success criteria

The page is successful only when an operator can compare preservation, follow-target, branching, and block as separate semantic acts rather than as one blurry repair button.
