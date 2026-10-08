# Resume authority review page — scheduler, manual, runtime, and expectedness interface spec

## Purpose

Once a quiet break candidate exists, the operator needs one decisive review page before blaming a seat, renewing the window, or reusing the old receipt.
This page decides whether the break was expected, authorized, surprising, or still ambiguous.

## Core decision

AnonSync should require a **resume authority review** whenever an existing quiet claim is weakened by reactivation evidence.

The review does not ask `did activity happen?`
It asks:

> what authority best explains the reactivation, and what does that authority do to the previous quiet claim?

## Fixed review order

1. **Prior window contract**
2. **Authority candidates**
3. **Expectedness verdict**
4. **Claim survival**
5. **Decision**

## 1) Prior window contract

Capture:

- quiet receipt id
- target subject
- declared window
- covered seats
- achieved stillness class
- previously allowed sentence

The prior contract must stay visible because the authority verdict is relative to that contract.

## 2) Authority candidates

Show a ranked table.

Columns:

- candidate authority
- seat
- evidence
- fit to observed time
- fit to observed behavior
- confidence

Candidate authorities include:

- `manual-resume`
- `global-resume`
- `scheduler-end`
- `declared-window-expiry`
- `startup-return`
- `background-runtime-never-stopped`
- `counterpart-not-covered`
- `unknown`

The page should make clear when two authorities are still competing.

## 3) Expectedness verdict

Compute one verdict:

- `expected-expiry`
- `authorized-early-resume`
- `unexpected-break`
- `outside-covered-scope`
- `ambiguous`
- `no-break-proven`

Below the verdict, show:

- why this is the best fit
- what weaker alternative remains plausible

## 4) Claim survival

Render what survived from the prior receipt.

Allowed values:

- `receipt-still-valid-until-window-end`
- `receipt-expired-on-time`
- `receipt-narrowed-to-subset`
- `receipt-invalidated`
- `receipt-uncertain`

Also show:

- strongest allowed sentence now
- stronger forbidden sentence now

## 5) Decision

Allowed decisions:

- `issue quiet break receipt`
- `reissue quiet request to one seat`
- `treat as ordinary window expiry`
- `narrow claim and proceed with weaker sentence`
- `discard previous quiet receipt`
- `gather more evidence`

## Example projection

```text
Resume authority review raur_01K...

Prior window contract
  receipt ............... qcr_01K...
  window ................ 03:00–03:30 UTC
  covered seats ......... wkstn-02, nas-01, laptop-ops

Authority candidates
  1. scheduler-end ...... laptop-ops .... strong timing fit
  2. manual-resume ...... laptop-ops .... possible, weaker evidence
  3. startup-return ..... wkstn-02 ...... poor timing fit

Expectedness verdict
  unexpected-break
  basis ................. scheduler boundary occurred before declared window ended

Claim survival
  verdict ............... receipt-invalidated
  allowed sentence ...... prior full quiet claim no longer stands
  forbidden sentence .... covered cohort still quiet enough for destructive repair
```

## Commands

```text
anonsync resume-authority review <break_id>
anonsync resume-authority apply <review_id>
```

## Success condition

A good resume authority review prevents the product from collapsing very different realities into one vague `quiet ended` story.
