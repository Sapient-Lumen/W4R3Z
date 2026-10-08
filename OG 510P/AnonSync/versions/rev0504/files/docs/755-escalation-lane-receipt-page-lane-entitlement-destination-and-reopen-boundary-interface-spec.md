# Escalation lane receipt page — lane, entitlement, destination, and reopen boundary interface spec

## Purpose

Leave one durable record of why this outbound route was chosen and what it actually meant.
This page should answer:

- which lane was used
- what entitlement or policy basis supported it
- what destination class received the package
- what delivery state occurred
- what response ceiling and reopen boundary now apply

This page exists so `we sent it to support` or `we posted it` becomes a typed receipt instead of remembered folklore.

## Inputs

- incident identifier
- escalation-lane object and review outcome
- destination-confirmation object
- exported package summary or local-save summary
- delivery status and timestamps
- expectation ceiling
- redirect / stale triggers

## Layout

### A. Receipt strip

Fields:

- escalation receipt id
- incident headline
- chosen lane
- destination class
- entitlement basis
- delivery state

### B. Lane meaning card

Show:

- why this lane was chosen
- rejected nearby lanes
- strongest honest statement about what this route means
- stronger forbidden statement

### C. Destination and package card

Show:

- recipient class
- package shape sent or saved
- privacy posture at time of handoff
- whether raw artifacts traveled or summary only
- whether package fit was full, provisional, or constrained

### D. Delivery and expectation card

Show:

- delivery state (`saved-local-only`, `submitted`, `posted`, `shared`, `delivery-uncertain`, `failed`)
- whether any response is owed, best-effort, peer-dependent, or undefined
- whether delivery success is separate from package sufficiency
- any immediate next action expected from the operator

### E. Reopen / redirect boundary card

Show conditions such as:

- entitlement basis changes
- issue class changes from technical to billing/licensing or vice versa
- package widened or split after this receipt
- a better lane becomes available
- the recipient redirects the operator elsewhere
- public summary now needs private artifact follow-up

## Required interactions

- `Copy escalation receipt summary`
- `Open escalation lane`
- `Open escalation review`
- `Open destination confirmation`
- `Reopen lane selection`
- `Create successor package`

## Guardrails

- Never equate `submitted` with `accepted for deep support`.
- Never omit the entitlement or policy basis.
- Never hide the destination class.
- Never merge `local save`, `public post`, and `private ticket` into one success state.
- Never let a later reroute silently overwrite this receipt in chronology.

## Output

A durable escalation receipt that preserves lane choice, entitlement basis, destination class, package shape, delivery state, response ceiling, and reopen/redirect boundary.
