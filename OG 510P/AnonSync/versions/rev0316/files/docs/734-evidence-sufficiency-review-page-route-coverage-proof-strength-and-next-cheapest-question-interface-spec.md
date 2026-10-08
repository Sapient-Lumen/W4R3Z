# Evidence sufficiency review page — route coverage, proof strength, and next-cheapest-question interface spec

## Purpose

Decide whether the current investigation already supports an honest conclusion or whether another route or heavier capture is justified.
This page exists so `collect logs from all peers` is never the default just because the operator feels stuck.

## Inputs

- incident identifier
- candidate explanations
- evidence objects already opened
- proof strength per explanation
- freshness of each evidence class
- unasked questions
- candidate next routes
- cost / disruption of heavier capture

## Primary questions this page must answer

1. What can we already say honestly now?
2. Which explanation is leading, and by how much?
3. What exact question remains unanswered?
4. Which next route is cheapest and strongest for that question?
5. Is heavier capture justified yet?

## Layout

### A. Current claim table

Columns:

- explanation
- supporting evidence
- contradicting evidence
- proof strength
- missing proof

### B. Coverage matrix

Rows might include:

- token meaning
- affected items
- source/peer proof
- queue/backlog state
- chronology
- local action aftermath
- heavier capture necessity

Columns:

- covered now
- partially covered
- not covered
- stale

### C. Next cheapest question card

Fields:

- missing question
- recommended next route
- proof expected from that route
- why cheaper alternatives are insufficient

### D. Heavier capture gate

Show only if relevant.
Fields:

- heavier capture class (`debug logs`, `trace`, `crash artifact`, `support packet`, `other`)
- exact gap it would address
- local cost / privacy cost / delay cost
- why it is justified or not justified yet

### E. Stop-here honesty block

Four lines:

- strongest safe sentence now
- stronger forbidden sentence now
- reason the stronger sentence is blocked
- whether closing the investigation now is acceptable

## Required interactions

- `Approve stop-here conclusion`
- `Open recommended next route`
- `Escalate to heavier capture`
- `Mark evidence stale and re-check`
- `Return to incident timeline`

## Guardrails

- Never escalate to heavier capture without naming the exact unanswered question.
- Never say `insufficient evidence` without showing what is already sufficient.
- Never recommend a route if it adds no unique proof.
- Never hide stale evidence inside a strong conclusion.
- Never force the operator to choose between overconfidence and endless escalation.

## Output

A reviewed proof-sufficiency decision that says whether the current case can close honestly, which cheaper route still matters, or why heavier capture is truly justified.
