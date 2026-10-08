# Reader-facing state object form

Introduced: `rev0022` / turn 14

## Purpose

Stop adding hidden receipts to P0001. The next honest machine-native test is whether the existing states can be made readable as one object.

## Required surfaces

- Closed state: selected surface alone.
- Open state: selected lines with branch-loss triplets.
- Traversal state: route through omitted candidates.
- Patched state: rendered mutation from patch_application receipt.
- Accessibility fallback: plain markdown with every state and receipt link.

## Verification

A future validator should confirm that the view links every visible transition to the exact JSON receipt that authorizes it and that the view contains no unverified quality claim.

## Risk

If the state object is not worth reading, the P0001 form family should be frozen as a useful laboratory failure rather than extended into another local mechanism.
