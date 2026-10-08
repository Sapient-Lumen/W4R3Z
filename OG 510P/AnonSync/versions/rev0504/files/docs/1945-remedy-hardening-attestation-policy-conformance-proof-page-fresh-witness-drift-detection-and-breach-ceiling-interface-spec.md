# Remedy-hardening-attestation policy-conformance proof page — fresh witness, drift detection, and breach ceiling

## Purpose

This page is the evidence-heavy proof surface for present-time conformance claims after rollout.
It proves the exact ceiling on any sentence that tries to say a deployed policy is still governing the named estate slice now.

## Required evidence blocks

### 1. Source rollout basis

Preserve:

- source rollout receipt and class
- original deployment scope
- last trusted conformance receipt
- reason present recertification is required now

### 2. Fresh conformance witness ledger

For each claimed population preserve:

- witness kind
- witness timestamp
- exact population covered
- whether the witness proves present conformance, only historical deployment, or only partial slice coverage
- recertification horizon implied by that witness

### 3. Drift and delta ledger

Preserve:

- manual overrides or newly divergent settings
- new arrivals whose inherited coverage is unproven
- service-world or principal-world splits
- reconnect or path-fork events
- delayed-detection or rescan-sensitive evidence
- resulting downgrade or suspicion class

### 4. Breach, containment, and repair ledger

Preserve:

- every confirmed breach
- exact scope of impact
- containment adequacy
- repair owner and due time
- repair already applied versus still pending
- whether recertification after repair has happened yet

### 5. Claim ceiling

Render:

- highest honest current conformance sentence
- highest honest current containment sentence
- highest honest whole-slice still-governing sentence
- blocked stronger sentence and exact blocker

## Evidence classes

The page must distinguish at least:

- rollout only
- fresh partial conformance proof
- fresh named-slice conformance proof
- inherited coverage incomplete
- recertification overdue
- suspected drift only
- confirmed breach with containment
- confirmed breach without containment
- repair applied pending recertification
- restored conformance after recertification
- broader still-governing sentence blocked

## Hard rules

The proof page must never treat:

- an old rollout artifact as proof of present conformance by itself
- one fresh witness as proof for uncovered populations
- `current ones remain as they are` semantics as if they proved older objects comply
- a service migration as invisible continuity by default
- repair intent as proof of restored conformance
