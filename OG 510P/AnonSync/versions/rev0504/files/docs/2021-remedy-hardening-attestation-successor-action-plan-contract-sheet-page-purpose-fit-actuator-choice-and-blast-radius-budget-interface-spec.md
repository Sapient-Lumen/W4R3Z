# Remedy-hardening-attestation successor action-plan contract sheet page — purpose fit, actuator choice, and blast-radius budget

## Purpose

This page is the compact contract for deciding whether a successor-world action that is already authorized is being pursued through the narrowest legitimate actuator.
It exists so the product can distinguish `action may happen`, `this lane is convenient`, `this lane is narrow enough`, `this lane overreaches the beneficiary slice`, `a safer alternative exists`, and `stronger least-harm sentence blocked`.

## Core fields

- successor-action-plan identifier
- source successor-action-authorization receipt identifier
- successor-world identifier
- governed slice identifier
- named action identifier
- purpose basis
- beneficiary slice identifier
- required outcome summary
- candidate actuator set
- chosen actuator family
- chosen actuator identifier
- actuator scope class
- expected spread set
- expected persistence horizon
- forwardability class
- auto-expansion exposure
- approval or step-up burden inherited from source authorization
- reversibility class
- rollback complexity class
- expiry or use-budget class
- alternative narrower actuator set
- alternative broader actuator set
- least-harm assessment state
- strongest currently safe public sentence
- strongest blocked stronger sentence
- next fact that upgrades plan standing now
- next fact that collapses plan standing now

## Actuator families

The page must model at least these families:

- linked-device automatic spread
- manual folder share by link or QR
- manual Standard-key detour
- manual Advanced-folder share
- one-time single-file transfer
- same-device local share
- config-mode multi-machine rollout
- reconnect existing folder path
- read-only actuator
- read-write actuator
- owner-grant actuator
- actuator family unresolved

## Scope classes

The page must support at least these classes:

- object-only
- named subfolder only
- named folder only
- named peer only
- named linked-device subset only
- all linked devices
- named estate slice only
- estate-wide or multi-machine rollout
- scope unresolved

## Least-harm assessment states

The page must support at least these states:

- actuator unreviewed
- chosen actuator appears narrower than known alternatives
- chosen actuator is one acceptable narrow option among equals
- safer narrower actuator exists
- chosen actuator broader than purpose requires
- chosen actuator broader for convenience only
- chosen actuator proportionate only because emergency exception applies
- proportionality unresolved

## Required page panels

### 1. Outcome board

Show:

- the required outcome
- the beneficiary slice
- whether the outcome needs bytes, standing access, ongoing sync, or one-time transfer
- whether persistence is required or temporary access is sufficient

### 2. Candidate actuator board

Show:

- all known candidate actuators
- which are narrower, broader, or incomparable
- which need manual detours
- which auto-expand to more devices, peers, or future arrivals

### 3. Blast-radius board

Show:

- expected spread set for the chosen actuator
- onward-sharing or forwarding exposure
- expected persistence and discoverability horizon
- rollback and revocation difficulty

### 4. Narrower-alternative board

Show:

- the best known narrower actuator
- why it does or does not satisfy the required outcome
- whether the broader actuator is chosen for necessity or convenience
- what stronger least-harm sentence remains blocked

### 5. Sentence chooser

The contract must be able to emit one and only one primary sentence class such as:

- action authorized, actuator family unreviewed
- one-time transfer sufficient, broader sync blocked
- read-only narrow lane available, broader write lane blocked
- local-only actuator sufficient, remote share blocked
- linked-device spread broader than purpose requires
- chosen actuator proportionate for named slice only
- emergency broader actuator tolerated temporarily
- stronger least-harm sentence blocked

## Hard rules

The contract must never let an operator hide:

- a broad linked-device lane inside `it was the easiest path`
- folder-level spread inside `the user only needed one file`
- estate-wide rollout inside `same setting anyway`
- a forwardable link inside `temporary access`
- convenience choice inside `no safer alternative existed`
