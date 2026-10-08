# Remedy-substrate lineage receipt page — cure capability, repair material, and blocked clean-repair sentences

## Purpose

This receipt is the concise audit artifact for whether honest cure was still materially available at a given moment.
It exists so a later reviewer can see, in one place, what repair substrate survived, what decay risk applied, and which stronger clean-repair sentence remained blocked.

## Mandatory receipt fields

- case identifier
- source downstream-consequence receipt identifier
- highest evidenced remedy posture rung overall
- required repair target
- cure-capable cohorts
- partial-cure-only cohorts
- compensation-only cohorts
- repair material classes by cohort
- live-source cohorts
- archive-backed cohorts
- placeholder-only cohorts
- unreadable-custody-only cohorts
- expiry risk summary
- free-space and runtime blocker summary
- platform ceiling summary
- strongest blocked stronger cure sentence
- next strengthening trigger
- next weakening trigger

## Required compact summaries

The receipt must be able to summarize outcomes like:

- `compensation owed; no surviving repair substrate evidenced`
- `repair material survives only in Archive on one desktop peer; partial cure remains possible for named claimants`
- `required-cohort cure blocked because the only surviving object exceeded versioning ceiling and was never archived`
- `cure lane collapsed after retention expiry; adjudication evidence survives but clean repair does not`
- `cure-proven for named cohorts, but public residue still blocks any stronger sentence that nothing downstream remains`

## Receipt invariants

- the receipt never upgrades archive visibility into cure proof by omission
- the receipt never upgrades placeholder knowledge into source survival
- the receipt never hides collapse causes such as expiry, no-source state, free-space failure, or platform limits
- the receipt always preserves the strongest blocked stronger cure sentence

## Stronger-sentence ceiling

This receipt may support the sentence `clean cure is or is not still materially available to this depth for these cohorts`.
It may not support any stronger claim that all harm is repaired unless the separate cure-execution and post-repair residue policy agrees.
