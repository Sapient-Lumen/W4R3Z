# Evidence-capture review page: live repro, log window, redaction, and safe-freeze boundary interface spec

## Purpose

The investigation sheet says what lanes and artifact classes exist.
This page reviews the narrower operator question:

> what exact capture plan should I run now, what must stay live, what must be stopped, how long must I wait, and when should I freeze the scene before evidence is lost or contaminated?

## Core decision

AnonSync must require an **Evidence-capture review** whenever the operator is about to turn on logging, reproduce an issue, export a bundle, clean up residue, or switch from live runtime evidence to postmortem evidence.

## Review layout

1. **Capture plan header**
2. **Live-vs-stopped decision card**
3. **Window and survivorship card**
4. **Redaction and sharing card**
5. **Freeze boundary and next actions**

### 1) Capture plan header

Show:

- incident ref
- current capture mode
- recommended next artifact class
- strongest safe sentence
- blocked stronger sentence
- review freshness

Supported capture modes:

- `observe-live-runtime`
- `reproduce-under-logging`
- `export-current-logs`
- `collect-post-crash-residue`
- `run-runtime-stopped-benchmark`
- `freeze-before-cleanup`
- `capture-plan-unknown`

### 2) Live-vs-stopped decision card

This card must keep these situations separate:

- Sync must remain running to catch the symptom in logs
- Sync should be restarted first so logging is truly active
- Sync must be stopped before the chosen benchmark is meaningful
- Sync should remain untouched because post-crash residue is the key artifact
- cleanup must not happen yet

High-surprise callouts must include:

- `Requested logging is weaker than witnessed active logging.`
- `A transport benchmark with runtime stopped does not prove in-process behavior.`
- `Cleanup can destroy the very logs you are trying to preserve.`

### 3) Window and survivorship card

Show these truths separately:

- minimum live window requested
- actual live window observed
- current rotation ceiling
- current cleanup threat
- whether export should happen before another reproduce attempt
- whether service-account or NAS path indirection remains unresolved

The operator must be able to answer:

> how long do I need to let this run, and what might disappear before I get there?

### 4) Redaction and sharing card

Action rows must include:

- `export as-is`
- `review for path / peer / address identifiers`
- `strip operator note only`
- `restrict to local receipt`
- `send through entitled lane`
- `share only derived summary`

Each row must show:

- expected information exposure
- evidence loss risk
- receiver class
- whether the resulting artifact remains support-grade or summary-only

### 5) Freeze boundary and next actions

The freeze boundary exists to stop evidence loss.
This section must say when the operator should freeze the scene before doing any of the following:

- restarting again
- turning cleanup on
- disabling logging
- rotating to a larger log size
- exporting from another account path
- running an offline benchmark

Actions must include:

- `freeze and export current evidence`
- `restart into witnessed logging posture`
- `wait for longer reproduction window`
- `collect postmortem dumps`
- `switch to offline benchmark lane`
- `defer sharing until redaction review`

## Hard rules

- capture review must focus on evidence integrity, not generic troubleshooting advice
- the product may not suggest cleanup until it has disclosed what evidence cleanup can erase
- live runtime and stopped-runtime capture plans must remain visibly incompatible when they are
- redaction review must show when the artifact becomes summary-only rather than source-grade
