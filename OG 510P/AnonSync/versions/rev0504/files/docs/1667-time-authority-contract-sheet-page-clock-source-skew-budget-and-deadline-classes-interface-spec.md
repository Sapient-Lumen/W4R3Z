# Time-authority contract sheet page — clock source, skew budget, and deadline classes

## Purpose

This page is the canonical declaration of how the product decides whether time-based claims are trustworthy.
It exists so the product can stop pretending that `timestamp present`, `UTC shown`, and `deadline valid` are the same truth.

The page must answer:

> for each action family and timer family in this case, what time source is authoritative, what skew budget is tolerated, when does time integrity degrade, and which deadline classes remain trustworthy?

## Mandatory time classes

At minimum the page must expose these classes separately:

- local device clock
- peer-reported clock
- normalized UTC projection
- file modification time
- action execution time
- notice delivery time
- notice completion time
- cooling start time
- cooling satisfaction time
- expiry time
- adjudicated override time

The implementation may add more classes, but it may not collapse them into one generic `timestamp`.

## Mandatory blocks

### A. Time-source block

- action family or timer family
- authoritative time source
- fallback time source
- whether the source is single-device, multi-peer, or adjudicated
- whether file mtimes are evidentiary, operational-only, or forbidden for this timer class

### B. Skew block

- tolerated skew budget
- tolerated timezone mismatch budget
- trusted clock class
- degraded clock class
- suspect clock class
- exact event that downgrades a timer from trusted to degraded or suspect

### C. Deadline block

- timer family name
- trigger that starts the timer
- whether the timer may run on degraded clocks
- whether the timer may ever mature on suspect clocks
- strongest sentence earned while time basis is only degraded
- stronger sentence earned only on trusted time basis

### D. Correction block

- what happens after clock correction
- whether prior timer progress is preserved, paused, reset, or manually reviewed
- whether already effective protective acts survive correction
- whether irreversible acts reopen automatically after correction
- manual adjudication route if clocks remain disputed

### E. Evidence block

- decisive clock-health evidence
- decisive normalization evidence
- decisive timer-start evidence
- decisive correction events
- evidence horizon after which temporal proof weakens

## Required comparisons

The page must keep these comparisons explicit:

- `timestamp observed` vs `deadline trusted`
- `local clock` vs `normalized UTC`
- `file mtime` vs `act time`
- `timer running` vs `timer trustworthy`
- `clock corrected` vs `deadline rehabilitated`

## Required badges

- `trusted-clock`
- `degraded-clock`
- `suspect-clock`
- `mtime-only`
- `deadline-running`
- `deadline-paused-for-time`
- `deadline-reset`
- `adjudicated-time`
- `irreversible-blocked-by-time`
- `protective-time-ok`

## Failure modes the page must prevent

- treating any displayed timestamp as sufficient proof that a fairness deadline matured
- treating file mtime as if it were the same thing as execution or notice time
- letting skew warnings remain cosmetic while irreversible timers keep advancing
- letting clock correction silently preserve a deadline that should be paused, reset, or reviewed
- forgetting that some protective consequences may survive while stronger irreversible consequences are frozen

## Stronger-sentence guard

The page may say `protective freeze can start on degraded clocks, but final waiver cooling cannot complete until trusted time basis is restored`.
It may not say `deadline elapsed` unless the exact deadline row says the time basis was strong enough for that sentence.
