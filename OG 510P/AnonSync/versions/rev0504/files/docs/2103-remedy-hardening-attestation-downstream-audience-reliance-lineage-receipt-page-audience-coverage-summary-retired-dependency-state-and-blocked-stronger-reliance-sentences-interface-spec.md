# Remedy-hardening-attestation downstream audience reliance lineage receipt page — audience coverage summary, retired dependency state, and blocked stronger reliance sentences

## Purpose

This receipt compresses the audience-wide reliance verdict into a portable record without flattening downstream coverage truth.
It exists so later readers can see whether the correction repaired only one beneficiary, a narrow downstream ring, or the full named audience boundary.

## Minimum receipt fields

The receipt must show at least:

- receipt identifier
- governed audience identifier
- governed slice identifier
- canonical correction identifier
- dependency graph version
- audience boundary rule
- current coverage class
- unresolved stale-dependency count
- strongest honest reliance sentence
- blocked stronger audience-wide sentence
- supersession state

## Required summary sentence

The receipt must render one sentence in plain language, such as:

- beneficiary-local adherence proven; audience-wide stale-dependency retirement remains unproven
- direct dependents refreshed, but stale delegated residue still blocks audience-wide sentence
- named audience boundary no longer relies on stale material; broader public-representation sentence remains blocked

The receipt must always preserve the blocked stronger sentence directly underneath.

## Required badges

Show compact badges for:

- beneficiary-only / narrow downstream / named audience repaired
- direct coverage / delegated coverage / transitive coverage
- stale residue open / none seen / unresolved
- named-boundary only / broader public blocked
- present-state graph / decayed evidence warning

## Portable truth requirement

A reader opening only this receipt must still be able to tell:

- whether the result is beneficiary-local or audience-wide
- whether downstream stale residue remains
- whether the proof includes transitive coverage or only direct coverage
- whether the sentence is narrow to one named boundary
- whether a stronger public-truth sentence is still blocked

## Hard rules

The receipt must never allow:

- `beneficiary repaired` to replace `audience repaired`
- `peer revoked` to replace `stale copy retired`
- `direct coverage` to replace `transitive coverage`
- a named-audience result to impersonate repaired public representation
