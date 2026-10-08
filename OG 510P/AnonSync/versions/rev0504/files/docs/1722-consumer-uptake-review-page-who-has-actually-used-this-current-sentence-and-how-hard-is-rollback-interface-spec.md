# Consumer-uptake review page — who has actually used this current sentence and how hard is rollback?

## Purpose

This page is the operator workspace for reviewing how far a current sentence has propagated into real decision use.
It exists to stop the product from collapsing `could see it` into `already relied on it`.

## Review sections

### 1. Current sentence summary

The page must show:

- strongest sentence currently operative
- source currentness rung
- sentence version handle
- fallback sentence if rollback occurs
- whether supersession already exists but is not yet consumed

### 2. Uptake map

The reviewer must be able to inspect consumer cohorts by uptake class:

- delivered only
- rendered only
- pinned but unused
- decision-bound
- action-started
- action-completed
- rollback-cleared
- unknown or contested

### 3. Rollback map

For each cohort the page must show:

- rollback lane available
- whether rollback is cheap, moderate, expensive, or blocked
- whether compensation is possible
- whether only annotation is possible after the fact
- what evidence supports that classification

### 4. Version-collision review

The page must compare:

- consumers still on lower sentence
- consumers on current sentence version V
- consumers on superseding sentence version V+1
- consumers whose pinned version is unknown
- consumers whose local cache or rendering surface is stale or contradictory

## Required reviewer prompts

- what is the strongest honest sentence about uptake right now?
- which consumers merely saw the sentence?
- which consumers pinned a version without using it?
- which consumers already made a bound decision?
- which consumers crossed into irreversible action?
- what is the smallest honest rollback claim now?
- what stronger reversal claim remains blocked?

## Invariants

- currentness does not imply uptake
- rendering does not imply pinning
- pinning does not imply decision use
- decision use does not imply action completion
- rollback for one cohort does not rewrite what another cohort already did

## Mandatory warnings

The page must warn when:

- a consumer acted on an older pinned sentence after a newer sentence became current
- a consumer surface may be stale because of known rendering divergence
- decision use is inferred rather than directly evidenced
- rollback language is stronger than the actual blast-radius evidence supports
- supersession happened but old-version residue still survives
