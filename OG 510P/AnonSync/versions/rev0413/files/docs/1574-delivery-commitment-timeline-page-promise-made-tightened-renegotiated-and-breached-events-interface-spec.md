# Delivery commitment timeline page: promise made, tightened, renegotiated, and breached events interface spec

## Purpose

This page renders the public life of a commitment from initial shaping through publication, tightening, widening, renegotiation, miss, breach, withdrawal, and replacement.

## Event classes

Supported `commitment_event_class` values:

- `forecast-basis-linked`
- `aspiration-published`
- `target-published`
- `conditional-commitment-published`
- `hard-commitment-published`
- `window-tightened`
- `window-widened`
- `invalidator-activated`
- `renegotiation-opened`
- `renegotiation-published`
- `target-missed`
- `breach-opened`
- `commitment-withdrawn`
- `replacement-commitment-linked`
- `breach-closed`

## Required columns

- timestamp
- event class
- commitment class before
- commitment class after
- public sentence before
- public sentence after
- trigger fact
- audience impacted
- operator who approved change

## Hard rules

- The timeline must preserve every published promise class, not only the newest one.
- A widened or downgraded promise may not overwrite the original promise event.
- Breach must remain visible even if a later replacement commitment succeeds.
- Replacement commitment ids must link forward and backward.

## Timeline summaries

At top of page show:

- total number of promise-class upgrades
- total number of widenings
- total number of renegotiations
- whether any miss occurred
- whether any breach occurred
- current surviving sentence

## Highlight rails

The page must visually distinguish:

- healthy tightening without class change
- class upgrade without new window
- widening that stays inside class
- widening that forces class downgrade
- miss without breach
- breach with replacement plan
- withdrawal to forecast-only
