# Freshness revalidation review page — prior claim, drift impact, and new proof threshold interface spec

## Purpose

The archive already had change freshness review.
What it still lacked was the dedicated page for the follow-up question:

> given the invalidator we just observed, what would now count as enough new proof to make a freshness claim again?

AnonSync should therefore issue a dedicated **freshness revalidation review** whenever an earlier claim was weakened, expired, or contested by posture drift.

## Review fields

The review must preserve:

- review id
- incident id
- prior receipt id
- linked invalidator version
- subject scope
- old claim summary
- drift-impact verdict
- current observation posture
- required proof threshold
- candidate revalidation events
- strongest allowed interim sentence
- stronger rejected interim sentence

## Required sections

### 1) Prior claim versus current posture

Publish the contrast in plain language, for example:

- `Earlier claim assumed notification-backed observation; current posture is SMB rescan-backed only.`
- `Earlier claim assumed a 10-minute rescan budget; cadence was later widened to 5 hours for NAS sleep.`
- `Earlier claim assumed the seat stayed awake; Android auto-sleep now limits checks to wake intervals.`

### 2) Drift impact verdict

Required verdicts:

- `claim unchanged`
- `claim weakened`
- `claim expired`
- `claim superseded already`
- `cannot compare honestly`

### 3) Required proof threshold

State what new evidence is strong enough now:

- one healthy notification after restored watcher capacity
- one completed scheduled rescan under current cadence
- one manual rescan under stable posture
- one wake cycle on mobile under allowed network
- one fresh restart plus stable path/runtime confirmation

### 4) Interim sentence ceiling

The review must publish both:

- strongest allowed interim sentence
- stronger rejected interim sentence

Examples:

- allowed: `The earlier lateness claim is no longer current because observation posture changed.`
- rejected: `The original delay finding still holds unchanged.`

### 5) Cheapest honest next rung

Show the least-strong honest next move:

- keep old receipt but downgrade language
- wait for declared revalidation event
- run a manual probe
- repair posture first, then gather evidence
- close old claim as superseded and issue a new receipt family

## Compact rendering obligations

Any compact rendering must still preserve:

- drift-impact verdict
- new proof threshold
- strongest allowed interim sentence
- cheapest next rung

## Anti-clone rule

Do not clone flows where the operator is expected to remember from support lore whether a restart, wake, service switch, or rescan really refreshed the old claim.
