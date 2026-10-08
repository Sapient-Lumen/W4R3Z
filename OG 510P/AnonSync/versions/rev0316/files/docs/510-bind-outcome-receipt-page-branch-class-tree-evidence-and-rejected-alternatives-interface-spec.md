# Bind outcome receipt page — branch class, tree evidence, and rejected alternatives interface spec

## Purpose

Typed intake receipts preserve what arrived.
Destination receipts preserve which world was chosen.
What still needs a distinct proof object is the answer to:

> what exact branch outcome did I commit at this target tree, what evidence justified it, and what meaningful alternatives did I reject?

This page exists so later troubleshooting, support, and audit do not reconstruct branch meaning from duplicate directories, later merge behavior, or memory.

## Core decision

Every reviewed bind decision with a non-trivial target tree must emit one first-class **Bind outcome receipt**.

That receipt is distinct from:

- typed intake receipt
- destination-world receipt
- later merge receipt
- later encrypted-custody receipt

## Receipt fields

### Required top-level fields

- `bind_outcome_receipt_id`
- `artifact_family`
- `destination_world_ref`
- `bind_lane`
- `target_path`
- `branch_verdict`
- `evidence_summary[]`
- `rejected_alternatives[]`
- `next_handoff_ref`
- `committed_at`
- `acted_by`

### Branch verdict values

Allowed values:

- `attach-same-lineage`
- `merge-into-existing-tree`
- `fork-new-sibling-branch`
- `blocked-same-id`
- `blocked-empty-only-required`
- `abandoned-before-commit`

### Evidence summary rows

Each row should show:

- evidence family
- strength class (`hard`, `strong`, `suggestive`, `missing`)
- short explanation

Examples:

- `same-share-id present · hard`
- `remembered continuity root match · strong`
- `non-empty target with no identity proof · suggestive`
- `ciphertext lane requires empty tree · hard`

### Rejected alternative rows

Each row should show:

- alternative branch
- why it was not chosen
- whether it remains available later

## Fixed receipt order

The receipt should render in this order:

1. **Committed branch strip**
2. **Target and world summary**
3. **Evidence used**
4. **Rejected alternatives**
5. **Next handoff**
6. **Audit/export notes**

### 1) Committed branch strip

Show:

- branch verdict
- target path
- strongest warning that remained true after commit

### 2) Target and world summary

Show:

- artifact family
- destination world
- bind lane
- whether bytes landed now or another deeper review still follows

### 3) Evidence used

Show the evidence rows that justified the verdict.

### 4) Rejected alternatives

Show the strongest alternatives that were explicitly not chosen, such as:

- `fork avoided by reroute`
- `merge deferred pending more proof`
- `empty ciphertext root chosen instead of non-empty ordinary tree`

### 5) Next handoff

Show:

- later merge review opened or not
- later custody review opened or not
- later reuse proof expected or not

### 6) Audit/export notes

Show:

- whether the receipt is safe to export without bearer secrets
- whether local paths need redaction for a given audience
- which previous receipt this one extends

## Main surface

A compact **Bind outcome receipt** card should show:

- committed branch chip
- target path chip
- strongest evidence chip
- next handoff chip

## CLI parity

Minimum commands:

- `anonsync bind-outcome receipt show <receipt-id>`
- `anonsync bind-outcome receipt export <receipt-id>`

## Acceptance criteria

A user can:

- prove later whether a bind was attach, merge, fork, or blocked
- see what evidence justified the verdict at commit time
- see which safer or riskier alternatives were rejected
- bridge this receipt cleanly to later merge, custody, or repair receipts
