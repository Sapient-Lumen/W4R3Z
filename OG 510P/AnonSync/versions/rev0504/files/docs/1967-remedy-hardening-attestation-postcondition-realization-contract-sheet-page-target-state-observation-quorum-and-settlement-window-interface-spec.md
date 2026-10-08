# Remedy-hardening-attestation postcondition-realization contract sheet page — target state, observation quorum, and settlement window

## Purpose

This page is the compact contract for deciding whether a verdict that is already executable has actually produced the intended state for the intended slice.
It exists so the product can distinguish `mandate routed only`, `target postcondition not yet observed`, `named-slice postcondition observed`, `observation contradicted`, `settlement window still open`, `governed-slice postcondition realized`, and `broader stronger sentence blocked`.

## Core fields

- postcondition-realization identifier
- source executable-mandate receipt identifier
- governing mandate sentence
- target postcondition sentence
- beneficiary slice identifier
- governed object set identifier
- required world and topology scope
- minimum observation quorum
- observation surface set identifier
- outcome witness class summary
- placeholder-or-metadata-only flag
- contrary observation flag
- settlement window identifier or duration
- rollback or survivor hazard inventory
- current postcondition-realization class
- highest currently safe realization sentence
- strongest blocked stronger sentence
- next fact that upgrades realization standing now
- next fact that collapses realization standing now

## Postcondition-realization classes

The page must model at least these distinct classes:

- mandate routed only
- target postcondition not yet observed
- target postcondition observed on route-local surface only
- target postcondition observed for named slice only
- target postcondition observed, but placeholder or metadata only
- target postcondition observed, but contrary evidence also present
- target postcondition observed, settlement window open
- rollback or survivor hazard dominates
- postcondition realized for governed slice
- broader stronger realization sentence blocked

## Outcome witness classes

The page must support at least these witness classes:

- actuator-fired witness only
- local-state witness
- remote-state witness
- byte-presence witness
- permission-enforcement witness
- beneficiary-can-act witness
- contradiction witness
- rollback witness

## Fixed rendering order

Every postcondition-realization contract sheet must render the same sections in the same order:

1. **Highest currently realization-safe sentence**
2. **Target postcondition, beneficiary slice, and governed object set**
3. **Observation quorum, witness classes, and current contrary evidence**
4. **Settlement window, survivor hazards, and current realization class**
5. **Next fact that upgrades or collapses realization standing**

## Hard rules

The contract sheet must never let an operator hide:

- route execution behind `the outcome landed`
- folder visibility behind `the bytes are present`
- placeholder presence behind `the beneficiary can actually act on the object`
- one-world observation behind a broader governed-slice sentence
- an open settlement window behind `the result is done`
