
# Post-create change preview page: live mutation, deferred apply, and recreate cost interface spec

## Purpose

Once an object exists, the operator needs a preview that distinguishes:

- **live edit now**
- **apply later / next run / restart**
- **future-only policy change**
- **recreate or successor cutover**

## What the preview must answer

> if I commit this requested change, what actually mutates in place, what waits, and what honestly cannot be changed without successor work?

## Fixed sections

1. current object and requested delta
2. in-place effects
3. deferred effects
4. recreate / successor costs
5. safest next action

### 1) Current object and requested delta

Show the field-by-field delta and the present mutability class for each changed field.

### 2) In-place effects

For every truly editable field, show:

- effect timing
- blast radius
- invalidators
- rollback posture

### 3) Deferred effects

For every deferred field, show:

- trigger (`next-run`, `restart`, `re-index`, `future descendants`, `external proof`)
- what remains old until then
- proof of effect required later

### 4) Recreate / successor costs

For every field that cannot be changed honestly in place, show:

- whether a successor object is required
- any empty-target or cutover requirement
- indexing / scan / merge / re-seed cost
- carryforward candidates and losses

### 5) Safest next action

The primary action must change with the truth, e.g.:

- `Apply live edit`
- `Stage deferred change`
- `Prepare successor cutover`
- `Cancel and keep birth commitment`

## Rules

- no mixed preview may end in a generic `Save`
- deferred fields must not impersonate live success
- successor-required fields must not hide inside `some changes require recreation`
