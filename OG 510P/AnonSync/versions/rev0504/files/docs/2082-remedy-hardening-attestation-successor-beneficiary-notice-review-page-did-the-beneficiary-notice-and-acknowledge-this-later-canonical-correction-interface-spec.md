# Remedy-hardening-attestation successor beneficiary-notice review page — did the beneficiary notice and acknowledge this later canonical correction?

## Purpose

This page is the decision review that forces the operator to say exactly how far a later correction got with respect to one named beneficiary.
It exists so the operator cannot leave with `we corrected it` when the real state is only `we published it`, `their device could have shown it`, or `they probably saw it`.

## Review question

The page must force a direct answer to:

**did this named beneficiary notice this later canonical correction, and if acknowledgement was required, was that acknowledgement actually completed?**

## Required sections

### 1. Correction and policy summary

Show:

- correction identifier and class
- beneficiary identifier
- source beneficiary-authority receipt
- notice policy
- acknowledgement requirement
- deadline / escalation policy

### 2. Carrier selection and delivery posture

Show all eligible carriers and mark one or more as:

- intended carrier
- observed carrier
- degraded carrier
- unavailable carrier
- ambiguous carrier

Supported carrier classes must include at least:

- in-product notification surface
- history/activity surface
- sync-state-only surface
- explicit review inbox or correction queue
- exported receipt or external notice channel
- manual-open required surface

### 3. Beneficiary observation evidence

For each evidence item show:

- evidence identifier
- evidence class (`device-surfaced`, `opened`, `focused`, `viewed`, `clicked`, `dismissed`, `signed`, `responded`)
- beneficiary binding strength
- timestamp
- whether this proves only surfacing, likely seeing, or explicit acknowledgement

The page must visually separate:

- `surfaced to beneficiary environment`
- `beneficiary likely saw`
- `beneficiary explicitly acknowledged`

### 4. Acknowledgement boundary

Show:

- whether acknowledgement is required for policy compliance
- whether acknowledgement is required only for high-severity corrections
- whether acknowledgement is complete, missing, stale, expired, or superseded
- whether follow-up corrections inherited or reset the acknowledgement requirement

### 5. Strongest-honest-sentence worksheet

The page must force the reviewer to choose one and only one primary sentence class:

- `later correction exists; beneficiary notice still unproven`
- `later correction reached the beneficiary environment; seen state still unproven`
- `beneficiary likely saw the correction; acknowledgement still unproven`
- `beneficiary acknowledged the correction under current policy`
- `beneficiary acknowledgement missing or overdue`
- `later contradiction narrowed prior notice confidence`

## Required layout

### Left column — intended correction contract

Show:

- governed slice
- correction severity
- notice policy
- acknowledgement rule
- escalation ladder
- unacceptable substitute states

### Right column — actual beneficiary-notice evidence

Show:

- actual carrier path
- actual surfacing evidence
- actual seen evidence
- actual acknowledgement evidence
- degradation / expiry factors
- blocker-by-blocker reasoning

### Bottom section — decision worksheet

This section must offer explicit toggles for the reviewer to mark:

- `surface only; no seen proof`
- `seen likely; acknowledgement still missing`
- `acknowledgement optional and absent`
- `acknowledgement required and overdue`
- `evidence too weak or too stale for stronger sentence`

Each toggle must immediately update the strongest-honest-sentence preview.

## Hard rules

The review must never let the operator leave without answering:

- through what carrier the correction was meant to reach the beneficiary
- whether it actually surfaced in that carrier
- whether any evidence proves the beneficiary saw it
- whether acknowledgement was required
- whether acknowledgement was actually completed
