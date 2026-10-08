# Policy provenance receipt page — effective rule, origin, scope, and residue interface spec

## Purpose

Issue a durable receipt after any reviewed policy mutation so later operators do not have to reverse-engineer why behavior changed.

## Inputs

- subject / seat identifier
- requested mutation
- executed mutation class
- effective rule after apply
- origin chain after apply
- authoritative surface after apply
- surviving shadow rules
- scope of immediate effect
- delayed effect boundaries
- strongest safe sentence
- stronger forbidden sentence
- rollback / follow-up route

## Layout

### A. Receipt verdict strip

Fields:

- effective rule now
- origin now
- surface now authoritative
- strongest safe sentence
- next review point

### B. What changed / what did not

Two lists:

- changed now
- remained unchanged or only future-scoped

### C. Surviving shadow rules card

Fields:

- shadow rules still stored
- reactivation trigger if known
- why they still matter

### D. Effect boundary card

Fields:

- immediate subjects
- future-only subjects
- restart / reload / reconnect still pending
- mode substitution if any

### E. Language block

Four lines:

- requested phrase
- approved phrase
- forbidden stronger phrase
- reason the stronger phrase stays blocked

## Guardrails

- Never issue a receipt that only records the edited field name.
- Never hide shadow residue or future-scope limits.
- Never imply `saved` equals `fully governing` when another apply boundary remains.
- Never omit which surface is now authoritative.

## Output

A durable provenance receipt that preserves why a rule currently wins, what still sits beneath it, and what the product is allowed to claim about the result.
