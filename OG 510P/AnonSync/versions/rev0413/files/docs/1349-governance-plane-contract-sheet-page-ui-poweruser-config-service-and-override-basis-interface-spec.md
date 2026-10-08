# Governance-plane contract sheet page — UI, power-user, config, service, and override basis

## Purpose

This page answers one ordinary question:

> where does this value actually live, who is allowed to mutate it, what scope does it govern, and is the current winner inherited or detached from a stronger default plane?

The page exists because visibility, mutability, precedence, and activation are not interchangeable.

## Core decision

Every serious mutable value must render one first-class **Governance-plane contract sheet**.
The page owns:

- value name
- authorship plane
- witness surface
- scope
- precedence class
- inheritance class
- activation boundary
- strongest safe sentence now

## Fixed page order

1. governance strip  
2. plane stack  
3. inheritance card  
4. activation card  
5. current witness card  
6. receipts

### 1) Governance strip

Show:

- value
- subject / scope target
- current winning value
- authorship plane: `share-ui`, `global-ui`, `advanced-ui`, `power-user`, `startup-config`, `service-storage`, `launch-switch`, `host-level`, `unknown`
- witness surface: `same-surface`, `other-surface`, `cold-plane-only`, `unknown`
- inheritance class: `live-inherited`, `manually-detached`, `config-pinned`, `service-world-owned`, `unknown`
- one honest next action

### 2) Plane stack

List all relevant planes from strongest current winner to weaker or shadowed candidates.
For each plane show:

- plane name
- candidate value
- scope
- why it does or does not currently win
- whether the current surface can edit it

The operator must be able to answer: **which plane is winning, and what lost?**

### 3) Inheritance card

This card publishes:

- whether the current value is inherited from a broader default
- whether a manual subject override severed future inheritance
- whether returning to a neutral-looking value would restore or fail to restore inheritance
- what stronger inheritance sentence is blocked

The operator must be able to answer: **is this still following the default, or did it fork?**

### 4) Activation card

Show:

- activation boundary: `live-now`, `after-rescan`, `after-app-restart`, `after-service-restart`, `after-world-shift`, `unknown`
- whether the winning plane is already active or merely saved
- what older runtime debt still survives

### 5) Current witness card

Show:

- best surface that can prove the active winner now
- weaker surfaces that only show stale or partial truth
- what proof remains missing

### 6) Receipts

Always link:

- latest governance-plane receipt
- latest activation-boundary receipt
- latest action-surface receipt if the witness surface differs from the mutation surface

## Copy rules

- Never collapse `visible here` into `editable here`.
- Never collapse `same shown value` into `same inheritance state`.
- Never collapse `saved` into `governing runtime now`.
- Never collapse `config-owned` into `ordinary preference`.