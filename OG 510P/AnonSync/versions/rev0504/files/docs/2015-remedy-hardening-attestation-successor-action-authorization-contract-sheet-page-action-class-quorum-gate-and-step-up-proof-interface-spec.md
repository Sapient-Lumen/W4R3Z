# Remedy-hardening-attestation successor action authorization contract sheet page — action class, quorum gate, and step-up proof

## Purpose

This page is the compact contract for deciding whether a successor world that already has an explicit controller roster may actually perform a named action now.
It exists so the product can distinguish `controller can exist`, `controller can act routinely`, `controller can perform this high-risk action unilaterally`, `controller needs quorum`, `controller needs fresh step-up`, `remembered approval may be reused`, and `stronger standing authorization sentence blocked`.

## Core fields

- successor-action-authorization identifier
- source successor-controller-roster receipt identifier
- successor-world identifier
- governed slice identifier
- named action identifier
- action family
- action risk class
- action blast-radius estimate
- purpose basis
- requested actor set
- currently eligible actor set
- actor-set completeness class
- authorization rulebook version
- quorum rule
- quorum satisfied state
- step-up requirement class
- step-up proof set
- approval freshness requirement
- remembered-authorization reuse state
- time window or expiry horizon
- execution ceiling if authorized
- fallback manual-review route
- strongest currently safe public sentence
- strongest blocked stronger sentence
- next fact that upgrades action standing now
- next fact that collapses action standing now

## Action families

The page must model at least these distinct families:

- read-only inspection action
- low-risk local mutation action
- write or delete action
- peer admission action
- permission-broadening action
- permission-lowering or revoke action
- key or handle issuance action
- successor-world bridge or inheritance action
- policy override or waiver action
- irreversible export or off-world release action
- emergency containment action
- action family unresolved

## Action-risk classes

The page must support at least these classes:

- routine
- sensitive
- high-risk
- emergency-but-reversible
- emergency-and-potentially-irreversible
- irreversible
- risk class unresolved

## Quorum rule classes

The page must support at least these rules:

- no action gate reviewed yet
- one eligible controller sufficient
- one eligible controller sufficient for named routine class only
- one controller plus fresh step-up proof
- two-controller quorum required
- two-controller quorum plus step-up proof required
- higher quorum required
- emergency single-controller containment allowed, broader mutation blocked
- manual out-of-band adjudication required

## Required page panels

### 1. Action summary board

Show:

- the named action
- its risk class and blast radius
- the beneficiary or affected slice
- whether this is routine, sensitive, high-risk, emergency, or irreversible

### 2. Actor-and-quorum board

Show:

- the requested actor set
- which actors are currently eligible
- whether a second controller is required
- whether quorum is satisfied now or only potentially satisfiable

### 3. Step-up board

Show:

- whether fresh step-up proof is mandatory
- what kind of proof qualifies
- whether remembered approval is allowed to substitute
- whether any prior standing authorization has expired

### 4. Execution window board

Show:

- the time window for the action if approved
- whether execution is one-shot or reusable
- whether the approval applies only to the named slice
- which broader action family remains blocked

## Hard rules

The contract sheet must never let:

- `controller exists` impersonate `controller may perform this action now`
- a narrow roster impersonate a satisfied quorum
- remembered approval impersonate fresh step-up proof
- an emergency revoke path impersonate permission-broadening authority
- link expiration and click limits impersonate action-legitimacy proof
- one successful action impersonate standing authorization for future actions
