# Admission-instrument lineage receipt page: join basis, credential class, and blocked stronger sentences interface spec

## Purpose

The archive repeatedly chooses receipts whenever a user may later need to prove not just *what happened*, but *what the product was willing to claim at the time*.
This receipt is the durable output for the admission-instrument family.

## Core decision

AnonSync must emit one **Admission-instrument lineage receipt** whenever a user-visible access sentence depends on automatic identity linking, manual key sharing, manual link flow, approval settings, certificate issuance, or local key rotation.

## Receipt layout

1. **Receipt header**
2. **Admission basis block**
3. **Gate and issuance block**
4. **Afterlife block**
5. **Blocked stronger sentences block**

### 1) Receipt header

Show:

- `admission_receipt_id`
- subject ref
- peer ref
- issued-at time
- receipt freshness horizon
- strongest safe sentence
- blocked stronger sentence

### 2) Admission basis block

Must preserve:

- admission basis
- transport wrapper
- underlying credential class
- granted permission class
- minting authority
- whether QR was only a representation wrapper

### 3) Gate and issuance block

Must preserve:

- approval requirement class
- whether approval was pending, bypassed, reused, or satisfied
- whether fingerprint review was witnessed
- whether certificate issuance was witnessed
- whether ACL installation was witnessed
- whether transfer eligibility was witnessed

This block exists so that future readers do not misread historical `shared`, `approved`, or `joined` language as a stronger statement than was actually proven.

### 4) Afterlife block

Must preserve:

- expiry basis if any
- use-count basis if any
- whether expiry affected only future joins
- whether key rotation occurred
- whether rotation auto-propagated or split the lineage
- whether manual redistribution remained necessary

### 5) Blocked stronger sentences block

Each receipt must preserve at least one blocked stronger sentence, for example:

- `This invite alone granted durable access.`
- `This QR code was a narrower credential than the copied link.`
- `This expired invite removed existing access.`
- `This key rotation moved the whole cohort.`

## Hard rules

- receipts may never serialize `shared` without reviewed admission meaning
- receipts must preserve both gate state and issuance state
- receipts must state whether the strongest sentence depended on runtime observation or only configured policy
- receipts must remain readable without cross-referencing the full sheet
