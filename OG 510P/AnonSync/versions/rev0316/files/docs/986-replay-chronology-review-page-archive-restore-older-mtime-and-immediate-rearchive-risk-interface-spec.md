# Replay chronology review page — archive restore, older mtime, and immediate re-archive risk

## Purpose

Own the specific workflow where a retained or archived candidate is reintroduced into a live subject whose current chronology may still outrank it.

This page answers:

> if I restore this candidate now, will it actually replay, merely sit locally, lose immediately, or bounce back into retention?

## Page order

1. candidate summary
2. time-authority basis
3. runtime condition card
4. winner forecast
5. safer replay ladder
6. apply barrier

### 1) Candidate summary

Show:

- selected retained candidate
- archived-at time
- original/source `mtime` if known
- destination subject

### 2) Time-authority basis

Show:

- active chronology basis
- whether restored candidate is older or newer under that basis
- skew-confidence class
- whether disk-visible time is trustworthy here

### 3) Runtime condition card

Show:

- whether the core/runtime must be actively running during restore
- whether replay depends on immediate publication versus later rescan
- whether peer reachability matters now

### 4) Winner forecast

Allowed verdicts:

- `replay expected to win`
- `local inspection only`
- `immediate re-archive risk`
- `likely remote overwrite`
- `chronology unsafe; manual side-by-side only`

### 5) Safer replay ladder

Possible next actions:

- `Restore side-by-side`
- `Restore live while runtime is active`
- `Pause and repair time authority first`
- `Export retained candidate without live replay`

### 6) Apply barrier

Before apply, require an explicit sentence acknowledging:

- current winner forecast
- whether re-archive or overwrite remains possible
- what stronger claim is still blocked

## Mandatory fields

- candidate identifier
- destination subject
- source/original `mtime`
- archive time
- time-authority basis
- runtime-needed verdict
- winner forecast
- stronger rejected sentence

## Interaction rules

- `Restore` must never be a bare primary button when the forecast is not plainly winning.
- If the main safe action is side-by-side recovery, make that the default CTA.
- Receipts must preserve whether replay depended on runtime being active at the moment of reintroduction.
