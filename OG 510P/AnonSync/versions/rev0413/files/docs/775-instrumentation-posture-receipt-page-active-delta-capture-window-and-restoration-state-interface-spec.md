# Instrumentation posture receipt page — active delta, capture window, and restoration state interface spec

## Purpose

Leave a durable receipt proving:

- what baseline posture existed before diagnostics changed
- what deltas were active during the capture window
- whether restart/activation conditions were actually satisfied
- what restoration has or has not yet happened
- what stronger sentence about normalcy, sufficiency, or cleanup is still forbidden

## Inputs

- instrumentation plan
- instrumentation change review
- coordinated capture run or evidence capture outcome
- instrumentation restore review
- retained-artifact and residue findings

## Primary questions this page must answer

1. What was the baseline before instrumentation changed?
2. Which diagnostic deltas were actually active during evidence collection?
3. Did restart and dwell conditions make that posture trustworthy?
4. What is the restoration state now?
5. When should the operator reopen instrumentation rather than trust this receipt as settled?

## Sections

### 1. Baseline and delta summary

Show:

- plan id / version
- baseline posture summary
- deltas requested
- deltas actually activated
- deltas that never took effect

### 2. Capture-window truth

Show:

- activation timestamp
- restart satisfied or not
- reproduction / dwell window observed or not
- strongest honest sentence about evidence posture during the run
- stronger forbidden sentence

### 3. Restoration state

Show:

- restored to baseline (`yes`, `partial`, `no`, `unknown`)
- still-live overrides
- retained residue classes
- cleanup still owed or intentionally deferred

### 4. Claim ceiling

Show:

- strongest supported normalcy / readiness sentence
- residual uncertainty (`restart-not-proven`, `buffer-inflation-left-on`, `hidden-override-present`, `residue-retained`, `baseline-unknown`, `none-significant`)
- what later evidence/export/ask receipts may still claim beyond this receipt

### 5. Reopen boundary

Trigger reopen when:

- a later operator cannot verify which deltas were active during capture
- restart was assumed rather than proven
- another evidence run needs the same or narrower posture
- hidden-file or power-user overrides remain after `restored` was claimed
- a recipient asks for longer capture because rotation or dwell may have clipped evidence

## Guardrails

- Never let this receipt read like packet delivery proof; it is about posture truth.
- Never collapse `requested`, `active`, and `restored` into one word.
- Never say `back to normal` unless baseline, active deltas, and residue all support it.
- Never omit hidden or advanced routes from the receipt.
- Never overclaim capture sufficiency when restart or dwell evidence is weak.

## Output

A durable instrumentation-posture receipt preserving baseline, active deltas during capture, restoration state, retained residue, and reopen boundary.
