# Remedy-hold proof page — held objects, retention overrides, and breach risk

## Purpose

This page is the evidentiary companion to the preservation review.
It proves what repair material is merely surviving, what is actively under hold, and why the honest preservation ceiling currently stops where it does.

## Mandatory proof fields

- case identifier
- proof time basis
- source remedy-substrate receipt identifier
- required cohorts
- protected material set
- protected locations
- live-source hold result
- archive hold result
- retention override result
- version-size inclusion result
- scan-or-restart activation result
- storage reservation result
- platform support result
- manual-duty residue
- strongest honest preservation sentence now
- strongest blocked stronger preservation sentence

## Acceptable proof bundles

The proof page must be able to join evidence such as:

- current retention settings plus proof that they actually cover the needed objects
- proof that the critical object was not excluded by version-size ceilings
- proof that required Archive or profile changes were activated and are not merely drafted
- proof that the protected object still exists on named peers or storage locations
- proof that ordinary cleanup or free-space policy is not about to reclaim the held material
- explicit breach signals showing that the hold failed or never covered the needed cohort

## Proof-ceiling examples

The page must support compact proof statements like:

- `cure-capable only: needed bytes survive, but no preservation hold is active and ordinary retention still governs`
- `hold active for named cohorts: archive-backed version is reserved on two desktop peers, though Android-only claimants remain outside the protected lane`
- `hold breach: required object remained above versioning ceiling and was never actually covered by the claimed retention extension`
- `required-cohort hold active: protected bytes, storage headroom, and restore lane are all reserved for the named case until the next review horizon`

## Invariants

- the proof page never upgrades a setting change into active protection without showing coverage of the needed object set
- the proof page never hides when preservation depends on manual duties that remain unperformed
- the proof page always states what evidence would strengthen, breach, or collapse the hold next
