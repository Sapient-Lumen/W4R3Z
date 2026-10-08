# Quiet event page — observed activity, prior receipt, and break-candidate interface spec

## Purpose

The archive already has quiet receipts and quiet-break pages.
What it still needs is the page that answers the earlier question:

> an event happened during a quiet claim — **what exactly happened, and is it even a real challenge yet?**

A serious maintenance or evidence workflow cannot treat every later event as self-explanatory.
AnonSync should model that later event as a first-class **quiet event** object before it becomes a break.

## Core decision

Every event observed against an active quiet receipt first opens a **quiet event page**.
The page does not assume the event is a quiet failure.
It answers five things:

1. which quiet receipt is being challenged
2. what exact event was observed
3. which seat and subject slice the event belongs to
4. whether the event is a plausible break candidate or an obvious residual class
5. what review must happen next

## Fixed review order

1. **Prior quiet receipt**
2. **Observed event**
3. **Scope relation**
4. **Candidate meaning**
5. **Claim risk now**
6. **Next safest action**

## 1) Prior quiet receipt

Show:

- quiet receipt id
- subject
- covered cohort / slice
- achieved stillness class
- declared residual allowances
- strongest previously allowed sentence
- issue time

The page must preserve the exact quiet claim now under challenge.

## 2) Observed event

Render one event row with:

- event time
- event class
- seat
- subject slice
- evidence basis
- confidence

Allowed event classes include:

- `delete-propagation`
- `zero-byte-or-control-update`
- `index-growth`
- `queue-growth`
- `counterpart-upload`
- `manual-resume`
- `scheduler-boundary`
- `startup-return`
- `background-runtime-activity`
- `unknown-motion`

The page may show multiple sightings, but must nominate one **current challenge event**.

## 3) Scope relation

Each challenge event must show:

- whether the event came from a covered seat, uncovered seat, or unknown seat
- whether the affected subject slice was inside the earlier quiet claim
- whether the event class was previously declared as allowed residue
- whether the evidence is direct, inferred, or mixed

Do not let an out-of-scope event auto-collapse an in-scope quiet receipt.

## 4) Candidate meaning

The page must classify the event initially as one of:

- `likely-allowed-residual`
- `possible-quiet-break`
- `outside-prior-claim`
- `insufficient-evidence`

This is not the final verdict.
It is the handoff into the allowance review.

## 5) Claim risk now

Below the candidate meaning, show:

- strongest safe sentence now
- stronger forbidden sentence now

Example:

- allowed: `quiet receipt qcr_01K still stands provisionally, but event evt_01L needs allowance review`
- forbidden: `quiet definitely failed at 03:14`

## 6) Next safest action

The page should recommend the lightest honest next step, such as:

- open residual allowance review
- mark event outside prior claim
- merge with earlier challenge cluster
- escalate to quiet break review
- request more evidence

## Example projection

```text
Quiet event — finance/share-a

Prior quiet receipt
  receipt ............... qcr_01K...
  stillness class ....... quiet-enough-for-declared-risk
  residual allowances ... delete-propagation, index-growth

Observed event
  time .................. 2026-03-22 03:09:41 UTC
  class ................. index-growth
  seat .................. nas-01
  evidence .............. share size increased while transfers stayed at zero

Scope relation
  seat scope ............ covered seat
  subject scope ......... inside prior claim
  prior allowance ....... yes

Candidate meaning
  verdict ............... likely-allowed-residual

Claim risk now
  allowed ............... quiet claim remains provisional pending allowance review
  forbidden ............. this event already proves quiet failed
```

## Commands

```text
anonsync quiet-event show <event_id>
anonsync quiet-event create --receipt <receipt_id> --event <event_ref>
anonsync quiet-event show <event_id> --json
```

## Success condition

A good quiet event page lets an operator answer:

- which quiet claim is being challenged
- what exact event was observed
- whether the event is even a real break candidate yet
- what review must happen next before stronger language is allowed
