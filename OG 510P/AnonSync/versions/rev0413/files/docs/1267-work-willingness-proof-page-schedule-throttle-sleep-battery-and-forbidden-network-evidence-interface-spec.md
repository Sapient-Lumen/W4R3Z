# Work-willingness proof page: schedule, throttle, sleep, battery, and forbidden-network evidence interface spec

## Purpose

The activity-posture sheet says what the node is currently willing to do.
This page proves *why* that sentence is safe.

## Core decision

AnonSync must require a **Work-willingness proof** whenever current behavior could be misunderstood because several different gates can produce superficially similar symptoms: slower sync, no visible peers, no downloads, or intermittent transfer.

## Proof layout

1. **Willingness headline**
2. **Evidence stack**
3. **Per-dimension verdict table**
4. **Runtime explanation sentence**
5. **Blocked stronger sentence**

### 1) Willingness headline

Show:

- subject ref
- current willingness verdict
- strongest safe sentence
- blocked stronger sentence
- proof freshness

Supported verdicts:

- `continuous-work-allowed`
- `work-allowed-under-cap`
- `download-blocked-by-policy`
- `periodic-wake-checking`
- `hard-stopped-by-power`
- `hard-stopped-by-network-policy`
- `unknown`

### 2) Evidence stack

Supported evidence classes:

- `manual-setting-evidence`
- `scheduler-slot-evidence`
- `runtime-rate-evidence`
- `sleep-cadence-evidence`
- `battery-threshold-evidence`
- `network-policy-evidence`
- `peer-visibility-evidence`
- `unknown-evidence`

Each item must show:

- source
- timestamp
- scope
- confidence
- which dimensions it governs

The operator must be able to answer:

> what makes us believe this node is slow, paused, asleep, or forbidden, instead of merely idle?

### 3) Per-dimension verdict table

Each row must show:

- dimension (`visibility`, `detection`, `upload`, `download`, `delete-propagation`, `budget`)
- current verdict
- governing evidence
- freshness
- uncertainty note

### 4) Runtime explanation sentence

This section must emit one exact sentence reusable across surfaces.
Examples:

- `Downloads are currently blocked by a scheduler rule, but discovery and delete propagation remain active.`
- `This device is asleep between wake checks; peers should not expect continuous visibility.`
- `Transfers are stopped because the current network is forbidden for this share.`
- `Traffic is limited only on Internet paths; LAN paths remain uncapped.`

### 5) Blocked stronger sentence

Examples:

- `The app is offline` blocked because it is merely waiting in a sleep interval and will wake automatically
- `This share cannot upload` blocked because only download is gated
- `No more change detection will occur` blocked because periodic wake checks remain active
- `The current speed cap explains all slow traffic` blocked because LAN paths are exempt

## Hard rules

- the proof must always separate cause from symptom
- `idle` may not be conflated with `gated`
- a hidden-from-peers state must state whether this is due to sleep, network policy, or loss of reachability
- every proof must preserve what remains uncertain about actual runtime semantics
