# Applicability lineage receipt page: fact pattern, governing doctrine, open gaps, and blocked stronger sentences interface spec

## Purpose

After the archive learned how to track routing history, it still needed one final handoff page that answers:

> what doctrine currently governs this case, which facts made that routing safe, what gaps remain, and what stronger sentence is still blocked if another operator picks this up later?

## Core decision

AnonSync must expose one first-class **Applicability lineage receipt** whenever a routed case is handed off, paused, escalated, or used to justify bounded next action.

## Fixed page order

1. **Receipt header**
2. **Current fact-pattern card**
3. **Governing-doctrine card**
4. **Open-gap and rival-route card**
5. **Claim-ceiling card**
6. **Blocked-stronger-sentence card**

### 1) Receipt header

Show:

- applicability receipt id
- case id
- current routing owner
- publication time
- latest rereview time
- current routing class

### 2) Current fact-pattern card

Required rows:

- primary symptom family
- decisive observed facts
- worlds/lanes relevant
- already-attempted actions
- current witness contradictions if any

### 3) Governing-doctrine card

Required rows:

- governing doctrine id or `none yet`
- routing class
- why this doctrine currently wins
- doctrine weight used
- next rereview trigger

### 4) Open-gap and rival-route card

Required rows:

- open factual gap
- rival routes still alive
- rival routes ruled out
- fact that would most likely reopen routing
- cross-route-safe action set if any

### 5) Claim-ceiling card

Required rows:

- strongest currently safe routing sentence
- action authority justified by that sentence
- weaker sentence if the route downgrades
- expiry or freshness boundary

### 6) Blocked-stronger-sentence card

Required rows:

- strongest blocked overclaim
- exact fact needed to unlock it
- who can supply that fact
- what evidence would collapse the current route instead

## Hard rule

An applicability receipt must let a later operator answer four questions immediately:

- what facts do we really know?
- what doctrine currently governs, if any?
- what rival routes are still alive?
- what stronger sentence is still blocked?

If any of those are missing, the receipt is incomplete.

## Empty state

If routing is still unclassified, show:

- `No applicability receipt yet: the case has not reached a stable routing stance.`
