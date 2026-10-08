# Remedy-hardening-attestation successor preview/commit binding proof page — bound snapshot, drift invalidators, and commit legitimacy ceiling

## Purpose

This page is the durable proof artifact that preserves what exact preview was bound to execution, which invalidators were checked, which remained blind, and what no-surprise sentence therefore stayed blocked.

## Minimum proof bundle

The proof page must preserve at least:

- source action-plan receipt identifier
- source action-envelope receipt identifier
- reviewed snapshot identifier
- snapshot creation timestamp
- snapshot scope hash or equivalent summary
- commit token identifier
- commit actor set
- freshness window at issue time
- pre-commit check timestamp
- drift-check result by invalidator family
- invalidators known to be unobserved
- replay prohibition state
- execute-if-unchanged verdict
- strongest safe sentence at commit time
- strongest blocked stronger sentence at commit time

## Proof sections

### 1. Bound snapshot summary

Show:

- what was reviewed
- what was excluded
- which assumptions had to stay true
- which assumptions were rechecked at commit time

### 2. Drift invalidator ledger

For each invalidator show:

- why it matters
- how it was checked
- pass / fail / unknown
- observer quality
- whether it alone forced refresh or full re-review

### 3. Freshness ledger

Show:

- snapshot age at commit
- window remaining or expired
- any pause, restart, reconnect, or rescan events since preview
- any settings or policy save events since preview if relevant
- whether the run still counted as single-use or replay

### 4. Commit ceiling statement

The page must end with a bounded statement such as:

- `snapshot bound, drift checks incomplete; stronger same-run sentence blocked`
- `snapshot still fresh for named slice only`
- `approval and participant sets unchanged; background-rescan blind spot remains`
- `commit token expired; re-review required`
- `execute-if-unchanged failed due to material drift`

## Evidence grading

The proof page must support at least these grades:

- preview only, not bindable
- snapshot bound, freshness window open, drift checks pending
- snapshot bound and basic drift checks passed
- snapshot bound and full required drift checks passed for named slice only
- snapshot invalidated before commit
- commit proceeded with known blind spots
- proof later contradicted by post-commit drift evidence

## Hard rules

The page must never:

- treat a surviving plan id as proof of same-run identity
- hide expired freshness behind urgency language
- erase unknown invalidators from the record
- treat missing observers as passed observers
- upgrade to `no surprise execution` merely because commit happened
