# Remedy-hardening-attestation successor execution completion lineage receipt page — attributed run, terminal disposition, and blocked stronger completion sentences

## Purpose

This page is the portable receipt summarizing what can honestly be claimed about the completion state of one attributed execution run.
Later pages must cite this receipt instead of improvising `the run completed`, `the reviewed changes fully landed`, or `the mixed state resolved itself` language.

## Receipt header

The header must show:

- receipt identifier
- action identifier
- execution-run identifier
- source execution-provenance receipt identifier
- current execution-completion standing
- current strongest safe sentence
- current blocked stronger sentence

## Mandatory receipt fields

- source execution-provenance receipt identifier
- source preview/commit-binding receipt identifier
- reviewed step-set summary
- started-step-set summary
- completed-step-set summary
- stalled or suspended-step-set summary
- residue summary
- placeholder-versus-byte summary
- queue and background-work summary
- terminal disposition summary
- resumability summary
- contradiction status
- superseding receipt identifier if any

## Standing states

The receipt must support at least these states:

- attributed run exists, not yet started
- attributed run started, completion still partial
- attributed run progressing, terminal disposition open
- attributed run suspended but resumable for named slice only
- attributed run completed for named slice only
- attributed run left blocking residue or contradiction
- later contradiction narrowed prior completion confidence
- receipt superseded

## Primary sentence classes

The receipt must be able to emit at least these classes:

- `attributed run exists; completion still unproven`
- `attributed run started; reviewed completion sentence still blocked`
- `reviewed steps completed for named slice only`
- `some reviewed effects landed; mixed-state residue remains`
- `placeholder-only or missing-byte residue blocks completion sentence`
- `conflict or ghost residue blocks reviewed completion sentence`
- `later contradiction narrowed completion confidence`
- `terminal disposition still open; stronger completion sentence blocked`

## Hard rules

The receipt must never let later pages say:

- this reviewed run completed as reviewed
- the intended bytes are present everywhere they needed to be
- no partial residue survived
- no later contradiction can narrow completion confidence
- completion is settled and final

unless the receipt actually carries the corresponding proof state.
