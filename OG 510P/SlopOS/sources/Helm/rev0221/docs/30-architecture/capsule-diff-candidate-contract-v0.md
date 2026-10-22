
# Capsule diff candidate contract v0

Purpose: make continuity and restore more honest by comparing the present shell graph against a selected capsule before or after restore.

A **capsule diff** is a shell-owned comparison surface between:
- the current live desktop state,
- a selected capsule or saved continuity object,
- and, when useful, the last restore attempt or receipt.

## Candidate posture

1. **Diffs are shell truth, not app-local folklore**
   - the shell compares the objects and anchors it actually knows
   - app-local memory may appear only as an attributed contributor, not as universal truth

2. **Diffs serve both before and after restore**
   - before restore: what will bind, what will repair, what will be skipped
   - after restore: what bound, what changed, what failed, what remains unavailable

3. **Diffs are graded, not binary**
   - exact match
   - repaired binding
   - partial carry
   - unavailable target
   - denied / not permitted

4. **Diffs should help the user act**
   - rebind one slot
   - ignore one missing target
   - open the receipt
   - reveal the live replacement
   - compare route or provider choice

## Candidate uses

- compare the current workspace against a stored capsule
- preview what a restore would change before committing it
- explain why a restore was partial instead of quietly claiming success
- compare a layout template's expected slots against current windows and anchors
- show whether one live lens, watchpoint, or Flow attachment is present, repaired, or absent

## Candidate v0 specimen

A narrow specimen could be:
- one capsule with three to five expected bindings,
- one pre-restore diff card,
- one post-restore diff receipt,
- and one rebind action for a missing target.

## Guardrails

- do not turn diffs into giant timeline theater before one useful specimen exists
- do not hide missing or repaired bindings under a generic “restored” badge
- do not overclaim exactness when the shell only has repair or partial truth

## Working stance

Capsule diffs look like the missing honesty surface that can make Recall, Overview, and restore feel serious instead of nostalgic.
Helm should keep them as a candidate contract until one proof-bearing slice exists.
