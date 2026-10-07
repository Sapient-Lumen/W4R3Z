# Release Flow

This is the repository's release flow for public papers.

## Principle

The main drafting line stays alive.
Publication happens through a separate, slower release path.

## Label and link discipline

- Old already-published papers may continue using their existing **Mathematics** wiki links.
- New releases must use **Anonymity** in the published name.
- A future operator must never infer that the old label carries forward to new releases.

## States

1. **Drafting**
   - the paper is still being actively rewritten, split, merged, or re-scoped.
   - no release action is taken.

2. **Hold**
   - the paper is promising, but not yet stable enough for public freezing.
   - a hold note should explain what is still moving.

3. **Candidate**
   - the paper appears potentially publishable, but still requires explicit review against the conservative release criteria.
   - entry into Candidate is not permission to publish.

4. **Published-ready queue**
   - the paper has passed the conservative gate and is waiting for a gentle release slot.
   - the paper should remain unchanged except for final naming and packaging checks.

5. **Published**
   - the paper is copied into `published/` under the exact wiki-facing naming scheme.
   - the canonical artifact is the `.tex` file.

## Required movement rule

Movement is intentionally slow:

- Drafting -> Hold or Candidate
- Candidate -> Hold or Published-ready queue
- Published-ready queue -> Published

A paper should not jump directly from Drafting to Published.

## Repository expectations

- Every state change must be written down.
- Every publish decision must cite the source `.tex` path that was frozen.
- Every hold decision should name the blocking reason.
- The queue should stay small.
- The default outcome of a review is **no promotion**.
