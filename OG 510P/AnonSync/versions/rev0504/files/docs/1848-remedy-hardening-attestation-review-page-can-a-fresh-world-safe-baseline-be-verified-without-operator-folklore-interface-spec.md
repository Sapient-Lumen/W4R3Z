# Remedy-hardening-attestation review page — can a fresh-world-safe baseline be verified without operator folklore?

## Purpose

This page is the operator's decision surface for answering whether a case that already has a bootstrap-reproducible hardened baseline may honestly claim independent verifier readiness.
It exists so later readers can review attestation quality directly rather than reconstructing it from UI calm, short history, logs, and support steps.

## Review question

The page must ask:

`Could a later verifier or successor operator inspect one durable bundle and honestly confirm the strongest supported hardening sentence without relying on current-world folklore?`

## Required review panes

### 1. Evidence-bundle pane

Show:

- attestation bundle identifier
- bundle generation time
- evidence freshness horizon
- evidence expiry horizon
- whether the bundle contains scars and blocked stronger sentences
- strongest blocked stronger sentence caused by missing or stale bundle contents

### 2. Provenance pane

Show:

- history-horizon sufficiency status
- log provenance status
- log capture mode status
- storage snapshot status
- startup-config snapshot status
- rebuild-proof inclusion status
- operator-memory dependence status
- strongest blocked stronger sentence caused by provenance weakness

### 3. Coverage pane

Show:

- folder-type coverage status
- platform and version lane coverage status
- required verifier cohort
- named attestation audience
- successor-handoff readiness status
- whether named-lane attestation is being mistaken for required-cohort attestation

### 4. Claim-ceiling pane

Show:

- current remedy-hardening-attestation posture rung
- highest honest current verifier-ready sentence
- strongest blocked stronger verifier-ready sentence
- next strengthening trigger
- next weakening trigger
- whether the current claim survives a fresh reviewer who lacks current operator memory

## Required review outcomes

The page must support outcomes such as:

- `safe and reproducible, but not yet independently verifier-ready`
- `verifier-ready only for named lanes or within named freshness bounds`
- `successor handoff is honest, but third-party-ready attestation remains blocked`
- `the evidence bundle is too current-operator-shaped for the stronger sentence`
- `the case is independently verifier-ready for the required cohort with scars preserved`

## Review discipline

The review must forbid these shortcuts:

- calm UI equals verifier-ready claim
- history exists equals durable attestation
- logs collected equals adequate provenance
- storage copy equals invariant bundle
- support workflow completed equals independent verification
- bootstrap reproducibility equals verifier readiness
- one successor handoff equals required-cohort independent attestability
