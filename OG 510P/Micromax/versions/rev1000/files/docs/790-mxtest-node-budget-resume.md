# Rev0831 — mxtest node-budget resume and budget-stop audit

Rev0831 continues the full-suite evidence lane without turning the turn into registry work.

## Problem

Rev0830 made aggregate suite attempts bounded by file count with `--max-new-files`, but a selected chunk can still contain a large or slow slice from one test file.  In that case a bounded file pass is not granular enough: an interruption inside the file forces the next run to retry the same file slice.

A rev0831 bounded aggregate probe also exposed a separate waste: once a global file/test budget was exhausted, `mxtest` still walked every remaining chunk and rewrote the large aggregate JSON after each synthetic `not_run` record.  That made a “bounded” pass spend time on bookkeeping instead of tests.

## Change

`tools/mxtest.py --run-chunks --isolate-files` now accepts:

```bash
--max-new-tests N
```

The budget is counted by newly run pytest node ids, not by file.  When the budget ends inside a file, mxtest records two manifest rows for the same file: a passed row for the node-id span that ran, and a `not_run` row for the remaining node-id span.  Each row now carries:

```text
nodeid_first
nodeid_last
nodeids_digest
selected
```

Resume now drops only the exact passed node-id span, not the whole file.  That lets a later pass continue from the remaining tests in the same file.

Budget exhaustion now stops the aggregate loop after the current chunk and appends the remaining chunks as `not_run` in one final manifest write.  This avoids the rev0830 wasteful pattern of repeatedly rewriting the source/environment-heavy JSON payload after the budget is already spent.

## Compatibility

Older rev829/rev0830 whole-file rows are still accepted when their digest and file selection match.  New partial-file rows require the node-id span/digest evidence before they can be reused.

## Validation

Focused tests added/updated:

```text
test_mxtest_max_new_tests_can_checkpoint_inside_one_file
test_mxtest_max_new_tests_resume_drops_only_passed_node_span_in_same_file
test_mxtest_max_new_tests_requires_run_chunks_and_isolation
```

The bounded smoke command showed a partial manifest can verify as resume-safe, then complete after a second `--resume --max-new-tests` invocation on the same source/environment.

## Recommended handoff command

Prefer a finer 64-chunk segment plan with both test and file budgets:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --max-new-tests 120 \
  --max-new-files 8 \
  --file-timeout 180 \
  --json .artifacts/mxtest-all-64.json \
  --durations 0
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --verify-current .artifacts/mxtest-all-64.json
```

A partial manifest is still not a full-suite pass, but it is now safer evidence: it can resume within a large test file instead of retrying the whole selected file slice.
