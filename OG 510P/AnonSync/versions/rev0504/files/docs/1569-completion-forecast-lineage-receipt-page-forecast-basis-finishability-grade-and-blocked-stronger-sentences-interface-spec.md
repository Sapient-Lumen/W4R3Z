# Completion forecast lineage receipt page: forecast basis, finishability grade, and blocked stronger sentences interface spec

## Purpose

Later operators need one durable receipt that says:

> what finish forecast was actually published, what remaining-work basis and finishability grade supported it, what ETA window survived honest review, and what stronger sentence stayed blocked at the time?

## Required receipt fields

- receipt id
- linked forecast id
- linked progress id
- linked work id
- linked claim id
- publication time
- forecast owner
- remaining-obligation basis summary
- finishability grade
- ETA claim class
- confidence grade
- deadline posture if any
- leading fragility source
- strongest allowed finish sentence
- strongest allowed ETA sentence
- strongest blocked stronger sentence
- next condition that would narrow the estimate most

## Supported receipt states

- `forecast-published`
- `forecast-revised`
- `forecast-widened`
- `forecast-withdrawn`
- `no-honest-forecast-published`
- `forecast-closed-on-completion`

## Hard rules

- A receipt may not publish a point ETA.
- A receipt may not claim a bounded window without both lower and upper bound.
- If `no-honest-forecast-published` is the state, the receipt must still preserve what weaker sentence survived.
- If a forecast is widened or withdrawn later, the earlier receipt remains visible in lineage.

## Example strongest sentences

Allowed:

- `The current route is finishable with a broad window, but a tighter ETA remains blocked by scheduled pauses and hidden preprocessing.`
- `Work is progressing and appears finishable after the next checkpoint, yet no narrow forecast is currently honest.`

Blocked:

- `Completion by 14:00 is assured.`
- `Current transfer speed implies a reliable finish time.`
- `Because progress exists, the deadline will be met.`
