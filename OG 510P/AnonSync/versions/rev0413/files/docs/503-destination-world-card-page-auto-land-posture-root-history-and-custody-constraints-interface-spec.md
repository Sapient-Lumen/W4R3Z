# Destination world card page — auto-land posture, root history, and custody constraints interface spec

## Purpose

`502` defines the full picker.
This document defines the portable summary object that keeps destination-world truth visible in lists, workbench rails, and side panels.

The card exists to answer one ordinary question:

> what kind of world is this, and why should I trust or avoid landing an arrival here?

## Core rule

Every world that can receive imported material must have one reusable **Destination world card**.
That card is the semantic home of:

- arrival posture
- root-history summary
- bind-lane availability
- strongest custody or duplicate warning

The card must not degrade to a mere seat name plus path string.

## Required card fields

### Identity and placement

Show:

- seat label
- world label / world ID when available
- host/device summary
- current runtime profile if it affects destination truth

### Posture and lane

Show:

- arrival posture (`announce-only`, `manual bind`, `auto-land default`, `remembered continuity`, `ciphertext custody`)
- whether manual path choice is available
- whether remembered-root reuse is available
- whether this world currently has a pending reroute or interruption review

### Root history

Show:

- standing default root
- last successful remembered root when relevant
- whether the current root draft came from standing policy, remembered continuity, or operator override
- whether duplicate-name fallback has ever occurred here

### Strongest warning

Show one strongest honest warning such as:

- `auto-land will use default root`
- `remembered root proof stale`
- `manual path unavailable on this surface`
- `ciphertext-only destination`
- `fresh empty root required`
- `duplicate-risk if left on default`

### Next honest action

Allowed primary actions include:

- `Choose world`
- `Inspect root history`
- `Reroute this arrival`
- `Review custody admission`
- `Keep unplaced`

## Card states

Use a small stable vocabulary:

- `safe manual candidate`
- `safe remembered-root candidate`
- `default-world caution`
- `ciphertext-only candidate`
- `blocked for this artifact`
- `proof stale`

## Expanded detail pane

Opening a card should reveal five mini-sections.

### 1) World summary

- world label
- posture
- bind-lane availability
- last verified time

### 2) Root lineage

- standing root
- remembered roots
- last chosen override
- strongest drift or duplicate indicator

### 3) Capability and custody constraints

- plaintext or ciphertext ceiling
- write ceiling
- decrypt ceiling
- special branch requirements

### 4) Current risks

- duplicate-name risk
- wrong-world risk
- stale remembered-root proof
- missing manual-path affordance

### 5) Recent receipts

- latest destination-choice receipt
- latest reroute receipt
- latest custody-admission receipt when applicable

## Narrow-width behavior

In narrow width the card may compress root history, but it may not hide:

- posture
- bind-lane availability
- strongest warning
- next honest action

## Acceptance criteria

This spec is satisfied when:

- operators can compare candidate worlds without opening multiple deep pages
- auto-land worlds and manual worlds remain visibly distinct
- encrypted-custody worlds remain visibly incompatible with ordinary plaintext expectations
- root history and duplicate risk remain adjacent
- the card always points to the next truthful review instead of pretending the decision is already settled
