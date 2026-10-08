
# Loss-class matrix and salvage-ladder component family interface spec

## Purpose

The archive now has several pages that need to explain destructive risk.
They should not each invent their own miniature warning language.
This document fixes the shared component family for two core questions:

> what exact work is at risk?

> what exact rescue ladder still exists before approval?

## Core decision

AnonSync must treat the **loss-class matrix** and **salvage ladder** as reusable semantic components, not ad hoc warning copy.
Any page that exposes destructive review, source-authoritative repair, destructive re-home, encrypted-seat reset, or successor-abandonment choice must render these same row contracts.

## Component 1: Loss-class matrix

### Required row families

The matrix must have stable rows for at least:

- edited existing material
- locally renamed material
- locally deleted material
- locally added material
- archived prior versions
- trash/recycle dependent material
- remote-only rescue candidates
- successor-only survivors
- unsalvageable local residue

### Required columns

Every row must preserve this order:

1. **work family**
2. **current holder/locality**
3. **post-action fate**
4. **best rescue rung**
5. **time pressure / expiry pressure**
6. **same-line vs side-survival verdict**
7. **proof confidence**
8. **safe sentence fragment**

### Allowed fate vocabulary

Rows must use a bounded vocabulary:

- `reverted in place`
- `restored from source`
- `left local-only`
- `survives only as residue`
- `recoverable before action`
- `recoverable only elsewhere`
- `already unsalvageable here`
- `unknown pending more proof`

Do not let vague words like `affected`, `changed`, or `may be lost` stand in for these fates.

### Interaction rules

- row click opens proof drawer to the evidence for that classification
- row compare opens before/after or source/locality compare when available
- row warnings must persist into the approval barrier without restating them differently

## Component 2: Salvage ladder

### Required rung families

The ladder must support these ordered rung types:

1. local trash / recycle
2. local archive
3. local snapshot / exported evidence
4. remote archive
5. remote live holder
6. successor branch / side promotion
7. no remaining easy salvage

### Required rung fields

Every rung must preserve this order:

1. **rung label**
2. **holder/locality**
3. **availability now**
4. **expiry or reachability pressure**
5. **recovery shape** (`same-line`, `side-survival`, `proof-only`)
6. **operator effort class**
7. **resulting claim ceiling**

### Rung states

Use a bounded state set:

- `available-now`
- `available-with-extra-step`
- `holder-unreachable`
- `expiring-soon`
- `spent`
- `not-applicable`
- `unknown`

### Ordering rule

The ladder must be ordered by safest/cheapest honest rescue first, not by storage location or implementation convenience.

## Cross-component rule

The matrix and ladder must cross-link.
Every loss row should name its best current rescue rung.
Every salvage rung should name which loss rows it helps.

## Copy rule

A page may summarize these components.
It may not replace them with a single sentence like `some local changes may be overwritten`.

## Public objects

### Loss-class matrix

Fields:

- `loss_class_matrix_id`
- `scope_ref`
- `row_groups[]`
- `overall_verdict`
- `strongest_safe_sentence`
- `generated_at`

### Salvage ladder

Fields:

- `salvage_ladder_id`
- `scope_ref`
- `rung_rows[]`
- `best_next_rung`
- `overall_viability_verdict`
- `generated_at`
