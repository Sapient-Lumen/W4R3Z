# Delivery truth receipt page — subject state, cause basis, and next safe sentence

## Purpose

Produce a durable receipt that records what the product concluded about a subject's non-arrival or non-advancement, what evidence supported that conclusion, what next move was chosen, and what sentence is safe to reuse later.

## Receipt fields

### Identity
- receipt id
- subject / lineage if known
- reviewed path
- seat and surface
- timestamp

### Reviewed verdict
- subject delivery verdict
- confidence posture
- strongest safe sentence
- stronger blocked diagnosis if any

### Evidence basis
- policy evidence summary
- source evidence summary
- route evidence summary
- local execution evidence summary
- filesystem / continuity evidence summary
- chronology evidence summary

### Chosen next move
- operator-requested fix
- reviewed minimal intervention
- broader blocked intervention
- chosen path (`waiting`, `applied`, `declined`, `rerouted`, `escalated`)

### Success / follow-up basis
- what future observation would prove improvement
- what follow-up page to open next if needed
- whether continuity was preserved, uncertain, or replaced by successor state

### Forbidden overclaims
Examples:

- `This was definitely stuck.`
- `The bytes no longer exist anywhere.`
- `Transport was the only problem.`
- `Re-add was required.`
- `The issue is fixed.`

## Entry points

This receipt must be reachable from:

- missing-item review flows
- warning rows when they bind to specific subjects
- fetchability pages when arrival/fetch ambiguity exists
- local-fault ladders
- continuity and successor-rebuild flows

## Success condition

A future reader should be able to tell, without reopening several troubleshooting articles or rerunning the diagnostic flow, why the subject was absent or blocked, what the product knew versus did not know, and what next sentence was actually safe.
