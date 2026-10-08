# Escalation lane page — entitlement, destination, and audience contract interface spec

## Purpose

Give the operator one durable page that answers:

- which outbound help or handoff lanes are actually available right now
- what entitlement, product-line, or question-class basis makes each lane valid
- who the likely audience is for each lane
- what privacy and package-shape expectations each lane carries
- what response ceiling the operator should honestly expect

This page exists so `Contact support`, `post on forum`, `use web form`, and `keep local for now` stop being mixed folklore and become typed product state.

## Inputs

- incident identifier
- evidence plan and manifest readiness if any
- product line / edition / seat entitlement facts
- commercial versus non-commercial posture if relevant
- current issue class (`functionality`, `crash`, `licensing`, `billing`, `commercial-use`, `general-question`, `other`)
- available external lanes and local-only lanes
- privacy posture and package sensitivity
- current claim ceiling

## Primary questions this page must answer

1. Which lanes are truly available right now?
2. Why is each lane available, blocked, or provisional?
3. What audience does each lane imply?
4. Which lane best fits the current question and package?
5. What stronger expectation should the product explicitly forbid?

## Layout

### A. Lane strip

Fields:

- incident headline
- issue class
- current recommended lane
- entitlement confidence
- package-readiness state

### B. Available lanes table

Columns:

- lane (`local-only`, `forum-summary`, `help-center-self-serve`, `private-ticket`, `billing-web-form`, `peer-handoff`, `other`)
- availability (`available`, `blocked`, `provisional`, `not-fit-for-question`)
- entitlement / policy basis
- audience class (`public-ish`, `private-vendor`, `billing`, `peer`, `self`)
- best-fit question classes
- package expectations
- strongest forbidden expectation

### C. Winning-lane explanation card

Show:

- why the recommended lane wins now
- what package shape it wants (`summary-only`, `manifest + summary`, `sanitized package`, `full private package`, `no export yet`)
- what redirection would force a different lane
- what answer / response ceiling is realistic

### D. Blocked or provisional lanes card

For each blocked or provisional lane show:

- what fact blocks it
- whether the block is entitlement, issue-fit, privacy, or readiness based
- what would have to change for that lane to become valid

### E. Expectations and honesty card

Show:

- whether a response is owed, possible, or merely hoped-for
- whether the lane is public-facing or private
- whether raw artifacts should travel in this lane
- whether a local save is the current safest outcome

## Required interactions

- `Adopt recommended lane`
- `Review another lane anyway`
- `Open escalation review`
- `Open destination confirmation`
- `Keep package local`
- `Return to evidence manifest`
- `Issue escalation lane receipt`

## Guardrails

- Never show a lane as available without naming the basis.
- Never let a generic `support` label hide audience class or entitlement.
- Never imply that `can send` means `will receive a substantive answer`.
- Never recommend a public/shared lane for a raw sensitive package without an explicit warning.
- Never hide when `no export yet` is the most honest lane outcome.

## Output

A reviewed escalation-lane object that makes available routes, entitlement basis, audience class, package fit, and expectation ceiling explicit before any outbound action.
