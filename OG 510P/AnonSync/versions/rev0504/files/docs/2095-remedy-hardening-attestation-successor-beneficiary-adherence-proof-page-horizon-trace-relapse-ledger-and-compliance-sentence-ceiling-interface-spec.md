# Remedy-hardening-attestation successor beneficiary-adherence proof page — horizon trace, relapse ledger, and compliance sentence ceiling

## Purpose

This page preserves the evidence needed to justify the strongest honest interval sentence about beneficiary adherence.
It is where the archive proves whether the claim is merely present-state alignment, recovered alignment, or genuine uninterrupted adherence across the governed horizon.

## Core sections

### 1. Horizon claim rail

Show:

- governed horizon identifier
- start time
- end time or still-open rule
- lapse-budget class
- current strongest honest adherence sentence

This rail must stay pinned while the operator scrolls.

### 2. Alignment trace

List every positive alignment checkpoint in order, including:

- checkpoint time
- artifact or pointer confirmed
- evidence source
- coverage class (`direct`, `derived`, `weak`)
- confidence effect on the strongest sentence

The page must visually reveal gaps between checkpoints instead of letting them disappear into a single summary.

### 3. Relapse ledger

Each relapse row must preserve:

- relapse identifier
- time opened
- channel (`archive restore`, `offline stale comeback`, `read-only divergence`, `pause`, `scheduler`, `delayed re-detection`, `alternate pointer return`, `other`)
- affected artifact or pointer
- governed-slice impact
- whether the lapse was budgeted
- whether recovery was later proven
- whether uninterrupted-adherence sentence remains blocked

### 4. Recovery ledger

Each recovery row must preserve:

- linked relapse identifier
- time recovered
- recovery mechanism
- proof source
- remaining uncertainty after recovery
- strongest sentence allowed after recovery

### 5. Sentence ceiling panel

This panel must always show:

- strongest honest sentence now
- next stronger sentence blocked
- exact blockers
- whether the blocker is horizon-open, evidence-weak, relapse-open, or interruption-disqualifying

## Visualization rules

The proof page must include:

- a continuous horizon band with visible interruption segments
- distinct visual treatment for `no evidence`, `weak evidence`, and `contradictory evidence`
- a count of unresolved relapse time, not just incident count
- an explicit marker whenever the page only proves present-state alignment rather than whole-horizon adherence

## Interaction requirements

The page must support:

- filtering the trace by relapse channel
- hovering over any gap to see why that interval remains under-proven
- expanding a relapse row into the exact evidence bundle that opened or closed it
- exporting a narrow proof package for one beneficiary and one governed horizon without flattening relapse versus recovery

## Hard rules

The page must never allow:

- a single adoption event to satisfy a whole-horizon proof need
- recovery evidence to erase the fact of prior relapse
- present-state correctness to overwrite interval uncertainty
- a stronger sentence to render unless every blocker has been named
