# Remedy-preservation review page — is the repair material actually protected now?

## Review question

This page answers one operator question:

> even if clean cure is still possible today, has the system actually protected the needed repair substrate from ordinary decay, cleanup, or displacement long enough for honest repair?

## Review sections

### 1. Preservation target

State exactly what must remain protected for the stronger preservation sentence to be honest.
Examples:

- one complete prior version for every required cohort
- at least one readable restore source plus one adjudication trace
- a reversible placeholder-to-full-byte lane for named claimants only
- a public correction package even if byte-perfect cure is no longer possible

### 2. Hold coverage

Review which substrate classes are actually under hold:

- archive-backed bytes
- live source peers
- exported backup copies
- restore-path metadata needed to make the bytes usable
- adjudication-only traces
- storage headroom and runtime lanes required to execute restore

### 3. Breach and decay risks

Review all ways an apparent preservation hold can fail:

- Archive TTL still shorter than the needed window
- version-size ceiling excluding the critical object
- manual clear or Archive disablement still allowed in practice
- required platform lacking a durable hold lane
- restart or scan timing needed before new retention settings actually govern
- free-space reclamation or ordinary operational cleanup consuming the substrate first
- source peer departure, folder removal, or placeholder-only downgrade collapsing the hold

### 4. Honest current verdict

Return one of these verdicts:

- cure-capable but not preserved
- hold requested only
- hold active for named cohorts
- hold active for required cohorts
- hold active but breach-prone
- preservation breached
- preservation collapsed

## Review invariants

- the review never treats Archive existence alone as preservation
- the review never treats a broad retention knob as equivalent to a named case hold without identifying coverage and breach ownership
- the review never hides when preservation depends on manual operator behavior rather than product-enforced reservation
- the review always explains what stronger preservation sentence remains blocked and why
