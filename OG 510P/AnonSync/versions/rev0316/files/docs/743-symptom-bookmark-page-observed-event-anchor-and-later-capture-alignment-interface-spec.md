# Symptom bookmark page — observed event anchor and later capture alignment interface spec

## Purpose

Pin one concrete observed symptom so later evidence collection aligns to an actual event rather than a vague memory.
This page should answer:

- what exact symptom we are bookmarking
- when it happened or was last seen
- who observed it and from where
- how later capture or witness requests should align to it
- when the bookmark is too stale or weak to keep using

## Inputs

- incident identifier
- current incident brief
- participant who observed the symptom if known
- event timestamp or window
- event source and confidence
- affected subject references
- nearest related warnings/history/queue events
- current capture windows or witness requests

## Primary questions this page must answer

1. What exact event are we trying to anchor?
2. How trustworthy is the time anchor?
3. Which participants and subjects does the bookmark implicate?
4. Which later capture windows should align to this event?
5. When should this bookmark be retired or replaced?

## Layout

### A. Bookmark strip

Fields:

- bookmark label
- incident headline
- observed symptom summary
- event time / window
- bookmark freshness

### B. Observation source card

Show:

- who observed it
- from which surface (`status row`, `history hit`, `queue view`, `manual note`, `external report`, `other`)
- whether the event is directly witnessed or inferred
- exact supporting evidence nearby

### C. Time quality card

Show:

- time source
- confidence grade
- timezone basis
- whether chronology is currently trustworthy
- whether the bookmark is suitable for log search, reproduction alignment, or only rough narrative use

### D. Capture alignment card

Show:

- which witness requests should inherit this bookmark
- whether the next run should reproduce the same symptom or a stronger one
- minimum dwell before the run is considered usable
- stale-after rule for the bookmark

### E. Invalidators card

List conditions such as:

- topology changed
- subject scope widened or narrowed
- clock trust repaired or invalidated
- stronger bookmark replaced this one
- symptom no longer matches the current explanation

## Required interactions

- `Confirm bookmark`
- `Adjust event window`
- `Link supporting evidence`
- `Mark bookmark approximate`
- `Mark bookmark stale`
- `Use bookmark in witness request`
- `Use bookmark in coordinated capture run`
- `Replace with newer bookmark`

## Guardrails

- Never pretend an approximate bookmark is exact.
- Never let a bookmark outlive a topology or subject change without review.
- Never reuse a bookmark for a different symptom family just because the time is nearby.
- Never detach the bookmark from the evidence or observer that created it.
- Never let later pages silently overwrite the bookmark's confidence.

## Output

One durable symptom bookmark that can align witness requests, reproduction runs, and later explanation receipts to a specific observed event.
