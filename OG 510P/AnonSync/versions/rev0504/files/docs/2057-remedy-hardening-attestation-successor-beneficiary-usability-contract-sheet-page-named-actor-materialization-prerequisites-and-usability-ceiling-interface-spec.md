# Remedy-hardening-attestation successor beneficiary-usability contract sheet page — named actor, materialization prerequisites, and usability ceiling

## Purpose

This page is the operator-facing sheet for deciding whether a landed reviewed result is actually usable by the named beneficiary in the intended way.
It exists to prevent `landed somewhere in the mesh`, `visible in the tree`, or `represented by a placeholder` from being mistaken for `usable by the person or system that needs it`.

## Core question

The page must answer:

**can the named beneficiary actually perform the intended action on the landed result now, from the intended world, with the required bytes, permissions, handlers, and update posture?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- execution-run identifier
- source outcome-conformance receipt identifier
- named beneficiary identifier
- intended beneficiary action class
- intended usable-result class
- required world or seat
- current materialization state
- online-source dependency state
- shell or handler dependency state
- access-permission state
- update-receipt state
- path, encoding, lock, and filesystem blocker summary
- strongest honest usable sentence now
- blocked stronger usable sentence now

## Standing ladder

The page must support at least these distinct standings:

- reviewed result landed elsewhere; beneficiary has no local usable object yet
- beneficiary sees folder or file name only
- beneficiary has placeholder or disconnected representation only
- beneficiary can fetch, but only while a source peer remains online
- beneficiary has bytes locally, but handler or shell path is blocked
- beneficiary has bytes locally, but access or update posture is degraded
- beneficiary can read or open only
- beneficiary can read and modify only within a named slice or limited mode
- beneficiary can use result as intended for named slice only
- beneficiary-usable sentence later narrowed by contradiction
- receipt superseded

## Required comparisons

The sheet must compare:

- landed result class versus beneficiary-usable result class
- intended beneficiary action versus currently possible action
- expected self-sufficiency versus online-source dependency
- expected ordinary affordance versus shell or handler workaround requirement
- expected live-updating copy versus degraded or no-update posture
- expected acceptable path/encoding/filesystem state versus actual blocker set

## Required layout

### Header

Show:

- action name
- beneficiary name
- usability posture
- materialization badge
- strongest honest sentence now

### Left column — intended use

Show:

- named beneficiary
- intended action class
- intended usable-result class
- required world, seat, or host
- forbidden substitute states

### Right column — actual present useability

Show:

- actual materialization state
- source dependency state
- shell or handler state
- access and update state
- blocker summary
- whether the beneficiary can currently read, open, modify, or only inspect metadata

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- result landed
- result visible only
- placeholder present
- bytes retrievable if source appears
- bytes local but blocked
- bytes local and beneficiary-usable now
