# Remedy-hardening-attestation successor execution completion proof page — terminal state, partial effects, and completion ceiling

## Purpose

This page is the durable proof artifact that preserves how far one attributed run actually got, which reviewed steps finished, which remained partial, which residue survived, and what stronger completion sentence therefore stayed blocked.

## Minimum proof bundle

The proof page must preserve at least:

- source execution-provenance receipt identifier
- source preview/commit-binding receipt identifier
- execution-run identifier
- reviewed step-set summary
- observed started-step-set summary
- observed completed-step-set summary
- observed stalled or suspended-step-set summary
- placeholder-versus-byte presence evidence
- queue and priority evidence
- pause or rescan evidence
- conflict or ghost evidence
- terminal disposition evidence
- resumability evidence
- contradiction evidence
- strongest safe sentence at proof time
- strongest blocked stronger sentence at proof time

## Proof sections

### 1. Claimed completion summary

Show:

- what steps were supposed to complete
- what completion for the named slice would have looked like
- what residue classes were forbidden
- what terminal disposition would have justified upgrade

### 2. Observed phase trace

For each observed phase component show:

- event time
- source actor or process
- source world
- reviewed step involved
- before state
- after state
- observer quality
- pass / fail / unknown for completion of that step

### 3. Residue ledger

For each residue family show:

- why it matters
- whether it remained hypothetical or became evidenced
- whether it is resumable, compensable, or terminally blocking
- whether it alone blocks the stronger completion sentence

### 4. Completion ceiling statement

The page must end with a bounded statement such as:

- `run completed for named slice only; broader reviewed completion still blocked`
- `run started and partially progressed; terminal disposition still open`
- `bytes absent for some reviewed members; placeholder-only state blocks completion sentence`
- `conflict or ghost residue remains; reviewed completion sentence blocked`
- `later contradiction narrowed prior completion confidence`

## Evidence grading

The proof page must support at least these grades:

- run planned only, not yet started
- run started, completion still partial
- run progressing with terminal disposition still open
- run suspended but resumable for named slice only
- run completed for named slice only
- run left blocking residue or contradiction
- completion receipt later narrowed or superseded

## Hard rules

The page must never:

- treat visibility as presence proof
- treat a quiet queue as completion proof
- erase partial residue from the record
- treat resumability as completion
- upgrade to `reviewed run completed as reviewed` merely because the first intended effect appeared
