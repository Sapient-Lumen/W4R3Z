# Permission-plane receipt page: mode basis, apply result, and claim ceiling interface spec

## Purpose

The receipt exists so a later operator does not have to reconstruct permission truth from job profiles, reference-seat lore, or substrate assumptions.
It must freeze the effective permission contract that resulted from a reviewed action.

## Receipt sections

Render in this order:

1. **Requested change**
2. **Effective result**
3. **Authority basis recorded**
4. **Seat-class outcomes**
5. **Claim ceiling recorded**
6. **Next review triggers**

### 1) Requested change

Record:

- requested mode
- requested authority basis
- requested affected scope
- actor and time

### 2) Effective result

Record:

- effective mode
- whether apply was live, recreate-only, successor-epoch, or blocked
- whether permissions now participate in sync comparison
- whether any seats fell back to local re-inherit, deferred-apply, or no-sync

### 3) Authority basis recorded

Record:

- reference seat / epoch if any
- whether authority is single-reference, merge, or local-only
- evidence grade and freshness

### 4) Seat-class outcomes

Record per seat class:

- native apply
- deferred apply
- local re-inherit
- claim narrowed by privilege gap
- blocked

### 5) Claim ceiling recorded

Record both:

- strongest safe sentence
- stronger forbidden sentence

### 6) Next review triggers

Record which events invalidate the receipt's strength, such as:

- reference-seat replacement
- substrate change
- privilege downgrade
- subject recreation
- policy epoch change

## Receipt object

Fields:

- `permission_plane_receipt_id`
- `review_ref`
- `subject_ref`
- `requested_mode`
- `effective_mode`
- `authority_basis`
- `compare_participation`
- `seat_outcomes[]`
- `strongest_safe_sentence`
- `stronger_forbidden_sentence`
- `review_triggers[]`
- `created_at`

## Acceptance criteria

A receipt reader can:

- see what was requested versus what became effective
- see who or what counted as permission authority
- see which seats applied, deferred, re-inherited, or narrowed the contract
- see whether permission drift now participates in sync work
- know exactly what the product may and may not claim afterward
