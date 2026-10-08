# Remedy-hardening-attestation successor beneficiary-adherence review page — did the beneficiary stay switched through the governed horizon?

## Purpose

This review page forces the operator to answer the harder interval question after beneficiary adoption:
not `did they switch once?`, but `did they stay switched for the whole governed horizon, and if not, what exactly broke that stronger sentence?`

## Review prompt

The page must begin with this sentence in operator-facing form:

**Did the named beneficiary stay switched to the corrected working state through the governed horizon, without unbudgeted relapse, stale comeback, or unresolved interruption?**

## Required direct answers

The reviewer must answer, explicitly and separately:

1. What is the governed horizon for this claim?
2. What counts as a relapse for this beneficiary and governed slice?
3. Was there any interval where the beneficiary was merely currently-correct rather than continuously-correct?
4. Did any archive restore, offline stale comeback, read-only divergence, pause window, scheduler hold, or delayed-detection interval keep the stronger sentence blocked?
5. If relapse occurred, was recovery proven, partial, or absent?
6. Is the strongest honest sentence `uninterrupted adherence`, `recovered after relapse`, `currently aligned but historical gap unresolved`, or `adoption only`?

## Required review cards

### Horizon card

Show:

- horizon start
- horizon end or still-open rule
- closure condition
- lapse-budget class

### Relapse-channel card

Show at least these channels:

- archive restore or manual stale restoration
- offline stale comeback
- read-only local divergence
- paused or scheduler-held interval
- delayed-detection interval
- stale derivative or alternate working-pointer return

Each channel must carry:

- observed
- not observed
- insufficiently observed
- observed but recovered
- observed and still blocking stronger sentence

### Strongest-sentence card

The page must force the reviewer to choose one:

- adoption proven, adherence not proven
- currently aligned, historical gap unresolved
- relapsed then recovered
- uninterrupted adherence for governed horizon
- broader compliance still blocked

### Narrowing card

Show every reason the stronger sentence is still blocked, including:

- missing horizon evidence
- open relapse interval
- recovery without bounded interruption proof
- detection coverage too weak
- stale downstream pointer not retired
- horizon still open

## Comparison rail

The page must keep these pairs visibly separate:

- adopted once / stayed switched
- currently aligned / continuously aligned
- recovered / uninterrupted
- no contradiction seen / positive proof
- beneficiary-local adherence / broader compliance

## Interaction requirements

The reviewer must be able to:

- click any relapse channel and see the specific evidence or lack of evidence behind the current standing
- open a horizon drawer that shows every interval with no positive adherence evidence
- downgrade the strongest sentence in one gesture when a relapse is logged
- compare multiple candidate wordings before locking the strongest honest sentence

## Hard rules

The page must never allow:

- the governed horizon to remain implicit
- a relapse to disappear merely because the current state looks corrected
- `recovered` to default to `uninterrupted`
- `currently synced` to stand in for `stayed switched`
