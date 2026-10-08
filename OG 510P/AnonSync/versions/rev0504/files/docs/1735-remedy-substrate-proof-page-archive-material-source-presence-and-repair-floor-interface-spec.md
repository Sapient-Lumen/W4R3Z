# Remedy-substrate proof page — archive material, source presence, and repair floor

## Purpose

This page is the evidentiary companion to the remedy-capability review.
It proves what repair material still exists, what has already decayed, and how high the honest repair floor currently reaches.

## Mandatory proof fields

- case identifier
- proof time basis
- source downstream-consequence receipt identifier
- required cohorts
- currently evidenced live sources
- currently evidenced archive sources
- placeholder-only locations
- no-source warnings in force
- retention horizon snapshots
- version-size coverage result
- free-space sufficiency result
- platform access result
- background/runtime sufficiency result
- strongest honest cure sentence now
- strongest blocked stronger cure sentence

## Acceptable proof bundles

The proof page must be able to join evidence such as:

- archive retention settings and current age of the needed object
- restore-path witness that the needed material is still accessible on a platform that supports restore
- source-peer proof that at least one peer still has full bytes rather than only placeholder knowledge
- free-space witness showing the restore/download lane can actually complete
- runtime witness showing the restore lane can run long enough to finish on the required platform
- explicit no-source or placeholder-only warnings that cap the repair floor

## Proof-floor examples

The page must support compact proof statements like:

- `clean cure blocked: only placeholders remain and no source-capable peer is evidenced`
- `partial cure possible: archive-backed prior version survives on one desktop peer, but required mobile cohort lacks a supported restore lane`
- `required-cohort cure-capable: archive-backed or live-source material exists on named peers, retention horizon is open, and current free-space headroom clears the restore lane`
- `repair floor degraded since last review because archive TTL now expired for the last complete version`

## Invariants

- the proof page never upgrades past the strongest evidence actually joined
- the proof page never treats unreadable encrypted custody as equivalent to readable cure material
- the proof page never hides when the repair floor is based on manual steps that have not yet been executed
- the proof page always states what evidence would strengthen or collapse the current cure sentence next
