# Hydration receipt page: engine basis, lane result, and history/collision ceiling interface spec

## Purpose

The receipt exists so a later operator does not have to reconstruct hydration truth from shell quirks, provider folklore, or scattered support notes.
It must freeze the effective hydration contract that resulted from a reviewed action.

## Receipt sections

Render in this order:

1. **Requested change**
2. **Effective engine**
3. **Lane result recorded**
4. **Eligibility basis recorded**
5. **History/collision ceiling recorded**
6. **Co-tenant findings recorded**
7. **Claim ceiling recorded**
8. **Next review triggers**

### 1) Requested change

Record:

- requested engine/lane change
- requested scope
- actor and time

### 2) Effective engine

Record:

- effective engine
- whether apply was live, migrate-path-first, recreate-only, or blocked
- policy source afterward

### 3) Lane result recorded

Record:

- shell/provider lane status
- in-app fallback status
- missing or degraded actions that remained

### 4) Eligibility basis recorded

Record:

- path class
- filesystem / provider basis
- strongest unmet prerequisite if any

### 5) History/collision ceiling recorded

Record both:

- retained-history class
- collision-detection class
- strongest one-line consequence for later recovery/conflict handling

### 6) Co-tenant findings recorded

Record:

- competing providers
- parallel runtimes if any
- inherited local flags if material
- whether any finding was merely warned, forced a fallback, or blocked the request

### 7) Claim ceiling recorded

Record both:

- strongest safe sentence
- stronger forbidden sentence

### 8) Next review triggers

Record which events invalidate the receipt's strength, such as:

- OS/provider upgrade or downgrade
- path migration
- filesystem change
- shell/provider extension degradation
- co-tenant provider appearance
- policy epoch change

## Receipt object

Fields:

- `hydration_receipt_id`
- `review_ref`
- `subject_ref`
- `requested_engine`
- `effective_engine`
- `lane_outcomes[]`
- `eligibility_basis`
- `history_guarantee`
- `collision_guarantee`
- `cotenant_findings[]`
- `strongest_safe_sentence`
- `stronger_forbidden_sentence`
- `review_triggers[]`
- `created_at`

## Acceptance criteria

A receipt reader can:

- see what hydration change was requested versus what became effective
- see what local lanes actually survived
- see why the path/seat qualified or failed
- see what rollback and collision promises remained
- know exactly what the product may and may not claim afterward
