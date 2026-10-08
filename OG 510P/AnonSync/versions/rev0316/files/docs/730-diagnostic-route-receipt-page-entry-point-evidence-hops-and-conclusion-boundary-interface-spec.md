# Diagnostic route receipt page — entry point, evidence hops, and conclusion boundary interface spec

## Purpose

Issue a durable receipt after an investigation path so later operators do not have to reconstruct which row started it, which surfaces were visited, and what conclusion was actually earned.

## Inputs

- initial entry row/token
- subject identifier
- route steps taken
- evidence objects opened on each step
- approved conclusion
- stronger forbidden conclusion
- unresolved gaps
- next recommended action or watch point
- issued-at time

## Layout

### A. Receipt verdict strip

Fields:

- entry row/token
- final approved conclusion
- unresolved gap count
- best next action

### B. Route chronology

Ordered list of steps:

1. entry row opened
2. first owned page reached
3. subsequent routes visited
4. final evidence-bearing surface
5. receipt issuance

Each row should include:

- route name
- why it was opened
- proof gained there
- proof not gained there

### C. Evidence gained / evidence still missing

Two lists:

- gained during this route
- still missing after this route

### D. Language block

Four lines:

- requested or hoped-for sentence
- approved sentence
- forbidden stronger sentence
- exact gap blocking the stronger sentence

### E. Follow-through card

Fields:

- safest next route or action
- whether the issue should stay in workbench/home queues
- whether the receipt expires on freshness decay

## Guardrails

- Never issue a receipt that only says `investigated`.
- Never omit the starting row/token; diagnostic continuity begins there.
- Never collapse several routes into one anonymous `checked status` phrase.
- Never hide unresolved gaps behind a confident conclusion.
- Never let this receipt imply repair or resolution unless the investigated route actually proved it.

## Output

A durable route receipt preserving where the diagnosis started, which hops were taken, what they proved, and what claim ceiling remains.
