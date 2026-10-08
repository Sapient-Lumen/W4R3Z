# Status row proof page — live window, historical window, and residue interface spec

## Purpose

The archive already has many deep object pages.
What it still lacked was one ordinary page for the row-level question:

> this row looks reassuring or alarming; what exact live proof, historical residue, and missing proof are inside it?

## Core decision

AnonSync must expose one first-class **Status row proof** page for any row that combines live state, historical inventory, or threshold-driven residue in one compact display.

## Fixed page order

1. **Row claim decomposition**
2. **Live window proof**
3. **Historical or threshold residue**
4. **Missing proof and claim ceiling**
5. **Action routing**

### 1) Row claim decomposition

Show each compact row field split into its own semantic family.
Example classes:

- live now
- ever seen
- aged out
- hidden from list
- changed at
- landed at
- last attempted

### 2) Live window proof

Show:

- latest live evidence
- what would make the live claim expire
- whether the row is sufficient for routine observation only or stronger action

### 3) Historical or threshold residue

Show:

- remembered peers or seats still counted
- aging thresholds in play
- hidden or disconnected members omitted from the cheerful summary
- whether the row is carrying old facts that still matter

### 4) Missing proof and claim ceiling

Show:

- what the row cannot prove
- strongest safe sentence
- stronger forbidden sentence
- which deeper page would provide the missing proof

### 5) Action routing

Actions may include:

- `Open peer presence review`
- `Open presence witness`
- `Open network eligibility`
- `Open freshness basis`
- `Open change publication`

## Public object

### Status row proof page

Fields:

- `status_row_proof_page_id`
- `row_ref`
- `row_field_rows[]`
- `live_proof_rows[]`
- `historical_residue_rows[]`
- `claim_ceiling`
- `next_pages[]`
- `generated_at`
