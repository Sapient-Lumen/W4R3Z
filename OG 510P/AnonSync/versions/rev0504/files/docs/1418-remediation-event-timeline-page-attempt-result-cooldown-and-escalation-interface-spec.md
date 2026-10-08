# Remediation-event timeline page: attempt, result, cooldown, and escalation interface spec

## Purpose

The **Remediation-event timeline** preserves what happened across intervention attempts.
It exists because operators otherwise remember the storyline as folklore:

- we restarted something
- then it looked better
- then a warning came back
- then someone re-added a folder
- then logs were captured
- then support said something different

AnonSync should preserve this as typed intervention history instead.

## Core operator question

> what interventions have already been tried, what changed after each one, what cooldowns or proof windows were respected, and when did we move to a higher ladder rung?

## Required event types

The timeline must support at least:

- `observe-window-started`
- `observe-window-ended`
- `intervention-approved`
- `intervention-started`
- `intervention-finished`
- `post-action-check-passed`
- `post-action-check-partial`
- `post-action-check-failed`
- `cooldown-started`
- `cooldown-ended`
- `retry-authorized`
- `rollback-started`
- `rollback-finished`
- `escalation-artifact-captured`
- `human-escalation-opened`
- `human-escalation-updated`
- `stronger-sentence-unblocked`
- `stronger-sentence-restill-blocked`

## Fixed page order

1. **Intervention ladder history strip**
2. **Attempt ledger**
3. **Cooldown and retry panel**
4. **Escalation and artifact panel**
5. **Sentence-change panel**

### 1) Intervention ladder history strip

Show each rung entered over time.
For every rung show:

- entry time
- trigger
- chosen action
- exit state

### 2) Attempt ledger

Each intervention attempt row must show:

- attempt number
- action class
- exact scope touched
- who executed it
- whether restart was involved
- immediate result
- observation window promised
- final adjudicated result

### 3) Cooldown and retry panel

The product must preserve whether operators honored cooldown before retrying.
Show:

- cooldown reason
- required wait window
- actual wait window
- retry eligibility verdict
- whether retry repeated same action or advanced the ladder

### 4) Escalation and artifact panel

Rows must include:

- artifact class
- capture basis
- reproduction basis
- freshness at capture
- escalation target
- outcome / response summary
- whether artifact changed the preferred action

### 5) Sentence-change panel

This panel is mandatory.
For each intervention boundary, preserve:

- sentence before action
- sentence after immediate effect
- sentence after observation window
- stronger sentence unblocked
- stronger sentence still blocked

## Hard rules

- the timeline must distinguish `attempted` from `adjudicated successful`
- repeated identical attempts must be visible as repeats, not quietly merged
- escalations without sufficient artifact basis must be marked as weak escalations
- a temporary quiet period must not be auto-recorded as durable recovery
