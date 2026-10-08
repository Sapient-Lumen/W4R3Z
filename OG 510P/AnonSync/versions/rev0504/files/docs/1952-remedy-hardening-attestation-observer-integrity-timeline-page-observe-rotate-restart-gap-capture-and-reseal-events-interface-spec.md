# Remedy-hardening-attestation observer-integrity timeline page — observe, rotate, restart, gap, capture, and reseal events

## Purpose

This page is the ordered event view for evidence-trust questions after conformance review.
It exists so later operators can see whether the case moved from weak clues into trusted observation, or whether rotation loss, world change, blind spots, or forensic-only detours kept the stronger sentence blocked.

## Event classes

The timeline must support at least these events:

- target sentence selected for evidentiary review
- observer lane enabled
- restart confirmed after enabling capture
- reproduction window opened
- reproduction window closed too early
- retention budget changed
- log rotated or old file discarded
- history horizon exceeded
- peer visibility expired
- storage world or service user changed
- sibling world discovered
- forensic dump capture requested
- dump captured from terminal or external lane
- blind spot opened
- known instrumentation omission attached
- tamper suspicion opened
- evidence trust upgraded
- evidence trust downgraded
- stronger sentence blocked
- evidence trust restored after re-capture

## Required columns

- timestamp
- event class
- affected witness lane
- source evidence reference
- resulting observer-integrity class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- enabling logging and restart confirmation into one event by default
- fresh artifact arrival and trustworthy observation into one event by default
- log rotation and benign retention metadata into one event by default
- storage-world change and scope continuity into one event by default
- dump capture and restored evidence trust into one event by default
