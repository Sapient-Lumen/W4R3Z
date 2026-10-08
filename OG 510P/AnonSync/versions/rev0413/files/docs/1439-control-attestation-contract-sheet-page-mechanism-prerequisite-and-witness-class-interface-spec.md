# Control attestation contract sheet page: mechanism, prerequisite, and witness class interface spec

## Purpose

After the archive learned to promote a control, it still needed one ordinary page for the next operator question:

> why are we still allowed to trust this control now, and what kind of witness would be strong enough to keep or regain that trust?

## Core decision

AnonSync must expose one first-class **Control attestation contract sheet** for every active control that claims more than `configured but unverified`.

## Fixed page order

1. **Attestation header**
2. **Mechanism card**
3. **Prerequisite card**
4. **Witness-class card**
5. **Trust-state card**
6. **Decision sentence**

### 1) Attestation header

Show:

- control id
- source case ids
- current control class
- current trust state
- last proof time
- proof freshness deadline
- next required attestation method
- current strongest safe sentence

Supported `current_trust_state` values:

- `configured-only`
- `applied-awaiting-proof`
- `attested-live`
- `attested-by-rehearsal`
- `passively-trusted-within-window`
- `stale-needs-rereview`
- `trust-withdrawn`

Hard rule:

`active` and `trusted` may never share one badge.

### 2) Mechanism card

This card explains how the control is supposed to work.
Required rows:

- mechanism family
- control surfaces involved
- activation requirement
- world / lane scope
- expected blocking behavior
- expected failure behavior
- known bypass paths

Supported `mechanism_family` values:

- `setting-enforced`
- `multi-surface-setting`
- `config-authored`
- `service-world-posture`
- `schedule-based`
- `environment-tuning`
- `detective-only`
- `runbook-only`

Hard rule:

If a control depends on more than one surface, the card must name every required surface and whether mismatch across those surfaces is detectable.

### 3) Prerequisite card

Required rows:

- minimum version / lane
- platform or world requirement
- privilege requirement
- restart or cold-apply requirement
- discovery / network prerequisite
- storage / config-location prerequisite
- observer prerequisite

Supported `restart_requirement` values:

- `none`
- `soft-reload`
- `restart-required`
- `cold-start-required`
- `unknown-activation-cost`

Hard rule:

A missing prerequisite must downgrade the control to `configured-only` or `trust-withdrawn`; it may not remain `trusted`.

### 4) Witness-class card

This card defines what evidence is allowed to sustain trust.
Required rows:

- preferred witness class
- backup witness class
- unacceptable weak witness
- rehearsal requirement
- passive window length
- trigger that forces stronger witness

Supported `preferred_witness_class` values:

- `live-read-only-check`
- `synthetic-drill`
- `passive-no-escape-window`
- `observed-blocked-repeat`
- `paired-surface-consistency-check`
- `world-continuity-check`

Supported `unacceptable_weak_witness` examples:

- `setting-value-visible-only`
- `old screenshot`
- `single-surface readout`
- `quiet-window-with-known-drift`
- `operator memory`

Hard rule:

Every control must publish at least one witness class that is stronger than `visible setting value`.

### 5) Trust-state card

Required rows:

- why the current trust state was earned
- what would raise trust
- what would lower trust
- what event withdraws trust immediately
- what remains unprovable without a real repeat

Supported `trust_withdrawal_trigger` values:

- `version-floor-change`
- `surface-mismatch`
- `world-fork`
- `stale-proof-window`
- `prerequisite-loss`
- `same-cause-escape`
- `manual-bypass`

### 6) Decision sentence

The page must end with one sentence in this shape:

> `Control <id> is currently <trust state> because <latest valid witness>, but any <withdrawal trigger> will block the stronger sentence <claim>.`
