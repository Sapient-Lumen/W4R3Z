# Remedy-hold-enforcement lineage receipt page — enforcement coverage, breach detectability, and blocked stronger sentences

## Purpose

This receipt is the durable compact proof of how strong the preservation hold really was at a specific moment.
It exists so later readers can see whether the product was honest about enforcement rather than merely optimistic about retention.

## Receipt body

The receipt must record:

- case identifier
- source remedy-hold receipt identifier
- current enforcement posture rung
- required custodians count
- acknowledged custodians count
- required lanes protected count
- known blind spots
- breach-detection basis
- undetected-breach floor
- last audit time
- strongest honest sentence
- strongest blocked stronger sentence
- exact blocker summary

## Receipt sentence families

The receipt must support concise summaries such as:

- `hold active but not yet binding on all required custodians`
- `hold binding on required custodians, but one cleanup lane remains unsuppressed`
- `hold enforced with delayed breach visibility until next rescan`
- `hold breached after manual clear on one custodian`
- `hold released after audit-clean enforcement window`

## Invariants

- the receipt never compresses acknowledgment, enforcement, and detectability into one word
- the receipt never hides blind spots just because no breach has been observed yet
- the receipt always preserves the blocker that prevented the stronger sentence
