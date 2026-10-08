# Remedy-hardening-attestation postcondition-realization review page — did the mandate actually make the intended state true here?

## Purpose

This page is the operator-facing review that answers the practical realization question after executable mandate review is already good enough: given the current executable mandate, did the intended state actually become true for the intended subject and object slice, across the required worlds, and what is the strongest realization sentence the product may honestly publish now?

## Primary review prompts

The review must answer these prompts in order:

1. **What target postcondition was the mandate supposed to produce?**
2. **For which beneficiaries, objects, worlds, and topologies must that state now be true?**
3. **What observations show the state is true now, and what observations only show route activity?**
4. **Are any observations merely placeholders, metadata, or local-surface evidence rather than realized effect?**
5. **What contrary observations, rollback risks, or survivor hazards still remain?**
6. **What is the strongest realization sentence the product may honestly say now?**

## Review sections

### 1. Target-state board

Show:

- source executable-mandate receipt
- target postcondition sentence
- beneficiary slice
- governed object set
- required world and topology scope

### 2. Observation board

Show:

- current observation surfaces
- minimum observation quorum
- which surfaces show route-only evidence
- which surfaces show beneficiary-usable outcome evidence

### 3. Settlement-and-hazard board

Show:

- settlement window
- rollback or survivor hazards
- contrary observations already present
- whether the current observation is stable, provisional, or collapsing

### 4. Realization-ceiling board

The review must output one and only one primary sentence class such as:

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

## Hard rules

The review must never let an operator hide:

- an actuator log behind `the beneficiary received the effect`
- placeholder visibility behind `the object is really here and usable`
- one peer observation behind `the whole governed slice realized`
- an open rollback hazard behind `the outcome is settled`
- a contradicted observation behind `the mandate worked as intended`
