# Route provenance receipt page — effective path, switch history, and reopen boundary interface spec

## Purpose

The archive already had measurement receipts and diagnostic conclusion receipts.
What it still lacked was the durable receipt for the next question:

> after route posture and route evidence were reviewed, what exact route claim became true, over what window, and what would force that claim back open?

AnonSync should therefore issue a dedicated **route provenance receipt** whenever a route statement is promoted into incident language, performance explanation, or policy-conformance language.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- route-posture version
- route-evidence version(s)
- reviewed pair / cohort / subject scope
- desired transport contract
- effective route verdict
- evidence window
- route-switch history summary
- mismatch verdict
- strongest allowed sentence
- stronger rejected sentence
- next widening or repair step if unresolved
- reopen conditions
- issuance timestamp

## Required sections

### 1) Route claim that won

Show the final durable statement, for example:

- `For peer pair A↔B during 14:02–14:19, the effective path was relayed.`
- `For uploader A to receiver B after predefined-host correction, a stable direct path was observed for the measured window.`

### 2) Scope and provenance

Publish exactly which pair, cohort, or subject the route claim covers and what witness basis supported it.
Do not reduce this to `share connected`.

### 3) Switch history summary

State whether the receipt saw:

- no observed route switch
- observed direct→relay switch
- observed relay→direct switch
- plausible switch but insufficient proof
- mixed route classes within the covered cohort

### 4) Stronger rejected claim

State the stronger claim the receipt explicitly refuses to make.
This is mandatory.

### 5) Reopen boundary

The receipt must say the route claim reopens if any of these happen:

- helper posture changes materially
- covered peers change network segment or NIC routing
- a new contradictory witness arrives
- the observation window goes stale relative to the incident
- a previously excluded peer/cohort becomes relevant
- route-switch evidence appears that weakens the current stable-window claim

## Compact rendering obligations

Any compact receipt chip must still preserve:

- route verdict
- covered scope label
- evidence-window label
- mismatch verdict
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `direct now`, `using relay`, or `tracker issue` without preserving what subject that sentence covered, how the path was witnessed, and what stronger route claim remained unsupported.
