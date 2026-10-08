# Remedy-hardening-attestation successor preview/commit binding lineage receipt page — bound preview, freshness window, and blocked no-surprise sentences

## Purpose

This page is the portable receipt summarizing what can honestly be claimed about preview-to-commit sameness for one action run.
Later pages must cite this receipt instead of improvising `same run`, `fresh enough`, or `no surprise execution` language.

## Receipt header

The header must show:

- receipt identifier
- action identifier
- reviewed snapshot identifier
- successor world identifier
- current commit-binding standing
- current strongest safe sentence
- current blocked stronger sentence

## Mandatory receipt fields

- source action-plan receipt identifier
- source action-envelope receipt identifier
- snapshot creation time
- freshness window summary
- commit token summary
- replay prohibition summary
- invalidator families checked
- invalidator families still blind
- last pre-commit drift-check time
- same-run verdict summary
- execute-if-unchanged verdict summary
- post-commit contradiction status
- superseding receipt identifier if any

## Standing states

The receipt must support at least these states:

- preview exists, not yet bindable
- preview bound, freshness window open
- preview bound, drift checks incomplete
- preview fresh and same-run checks passed for named slice only
- preview expired before commit
- preview invalidated by material drift
- commit happened with blind spots preserved
- post-commit contradiction discovered
- receipt superseded

## Primary sentence classes

The receipt must be able to emit at least these classes:

- `reviewed preview exists, same-run sentence still blocked`
- `preview bound, freshness window open, commit not yet justified`
- `preview fresh for named slice only; no-surprise sentence still blocked`
- `execute-if-unchanged checks passed for named invalidators only`
- `preview expired; re-review required`
- `material drift invalidated bound preview`
- `commit proceeded with blind spots preserved`
- `post-commit contradiction narrowed same-run confidence`

## Hard rules

The receipt must never let later pages say:

- this is definitely the same run we reviewed
- nothing material changed between preview and commit
- the bound preview covered all relevant drift
- commit was no-surprise execution
- refresh was unnecessary

unless the receipt actually carries the corresponding proof state.
