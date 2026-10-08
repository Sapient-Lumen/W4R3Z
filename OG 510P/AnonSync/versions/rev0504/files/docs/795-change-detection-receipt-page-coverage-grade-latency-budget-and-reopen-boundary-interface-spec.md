# Change-detection receipt page — coverage grade, latency budget, and reopen boundary interface spec

## Purpose

The archive already had route provenance receipts and topology measurement receipts.
What it still lacked was the durable receipt for this question:

> after posture, coverage, and freshness were reviewed, what exact delay/freshness claim became true, over what blind window, and what would force that claim back open?

AnonSync should therefore issue a dedicated **change-detection receipt** whenever lateness, staleness, or `needs rescan` language is promoted into durable incident language.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- detection-posture version
- observation-coverage version
- freshness-review version
- covered subject scope
- active detection plane verdict
- notification coverage grade
- expected latency budget
- blind-window statement
- chosen intervention rung
- strongest allowed sentence
- stronger rejected sentence
- reopen conditions
- issuance timestamp

## Required sections

### 1) Freshness claim that won

Show the durable statement, for example:

- `For share A on host B, timely notification coverage was degraded by watcher exhaustion; freshness remained open until manual or scheduled rescan.`
- `For subject X, the observed delay was still within the declared 10-minute rescan budget.`

### 2) Coverage and blindness summary

Publish the active detection plane, evidence grade, and blind-window basis together.
Do not reduce this to `rescanned` or `watching`.

### 3) Intervention that was justified

State whether the product judged:

- no intervention yet
- manual rescan justified
- posture repair justified
- only lower-confidence language justified

### 4) Stronger rejected claim

State the stronger sentence the receipt explicitly refuses to make.
This is mandatory.

### 5) Reopen boundary

The receipt must say the claim reopens if any of these happen:

- notification posture changes materially
- watcher-capacity or storage class assumptions change
- a new timing anchor contradicts the current age estimate
- rescan cadence changes
- a contradictory healthy-notification witness arrives
- the observation window goes stale relative to the incident

## Compact rendering obligations

Any compact receipt chip must still preserve:

- freshness verdict
- coverage grade
- latency-budget label
- intervention summary
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `rescanned`, `watching normally`, or `delay` without preserving what subject that sentence covered, what blind window existed, and what stronger claim remained unsupported.
