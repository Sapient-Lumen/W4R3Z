# Burst borrow contract sheet page — exception scope, expiry, harmed claimants, and payback basis

## Purpose

This page is the canonical object for any active claimant that is consuming beyond ordinary award but may be doing so under an explicit temporary exception.
It must answer the next operator question after envelope conformance:

> is this claimant simply out of bounds, or is it operating under a narrow, expiring, and repayable burst-borrow exception with explicit consequence on reserve and neighboring claimants?

## Primary questions the page must answer

1. What ordinary room was originally awarded?
2. What extra room is being borrowed temporarily, and from where?
3. Who authorized the exception and for what exact reason?
4. When does the exception expire or require renewal?
5. What reserve or claimant harm must be repaid or relieved afterward?

## Required fields

### A. Base award block

- contention case link
- winning claimant name
- ordinary award amount
- original conformance class
- protected-reserve floor before exception
- impacted claimant set before exception

### B. Exception authority block

- exception class (`emergency-burst`, `deadline-protection`, `containment-move`, `make-good-override`, `manual-executive-exception`)
- authorizing actor
- authority quality (`standing-policy`, `delegated`, `co-sign-required`, `manual-one-off`)
- typed reason for borrow
- borrowed extra room amount
- source of borrowed room (`protected-reserve`, `adjacent-claimant-room`, `shared-headroom`, `temporary-throttle-on-others`)
- open time
- expiry time
- renewal limit if any

### C. Harm and payback block

- protected-reserve impact
- harmed claimant set
- harmed promise or dispatch set
- payback class (`restore-reserve`, `repay-claimant-room`, `narrow-next-award`, `time-box-only-no-renewal`, `manual-compensate`)
- payback due time
- payback completion criteria

### D. Current status block

- current live consumption
- current exception state
- last valid exception witness
- next forced review time
- correction route if exception fails

## Required states

The page must keep these states separate:

- `exception-requested`
- `exception-authorized-not-started`
- `exception-live-within-extra-room`
- `exception-live-at-limit`
- `exception-overrun-even-with-borrow`
- `exception-expired-pending-payback`
- `exception-renewed`
- `exception-denied`
- `exception-withdrawn`
- `payback-open`
- `payback-partial`
- `payback-complete`
- `exception-normalization-risk`

## Page obligations

- never let ordinary overdraw impersonate authorized burst borrow
- never let authorized borrow hide the harmed claimant set
- always show the borrowed amount separately from the ordinary award
- always show expiry and payback criteria on the same page as authority
- always link backward to contention, occupancy, and envelope lineage and forward to authorization review and receipt

## Stronger-sentence guard

The page may say `claimant is temporarily authorized to exceed the ordinary envelope`.
It may not say `claimant now owns this extra room` unless a later explicit re-award or successor allocation says so.