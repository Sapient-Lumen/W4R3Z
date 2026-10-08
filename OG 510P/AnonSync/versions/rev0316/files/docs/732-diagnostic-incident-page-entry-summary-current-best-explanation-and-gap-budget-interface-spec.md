# Diagnostic incident page — entry summary, current best explanation, and gap-budget interface spec

## Purpose

Give the operator one durable home for an investigation so diagnosis no longer lives as a trail of clicks and memory.
This page should answer:

- what problem this incident is about
- where it started
- which explanation is currently strongest
- which alternatives remain live
- what proof is still missing
- what the next cheapest honest question is

## Inputs

- incident identifier
- entry point (`status row`, `warning`, `history hit`, `queue row`, `peer route`, `manual incident`, `other`)
- current headline
- subject identifier(s)
- current strongest explanation
- active alternative explanations
- supporting evidence summary
- unresolved gaps
- next candidate routes
- last-updated time and freshness score

## Primary questions this page must answer

1. What investigation am I in right now?
2. What started it?
3. What explanation is strongest so far?
4. What other explanations are still plausible?
5. What proof is still missing?
6. What is the cheapest next question worth asking?

## Layout

### A. Incident strip

Fields:

- incident headline
- entry point label
- subject scope
- current best explanation
- freshness of the incident summary

Example labels:

- `Case: files not arriving — started from no-source status row`
- `Case: transfer stalled — started from backlog row`
- `Case: path blocked — started from continuity warning`

### B. Current best explanation card

Fields:

- strongest safe sentence now
- supporting evidence count
- confidence grade (`strong`, `moderate`, `weak`, `split`, `unknown`)
- stronger forbidden sentence

### C. Alternatives still alive card

Ordered list of remaining explanations.
Each row must show:

- alternative explanation
- why it is still plausible
- missing proof needed to rule it in or out

### D. Gap budget card

Fields:

- missing proof items
- cheapest next question
- more expensive later questions if any
- whether heavier capture is justified yet

### E. Route plan card

Ordered actions such as:

- `Open incident timeline`
- `Open evidence sufficiency review`
- `Open affected items`
- `Open peer/source proof`
- `Open queue explanation`
- `Escalate to heavier capture`

Each action must state what proof it adds and what it still will not prove.

## Required interactions

- `Open incident timeline`
- `Open evidence sufficiency review`
- `Pin current explanation`
- `Re-rank alternatives`
- `Issue diagnostic conclusion receipt`

## Guardrails

- Never make the operator reconstruct the investigation headline from several rows.
- Never show only one explanation when alternatives are still live.
- Never recommend heavier capture without naming the exact gap it is meant to close.
- Never let this page imply final diagnosis if the confidence grade is still split or weak.
- Never lose the original entry point once the incident exists.

## Output

A durable investigation home that preserves entry, current best explanation, alternatives, and the remaining proof budget.
