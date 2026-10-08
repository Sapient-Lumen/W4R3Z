# Publication timeline page — proposal, notice, publication, redaction, and retraction events

## Purpose

This page is the time-ordered event surface for how a typed act moved from internal draft to published or withdrawn views across different audiences.
It exists so the archive can distinguish `the underlying act changed` from `what each audience was allowed to know and rely on at each step`.

## Mandatory event families

- draft created
- internal circulation
- participant notice issued
- participant notice completed
- external redacted publication issued
- adjudicator full publication issued
- public summary issued
- publication corrected
- publication superseded
- publication retracted
- reliance widened
- reliance narrowed

## Mandatory columns

- event time
- event type
- source act version
- affected audience class
- redaction profile in force
- reliance class in force after event
- stronger sentence newly earned or newly blocked
- exact cause of widening, narrowing, supersession, or retraction

## Required comparisons

The timeline must keep these comparisons explicit:

- `act executed` vs `publication issued`
- `participant notice completed` vs `external publication completed`
- `same source act` vs `different published views`
- `publication corrected` vs `publication retracted`
- `trace still visible` vs `reliance still allowed`

## Required badges

- `draft-only`
- `internal-circulation`
- `participant-published`
- `external-redacted`
- `public-summary-live`
- `adjudicator-live`
- `superseded-view`
- `retracted-view`
- `reliance-widened`
- `reliance-narrowed`

## Failure modes the timeline must prevent

- collapsing all audiences into one publication moment
- losing the difference between a correction and a retraction
- implying that a superseded view never existed
- forgetting when a viewer's reliance rights widened or narrowed
- confusing encrypted custody or metadata visibility with semantic publication

## Stronger-sentence guard

The timeline may say `participants received a redacted notice on day 1, adjudicator-grade publication issued on day 3, and the public summary was retracted on day 5 after correction`.
It may not say `publication complete on day 1` unless every audience row actually supports that stronger sentence.
