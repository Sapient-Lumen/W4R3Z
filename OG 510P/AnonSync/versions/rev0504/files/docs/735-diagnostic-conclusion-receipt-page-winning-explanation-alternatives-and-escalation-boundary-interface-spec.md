# Diagnostic conclusion receipt page — winning explanation, alternatives, and escalation-boundary interface spec

## Purpose

Issue a durable receipt for the current diagnostic conclusion so handoff does not destroy the investigation narrative.
This receipt should preserve not just the winner, but the losing or still-live alternatives and the boundary of what was *not* proved.

## Inputs

- incident identifier
- approved winning explanation
- supporting evidence set
- alternatives rejected or left live
- strongest safe sentence
- stronger forbidden sentence
- next action or watch point
- reopen condition
- issued-at time

## Primary questions this page must answer

1. What explanation won?
2. What evidence made it win?
3. Which alternatives were rejected, and why?
4. Which alternatives are still live but weaker?
5. What stronger claim is still forbidden?
6. When should the incident be reopened or escalated?

## Layout

### A. Conclusion strip

Fields:

- incident headline
- approved conclusion
- confidence grade
- next action
- reopen trigger summary

### B. Evidence basis card

List the evidence that carried the winning explanation.
Each row must show:

- evidence object
- what it proved
- freshness at receipt time

### C. Alternatives ledger

Two groups:

- `Rejected alternatives`
- `Still-live but weaker alternatives`

Each alternative must state the reason it lost or remained unresolved.

### D. Language boundary block

Four lines:

- requested or hoped-for sentence
- approved sentence
- stronger forbidden sentence
- exact gap blocking the stronger sentence

### E. Reopen / escalation card

Fields:

- event that should reopen the incident
- evidence decay condition that should reopen the incident
- condition that justifies heavier capture or outside escalation
- whether the current receipt expires on freshness decay

## Required interactions

- `Copy safe conclusion`
- `Reopen incident`
- `Escalate with this receipt`
- `Compare with previous conclusion receipt`

## Guardrails

- Never issue a receipt that only says `looks fixed`.
- Never hide rejected alternatives; they are part of the diagnostic memory.
- Never let this receipt claim repair if it only justifies diagnosis.
- Never omit freshness and reopen conditions.
- Never collapse uncertainty into one confident sentence.

## Output

A durable diagnostic conclusion receipt that preserves the winning explanation, the non-winning alternatives, the claim ceiling, and the condition for reopening or escalation.
