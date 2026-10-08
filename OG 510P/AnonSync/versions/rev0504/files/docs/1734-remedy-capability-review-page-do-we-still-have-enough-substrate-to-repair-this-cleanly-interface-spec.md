# Remedy-capability review page — do we still have enough substrate to repair this cleanly?

## Review question

This page answers one operator question:

> given what already changed in the world, do we still have enough surviving repair substrate to promise clean cure, partial cure, or only compensation?

## Review sections

### 1. Required repair target

State the target that would have to become true for the stronger cure sentence to be honest.
Examples:

- restore missing bytes for every required cohort
- restore prior semantic version for named claimants
- restore only access parity, not byte parity
- restore history enough for adjudication but not enough for full semantic repair

### 2. Surviving repair substrate

Review all materially distinct substrate classes:

- live source peers
- archive-backed versions
- offline peers likely to hold bytes
- placeholder-only representations
- encrypted unreadable custody
- external backup or exported copies
- audit-only traces that help adjudication but do not themselves cure the harm

### 3. Decay and collapse risks

Review all ways the apparent cure lane can weaken:

- archive TTL expiration
- version-size exclusion
- required peer staying offline too long
- placeholder-only meshes with no source peer
- platform inability to access or restore the material
- free-space threshold preventing download or patch staging
- runtime/background limits delaying the restore long enough for expiry or conflict

### 4. Honest current verdict

Return one of these verdicts:

- no cure evidence yet
- partial cure plausible
- cure-capable for named cohorts only
- cure-capable for required cohorts
- cure path armed but execution-blocked
- cure collapsed; compensation-only posture remains

## Review invariants

- the review never treats archive or placeholder presence as semantic repair by itself
- the review never hides when cure is manual-only
- the review never hides when only adjudication evidence survives but restorative bytes do not
- the review always explains what stronger cure sentence remains blocked and why
