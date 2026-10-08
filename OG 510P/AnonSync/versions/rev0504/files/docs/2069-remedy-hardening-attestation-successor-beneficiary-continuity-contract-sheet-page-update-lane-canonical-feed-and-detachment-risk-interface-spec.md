# Remedy-hardening-attestation successor beneficiary-continuity contract sheet page — update lane, canonical feed, and detachment risk

## Purpose

This page is the operator-facing sheet for deciding whether a beneficiary who already holds a durable copy also remains attached to the canonical future-correction lane for that result.
It exists to prevent `downloaded once`, `kept a local copy`, or `still has the folder on disk` from being mistaken for `will keep receiving future fixes, supersessions, and withdrawals`.

## Core question

The page must answer:

**does the named beneficiary remain enrolled in the canonical successor update lane for this result, or are they now holding only a detached snapshot, diverged local copy, or reconnect-later residue?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-custody receipt identifier
- named beneficiary identifier
- intended continuity class
- canonical source or successor lane identifier
- current enrollment state
- detached-snapshot versus live-subscription state
- future-fix and supersession reach state
- withdrawal or recall reach state
- local divergence or stop-updating risk state
- reconnect, path-rebind, or topology sensitivity summary
- forwardability or onward-fork summary
- strongest honest continuity sentence now
- blocked stronger continuity sentence now

## Standing ladder

The page must support at least these distinct standings:

- beneficiary custody proved, continuity still unproven
- detached snapshot only
- continuity available only through manual reconnect or rebind
- live lane present, but local-share or topology fragility remains
- live lane present, but local divergence can stop later updates for named files
- canonical future-update lane for named slice only
- canonical future-update plus withdrawal reach for named slice only
- continuity later narrowed by disconnect, divergence, supersession, or contradiction
- receipt superseded

## Required comparisons

The sheet must compare:

- beneficiary-custody standing versus beneficiary-continuity standing
- intended continuity class versus actual enrollment state
- durable possession versus live future-update reach
- expected canonical lane versus actual source or share relation
- expected withdrawal reach versus actual recall or supersession reach
- expected no-surprise continuity versus actual detachment or divergence hazards

## Required layout

### Header

Show:

- action name
- beneficiary name
- continuity posture
- enrollment badge
- strongest honest sentence now

### Left column — intended continuity

Show:

- named beneficiary
- intended continuity class
- expected canonical source or lane
- expected future-fix and withdrawal reach
- forbidden substitute states

### Right column — actual current continuity

Show:

- current enrollment state
- detached-snapshot versus live-subscription state
- current supersession and withdrawal reach
- divergence and stop-updating hazards
- reconnect, path, topology, or onward-fork summary
- whether the beneficiary is subscribed, detached, or only reconnectable later

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- durable copy only
- detached snapshot only
- reconnectable later but not live now
- live lane with fragility
- canonical future-update lane for named slice only
- stronger continuity sentence still blocked
