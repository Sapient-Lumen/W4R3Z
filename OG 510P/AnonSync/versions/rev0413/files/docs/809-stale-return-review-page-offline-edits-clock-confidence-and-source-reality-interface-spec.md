# Stale-return review page — offline edits, clock confidence, and source reality interface spec

## Purpose

The archive already had same-path winner review, source-witness work, next-opportunity review, and freshness invalidation.
What it still lacked was one review page for the return question:

> after dormancy, what exactly makes this return risky or safe: offline edits, clock drift, stale announcements, roster expiry, or no remaining full source?

AnonSync should therefore expose a first-class **stale-return review page** whenever a return is not obviously safe.

## Core decision

No seat or subject should silently jump from `uncertain` to `ordinary` just because it became visible again.
The review must preserve five truths:

1. return class under test
2. chronology-risk rows
3. source-reality rows
4. safest next action
5. strongest rejected sentence

## Fixed review order

1. **Return under test**
2. **Chronology risk review**
3. **Source and announcement reality**
4. **Safe action ladder**
5. **Allowed and rejected language**

## 1) Return under test

Show:

- reviewed seat / subject
- current re-entry class
- dormancy interval summary
- why this return is not yet ordinary by default

## 2) Chronology risk review

Publish separate rows for:

- offline local edits present or plausible
- reopen / restart re-indexing risk
- time or timezone invalid
- dormancy long enough that `latest` is only guarded
- no chronology risk presently supported

Each row must say whether it is:

- `supported`
- `plausible`
- `ruled out`
- `blocked by missing evidence`

## 3) Source and announcement reality

Publish separate rows for:

- live full source peer proved
- returning peer visible but full source not proved
- ghost announcement likely
- source absent despite announcement
- stale placeholder-only world likely

The operator must be able to answer:

> is the return actually fetch-capable, or did only the announcement survive?

## 4) Safe action ladder

Examples:

- normalize as ordinary wake
- keep under re-entry observation
- repair clocks first
- verify full source peers first
- reopen source witness
- reopen chronology / winner review
- avoid destructive reconciliation until stronger proof exists

Each action must preview its claim delta and its non-effects.

## 5) Allowed and rejected language

Required allowed examples:

- `The seat returned, but chronology confidence is guarded.`
- `The peer is visible again, but full source proof is incomplete.`
- `The announcement persists, but source reality is currently broken.`

Required rejected examples:

- `Everything is normal again.`
- `This is definitely the latest copy.`
- `The missing file will arrive now.`

## Compact rendering obligations

Any compact review card must still preserve:

- dominant stale-return risk
- source-reality verdict
- safest next action
- strongest rejected sentence

## Anti-clone rule

Do not clone workflows where `back online` or `peer visible again` can erase chronology, source, or dormancy risk without one explicit review object.
