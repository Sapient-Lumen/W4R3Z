# Permission-apply evidence page: reference lineage, inheritance rewrite, and substrate proof interface spec

## Purpose

This page exists because later operators need proof, not folklore.
If the product says permissions came from a reference source, were re-inherited locally, or were preserved until a compatible substrate, the evidence has to be inspectable.

## Evidence families

The page should group evidence into four families:

1. **Authority evidence**
2. **Application evidence**
3. **Substrate compatibility evidence**
4. **Comparison-equation evidence**

### 1) Authority evidence

Show:

- reference seat / source epoch
- last completed settlement against that source
- whether authority is current, missing, stale, or disputed
- why a merge basis was used if no single reference exists

### 2) Application evidence

Show:

- whether permissions were applied natively, re-inherited locally, preserved for later, or dropped with receipt
- if local re-inheritance was used, what parent/root supplied the inherited permissions
- whether owner/group application succeeded or narrowed
- whether any files were blocked by insufficient rights

### 3) Substrate compatibility evidence

Show:

- local filesystem / storage class
- compatibility with the active permission mode
- deferred-apply reasons
- seats or future landings where preserved permissions are expected to become active

### 4) Comparison-equation evidence

Show:

- whether permissions are currently part of the sync-decision attributes
- the last comparison run that used or excluded them
- what policy/source caused that inclusion or exclusion

## Detailed surface

### Table A — Seat evidence

Columns:

- seat
- mode now
- authority basis
- apply class
- privilege grade
- compare participation
- evidence freshness

### Table B — Affected path samples

Columns:

- path sample
- permission outcome
- owner/group outcome
- local re-inherit basis if any
- deferred-apply marker if any
- error or narrowing

### Timeline

Show:

- reference selection / replacement
- subject recreation or epoch split
- last initial settlement or resettlement
- last privilege failure
- last substrate change that altered claim ceiling

## Safe claims this page should enable

- `Permissions on this seat are inherited locally from /Projects instead of preserved from the remote source.`
- `Permissions are preserved across this cloud seat but will only be applied on compatible NTFS landings.`
- `Reference authority is home-nas; last full permission settlement completed 2h ago.`
- `Permission differences do not currently participate in sync comparison for this subject.`

## Acceptance criteria

A later operator can:

- verify who the authority source was
- verify whether local re-inheritance happened
- verify whether the seat could apply or only preserve the plane
- verify whether permission differences were in the comparison equation
- distinguish proof from inference
