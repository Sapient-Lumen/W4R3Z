# Quiet break timeline page — window start, break event, and coverage collapse interface spec

## Purpose

Quiet loss is often temporal before it is semantic.
Operators need one timeline page that shows how long the receipt held, when the first weakening event landed, and whether later events were causes or merely aftershocks.

## Core decision

Every reviewed quiet break should render a **quiet break timeline**.

The timeline is not generic history.
It is a purpose-built chronology for one question:

> when did the quiet claim stop being safe, and what evidence defines that boundary?

## Required sections

1. **Window spine**
2. **Proof landmarks**
3. **Break sequence**
4. **Coverage-collapse line**
5. **Successor options**

## 1) Window spine

Show:

- declared quiet window start
- declared quiet window end
- receipt issue time
- actual observed quiet tenure
- expiry line

Quiet tenure must be computed from the issued receipt to the first accepted break boundary, not merely to the latest visible event.

## 2) Proof landmarks

List evidence that supported the prior receipt:

- quiet acknowledgements
- matched proof arrivals
- covered-seat confirmations
- excluded-seat rationale
- previous strongest safe sentence

These landmarks give context for how strong the claim was before it weakened.

## 3) Break sequence

Each event row must show:

- timestamp
- seat
- event class
- authority candidate
- evidence basis
- whether the event is the first break boundary or only a later consequence

Example classes:

- `manual resume pressed`
- `scheduler returned to active cell`
- `startup completed`
- `background activity observed`
- `new relevant writable seat appeared`
- `window expiry reached`
- `claim narrowed`

## 4) Coverage-collapse line

Show a mini-ledger of claim status over time:

- `covered and valid`
- `narrowed but still partially valid`
- `invalidated`
- `expired on time`
- `uncertain`

This line should let the operator see whether the break was immediate, partial, or only claim-limiting.

## 5) Successor options

At the end of the timeline, propose the next lawful step:

- renew quiet for same cohort
- issue narrower successor receipt
- stop using quiet-dependent language
- close as expected expiry
- escalate unexpected break

## Example projection

```text
Quiet break timeline qbt_01K...

Window spine
  declared window ....... 03:00–03:30 UTC
  receipt issued ........ 03:02:10
  first break boundary .. 03:12:00
  quiet tenure .......... 9m 50s

Proof landmarks
  03:01:44 nas-01 matched with proof
  03:02:10 receipt qcr_01K issued

Break sequence
  03:12:00 laptop-ops scheduler-end ........ first break boundary
  03:12:09 payload activity observed ....... consequence
  03:12:40 prior claim narrowed ............ review output

Coverage-collapse line
  03:02–03:11 .......... covered and valid
  03:12 onward ......... invalidated
```

## Commands

```text
anonsync quiet-break timeline <break_id>
anonsync quiet-break timeline <receipt_id> --json
```

## Success condition

A good quiet break timeline lets a future operator answer:

- how long quiet actually held
- which event first broke it
- whether later activity was cause or aftershock
- where the old sentence stopped being safe
