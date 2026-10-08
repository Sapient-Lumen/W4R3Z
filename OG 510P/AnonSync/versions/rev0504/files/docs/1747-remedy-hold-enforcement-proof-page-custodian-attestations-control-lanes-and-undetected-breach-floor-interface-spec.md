# Remedy-hold-enforcement proof page — custodian attestations, control lanes, and undetected-breach floor

## Purpose

This page is the evidence view for proving that a preservation hold is not merely declared but meaningfully binding.
It exists so later operators can inspect whether enforcement rests on acknowledgments, policy suppression, runtime controls, or merely optimistic interpretation.

## Proof bundles

The page must preserve at least these evidence bundles:

- custodian attestations and acknowledgment timestamps
- control-plane settings that suppress ordinary cleanup or retention expiration
- platform-specific enforcement gaps and exceptions
- notification coverage and blind-spot notes
- rescan-window assumptions where immediate sensing is absent
- storage pressure or deletion policy risks that remain unsuppressed
- observed breach events or near-breach incidents
- strongest blocked stronger enforcement sentence

## Required evidence distinctions

The page must keep separate:

- evidence that the hold was requested
- evidence that a custodian acknowledged the hold
- evidence that a cleanup path was actually suppressed
- evidence that a breach would be surfaced quickly enough
- evidence that one lane is protected versus all required lanes being protected
- evidence that no breach was detected versus evidence that no undetected breach was plausible inside the covered window

## Minimum evidence questions

The proof page must answer:

- who actually acknowledged preservation duty
- which material classes each custodian still controls
- which deletion, purge, disablement, or reclamation paths remain live
- how quickly a breach would become visible on each environment
- whether any required lane still depends on manual memory rather than enforced controls
- what the current undetected-breach floor is

## Proof verdict vocabulary

The page must support verdicts such as:

- `acknowledged but not enforced`
- `enforced on desktop lanes only`
- `enforced with rescan-latency blind spot`
- `enforced for required custodians with one delegated-storage exception`
- `breach observed`
- `no breach observed but undetected-breach floor remains material`
