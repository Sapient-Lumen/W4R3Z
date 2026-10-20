# ADR 0351: Skip empty unselected projection work

- Status: accepted and implemented
- Date: 2026-09-09

## Context

Tree-v2 projection exchange has to preserve recipient-local paths outside the selected custody set.
That preservation is intentionally conservative: it walks the current visible tree, copies
unselected entries into the staged replacement, then verifies the exchanged old and new sides before
discarding the old projection.

For a complete projection policy, `includes` and `excludes` are both empty. Under the frozen
selection rules this means every valid user path is selected, while the generated
`.iotox-conflicts` control tree is never preserved. The old implementation still ran the unselected
preservation and comparison walkers even though their user-path result set had to be empty.

## Decision

Add an explicit complete-projection fast path:

- if `includes` and `excludes` are empty, `preserve_unselected_tree()` returns success without
  walking the old projection;
- the post-exchange unselected-tree comparison also returns success for the same complete policy;
- `TreeV2WorktreeUpdateResult` now reports content-free preserved-unselected counters so tests and
  public reconcile diagnostics can distinguish complete-policy no-op preservation from sparse
  preservation.

The change does not skip the baseline scans before and after staging, does not skip visible-target
validation, and does not skip old-projection validation. Held-descriptor writes to the old side still
make the exchange fail closed and preserve the old tree for operator recovery.

## Consequences

Complete tree-v2 projection exchange removes two avoidable empty preservation walks. Sparse
projection still preserves local exclusions and unrelated paths exactly as before, because those
paths are real local data outside sync custody.

This is not path-level incremental projection. A changed complete projection still materializes and
validates the complete selected tree before atomic exposure. The next projection optimization needs a
stronger descriptor-safe design, not a path-cache shortcut that could widen same-UID races.
