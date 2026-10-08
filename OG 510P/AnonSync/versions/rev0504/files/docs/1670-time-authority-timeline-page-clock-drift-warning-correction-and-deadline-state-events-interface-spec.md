# Time-authority timeline page — clock drift warning, correction, and deadline-state events

## Purpose

This page is the time-ordered witness for how temporal trust changed over the life of a case.
It must answer:

> at each point in time, were deadlines trusted, degraded, frozen, corrected, reopened, or adjudicated, and which stronger time-based sentences became available or blocked?

## Mandatory event classes

### A. Clock-health events

- trusted clock established
- timezone mismatch detected
- skew threshold crossed
- suspect clock warning raised
- peer removed from decisive timing set
- trusted time restored

### B. Timer events

- deadline started
- deadline paused for time integrity
- deadline resumed
- deadline reset
- deadline completed on trusted basis
- deadline completed only provisionally pending review

### C. Correction events

- automatic time correction applied
- manual timezone correction applied
- restart after correction
- prior timer rehabilitated
- prior timer reopened
- adjudicated override issued

### D. Effect events

- protective effect remained active during degraded time
- irreversible effect blocked by temporal integrity
- irreversible effect later matured
- earlier irreversible claim withdrawn after correction
- temporal proof narrowed
- stronger temporal sentence finally earned

## Required fields per event

- event time
- authoritative time class before the event
- authoritative time class after the event
- deadline families affected
- strongest temporal sentence gained or lost
- weaker truths preserved after the event
- exact skew, correction, or adjudication trigger involved

## Required comparisons

The timeline must keep these comparisons explicit:

- `clock healthy` vs `clock usable for irreversible deadlines`
- `deadline running` vs `deadline trustworthy`
- `corrected` vs `rehabilitated`
- `corrected` vs `reopened`
- `protective effect survived` vs `irreversible effect matured`

## Failure modes the page must prevent

- flattening a long period of degraded time into one neat completion timestamp
- forgetting that correction may happen after an apparently completed deadline
- forgetting that some effects can persist while stronger ones remain frozen
- forgetting which event actually restored time trust
- erasing provisional deadline claims after later adjudication or reset

## Stronger-sentence guard

The timeline may show `day 1 execution and deadline start; day 2 skew warning; day 2 timer frozen; day 4 timezone corrected; day 4 timer reset; day 7 trusted cooling completed`.
It may not flatten that into `cooling completed on day 4`.
