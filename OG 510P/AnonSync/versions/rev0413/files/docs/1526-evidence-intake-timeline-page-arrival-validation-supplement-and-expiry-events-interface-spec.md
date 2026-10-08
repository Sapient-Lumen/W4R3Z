# Evidence intake timeline page: arrival, validation, supplement, and expiry events interface spec

## Purpose

Operators need one timeline that preserves how a packet moved from arrival to judgment.
The page answers:

> what arrived when, what was validated, when sufficiency improved or decayed, what supplement loops opened, and when the packet aged out or was superseded?

## Timeline event families

The page must support the following event families:

- `packet-arrived`
- `packet-opened`
- `validation-failed`
- `fit-question-updated`
- `fit-world-mismatch-found`
- `window-miss-found`
- `supplement-request-sent`
- `supplement-response-partial`
- `supplement-response-complete`
- `supplement-expired`
- `sufficiency-grade-upgraded`
- `sufficiency-grade-downgraded`
- `packet-superseded`
- `packet-recalled`
- `packet-staled-out`

## Required timeline rows

Every event row must include:

- event time
- actor
- source packet or supplement id
- changed field or grade
- previous safe sentence
- new safe sentence
- strongest blocked sentence after event

Hard rule:

The timeline may not record only packet logistics.
It must record sentence-ceiling changes.

## Special timeline rules

### Arrival without opening

A packet may arrive and still remain epistemically weak.
`packet-arrived` alone cannot lift sufficiency grade.

### Supplement loops

Each supplement branch must stay attached to the gap it was trying to close.
Operators must not lose track of why a follow-up was opened.

### Staleness

A once-decision-grade packet may later age into a weaker posture if freshness, version, or world assumptions expire.
That downgrade must be visible.

### Supersession

A newer packet may supersede an older one for some questions but not all.
The timeline must support partial supersession.

### Recall

If a packet is recalled for custody or integrity reasons, the intake timeline must preserve which conclusions now lose support.

## Output sentence

The page footer must state:

> Intake history shows **[current grade]** as of **[time]**, reached through **[key transitions]**. The current safe sentence is **[safe sentence]**. The strongest blocked sentence is **[blocked sentence]** because **[live blocking gap or stale condition]**.
