# Salvage export receipt page — preserved remnant proof and reintroduction ceiling interface spec

## Purpose

A pre-destructive export should leave behind a durable object that says what was actually preserved and what that preservation still does not mean.
This page exists to prevent later folklore such as:

> we exported it first, so nothing was really at risk anymore.

## Core decision

AnonSync must emit one first-class **Salvage export receipt** whenever at-risk residue is exported from a dangerous workflow.
The receipt is the proof object behind `Approve after export`.

## Fixed page order

1. **Receipt verdict**
2. **Preserved residue summary**
3. **Destination and integrity witness**
4. **Approved language and reintroduction ceiling**
5. **Continuation boundary**

### 1) Receipt verdict

Show:

- `salvage_export_receipt_page_id`
- destructive action supported
- scope
- receipt state (`export-complete`, `partial-export`, `proof-only-export`, `failed`, `mixed`)
- strongest honest summary

### 2) Preserved residue summary

Show rows for:

- full-copy residue preserved
- manifest-only residue preserved
- side-survival successor seed created
- rows not preserved
- rows preserved only elsewhere already

Each row must state:

- work family
- preserved shape
- holder/locality
- whether same-line recovery is enabled or still absent

### 3) Destination and integrity witness

Show:

- destination handle
- package/bundle identifier if any
- integrity witness (`hash`, `manifest`, `none`, `unknown`)
- actor and timestamp
- any weakness or incompleteness that lowers confidence

### 4) Approved language and reintroduction ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- what further work would be required to reintroduce the residue

Examples:

- safe: `local variants now survive as export residue and may support later successor or manual reintroduction`
- forbidden: `local variants are now safely back in the shared line`

### 5) Continuation boundary

Show:

- direct return path to destructive barrier
- direct link to latest shell and ledger
- invalidators (deleted export, failed integrity check, destination loss)
- later supersession path if residue is promoted or restored

## Public object

### Salvage export receipt page

Fields:

- `salvage_export_receipt_page_id`
- `destructive_action_ref`
- `scope_ref`
- `receipt_state`
- `preserved_rows[]`
- `destination_rows[]`
- `integrity_witness_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `continuation_rows[]`
- `generated_at`
