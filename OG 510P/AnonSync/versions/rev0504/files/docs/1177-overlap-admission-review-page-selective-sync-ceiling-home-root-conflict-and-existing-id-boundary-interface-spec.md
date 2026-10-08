# Overlap admission review page: selective-sync ceiling, home-root conflict, and existing-ID boundary interface spec

## Purpose

This page answers one ordinary question:

> is this overlap even admissible here, or does a hidden boundary already make the larger claim false or unsafe?

The page exists because `folder exists`, `folder is non-empty`, `folder is disconnected`, `folder already has this ID`, and `folder contains another syncing interior` are not the same truth.

## Core decision

Every serious overlap-admission attempt must open one first-class **Overlap admission review**.

The review owns:

- requested claim
- existing interior boundary
- ID collision class
- selective-sync ceiling
- reconnect class
- apply verdict

## Fixed page order

1. admission request header
2. existing-boundary card
3. materialization eligibility card
4. reconnect and non-empty card
5. apply verdict

### 1) Admission request header

Show:

- requested root or child path
- requested action (`add-parent`, `add-child`, `reconnect-existing`, `claim-home-root`, `other`)
- strongest safe sentence
- stronger rejected sentence

### 2) Existing-boundary card

Show:

- `.sync/ID` presence class
- same-path already-added risk
- same-key other-path risk
- contains-existing-subject risk
- interior service/license material risk
- resulting boundary verdict (`fresh`, `same-subject collision`, `contains-subject`, `blocked by service interior`, `unknown`)

### 3) Materialization eligibility card

Show:

- parent selective-sync posture
- child selective-sync posture
- nested-overlap eligibility verdict
- explicit note if nested admission requires selective-sync disabled on both sides

### 4) Reconnect and non-empty card

Show:

- whether the target path is already populated
- whether explicit confirmation is required
- whether the action is `reconnect to existing material` rather than `fresh empty bind`
- strongest blocked sentence if hash/merge proof is not yet available

### 5) Apply verdict

Possible outcomes:

- `apply overlap admission`
- `apply reconnect-to-existing with confirmation`
- `block; same-ID collision`
- `block; contains-existing-subject interior`
- `block; nested overlap disallowed under selective materialization`
- `cancel and reopen contract sheet`

## Rules

### Rule 1 — path availability must not impersonate admissibility

A pickable path is weaker than permission to claim it as one subject boundary.

### Rule 2 — same-ID collision and contains-existing-subject conflict stay separate

The page must distinguish `this is already that subject` from `this larger root would swallow a different subject interior`.

### Rule 3 — reconnect confirmation and merge proof stay separate

Confirming a non-empty destination is weaker than proving safe convergence.
