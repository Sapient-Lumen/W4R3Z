# Control lineage receipt page: case origin, coverage class, and blocked stronger sentences interface spec

## Purpose

The contract sheet, promotion review, activation proof, and recurrence timeline all carry detail.
What the archive still needs at handoff time is one compact durable receipt answering:

> what case created this guardrail, what class of protection does it really provide, and what stronger preventive sentence are we still not allowed to say?

## Core decision

AnonSync must emit one **Control lineage receipt** whenever a control is approved, revised, superseded, retired, or disproven by an escape.

## Required receipt fields

### Identity block

- `control_id`
- control title
- current revision
- current posture
- source case ids
- owning team or person

### Protection block

- control class
- hazard signature
- scope strength
- platform / world coverage
- activation surface
- restart / cold-apply requirement

### Truth block

- strongest safe sentence
- blocked stronger sentence
- explicit anti-claim
- confidence grade
- latest effectiveness verdict
- last rereview time

### Failure and drift block

- latest known escape class
- latest known drift class
- automatic reopen trigger
- next required review page
- retirement or successor control if any

## Supported compact verdict language

The receipt must support compact but precise verdict phrases such as:

- `preventive within Linux watcher-tuned worlds only`
- `detective-watch only; not proven preventive`
- `containment after restart-bound activation`
- `capture-on-repeat only; source case insufficient for stronger claim`
- `superseded by control <id>`
- `escaped on same-cause repeat; preventive claim withdrawn`

## Hard rules

### 1) Source-case origin stays visible forever

A control may be revised or generalized, but the receipt must always preserve the originating case ids or explicitly mark that the origin is now a merged family.

### 2) Protection class may not be rounded up

`detective-watch` must never collapse into `preventive` merely because no repeat was seen for a while.

### 3) Anti-claim is mandatory

Every receipt must preserve one explicit sentence about what the control does not protect.

### 4) Escape downgrades are durable

If a same-cause escape occurs, the receipt must preserve that downgrade even if a later revision repairs the control.
The repaired revision may earn a new stronger sentence, but the historical escape may not disappear.

### 5) Handoff must preserve the next forbidden overclaim

The receipt is not complete unless it tells the next operator what sentence would be too strong right now.
