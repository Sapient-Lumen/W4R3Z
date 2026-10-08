# Return-delta timeline page: accepted drift, expiry, promotion, and reopen events interface spec

## Purpose

After the archive learned how to prove the fate of return debt, it still needed one timeline page that preserves how a changed return aged over time.

## Core decision

AnonSync must expose one first-class **Return-delta timeline** page for every non-trivial accepted delta.

## Event classes

The timeline must preserve at least these event types:

- `delta-accepted`
- `owner-assigned`
- `expiry-set`
- `proof-window-missed`
- `delta-worsened`
- `same-cause-near-miss`
- `same-cause-recurrence`
- `temporary-reaffirmed`
- `exact-restore-started`
- `exact-restore-completed`
- `successor-promotion-started`
- `successor-baseline-created`
- `claim-narrowed`
- `reopened`
- `debt-retired`

## Fixed page order

1. **Timeline header**
2. **Debt aging ribbon**
3. **Event ledger**
4. **Sentence-change rail**
5. **Next trigger card**

### 1) Timeline header

Show:

- return-delta id
- age
- current delta status
- current owner
- next expiry / rereview

### 2) Debt aging ribbon

A horizontal band showing:

- accepted
- stable temporary
- expiring
- overdue
- promoted
- restored
- reopened

Hard rule:

The ribbon must not show `healthy` without showing whether debt still exists.

### 3) Event ledger

Each event row must show:

- timestamp
- event type
- actor
- before sentence
- after sentence
- debt size change (`smaller`, `same`, `larger`, `retired`)
- notes

### 4) Sentence-change rail

This rail shows how the strongest safe sentence changed over time.
It must make visible:

- initial blocked stronger sentence
- weaker sentence during temporary acceptance
- sentence after reaffirmation or promotion
- sentence after exact restore or reopen

### 5) Next trigger card

Required rows:

- next forced review
- next automatic downgrade
- next proof expected
- next event that would retire debt
- next event that would reopen immediately

## Required interactions

### A) `Jump to proof`

From any event that changed claim ceiling.

### B) `Compare before and after`

For exact restore, promotion, and reopen events.

### C) `Escalate now`

Available when overdue or worsened.

## Anti-goals

Do not:

- reduce the timeline to operational uptime
- omit missed proof windows
- hide sentence downgrades because bytes kept flowing

## Why this page exists

Because accepted drift is not static.
The operator needs to see whether the gap is shrinking honestly, being normalized dangerously, or getting worse until reopen is unavoidable.
