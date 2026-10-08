# Rev0994 audit — live-growth fast-dirty and single-pass long-line repair

## Priority chosen

Rev0993 identified huge-line editing beyond creation-time automatic `fastdirty`
as the next user-visible risk. Rev0994 reproduced the path and repaired the
existing policy before authorizing a new text representation.

## Severe and wasteful findings corrected

- A small or empty buffer could grow past the 1 MiB threshold and remain on
  complete-document exact hashing forever.
- Exact dirty classification discarded the current generation signature and
  hashed the same text again at `mark_clean()`; idempotent option resync also
  rehashed every unrelated exact buffer.
- Same-line insert, delete, and replace duplicated chained immutable string
  construction. During consolidation, the audit caught an initial cross-line
  single-fragment branch that duplicated replacement text and left two rows; it
  was corrected before publication and pinned against a flat-text oracle.
- Generation-signature reuse made the observed mutable `Buffer.lines` seam a
  potential stale-cache path; it now invalidates before raw writes.
- Rev0993's random recovery IDs made rev0986/rev0987 differential transaction
  oracles report false implementation mismatches; the nondeterministic identity
  alone is normalized.

## Landing

- The first exact generation at or above 1 MiB promotes a buffer with no local
  override to visible, sticky `fastdirty=true`; the crossing mutation remains
  exactly classified.
- `setlocal fastdirty false` is the explicit per-buffer exact-mode opt-out.
- Exact current-generation signatures are cached, invalidated at every owned
  mutation/restore boundary, reused by save and recovery owners, and excluded
  from undo change comparison as derived state. Reapplying an unchanged dirty
  mode is now a no-op, eliminating workspace-wide exact rehashes on local policy
  changes.
- Same-line mutations share one clamped `_splice_line_text()` constructor using
  one `str.join()` operation and preserving empty no-op identity. Cross-line
  replacement with one logical line merges the two surviving outer fragments
  exactly rather than entering the multi-part branch.
- Macro rollback restores derived automatic-promotion authority; failed save
  cleanup restores the prior generation cache.

## Measurement and qualification

The permanent 32-million-character artifact reports one signature call instead
of 33 for threshold crossing plus 32 follow-up edits, with 87.863% lower local
elapsed time in that journey. The shared splice constructor reports 7.343% lower
local median elapsed time, exact output, and essentially unchanged ~64 MB traced
peak. These are cloudtainer attribution measurements, not portable benchmark,
RSS, or total-memory claims.

The representation remains a Python list of immutable line strings. One huge
changed line is still O(line length); no rope, piece tree, gap buffer, or second
document model was added.

## Evidence

The pre-publication product lane passed 295 selected tests: 223 fastdirty,
compact-history, sparse replay, aggregate transaction, recovery-history, splice,
and measurement cases; five save/rollback cases; five bounded interrupted-save/
recovery cases; and 62 simultaneous-edit, query-replace, multicursor, and sparse-
history cases. Context/revision/document hygiene passed 12 tests, effect/audit
tooling passed 9, and the archive tool passed 53 tests (one expected duplicate-
member warning): 369 selected tests total. The randomized edit oracle includes
2,000 same-line Unicode/lone-surrogate cases plus 1,500 multi-line replacements
with exact inverse-witness replay.

Compilation, `mxlint`, generated effect contracts, context, structural audit, and
`git diff --check` passed. `make timely` passed context, audit, lint, 172/172
portability cases, and doctor preflight. One durable-recovery normalization case
exceeded its isolated 120-second bound on this filesystem, and the monolithic
suite was not claimed. `make typecheck` reported that mypy is unavailable rather
than producing a typecheck pass. The final linked zip is additionally checked by
`mkrevzip --verify-archive` and `unzip -t` after construction. The online
comparison and complete residual-risk statement are in
`docs/951-dynamic-fastdirty-growth-single-pass-longline-audit.md`.
