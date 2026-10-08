# Current sync mode page — current share, future default, and path-basis interface spec

## Purpose

Give the operator one reviewed answer to:

- what this visible mode means for the current share right now
- what the seat's future-arrival default is in the reviewed scope
- what byte posture the current share actually has
- what path basis produced the current local bind or disconnect state
- what return contract applies if the operator later clears, removes locally, disconnects, or reconnects

This page is the mode-native companion to share-local presence, byte-posture, disconnected-share, and future-arrival-default pages.
It should appear whenever a mode chip or share-detail surface could plausibly be read as stronger explanation than it really provides.

## Inputs

- seat identifier
- share identifier
- platform family (`desktop`, `android`, `ios`, `web`, `unknown`)
- current mode label (`disconnected`, `selective`, `synced`, `connected`, `unknown`)
- current share posture (`announced-only`, `pathless-disconnected`, `bound-placeholder-backed`, `bound-partial`, `bound-full`, `removed-local-only`, `unknown`)
- future-arrival default (`disconnect-by-default`, `placeholder-by-default`, `full-by-default`, `review-required`, `unknown`)
- current byte posture (`names-only`, `placeholders`, `partial-local`, `full-local`, `none`, `unknown`)
- current path basis (`reviewed-bind`, `default-path`, `template-derived`, `reconnect-proposed`, `collision-suffixed`, `none`, `unknown`)
- return contract (`clear-returns-to-placeholder`, `disconnect-preserves-filesystem-and-row`, `remove-local-and-preserve-remote`, `reconnect-path-review-needed`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence
- nearest honest next action

## Primary questions this page must answer

1. What does this visible mode mean for the current share right now?
2. What will later arrivals on this seat do by default?
3. What bytes are actually local here now?
4. Where did the current path or pathless state come from?
5. What exact return contract applies after clear, remove-local, disconnect, or reconnect?

## Layout

### A. Mode verdict strip

Fields:

- share label
- seat label
- current mode label
- current-share posture
- strongest safe sentence

Example verdicts:

- `Selective on this share; current bytes are placeholders here, future arrivals on this seat also default to placeholder-backed unless changed separately`
- `Disconnected for this current share; later linked-device arrivals still default to placeholder-backed on this seat`
- `Synced now; reconnect history shows the current path was auto-proposed after a prior disconnect`

### B. Current-share card

Show:

- current share posture
- whether the share is currently bound or pathless
- whether the share is active, disconnected, or locally absent
- what exact state the mode label is proving

This card exists so the operator can stop treating one mode chip as a full explanation.

### C. Future-default card

Show:

- the future-arrival default for the relevant scope
- whether that default is seat-wide, linked-device-only, or narrower
- whether changing it would leave the current share untouched
- strongest safe sentence about later arrivals

### D. Byte-posture card

Show:

- current byte posture
- whether subtrees are mixed or uniform
- whether the current label is descriptive of bytes or only suggestive
- strongest action still truthful now

### E. Path-basis card

Show:

- current local path or pathless state
- path basis (`reviewed`, `default-proposed`, `reconnect-derived`, `collision-suffixed`, `unknown`)
- whether a `(1)` duplicate fallback or default-folder policy is in effect
- freshness of the path evidence

### F. Return-contract card

Show together:

- what `Clear` would preserve
- what `Remove from this device` would preserve
- what `Disconnect` would preserve
- what reconnect would later need to prove

This card must make it obvious that these actions are not interchangeable.

### G. Claim-ceiling card

Show three sentences together:

- strongest approved sentence
- stronger forbidden sentence
- blocker basis

Example:

- approved: `This share is currently placeholder-backed here; future arrivals on this seat also default to placeholder-backed unless changed separately.`
- forbidden: `This share is fully local here and future arrivals will behave identically.`
- blocker basis: `current subtree mix plus separate seat default still in force`

## Compact row contract

A truthful compact row should preserve this order:

1. current mode label
2. current-share posture
3. future-arrival default
4. path basis
5. next honest action

Example:

```text
Selective    placeholders here now    future default: placeholders    reconnect path: reviewed bind    Review
```

## Success criteria

A good page lets a later operator answer:

1. what this mode means for the current share
2. what it separately means for future arrivals
3. what bytes are local now
4. what path basis is in force
5. what clear/disconnect/reconnect would honestly do next
