# Finish setup page: readiness ladder, reachability proof, and attestation interface spec

## Purpose

`240` established the semantic contract for installation and first-run readiness.
This document makes it concrete as one page.

The page exists to answer one ordinary operator question:

> is this seat merely installed, or is it actually trusted, started, reachable, and safe to use, and what exact blocker remains if not?

## Core decision

Every fresh install, service promotion, or major reinstall must expose one first-class **Finish setup** page.
That page is the semantic home of:

- package trust
- OS and system-consent gates
- runtime readiness
- control reachability
- network exposure
- install receipts and remaining blockers

## Primary page layout

The page always renders the same top-level regions in the same order:

1. readiness ladder header
2. package trust card
3. consent gates card
4. runtime state card
5. reachability and exposure card
6. remaining blockers list
7. completion receipt

### 1) Readiness ladder header

The header shows the current rung on an explicit ladder:

- `package obtained`
- `package trusted`
- `installed`
- `runtime started`
- `control reachable`
- `ready`

The header also names the single strongest blocker if the seat is not yet ready.

### 2) Package trust card

Show:

- package source
- signature / package verification result
- whether the OS raised a trust or reputation warning
- whether the operator bypassed such a warning
- package version and channel

A bypassed OS warning must remain visible here even after the install succeeds.

### 3) Consent gates card

Show the current state of:

- elevation or installer privilege
- service registration
- firewall / listener consent
- protocol or shell registration if relevant
- any pending OS restart or login requirement

Each row should say `granted`, `denied`, `skipped`, `not needed`, or `still pending`.

### 4) Runtime state card

Show one explicit runtime verdict:

- `installed only`
- `installed and starting`
- `started but not initialized`
- `started with degraded readiness`
- `ready`

This card should also show the current seat identity and runtime owner.

### 5) Reachability and exposure card

Show:

- whether local control is reachable now
- whether any listeners are open
- exposure scope of each listener
- whether share/join actions are safe now
- whether trust is degraded even though reachability exists

This card is where install, reachability, and trust finally meet without being conflated.

### 6) Remaining blockers list

If the seat is not ready, list blockers in strict execution order.
Each blocker row shows:

- blocker class
- why it matters
- exact action needed
- whether the product can perform it directly or must hand off to the OS
- what stronger ladder rung it unlocks

### 7) Completion receipt

When the seat becomes ready, emit a receipt that records:

- package trust result
- OS warnings encountered or bypassed
- consent-gate outcomes
- runtime readiness at completion
- local control reachability result
- remaining caveats, if any

## Page entry points

The page must be reachable from:

- first run
- service promotion or migration
- update flows that materially change listeners or trust posture
- settings when the seat is degraded or incomplete
- startup diagnostics when a seat is installed but not participating

## Acceptance criteria

This spec is satisfied when:

- `installed` and `ready` are never conflated
- OS trust warnings remain visible after installation rather than disappearing into lore
- the operator can see exactly what rung blocks readiness
- local control reachability and network exposure are visible before the seat invites participation
- completion emits one product-owned attestation receipt
