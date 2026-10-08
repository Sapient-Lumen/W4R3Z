# Witness request page — target peer, artifact class, capture window, and privacy envelope interface spec

## Purpose

Turn one evidence ask into a first-class reviewed object.
This page should answer:

- what exactly we are asking this participant to provide
- why this participant is being asked
- what time window or reproduction window matters
- how the evidence should be handled and disclosed
- what will count as complete, partial, or failed return

This page exists so `send logs` becomes a typed request instead of vague coordination.

## Inputs

- incident identifier
- target participant identifier
- target participant role and confidence
- requested artifact family (`recent logs`, `debug logs`, `queue snapshot`, `route proof`, `crash artifact`, `screen evidence`, `other`)
- capture window / reproduction window
- disclosure posture
- send lane
- current witness-set requirement level

## Primary questions this page must answer

1. Why are we asking this participant rather than another one?
2. What exactly should they collect or export?
3. What timeframe matters?
4. What sensitive classes may be included?
5. What counts as success, partial return, or failure?

## Layout

### A. Target strip

Fields:

- participant label
- current role
- required versus optional status
- current send lane
- shortest honest summary of why this participant matters

### B. Necessity card

Show:

- missing question this participant helps answer
- evidence unique to this participant
- stronger alternative participant if one exists
- what conclusion remains blocked without this participant

### C. Requested artifact card

Show:

- artifact family requested
- exact time window or reproduction instructions
- subject/share/file names already prefilled
- incident timestamp anchors already prefilled
- whether a restart, hold time, or special capture ritual is required

### D. Privacy and disclosure card

Show:

- whether the result stays local, goes to another operator, or leaves the constellation
- default redaction posture
- fields likely to be sensitive
- whether the participant may review before sending

### E. Completion proof card

Show:

- expected return object
- minimum acceptable completeness
- stale-after time
- partial-return reasons
- failure reasons (`unreachable`, `refused`, `too-large`, `expired`, `other`)

## Required interactions

- `Copy witness request`
- `Open local collection path`
- `Mark request sent`
- `Mark witness returned`
- `Mark partial return`
- `Mark impossible / unreachable`
- `Return to witness completeness review`

## Guardrails

- Never issue a generic request that omits the participant's role, target subject, or relevant time window.
- Never force the operator to rewrite known context such as share names, timestamps, or incident headline.
- Never hide the disclosure boundary behind one button.
- Never treat request delivery as witness completion.
- Never accept a returned artifact as complete without checking it against the requested family and window.

## Output

One reviewed participant-specific evidence ask with explicit necessity, artifact class, time window, privacy posture, and completion proof.
