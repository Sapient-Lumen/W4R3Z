# Promise authority timeline page: breach, downgrade, probation, restoration, and suspension events interface spec

## Purpose

The operator needs one timeline that answers:

> how did promise authority change over time, what event downgraded it, when did probation begin, when was it partly restored, and what later event suspended or widened it again?

## Core decision

AnonSync must keep one first-class **Promise authority timeline** for every actor, service, or governed promise lane whose authority can change after breaches, recoveries, reviews, or overrides.

## Supported event families

- `authority-created`
- `authority-narrowed`
- `authority-co-sign-imposed`
- `authority-target-only`
- `authority-blocked`
- `probation-opened`
- `probation-tightened`
- `probation-extended`
- `clean-delivery-credit`
- `accepted-recovery-credit`
- `authority-restored-partial`
- `authority-restored-full`
- `authority-suspended`
- `authority-revoked`
- `manual-override`
- `override-expired`

## Fixed page order

1. **Timeline header**
2. **Authority-state ladder**
3. **Budget-change lane**
4. **Override and suspension lane**
5. **Current posture summary**

### 1) Timeline header

Show:

- subject of authority
- current authority class
- current probation status
- current credibility budget grade
- current strongest allowed promise sentence
- last widening event
- last narrowing event
- next scheduled review

### 2) Authority-state ladder

The ladder must show transitions among:

- `fully-authorized`
- `co-sign-required`
- `narrowed-scope-only`
- `target-only`
- `checkpoint-only`
- `blocked`
- `suspended`

Hard rule:

A later widening event may not erase earlier downgrades.
The timeline must preserve the full path.

### 3) Budget-change lane

Each event must say:

- whether it consumed credibility budget
- whether it restored any budget
- whether it changed only scope cap or also promise-class cap
- whether it opened or closed probation

### 4) Override and suspension lane

Show:

- human overrides
- emergency permissions
- override duration
- surviving caps during override
- what happens when override expires

Hard rule:

Override may widen authority temporarily, but it may not rewrite the normal authority basis.

### 5) Current posture summary

End with one state line in this form:

- current authority class
- scope cap
- co-sign rule
- probation state
- next event that would widen or narrow authority again
