# Revision 0979 tests

This record separates focused Linux-cloudtainer evidence from complete-suite and
cross-platform claims. Expected Python warnings come only from tests that
explicitly exercise legacy `fork` while another thread is live.

## Changed-surface evidence

- `tests/test_worker_process.py` passed **25/25 in 13.65 s**. Coverage includes a
  3 MiB `spawn` round trip, incomplete-header/body deadline and EOF cases,
  oversize declaration rejection before body growth, malformed and trailing
  pickle rejection, crash-without-result classification, a producer that
  publishes but does not exit, constructor failure, ordinary start failure, and
  a simulated start that partially launched before raising.
- Regex compatibility transport, save-worker lifecycle, plugin fingerprint
  budgets, project-picker worker behavior, exact/fast dirty tracking, and the
  structural audit passed **76/76 in 29.34 s**.
- Those changed files total **101/101** focused tests.

## Product-owner integration evidence

- Contained filesystem read/list/stat passed **26/26 in 12.69 s**, including
  large and timed worker paths; eight warnings are the tests' deliberate
  multithreaded-`fork` compatibility cases.
- The complete open/save module passed **92/92** in three bounded shards
  (**32/32 in 26.82 s**, **32/32 in 16.66 s**, and **28/28 in 29.66 s**). This
  covers large open results, save planning, freshness, parent creation, atomic
  writes, timeout cleanup, residue handling, external-change witnesses,
  permission durability, and buffer/undo semantics.
- Docs indexing, plugin package snapshots, save-residue cleanup, the pure
  project-picker model, and the restricted-plugin journey passed **43/43 in
  6.69 s**.
- The distinct selected product and changed-surface files above total **262/262
  passing tests**.

## Dirty-tracking benchmark and regression evidence

A many-short-line local benchmark measured median milliseconds per mutation:

| Path | 1 MiB | 4 MiB |
| --- | ---: | ---: |
| rev0978 exact | 2.22 | 8.90 |
| rejected per-line Python exact walker | 21.9 | 149 |
| final rev0979 explicit exact | 2.23 | 9.03 |
| final rev0979 automatic `fastdirty` edit core | <0.001 | <0.001 |

The benchmark isolates buffer mutation/dirty accounting; it is not a renderer,
search, syntax, terminal, whole-editor latency, or cross-host claim. Tests prove
exact LF/unicode/surrogate signature equivalence, visible local automatic policy,
explicit reversal to exact mode, and unchanged below-threshold semantics.

## Structural and publication evidence

- `python tools/mxaudit.py --check` passes at rev0979 with full-frame worker and
  large-buffer dirty-policy flags.
- `python tools/mxeffects.py --write-help-doc --check-help-doc --check` regenerated
  and validated the 24-row rev0979 installed effect/resource contract.
- Changed Python files compile. Focused fatal Ruff checks pass for every changed
  Python file except `editor.py`; its **44** pre-existing fatal diagnostics are
  byte-for-byte the same categories/count as rev0978, with no new diagnostic.
- Revision-index, living-document, context, structural-audit, and effect-contract tests passed
  **21/21**. The generated handoff retains every current-revision code path while
  holding both document and code pointer lists to **64** entries.
- Archive generation, deterministic-repeat, mutation-rejection, revision-lineage,
  and verifier tests passed **52/52** (plus the deliberate duplicate-member test's
  expected `zipfile` warning).
- Revision/context hygiene, repository lint, context regeneration, and final
  archive verification are rerun after publication cleanup and recorded by the
  linked verified ZIP.

No complete pytest suite, Windows run, preemptible `Process.start`, hostile
pickle boundary, child pre-serialization/total-memory cap, syscall filter,
native-crash recovery, rope, or hostile-plugin sandbox is claimed.
