# Ask fulfillment review page — request coverage, gaps, and excess disclosure interface spec

## Purpose

Review whether the prepared return actually satisfies the current recipient ask without oversharing.

This page exists so `attach logs` or `send dump` becomes a coverage decision instead of a hopeful gesture.

## Inputs

- recipient ask object
- current evidence manifest
- candidate packet members
- sensitivity and redaction findings
- participant / subject scope map
- binding token and lane requirements

## Primary questions this page must answer

1. Which ask clauses are fully covered by the current return?
2. Which clauses are only partially covered or still missing?
3. What candidate members exceed the ask and widen disclosure without need?
4. What strongest honest sentence can the product make about ask satisfaction now?
5. What smaller or additional action is the best next move?

## Sections

### 1. Coverage ledger

Per ask clause show:

- requested member or explanation
- matched return member(s)
- coverage verdict (`full`, `partial`, `none`, `unclear`)
- reason code

### 2. Gap card

Show:

- unresolved clauses
- whether the gap requires new capture, new participant, new redaction, or new lane
- claim ceiling while the gap remains

### 3. Excess disclosure card

Show:

- candidate members not required by the ask
- privacy or audience widening risk
- safer narrowed packet alternative

### 4. Satisfaction sentence card

Show one approved sentence, for example:

- `covers all requested logs and one requested timestamp note`
- `covers the asked desktop log set but not the requested NAS dump`
- `cannot yet satisfy the ask because return lane requires upload-link issuance first`

Also show one stronger forbidden sentence.

### 5. Next move card

Show the smallest honest next action:

- `return reviewed packet now`
- `capture one missing artifact`
- `request upload link`
- `narrow the packet`
- `clarify ambiguous clause`
- `hold and escalate`

## Required interactions

- `Exclude extra members`
- `Mark clause partial`
- `Open missing-clause capture`
- `Open return lane review`
- `Approve satisfaction sentence`
- `Issue fulfillment receipt draft`

## Guardrails

- Never call a packet `complete` while any required clause is uncovered.
- Never hide extra members once the ask is narrower than the packet.
- Never let redaction silently change clause coverage.
- Never let delivery success substitute for ask satisfaction.

## Output

A reviewed fulfillment decision preserving clause coverage, missing work, excess-disclosure warnings, and strongest supported satisfaction language.
