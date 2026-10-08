# Remedy-hardening-attestation successor action-envelope lineage receipt page — reviewed scope, tripped guardrails, and blocked stronger containment sentences

## Purpose

This page is the portable receipt summarizing what can honestly be claimed about one execution envelope after review and, if applicable, after runtime.
It is the receipt that later pages must cite instead of improvising stronger within-envelope language.

## Receipt header

The header must show:

- envelope identifier
- successor world identifier
- action identifier
- chosen actuator
- beneficiary slice
- current envelope standing
- current strongest safe sentence
- current blocked stronger sentence

## Mandatory receipt fields

- source authorization receipt identifier
- source action-plan receipt identifier
- reviewed touched-set summary
- reviewed exclusions summary
- armed guardrail summary
- hard-stop class
- fail-closed versus fail-open class
- known automatic side-effects summary
- remembered-approval exposure summary
- rescan or restart exposure summary
- hydration exposure summary
- runtime result summary
- overspill summary
- cleanup status summary
- contradiction status summary
- superseding receipt identifier if any

## Standing states

The receipt must support at least these states:

- plan reviewed only, envelope not yet trusted
- envelope reviewed, guardrails incomplete
- envelope armed, runtime not yet started
- runtime started, no trip seen yet
- trip detected, abort underway
- abort completed, residue under review
- runtime completed within reviewed envelope for named slice only
- runtime contradicted reviewed envelope
- receipt superseded

## Primary sentence classes

The receipt must be able to emit at least these classes:

- `least-harm plan selected, runtime envelope not yet trusted`
- `reviewed envelope armed, stronger within-envelope sentence still blocked`
- `placeholder-only path allowed, full-hydration path blocked`
- `remembered-approval lane blocked for this action`
- `trip detected and abort initiated`
- `abort completed, residual overspill still under review`
- `within-envelope completion observed for named slice only`
- `reviewed envelope contradicted by runtime spillover`

## Hard rules

The receipt must never let later pages say:

- `execution stayed within scope`
- `nothing else was touched`
- `we could have stopped all spillover`
- `pause would have been enough`
- `all side-effects were contained`

unless the receipt actually carries the corresponding proof state.
