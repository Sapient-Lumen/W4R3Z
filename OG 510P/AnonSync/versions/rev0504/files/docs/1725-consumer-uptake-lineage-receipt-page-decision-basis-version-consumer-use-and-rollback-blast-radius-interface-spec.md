# Consumer-uptake lineage receipt page — decision-basis version, consumer use, and rollback blast radius

## Purpose

This receipt is the concise audit artifact for how a current sentence was actually consumed.
It exists so a later reviewer can see, in one place, which sentence version was current, which cohorts pinned it, which cohorts used it, and what rollback blast radius survived.

## Mandatory receipt fields

- case identifier
- source current-sentence receipt identifier
- strongest sentence currently operative at issuance time
- sentence version handle
- fallback sentence if rollback occurs
- consumer cohorts by strongest uptake class
- decision-bound cohorts
- action-started cohorts
- action-completed reversible cohorts
- action-completed irreversible cohorts
- rollback-cleared cohorts
- unknown or contested cohorts
- strongest blocked rollback sentence
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `sentence current but only rendered; no pinned or decision-bound cohorts proven`
- `sentence current and pinned by automation cohort, but not yet used for a bound decision`
- `sentence version S-17 used by human review cohort for a reversible decision; rollback remains available with compensation`
- `sentence version S-17 already drove irreversible downstream action for public cohort; rollback of that path is blocked and residue annotation remains`
- `superseding sentence S-18 is current, but cohorts B and C still carry decision residue from S-17`

## Receipt invariants

- the receipt never upgrades currentness into decision use by omission
- the receipt never hides version-specific uptake
- the receipt never hides the difference between reversible and irreversible downstream acts
- the receipt never hides contested or inferred evidence
- the receipt always preserves the strongest blocked rollback sentence

## Stronger-sentence ceiling

This receipt may support the sentence `these named cohorts did or did not consume this sentence version to this depth`.
It may not support any stronger normative claim about whether that consumption was good, fair, or compensable unless the relevant policy row separately agrees.
