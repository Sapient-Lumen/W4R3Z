# Status drilldown page — local explanation, scope, and next-route interface spec

## Purpose

Give the operator one owned answer to:

- what this current status token or row is claiming
- what subject scope it covers
- whether the click opens meaning, affected items, or a route choice
- which stronger statement is still unsupported
- what next route is safest

This page exists so a serious row click never begins with external help prose as the primary product answer.

## Inputs

- entry surface (`share row`, `item row`, `warning chip`, `history row`, `queue row`, `peer row`, `other`)
- status token label
- subject identifier
- current scope class (`share`, `item`, `peer-pair`, `seat`, `mixed`, `unknown`)
- current evidence summary
- strongest safe sentence
- stronger forbidden sentence
- affected-item count if known
- available next routes
- whether route choice is required now
- freshness of the evidence

## Primary questions this page must answer

1. What exactly is this row/token saying right now?
2. What scope does it cover?
3. What evidence is already local to this surface?
4. Are there concrete affected items behind it?
5. Which next route is strongest for the current question?
6. What stronger sentence is still unsafe?

## Layout

### A. Current answer strip

Fields:

- token label
- scope label
- strongest safe sentence
- stronger forbidden sentence
- next safest route

Example labels:

- `No source peers for these files — item scope`
- `Locked files detected — affected items available`
- `Peers mismatch suspected — peer route review recommended`
- `Transfer backlog only — open queue, not warning repair`

### B. What this row already proves card

Fields:

- current evidence local to this row
- freshness window
- whether the row is meaning-complete or only an entry point
- whether the current click came from a durable receipt or a live row

### C. Scope and affected-items card

Fields:

- subject(s) covered
- count of affected items if known
- whether all affected items are enumerated now or only partially known
- whether item navigation is safe from this surface

### D. Next-route chooser

Ordered cards such as:

- `Open affected items`
- `Open diagnostic router`
- `Open peer/route evidence`
- `Open transfer queue explanation`
- `Open history context`
- `Keep narrow claim`

Each card must state:

- what new proof it can add
- what it still will not prove
- whether context is preserved

### E. Claim ceiling block

Three stacked lines:

- **proved now**
- **not yet proved**
- **best next route for the missing proof**

## Required interactions

- `Open affected items`
- `Open diagnostic router`
- `Jump to strongest route`
- `Export diagnostic route receipt`

## Guardrails

- Never let a serious row click bypass this page straight into external help as the primary answer.
- Never make the operator guess whether a click leads to meaning, items, queue, or peer evidence.
- Never show a comforting token without its scope class.
- Never imply this row explains root cause when it only proves symptom or route class.
- Never lose entry context when routing onward.

## Output

A local first-stop diagnostic object that says what the row means, what it covers, and which route should come next.
