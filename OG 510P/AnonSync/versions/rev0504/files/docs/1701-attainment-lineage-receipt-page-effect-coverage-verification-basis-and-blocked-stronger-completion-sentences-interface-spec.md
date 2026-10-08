# Attainment-lineage receipt page — effect coverage, verification basis, and blocked stronger completion sentences

## Purpose

This page is the compact carry-forward receipt for what attainment sentence was actually earned for a specific act version.
It exists so later operators can answer `what outcome really landed, for whom, under what proof basis, and what stronger completion claim is still blocked?` without reopening the whole case.

## Mandatory receipt fields

- source act identifier
- source version identifier
- effect lane covered by this receipt
- highest attainment rung earned
- coverage class
- verification basis class
- residue posture
- highest honest completion sentence earned
- strongest blocked stronger completion sentence
- next event that could strengthen or weaken the receipt

## Required compact verdicts

At minimum the receipt must be able to state verdicts like:

- `execution valid; local attainment only`
- `connected cohort complete; required cohort still open`
- `required cohort complete; verification still pending`
- `verified attained with nonblocking residue`
- `ghost/no-source residue blocks stronger completion sentence`
- `attainment previously claimed; later reopen now active`

## Required comparisons

The receipt must keep these comparisons explicit:

- `execution complete` vs `effect attained`
- `effect attained` vs `verified attained`
- `connected cohort` vs `required cohort`
- `residue absent` vs `warning absent`
- `initial completion sentence` vs `current reopened posture`

## Failure modes the receipt must prevent

- later operators assuming that valid execution itself meant the intended outcome was fully achieved
- later operators assuming that a green check or quiet UI meant all required recipients were covered
- losing whether residue was blocking or tolerated
- losing the exact verification basis on which completion language was allowed
- losing why a stronger fully-complete sentence stayed blocked

## Stronger-sentence guard

This receipt may say `local commit proven; connected cohort caught up; required cohort still incomplete because one named recipient is offline and one announced item remains no-source residue under rescan review`.
It may not say `final completion proven for all required parties` unless that stronger sentence was actually earned.
