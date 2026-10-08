# Downstream-consequence lineage receipt page — world change, compensation posture, and blocked stronger reversal sentences

## Purpose

This receipt is the concise audit artifact for what a sentence version already changed downstream.
It exists so a later reviewer can see, in one place, which world mutations fired, what repair lane remains honest, and what residue still blocks stronger rollback language.

## Mandatory receipt fields

- case identifier
- source consumer-uptake receipt identifier
- sentence version handle
- highest evidenced downstream-consequence rung overall
- consequence cohorts by strongest rung
- haltable cohorts
- rollback-available cohorts
- compensation-owed cohorts
- compensation-cleared cohorts
- irreversible-residue cohorts
- unknown or contested cohorts
- strongest blocked stronger reversal sentence
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `sentence used, but no downstream world mutation proven`
- `sentence used and local mutation started, but halt occurred before required-cohort world change`
- `sentence version S-18 already changed connected-cohort state; direct rollback is incomplete and compensation debt remains`
- `sentence version S-18 produced irreversible external residue; compensation may narrow harm but cannot honestly erase the consequence`
- `superseding sentence is current, but older sentence residue still survives on named cohorts`

## Receipt invariants

- the receipt never upgrades decision use into world mutation by omission
- the receipt never hides which consequence cohort actually changed
- the receipt never hides the difference between rollback, inverse action, compensation, and residue
- the receipt never hides contested or inferred evidence
- the receipt always preserves the strongest blocked stronger reversal sentence

## Stronger-sentence ceiling

This receipt may support the sentence `these named downstream consequences did or did not happen to this depth`.
It may not support any stronger claim that the world is fully repaired unless the relevant compensation and residue policy separately agrees.
