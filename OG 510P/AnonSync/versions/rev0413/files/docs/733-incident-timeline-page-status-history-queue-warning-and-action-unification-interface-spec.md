# Incident timeline page — status, history, queue, warning, and action unification interface spec

## Purpose

Show one chronological braid for the current incident so the operator can see the order of symptoms, route hops, and interventions without hopping between unrelated surfaces.

## Inputs

- incident identifier
- initial entry point
- relevant status snapshots
- relevant history events
- peer/queue events
- warning transitions
- operator actions
- receipts or evidence objects issued
- freshness / retention horizon

## Primary questions this page must answer

1. What happened first?
2. Which facts are current versus historical?
3. Which route hops were diagnostic only versus mutating actions?
4. What changed after each intervention?
5. What evidence has already gone stale or will soon decay?

## Layout

### A. Timeline verdict strip

Fields:

- incident headline
- current state (`still live`, `improving`, `quiet but unresolved`, `closed`, `stale`)
- most recent meaningful change
- next watch point

### B. Braided chronology

Render one ordered event stream with typed rows such as:

- `Status row observed`
- `Warning meaning opened`
- `History hit found`
- `Peer list checked`
- `Queue reviewed`
- `Operator changed setting`
- `Restart performed`
- `Heavier capture raised`
- `Conclusion receipt issued`

Each row must show:

- timestamp
- event family
- what changed
- whether the row is evidence, action, or commentary

### C. Before/after joins

For mutating actions, show paired rows:

- action taken
- expected effect
- observed aftermath
- whether the action changed the best explanation

### D. Freshness and decay card

Fields:

- oldest still-relied-on evidence
- evidence that has decayed or gone stale
- whether the current conclusion depends on stale evidence
- re-check recommendations

### E. Timeline filters

Common filters:

- `Evidence only`
- `Actions only`
- `Current state transitions`
- `Historical precursors`
- `Routes opened`

## Required interactions

- `Filter to evidence only`
- `Jump to entry point`
- `Compare before/after action`
- `Open supporting evidence from event`
- `Return to incident page`

## Guardrails

- Never mix current and historical facts without visible labels.
- Never hide operator actions among passive events.
- Never let a restart or setting change appear to have worked unless the timeline shows the post-action evidence.
- Never force the operator back into separate history and queue surfaces just to understand chronology.
- Never rely on stale evidence without marking it.

## Output

One braided chronology that preserves what happened, in what order, and what each intervention actually changed.
