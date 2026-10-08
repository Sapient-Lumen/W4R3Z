# Current-sentence timeline page — promotion, commit, publish, rollout, and rollback events

## Purpose

This page gives the operator a chronological view of how a stronger sentence moved from being merely authorized to becoming current, partially current, rolled back, or superseded.
It exists so the product can show when commitment began, when named consumer families switched, when drift surfaced, and when rollback or supersession occurred.

## Required event classes

The timeline must distinguish at least:

- promotion authorized
- commit requested
- commit blocked
- preview current started
- staged rollout began
- consumer family switched to stronger current
- reconciliation passed
- all-required-consumer current reached
- stale or contradictory surface detected
- rollback armed
- rollback executed
- rollback completed
- stronger sentence superseded
- lower sentence restored
- currentness re-established after repair

## Required event payloads

Each event must carry:

- timestamp and trusted time basis
- actor or system source
- sentence affected
- consumer scope affected
- whether the event strengthens, weakens, or merely annotates currentness
- lower sentence that remains operative after the event
- strongest blocked stronger sentence after the event

## Required event examples

The page must be able to render events like:

- `promotion authorized; currentness remained unchanged pending manual commit`
- `preview current opened for adjudicator-only cohort; external consumers remained on lower sentence`
- `automation subscribers reconciled; stronger sentence became current for core execution cohort`
- `public-consumer rollout blocked because notification visibility was disabled and receipt reconciliation had not completed`
- `contradiction detected between API and durable receipt; stronger currentness frozen and rollback armed`
- `rollback executed; lower sentence restored as operative current for all required consumers`
- `newer sentence superseded prior current state after direct handoff`

## Timeline interpretation rules

- authorization is different from commitment
- commitment is different from consumer rollout
- current for some consumers is different from current for all required consumers
- rollback is different from supersession
- the viewer must always be able to tell whether the likely next move is commit, widen rollout, freeze, rollback, or supersede

## Mandatory visual cues

The page must visibly distinguish:

- consumer-scope widening
- consumer-scope shrinkage
- contradiction or stale-surface events
- rollback-risk intervals
- the exact interval during which a sentence was truly current for each required cohort

