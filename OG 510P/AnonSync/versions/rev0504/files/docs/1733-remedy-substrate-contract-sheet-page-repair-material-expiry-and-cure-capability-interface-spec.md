# Remedy-substrate contract sheet page — repair material, expiry, and cure capability

## Purpose

This page is the operator's compact contract for whether a damaged state still has enough substrate to support honest repair.
It exists so the product can distinguish `harm happened`, `compensation is owed`, `some residue survives`, and `clean cure is still materially possible`.

## Core fields

- case identifier
- source downstream-consequence receipt identifier
- harmed cohorts
- required repair target
- current remedy posture rung
- repair material locations
- repair material classes by location
- source-capable peers
- placeholder-only peers
- archive-backed peers
- encrypted-but-unreadable custody peers
- retention horizon by material class
- version-size exclusion risk
- free-space headroom by required repair lane
- platform support ceiling
- manual steps still required
- strongest blocked stronger cure sentence
- next strengthening trigger
- next weakening trigger

## Remedy posture rungs

The page must model at least these distinct rungs:

- compensation owed
- possible cure signal only
- repair material evidenced
- repair material sufficient for partial cure
- cure-capable for named cohorts
- cure-capable for required cohorts
- cure executed but not yet verified
- cure-proven
- cure-collapsed

## Required distinctions

The page must keep these truths separate:

- archived bytes versus live source bytes
- placeholder visibility versus recoverable content
- readable repair material versus encrypted custody only
- desktop/manual repair lane versus mobile-limited lane
- retention present versus retention about to expire
- repair theoretically possible versus currently executable under free-space and runtime constraints

## Operator promises

The contract sheet must let the operator say things like:

- `compensation is owed, but clean cure is not yet evidenced`
- `repair material exists on two archive-backed desktop peers, though only one required cohort is still cure-capable`
- `the needed file survives only as placeholder knowledge; clean cure is blocked because no source-capable peer remains`
- `repair lane exists, but version-size ceiling excludes the missing object and only partial cure can be promised`
- `archive-backed cure expires in 19 hours unless a manual restore and verification lane starts now`

## Invariants

- the page never upgrades Archive presence into cure sufficiency by omission
- the page never upgrades placeholder presence into source survivorship
- the page never upgrades one recoverable peer into required-cohort cure without naming the cohort gap
- the page never hides expiry, size ceiling, platform ceiling, or free-space blockers
- the page always preserves the strongest blocked stronger cure sentence
