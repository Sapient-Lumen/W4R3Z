# Evidence-retention timeline page: log rotation, repro window, and postmortem artifact survival interface spec

## Purpose

The investigation sheet answers *what is collectible now*.
This page answers the follow-on question:

> when was capture turned on, how long did the scene stay useful, what rotated away, what cleanup or restart changed the evidence set, and when did the incident stop being observable live?

## Core decision

AnonSync must require an **Evidence-retention timeline** whenever diagnostic truth depends on time-varying capture posture, rotation ceilings, cleanup events, or transition from live evidence to residue-only evidence.

## Timeline layout

1. **Current evidence banner**
2. **Evidence-event sequence**
3. **Survival / loss rail**
4. **Live-to-postmortem intervals**
5. **Blocked stronger sentence**

### 1) Current evidence banner

Show:

- current evidence posture
- entered-at time
- strongest safe sentence
- next expected rotation / cleanup / freeze event if known
- blocked stronger sentence

### 2) Evidence-event sequence

Supported events:

- `debug-requested`
- `runtime-restarted-into-debug`
- `repro-window-opened`
- `repro-window-insufficient`
- `log-size-increased`
- `log-rotated`
- `automatic-feedback-sent`
- `manual-export-completed`
- `cleanup-ran`
- `crash-occurred`
- `dump-collected`
- `runtime-stopped-for-benchmark`
- `postmortem-residue-only`
- `evidence-redacted`
- `unknown-transition`

Each event must show:

- timestamp
- cause class
- changed truths
- source evidence
- resulting strongest safe sentence

### 3) Survival / loss rail

This rail must answer:

- what evidence survived?
- what rotated away?
- what cleanup removed?
- what became stale because the repro window was too short?
- what remains only as external benchmark or operator summary?

Supported forecast states:

- `live-evidence-still-growing`
- `rotation-risk-rising`
- `current-window-still-insufficient`
- `source-grade-export-preserved`
- `cleanup-removed-current-logs`
- `postmortem-only`
- `benchmark-only-for-transport`
- `unknown`

### 4) Live-to-postmortem intervals

This section preserves periods where one optimistic sentence would be dangerously wrong, including:

- logging requested but not yet restarted
- live window too short to justify a claim
- logs rotated before export
- cleanup after export versus cleanup before export
- crash residue available but live runtime already gone
- runtime stopped for iperf, so comparative transport evidence exists while in-process evidence does not

The operator must be able to answer:

> when did this stop being a live-observation incident and become a residue-only incident?

### 5) Blocked stronger sentence

Examples:

- `We captured the whole incident` blocked because the log window was too short or rotated
- `The current logs still contain the first failure` blocked because survivorship was not proven
- `This benchmark explains the crash` blocked because the benchmark only covered transport with runtime stopped

## Hard rules

- rotation, cleanup, restart, and crash must stay distinguishable
- the timeline must never collapse `logging requested` into `logging witnessed active`
- export and redaction events must identify whether the artifact stayed source-grade
- forecast confidence must be explicit
