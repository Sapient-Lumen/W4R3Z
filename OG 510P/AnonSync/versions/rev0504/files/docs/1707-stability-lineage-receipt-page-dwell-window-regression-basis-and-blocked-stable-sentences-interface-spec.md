# Stability-lineage receipt page — dwell window, regression basis, and blocked stable sentences

## Purpose

This receipt is the concise audit artifact for the stability verdict.
It exists so a later reviewer can see, in one place, whether the effect merely attained, was under observation, earned stable promotion, or was later reopened.

## Mandatory receipt fields

- source act identifier
- source attainment proof identifier
- stability rule version
- current stability rung
- attainment start time
- observation window class
- trusted time basis
- required cohort
- observed cohort
- material reopen powers still outstanding, if any
- regression events counted as material
- residue tolerated, if any
- smallest honest current sentence
- strongest blocked stronger sentence
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `attained but not yet stability-earned because one required offline participant still retains reopen power`
- `stability-earned for the required cohort after a 24-hour clean dwell window with no material regression`
- `previously stability-earned, later reopened by rescan-discovered conflict from offline peer`
- `stable for operational cohort only; fairness-grade stable sentence blocked`

## Receipt invariants

- the receipt never upgrades `attained` into `stable` by omission
- the receipt never hides whether connected-only evidence was used
- the receipt never hides whether the dwell clock was restarted
- the receipt never hides whether a later reopen happened
- the receipt always names the strongest blocked sentence still unavailable

## Stronger-sentence ceiling

This receipt may support the sentence `stable enough for the typed next step under the current rule version`.
It may not support any stronger irreversible sentence unless the relevant authority, enactment, attainment, and time-authority receipts independently agree.
