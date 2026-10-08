# Cohort census lineage receipt page: live set, roster basis, and capability ceiling interface spec

## Purpose

The contract sheet explains the cohort now.
The review and proof pages explain why.
This receipt preserves the specific answer that was safe at one moment.

It exists so later operators can answer:

> what exactly did we mean by the participant count at this time, and what stronger resilience sentence did we refuse to make?

## Receipt sections

1. **Header**
2. **Counting basis snapshot**
3. **Current capability snapshot**
4. **Historical / hidden residue snapshot**
5. **Blocked stronger sentence**
6. **Reopen triggers**

### 1) Header

Show:

- `cohort_receipt_id`
- subject ref
- issued_at
- operator / actor
- strongest safe sentence

### 2) Counting basis snapshot

Must preserve at least:

- `live_reachable_count`
- `historical_roster_count`
- `visible_row_count`
- `source_capable_independent_count`
- `authority_capable_count`
- `self_derived_branch_count`
- `counting_basis_summary`

### 3) Current capability snapshot

For each named critical row, preserve:

- online proof grade
- source-capable grade
- serve-eligible grade
- authority-capable grade
- independence class

### 4) Historical / hidden residue snapshot

Preserve:

- hidden rows that can reappear automatically
- disconnected gray rows
- visibility-only disconnected rows
- auto-expired rows
- severed rows excluded from the cohort

### 5) Blocked stronger sentence

Examples:

- `We did not claim multi-source resilience because only one independent source-capable peer was proved live.`
- `We did not claim the hidden roster was gone because those rows could reappear automatically.`
- `We did not claim five peers added five-way redundancy because two rows were self-derived local branches.`

### 6) Reopen triggers

A receipt must declare it stale and reopen if any of these happen:

- a hidden row returns online
- a live independent source-capable row goes stale or auto-expires
- a self-derived branch is mistaken for independent redundancy by a later surface
- counting-basis logic changes
- detachment / revocation changes cohort membership

## Hard rules

- receipts must preserve both the displayed count and the counting basis
- receipts must preserve independence class for every row used in a resilience claim
- receipts must preserve the blocked stronger sentence verbatim
- receipts must never summarize `3 of 7 peers` without the typed expansion
