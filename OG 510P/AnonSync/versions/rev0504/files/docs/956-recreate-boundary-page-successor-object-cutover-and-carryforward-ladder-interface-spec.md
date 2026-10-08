
# Recreate boundary page: successor object, cutover, and carryforward ladder interface spec

## Purpose

This page exists for the moment when the honest answer is no longer `edit this object` but:

> create a successor, carry forward what is safe, and cut over without lying that the old object was edited in place.

## Required sections

1. **Why in-place edit is dishonest**
2. **Successor object proposal**
3. **Carryforward ladder**
4. **Cutover and fallback**
5. **Receipt promise**

### 1) Why in-place edit is dishonest

Show:

- the exact field or assumption blocking live edit
- the current object's birth commitments
- the stronger rejected sentence

### 2) Successor object proposal

Show:

- proposed successor kind and settings
- whether it preserves subject continuity, only lineage continuity, or neither
- required empty-path / target conditions

### 3) Carryforward ladder

For each carryforward candidate show one verdict:

- `preserve as-is`
- `translate`
- `reuse after reproof`
- `preserve only as history`
- `cannot carry forward honestly`

Candidates should include at least:

- receipts
- cached bytes / pre-seeded evidence
- grants or authority policy
- route policy
- history / diagnostics
- aliases and labels

### 4) Cutover and fallback

Show:

- drain / quiet requirements
- branch / duplicate risk
- rollback path if successor validation fails
- what stays on the old object after cutover

### 5) Receipt promise

The receipt must preserve:

- predecessor object
- successor object
- carryforward decisions
- rejected stronger reading that this was merely an in-place edit

## Rules

- recreate is not repair folklore; it is a first-class boundary
- cutover must preserve predecessor and successor identity separately
- if cached-byte reuse occurs, the product must still say `successor object` rather than `edited existing object`
