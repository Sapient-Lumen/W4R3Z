# Diagnostic router page — status, peer, history, and queue unification interface spec

## Purpose

Review the best next diagnostic route for a current subject without making the operator remember support-style rituals.
The page should turn `what do I open next?` into a first-class comparison, not folklore.

## Inputs

- entry row/token
- subject identifier
- current diagnostic question class (`meaning`, `affected-items`, `peer/source`, `queue/backlog`, `timeline`, `mixed`, `unknown`)
- currently available local evidence
- candidate routes
- expected proof gain per route
- expected cost / interruption per route
- context-preservation state
- strongest safe sentence now
- stronger forbidden sentence now

## Primary questions this page must answer

1. Which route is strongest for the current question?
2. What proof does each route add?
3. Which route is redundant or weaker right now?
4. Which route preserves context best?
5. What conclusion is available now even before another hop?

## Layout

### A. Current question strip

Labels:

- `Need warning meaning`
- `Need affected-item slice`
- `Need peer/source proof`
- `Need queue/backlog answer`
- `Need recent timeline context`
- `Need mixed route comparison`

### B. Route comparison table

Columns:

- route name
- best for
- proof added
- cost / disruption
- preserves context?
- strongest approved sentence after opening

Example routes:

- `Affected items`
- `Peer route / presence`
- `Transfer queue`
- `History context`
- `Warning meaning`

### C. Evidence coverage matrix

Rows might include:

- meaning of current token
- concrete files/items
- online/offline source proof
- queue state / backlog reason
- recent chronology
- action-safe next step

Columns:

- current page
- affected items
- peer route
- queue
- history

### D. Best-next-route card

Fields:

- recommended next route
- why it wins now
- what later second hop is likely if any
- what stronger claim stays blocked even after that route

### E. Stay-here claim block

Four lines:

- current question
- strongest answer available without another hop
- missing proof
- why another route is still justified

## Required interactions

- `Open recommended route`
- `Pin route comparison`
- `Open secondary route`
- `Issue route receipt`

## Guardrails

- Never make the user open peers, history, and queue merely because that is the traditional ritual.
- Never recommend a route without stating what proof it adds.
- Never hide weaker candidate routes when they remain plausible alternatives.
- Never drop the original row/token context while routing.
- Never let external help be the first-class route when an owned local route exists.

## Output

A reviewed route decision that unifies diagnostic surfaces and preserves the reason each hop was chosen.
