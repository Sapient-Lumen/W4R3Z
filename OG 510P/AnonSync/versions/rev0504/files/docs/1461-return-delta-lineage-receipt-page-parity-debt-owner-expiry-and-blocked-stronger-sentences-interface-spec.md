# Return-delta lineage receipt page: parity debt, owner, expiry, and blocked stronger sentences interface spec

## Purpose

After the archive learned how to register, review, and prove accepted return debt, it still needed one durable handoff page for the next operator.

## Core decision

AnonSync must expose one first-class **Return-delta lineage receipt** whenever a changed return remains active, is reaffirmed, is promoted, or is retired.

## Fixed page order

1. **Receipt header**
2. **Current debt summary**
3. **Owner and expiry summary**
4. **Baseline relation summary**
5. **Safe language summary**
6. **Next action summary**

### 1) Receipt header

Show:

- receipt id
- return-delta id
- linked return id
- emitted time
- emitted because

Supported `emitted_because` values:

- `delta-created`
- `temporary-reaffirmed`
- `promotion-decided`
- `exact-restore-finished`
- `reopened`
- `handoff-requested`

### 2) Current debt summary

Required rows:

- current delta status
- accepted delta class
- one-line difference summary
- debt active?
- current age

### 3) Owner and expiry summary

Required rows:

- owner
- expiry type
- expiry time
- overdue?
- next rereview

### 4) Baseline relation summary

Required rows:

- old baseline relation
- new baseline relation if any
- exact restore still planned?
- successor promotion already approved?

### 5) Safe language summary

Required rows:

- strongest safe sentence now
- blocked stronger sentence
- unsafe overclaim to avoid
- next proof that could improve the sentence

### 6) Next action summary

Required rows:

- next required action
- next allowed action
- next forbidden silent normalization
- immediate reopen trigger

## Receipt sentence

Format:

> `This receipt says the subject is currently in [current delta status] under a [accepted delta class] difference owned by [owner] until [expiry time]. Safe language stops at [strongest safe sentence now]. Do not silently normalize this into [blocked stronger sentence].`

## Anti-goals

Do not:

- omit owner or expiry
- omit whether debt is still active
- state that the baseline changed unless promotion was explicit
- hide the next forbidden overclaim

## Why this page exists

Because the next operator needs a compact answer to the hardest post-return truth:

> are we still carrying accepted parity debt, who owns it, when does it expire, and what stronger sentence is still unsafe to say?
