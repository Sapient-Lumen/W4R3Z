# Control decay timeline page: version drift, world fork, missed check, and trust loss interface spec

## Purpose

After a control is promoted and possibly rehearsed, the product still needs one durable page for the evidence that weakens trust over time:

> what changed that made this control weaker, stale, or unsafe to overclaim, even if no user-visible incident has happened yet?

## Core decision

AnonSync must expose one first-class **Control decay timeline** for every control that can lose trust through time, drift, bypass, missed review, or world transition.

## Fixed page order

1. **Timeline header**
2. **Trust-history stream**
3. **Decay event card**
4. **Automatic downgrade ladder**
5. **Recovery path card**
6. **Reopen hooks**

### 1) Timeline header

Show:

- control id
- current trust state
- current strongest safe sentence
- last valid proof
- next freshness deadline
- current decay pressure level

Supported `current_decay_pressure_level` values:

- `none`
- `watching`
- `freshness-risk`
- `drift-observed`
- `trust-withdrawn`
- `superseded`

### 2) Trust-history stream

Each row must include:

- event time
- event class
- impacted scope
- old trust state
- new trust state
- withdrawn claim if any
- linked proof or case id

Supported `event_class` values:

- `attestation-passed`
- `passive-window-renewed`
- `rehearsal-passed`
- `freshness-expired`
- `version-floor-changed`
- `surface-mismatch-found`
- `world-fork-created`
- `prerequisite-lost`
- `manual-bypass`
- `same-cause-escape`
- `superseded`

### 3) Decay event card

When the selected timeline row is a decay event, show:

- decay source
- first observed signal
- affected subjects / worlds
- whether the old proof remains partially valid
- whether a case or rollout must reopen
- weakest surviving sentence

Supported `decay_source` values:

- `version-drift`
- `service-or-config-world-fork`
- `desktop-mobile-lane-mismatch`
- `stale-proof-window`
- `setting-ignored-or-deprecated`
- `cached-behavior-persisted`
- `ownership-gap`

### 4) Automatic downgrade ladder

The page must preserve this downgrade order:

1. `passively-trusted-within-window`
2. `stale-needs-rereview`
3. `trust-withdrawn`
4. `configured-only`
5. `retired-or-superseded`

Hard rule:

A control may skip to a lower rung when a severe event occurs, but the skipped rungs must remain visible as history.

### 5) Recovery path card

Required rows:

- next acceptable witness
- whether a rehearsal is mandatory
- whether a case must reopen first
- scope that can recover sooner than the rest
- what stronger sentence can return after recovery

### 6) Reopen hooks

Each hook must show:

- trigger description
- reopened object (case / control / rollout / profile)
- automatic vs manual reopen
- first required review page
- sentence withdrawn immediately

Hard rule:

A missed attestation window with known drift risk must withdraw the stale stronger sentence automatically.
