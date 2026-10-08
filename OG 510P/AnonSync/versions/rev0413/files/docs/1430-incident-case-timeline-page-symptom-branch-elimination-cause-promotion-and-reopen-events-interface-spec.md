# Incident case timeline page: symptom branch elimination, cause promotion, and reopen events interface spec

## Purpose

The archive already had remediation timelines and rollout-health timelines.
What it still lacked was the case-history answer to:

> how did our understanding evolve over time, which cause branches died when, when did closure strength change, and what exactly caused the case to reopen?

## Core decision

AnonSync must expose one first-class **Incident case timeline** for every case that has:

- more than one evidence event
- any hypothesis promotion, refutation, split, or merge
- any remediation run attachment
- any closure or reopen event

## Required event families

The timeline must support these event families explicitly:

- `symptom-observed`
- `scope-expanded`
- `scope-narrowed`
- `evidence-added`
- `evidence-staled`
- `hypothesis-added`
- `hypothesis-promoted`
- `hypothesis-refuted`
- `hypothesis-split`
- `hypothesis-merged`
- `run-started`
- `run-checkpoint-passed`
- `run-aborted`
- `closure-proposed`
- `closure-approved`
- `watch-window-started`
- `watch-window-ended`
- `reopen-triggered`
- `case-merged`
- `case-superseded`

## Fixed page zones

1. **Timeband header**
2. **Understanding-change stream**
3. **Closure-strength stream**
4. **Reopen stream**
5. **Sentence ladder footer**

### 1) Timeband header

Show:

- case id
- current phase
- current favored cause
- current closure class
- current watch state

### 2) Understanding-change stream

Each event must show:

- timestamp
- event family
- actor
- affected hypothesis ids
- changed sentence
- why the sentence changed

Hard rule:

A hypothesis promotion event is invalid unless it links to the evidence ids that justified it.

### 3) Closure-strength stream

This stream shows how the closure ceiling moved over time.
Supported `closure_strength_delta` values:

- `none`
- `weaker`
- `stronger`
- `more-honest-but-not-stronger`

Example:

- changing from `resolved` to `mitigated` is `more-honest-but-not-stronger`
- changing from `unknown` to `best-current-explanation` is `stronger`

### 4) Reopen stream

For any reopen or near-reopen event, show:

- trigger source
- trigger verdict
- auto or manual reopen
- revived hypothesis ids
- what prior closure sentence was revoked
- what new watch window started

Supported `trigger_verdict` values:

- `not-a-reopen`
- `watch-only`
- `reopen-same-case`
- `spawn-linked-case`
- `merge-into-existing-case`

### 5) Sentence ladder footer

Always end the page with three ordered ladders:

- strongest sentence ever claimed
- strongest sentence currently safe
- strongest sentence now forbidden

## Mandatory interaction rules

- The timeline must preserve wrong turns; refuted hypotheses cannot disappear from history.
- Closure weakening is a first-class event, not an embarrassment to hide.
- Reopen must visibly revoke earlier claims rather than quietly superseding them.

## Why this page exists

Operators need to see not only what happened to the system, but what happened to their own understanding of the system.
