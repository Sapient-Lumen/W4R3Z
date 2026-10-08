# Link target boundary page — reference preservation, target exclusion, and follow blocking

## Purpose

Make the reference-object versus target-object boundary unmissable.

This page exists because preserving a symbolic link object and syncing its target are different commitments.
A product that blurs them invites silent over-sharing, missing data, or false completion claims.

## Required sections

### 1. Reference object section

Must show:

- link path
- link payload / target witness if locally readable
- whether the reference object itself is being preserved
- whether preserving it is cohort-safe

### 2. Target boundary section

Must show:

- whether the target is inside the same subject, outside it, unknown, or unavailable
- whether following the target would cross subject/audience boundaries
- whether target adoption requires a separate reviewed action

### 3. Follow posture

Allowed postures:

- `preserve-reference-only`
- `preserve-reference-and-review-target-separately`
- `do-not-preserve-reference`
- `blocked-due-to-cross-boundary-risk`

The interface must not allow a silent `follow target` default.

### 4. Propagation warning

Must show when any of the following are true:

- target is not included and peers may see only the reference object
- Windows peers may conflict on the object class
- current settings suppress symbolic-link syncing entirely

### 5. Receipt fields

Must preserve:

- reviewed reference object verdict
- reviewed target verdict
- whether target follow was intentionally rejected
- blocked stronger sentence such as `the referenced data is included here`
