# Device roster page: hidden offline, duplicate, and returning seat interpretation interface spec

## Purpose

The archive already has strong roster, retirement, and continuity doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> what exactly is this row in my device roster — a live seat, an offline but still linked seat, a hidden row that may return, a duplicate reset artifact, or a stale row I should retire?

## Core decision

Every serious multi-seat product must own one first-class **Device roster** page.
That page is the semantic home of:

- roster row classification
- current reachability
- linkage / retirement state
- duplication / residue interpretation
- strongest next-safe action
- roster receipts

The product must not let `offline`, `hidden`, or `duplicate-looking` rows carry the whole semantic load by themselves.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. roster-row strip
2. row-classification card
3. reachability-and-linkage card
4. duplicate / residue interpretation card
5. retirement-and-return card
6. recent roster receipts
7. expert details drawer

### 1) Roster-row strip

Show:

- row label
- current best seat identity handle
- strongest next-safe action
- whether the row is live, stale, hidden, or historical-only

The strip should answer `which row am I looking at right now?`

### 2) Row-classification card

Show one explicit verdict:

- `live linked seat`
- `offline but still linked`
- `hidden row that may return`
- `duplicate artifact from reset or rehome`
- `reviewed successor pair`
- `stale row awaiting retirement`
- `insufficient evidence`

### 3) Reachability-and-linkage card

Show:

- reachability state
- whether the row is still linked
- whether hide is only presentation-level
- whether unlink / retire has happened
- whether remote unlink is impossible from current posture

This card should answer `is this row gone, or only absent from view / network right now?`

### 4) Duplicate / residue interpretation card

Show:

- why the row looks duplicate
- whether the duplicate is benign residue or a second live seat
- whether a reset, rehome, service-world shift, or app reinstall likely created it
- what evidence would upgrade or downgrade that interpretation

This card should answer `is this duplicate dangerous, harmless, or unresolved?`

### 5) Retirement-and-return card

Offer actions such as:

- `Hide row only`
- `Retire stale row`
- `Keep because seat may return`
- `Open seat-lineage review`
- `Treat as fresh foreign seat`

Every action must preview whether the row can reappear later and whether trust / grants remain live.

### 6) Recent roster receipts

Show recent receipts with:

- row
- classification verdict
- hide / retire / lineage decision
- deciding operator / seat
- return or reappearance witness

### 7) Expert details drawer

Hide raw peer IDs, observation timestamps, list-origin details, and reappearance witnesses behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. row phrase
2. classification phrase
3. linkage phrase
4. duplicate/residue phrase
5. strongest next action

Example:

```text
Desktop-old row · hidden residue that may return · still linked, not retired · likely duplicated by credential reset on 2026-03-21 · Open seat-lineage review before retirement
```

## Mandatory fields

- `roster_row_ref`
- `best_identity_handle`
- `row_classification_verdict`
- `reachability_state`
- `linkage_state`
- `duplicate_interpretation_summary`
- `return_risk_summary`
- `available_roster_actions[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- distinguish hidden rows from truly retired seats
- tell whether a duplicate-looking row is live or merely residue
- preserve continuity review before retiring ambiguous rows
- predict whether the row may legitimately reappear later
