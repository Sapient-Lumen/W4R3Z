# Freshness rollover receipt page — expired claim, revalidated window, and supersession boundary interface spec

## Purpose

The archive already had change-detection receipts.
What it still lacked was the durable receipt for the next question:

> after posture drift reopened the freshness question, what exactly happened to the old claim, what new claim replaced it, and what would reopen this newer claim again?

AnonSync should therefore issue a dedicated **freshness rollover receipt** whenever an earlier freshness claim is weakened, expired, revalidated, or superseded.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- prior freshness receipt id
- invalidator version
- revalidation review version
- posture-drift timeline version
- covered subject scope
- prior claim status (`kept`, `downgraded`, `expired`, `superseded`)
- new coverage epoch
- new latency budget or `none declared`
- new strongest allowed sentence
- stronger rejected sentence
- supersession timestamp
- reopen conditions

## Required sections

### 1) What happened to the old claim

Show one durable sentence, for example:

- `The prior freshness receipt expired after the subject moved into rescan-only observation.`
- `The prior receipt remained usable, but only under a weaker blind-window sentence.`
- `The prior receipt was superseded after a fresh healthy-notification witness restored immediate-observation posture.`

### 2) New claim that won

Publish the replacement statement clearly.
Do not reduce this to `rescanned`, `restarted`, or `issue checked again`.

### 3) Supersession boundary

State exactly when the older claim stopped carrying load and when the newer one began.
This is mandatory.

### 4) Stronger rejected sentence

State the stronger sentence the new receipt refuses to make.
This is mandatory.

### 5) Reopen conditions

The receipt must say the new claim reopens if any of these happen:

- another posture-class change occurs
- cadence, watcher, or network eligibility changes again
- the new observation window itself becomes stale
- contradictory fresh evidence arrives
- subject scope changes materially

## Compact rendering obligations

Any compact receipt chip must still preserve:

- prior-claim status
- new epoch label
- new strongest allowed sentence
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `rechecked`, `still delayed`, or `working now` without preserving what expired, what replaced it, and where the new claim would stop being trustworthy.
