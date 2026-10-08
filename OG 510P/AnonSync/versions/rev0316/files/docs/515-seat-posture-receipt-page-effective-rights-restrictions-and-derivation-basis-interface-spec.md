# Seat posture receipt page — effective rights, restrictions, and derivation basis interface spec

## Purpose

Join receipts preserve what path created a seat relationship.
Bind receipts preserve what target commitment happened.
What still needs a distinct proof object is the answer to:

> what effective posture did this seat actually hold at this time, what restrictions were in force, and what derivation or custody basis made that true?

This page exists so later troubleshooting, audit, and handoff do not reconstruct seat posture from remembered caveats and current symptoms.

## Core decision

Any reviewed posture inspection, posture-affecting event, or descendant-sensitive posture change must emit one first-class **Seat posture receipt**.

## Receipt fields

### Required top-level fields

- `seat_posture_receipt_id`
- `seat_ref`
- `subject_ref`
- `requested_posture`
- `effective_posture`
- `capability_vector[]`
- `materialization_class`
- `local_mutation_contract[]`
- `delegation_verdict`
- `derivation_basis[]`
- `descendant_effects[]`
- `generated_at`
- `acted_by`

### Effective posture values

Allowed values include:

- `owner-effective`
- `readwrite-effective`
- `receive-only-effective`
- `observe-only-effective`
- `ciphertext-custody-effective`
- `derived-narrowed-effective`
- `unknown-effective`

### Derivation basis rows

Each row should show:

- basis family
- strength (`hard`, `strong`, `suggestive`, `stale`)
- short explanation

Examples:

- `linked-family default · strong`
- `read-only artifact bound on this seat · hard`
- `encrypted custody lane · hard`
- `local derivative of source seat · strong`
- `source right lowered and cascaded · strong`

### Descendant effect rows

Each row should show:

- descendant or family in scope
- current inherited ceiling
- strongest pending or active cascade

## Fixed receipt order

1. **Effective posture strip**
2. **Capability basis summary**
3. **Local mutation contract**
4. **Derivative / descendant notes**
5. **Next handoff or none**
6. **Audit / export notes**

### 1) Effective posture strip

Show:

- seat
- subject
- effective posture
- strongest narrowing or forcing basis

### 2) Capability basis summary

Show the most important capability rows and their bases.

### 3) Local mutation contract

Show the rules that governed local edit/delete/rename/add behavior at receipt time.

### 4) Derivative / descendant notes

Show any inherited ceilings or cascade obligations that make this posture matter elsewhere.

### 5) Next handoff or none

Show whether this receipt points to:

- local-mutation review
- derived-rights graph
- posture-narrowing review
- no further action

### 6) Audit / export notes

Show:

- whether the receipt is safe to export without bearer secrets
- whether local paths require redaction for the audience
- whether this receipt supersedes or extends a prior posture receipt

## Main surface

A compact **Seat posture receipt** card should show:

- effective posture chip
- strongest basis chip
- local-mutation chip
- descendant-effect chip

## CLI parity

Minimum commands:

- `anonsync seat-posture receipt show <receipt-id>`
- `anonsync seat-posture receipt export <receipt-id>`

## Acceptance criteria

A user can:

- prove later what effective posture a seat actually held
- see which restrictions were contractually active at that time
- see whether derivative or descendant ceilings depended on that posture
- hand the receipt to support or another operator without exporting bearer secrets
