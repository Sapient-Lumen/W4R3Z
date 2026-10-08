# Remedy-hold lineage receipt page — preserved repair material, coverage, and blocked stronger sentences

## Purpose

This receipt is the concise audit artifact for whether honest repair material was actually under preservation hold at a given moment.
It exists so a later reviewer can see, in one place, what was protected, for whom, until when, and which stronger preservation sentence remained blocked.

## Mandatory receipt fields

- case identifier
- source remedy-substrate receipt identifier
- highest evidenced preservation posture rung overall
- required repair target
- hold-covered cohorts
- uncovered required cohorts
- protected material classes by cohort
- live-source reserved cohorts
- archive-reserved cohorts
- exported-backup reserved cohorts
- manual-duty residues
- retention override summary
- storage reservation summary
- platform ceiling summary
- strongest blocked stronger preservation sentence
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `cure-capable only; no preservation hold active`
- `hold active for named claimants; required cohort still partially uncovered`
- `global never-delete posture present, but case-scoped reservation absent and manual breach risk remains`
- `preservation breached when the held Archive item expired before the requested review completed`
- `required-cohort preservation active, though cure execution and post-repair residue still block any stronger full-repair sentence`

## Receipt invariants

- the receipt never upgrades retention settings into actual hold coverage by omission
- the receipt never hides whether preservation is product-enforced or manual-duty-dependent
- the receipt never hides breach causes such as expiry, manual clear, platform ceiling, storage reclamation, or source loss
- the receipt always preserves the strongest blocked stronger preservation sentence

## Stronger-sentence ceiling

This receipt may support the sentence `repair material for this case is or is not actively preserved to this depth for these cohorts`.
It may not support any stronger claim that clean repair is now guaranteed unless the separate cure-execution and post-repair residue policy agrees.
