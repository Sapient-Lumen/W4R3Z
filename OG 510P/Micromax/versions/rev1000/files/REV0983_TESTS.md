# Rev0983 tests and evidence

## Focused history/edit tests

```bash
PYTHONPATH=src pytest -q \
  tests/test_rev0983_undo_retention.py \
  tests/test_multicursor_edit_journey.py \
  tests/test_editor_core.py::test_editor_insert_undo_redo \
  tests/test_simultaneous_edits.py::test_multicursor_insert_has_one_buffer_mutation_witness
```

Observed during development: `26 passed`.

A broader focused union covering the revised history path and related editor behavior completed with `153 passed in 5.87s`. A separately selected action-impact union completed with `146 passed in 15.23s`. Those selections overlap and therefore are not presented as 299 unique tests.

The unions covered editor core, simultaneous edits, macro aggregate transactions, scripted undo transactions, query-replace boundaries, undo authority, line-edit geometry, autoindent/tabs, fast-dirty tracking, clipboard authority/import/export, read-only behavior, viewport typing, transient state, hostcall transactions, action authority, and named macros.

## Permanent memory witness

```bash
PYTHONPATH=src python tools/measure_undo_retention.py
```

Five-sample default, 4,000,000 characters, ten one-character edits:

- compact current median: 4,037,597 B;
- snapshot-reference current median: 40,021,417 B;
- compact incremental history after first edit: 30,834 B;
- snapshot-reference incremental history: 36,018,087 B;
- current traced-allocation reduction: 89.911%;
- incremental retained-history reduction: 99.914%; and
- both shapes complete exact undo and redo.

These are narrow Python `tracemalloc` observations, not RSS, total-memory, latency, allocator, or portable bounds.

## Structural and portability validation

The final source tree completed:

- Python compilation for touched code;
- `python tools/mxlint.py` with `mxlint: ok`;
- effect-contract generation/checking;
- `python tools/mxaudit.py --check`;
- revision-index, living-doc, context, audit, effect-contract, and archive-tool tests; and
- `python tools/mxportable.py --quiet` with `172/172 portability cases passed`.

`make timely-tests` completed all five planned steps in 22.058 seconds. Context, audit, lint, and portability passed; its bounded `mxtest` slice was classified as a clean budget-limited checkpoint. The packaged `.artifacts/mxtimely-summary.json` is the machine-readable receipt.

## Full-suite boundary

The complete pytest lane collected 3,189 tests but did not finish within the 15-minute execution ceiling used for this revision session. Its supervisor received termination, cleaned up its pytest child, and left no test process running. This is incomplete evidence, not a full-suite pass.

The resumable release manifest is also deliberately retained as partial: no release batch completed in its bounded window, 22 batches remain, and `release-verify` correctly refused to certify the incomplete manifest. The packaged `.artifacts/mxrelease-full-suite.json` records that state and the exact continuation command.

The archive therefore claims the completed focused, structural, portability, and timely lanes above; it does not claim a completed 3,189-test or release-suite lane.
