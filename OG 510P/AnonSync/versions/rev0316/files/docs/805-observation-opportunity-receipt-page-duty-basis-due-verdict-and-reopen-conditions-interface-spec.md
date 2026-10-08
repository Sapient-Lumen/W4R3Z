# Observation opportunity receipt page — duty basis, due verdict, and reopen conditions interface spec

## Purpose

The archive already had freshness receipts and rollover receipts.
What it still lacked was the durable receipt for the question:

> at this moment, what was this seat's next honest observation opportunity, was the claim due yet, and what would make that judgment change?

AnonSync should therefore issue a dedicated **observation opportunity receipt** whenever it resolves a `not yet due`, `due now`, or `overdue` question.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- seat / subject scope
- duty class
- opportunity type
- opportunity basis
- unmet preconditions at issuance
- due timestamp or `not schedulable`
- lateness verdict
- strongest allowed sentence
- stronger rejected sentence
- supporting page ids (`802`, `803`, `804`)
- issued-at timestamp
- reopen conditions

## Required sections

### 1) Duty basis

State the runtime class and the basis that mattered, for example:

- `Android seat in interval-wake mode with 30-minute wake cycle`
- `Host in rescan-backed observation with 600-second cadence`
- `iOS seat in foreground-only posture`
- `Seat blocked until allowed network returns`

### 2) Due verdict

Publish one durable sentence, for example:

- `The change was not yet due because the next honest wake window had not arrived.`
- `The claim became due at the end of the current rescan-backed budget.`
- `The delay is overdue under the current posture because the due opportunity passed with witness.`
- `No due time could be issued because required network eligibility had not returned.`

### 3) Stronger rejected sentence

This is mandatory.
Examples:

- `The seat missed the change.`
- `Background sync failed.`
- `The app ignored the update.`

### 4) Reopen conditions

The receipt must say the judgment reopens if any of these happen:

- duty class changes
- wake or rescan cadence changes
- network/source eligibility changes materially
- a stronger opportunity-passed witness appears
- freshness invalidation supersedes the basis

## Compact rendering obligations

Any compact receipt chip must still preserve:

- duty class
- due verdict
- strongest allowed sentence
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `checked`, `still waiting`, or `late` without preserving what duty basis made that statement honest and what change would reopen it.
