# Downstream-consequence review page — what this sentence version already changed and what unwind remains?

## Purpose

This page is the operator workspace for reviewing how far a sentence version has already changed downstream world state.
It exists to stop the product from collapsing `used as basis` into `nothing material happened` or `everything can still be rolled back cleanly`.

## Review sections

### 1. Source sentence summary

The page must show:

- sentence version used
- source consumer-uptake rung
- decision class that launched the consequence lane
- fallback sentence if unwind occurs
- whether supersession already exists but downstream residue still survives

### 2. Consequence map

The reviewer must be able to inspect named consequence cohorts by strongest rung:

- armed only
- emitted only
- mutation-started
- world-mutated
- partially unwound
- compensation-owed
- compensation-issued
- compensation-cleared
- irreversible residue
- unknown or contested

### 3. Repair map

For each consequence cohort the page must show:

- whether halt is still available
- whether direct rollback is available
- whether inverse action is required
- whether compensation is required
- whether only annotation or debt recording remains
- what evidence supports that classification

### 4. Residue collision review

The page must compare:

- downstream consequences that were fully unwound
- downstream consequences that were compensated but still leave residue
- consequences still active under the current sentence
- consequences still active under a stale or superseded sentence version
- consequences whose actual world-mutation depth is unknown or contested

## Required reviewer prompts

- what is the strongest honest sentence about downstream world change right now?
- which mutations have not yet crossed from armed to world-mutated?
- which paths can still be halted rather than compensated?
- which paths already require compensation debt tracking?
- which irreversibilities survive even after repair?
- what is the smallest honest unwind sentence now?
- what stronger repair sentence remains blocked?

## Invariants

- decision use does not imply world mutation
- world mutation does not imply clean unwind
- compensation issued does not imply compensation cleared
- one repaired cohort does not erase residue on another cohort
- revocation or disconnect does not by itself prove clawback

## Mandatory warnings

The page must warn when:

- downstream mutation is inferred only from visibility or permission evidence
- a supposedly reversed path still leaves durable bytes or access elsewhere
- repair language is stronger than the actual compensation evidence supports
- a later reconnect, rescan, or relink may re-materialize the mutation
- supersession happened but old-version world residue still survives
