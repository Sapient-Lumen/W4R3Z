# Quiet break page — broken window, resume authority, and seat-origin interface spec

## Purpose

The archive now has quiet cohort receipts.
What it still needs is the page that answers the next hard question:

> the quiet claim changed — **what broke it first?**

A serious maintenance or evidence workflow cannot treat quiet loss as a vague background fact.
AnonSync should model that loss as a first-class **quiet break** object.

## Core decision

Every quiet cohort receipt may later emit a **quiet break page** when evidence suggests the covered stillness class has weakened, expired, or been contradicted.

The page answers four things:

1. which quiet receipt is being challenged
2. what event appears to have broken or downgraded it
3. which seat and authority class the break came from
4. what sentence is still safe now

## Fixed review order

1. **Prior quiet basis**
2. **Candidate break event**
3. **Break origin**
4. **Coverage collapse**
5. **Post-break sentence**
6. **Next safest action**

## 1) Prior quiet basis

Show:

- quiet cohort receipt id
- subject
- achieved stillness class
- declared window
- issuing actor
- issue time
- strongest previously allowed sentence

The page must preserve the exact quiet claim now under challenge.

## 2) Candidate break event

Render one candidate event row with:

- event time
- event class
- evidence basis
- confidence

Allowed event classes include:

- `manual-resume`
- `global-resume`
- `scheduler-boundary`
- `window-expired`
- `startup-return`
- `background-runtime-activity`
- `counterpart-never-matched`
- `new-seat-became-relevant`
- `unknown-reactivation`

The page may show multiple candidates, but must nominate one **first break candidate**.

## 3) Break origin

Each break candidate must show:

- originating seat
- origin scope (`local-seat`, `covered-counterpart`, `outside-covered-cohort`, `unknown`)
- authority class
- whether the break was expected under the declared window
- strongest safe sentence for that row

Authority class may be:

- `operator-manual`
- `scheduled`
- `window-expiry`
- `runtime-autostart`
- `background-continuation`
- `unreviewed-counterpart`
- `unknown`

## 4) Coverage collapse

The page must compute what changed in the prior claim.

Allowed values:

- `no-break-proven`
- `local-break-only`
- `covered-subset-weakened`
- `quiet-receipt-invalidated`
- `full-cohort-quiet-ended`
- `unknown`

Do not silently jump from one seat resuming to `all quiet lost` unless the seat actually mattered to the previous receipt's strongest sentence.

## 5) Post-break sentence

Below the verdict, show:

- strongest allowed sentence now
- stronger forbidden sentence now

Example:

- allowed: `quiet remained valid for nas-01 until 03:14, but the covered writable cohort is no longer fully quiet`
- forbidden: `maintenance isolation is still active everywhere`

## 6) Next safest action

The page should recommend the lightest honest next step, such as:

- issue quiet break receipt
- narrow the active claim to surviving covered seats
- request renewed quiet from one resumed seat
- let the prior window expire and stop using the old receipt
- start a successor quiet cohort review

## Example projection

```text
Quiet break — finance/share-a

Prior quiet basis
  receipt ............... qcr_01K...
  achieved class ........ quiet-enough-for-declared-risk
  window ................ 2026-03-22 03:00–03:30 UTC

Candidate break event
  first break ........... scheduler-boundary
  time .................. 2026-03-22 03:12:00 UTC
  evidence .............. local schedule returned to full-bandwidth cell

Break origin
  seat .................. laptop-ops
  authority ............. scheduled
  expectedness .......... unexpected within declared window

Coverage collapse
  verdict ............... quiet-receipt-invalidated

Post-break sentence
  allowed ............... previous quiet receipt no longer supports cohort-wide stillness
  forbidden ............. destructive repair still protected by prior quiet claim
```

## Commands

```text
anonsync quiet-break show <subject>
anonsync quiet-break create --receipt <receipt_id>
anonsync quiet-break show <break_id> --json
```

## Success condition

A good quiet break page lets an operator answer:

- what prior quiet claim is under challenge
- what likely broke it first
- whose authority that break came from
- what sentence remains safe right now
