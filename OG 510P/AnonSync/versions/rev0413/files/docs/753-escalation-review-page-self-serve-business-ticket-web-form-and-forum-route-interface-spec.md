# Escalation review page — self-serve, business ticket, web form, and forum route interface spec

## Purpose

Force one explicit review before a serious package leaves the product.
This page should answer:

- why the chosen lane is better than nearby alternatives
- whether the current package actually fits that lane
- what privacy, visibility, and response tradeoffs the lane creates
- whether the operator is solving the right problem or just following the nearest button

This page exists so `send` is no longer the first moment where lane contradictions become visible.

## Inputs

- escalation-lane object
- incident brief and current question class
- evidence manifest summary
- package sensitivity findings
- destination candidates
- entitlement basis and confidence
- current operator intent (`ask-for-help`, `submit-evidence`, `ask-licensing`, `ask-billing`, `share-with-peer`, `save-for-later`)

## Primary questions this page must answer

1. Why does this lane beat the closest alternatives?
2. Is the current package too wide, too raw, or too weak for this lane?
3. What privacy or visibility consequence follows from this route?
4. What response or turnaround expectation is actually justified?
5. Should the operator redirect, narrow, split, or stop instead?

## Layout

### A. Review strip

Fields:

- chosen lane
- operator intent
- entitlement basis
- current fit verdict (`good-fit`, `needs-summary`, `split-first`, `wrong-lane`, `hold-local`)

### B. Lane comparison table

Columns:

- candidate lane
- why it is tempting
- why it loses or wins
- audience/visibility
- package fit
- response expectation
- redirect trigger

### C. Package-fit review card

Show:

- whether the lane wants summary, manifest, or raw artifacts
- whether the current package is overshared, underspecified, or correctly shaped
- which members would need splitting or redaction
- whether the current diagnostic question belongs in another route entirely

### D. Operator-expectation card

Show:

- whether the lane is for technical troubleshooting, billing/licensing, public discussion, or private peer coordination
- whether response priority is defined, weakly implied, or absent
- whether silence/non-answer remains compatible with the lane
- what the product will not promise

### E. Decision card

Actions presented as explicit outcomes:

- proceed with lane
- switch lane
- split package first
- export summary only
- keep local and revisit later

## Required interactions

- `Proceed with this lane`
- `Switch to another lane`
- `Split package first`
- `Export summary only`
- `Keep local for now`
- `Open destination confirmation`
- `Issue escalation lane receipt`

## Guardrails

- Never let `nearest button` outrank `best-fit lane` without a visible warning.
- Never treat entitlement uncertainty as an invisible footnote.
- Never let the operator proceed without seeing audience visibility.
- Never merge `billing/licensing question` with `technical troubleshooting` under one generic route.
- Never let a misfit package travel unreviewed just because a form exists.

## Output

A reviewed escalation decision that records the winning lane, rejected alternatives, package-fit verdict, visibility consequences, and expectation ceiling.
