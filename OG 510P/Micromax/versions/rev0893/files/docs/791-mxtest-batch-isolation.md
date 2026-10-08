# Rev0832: mxtest batch isolation for resumable in-file progress

Rev0831 made aggregate progress resumable inside a selected file when `--max-new-tests` split the file at a budget boundary. A real bounded aggregate probe showed the remaining weak spot: if the cloudtainer interrupted the pytest subprocess before that file span finished, mxtest could preserve the running/partial span but could not safely reuse the individual tests that had already printed dots inside that subprocess.

Rev0832 adds:

```bash
python tools/mxtest.py --isolate-files --test-batch-size 8 ...
```

The option splits each selected file group into ordered pytest subprocess batches of at most N node ids. Each completed batch is written as a normal isolated row with `nodeid_first`, `nodeid_last`, and `nodeids_digest`. The existing span-resume logic can therefore reuse passed batches and rerun only unfinished or `not_run` spans.

## Behavior

Unset or zero `--test-batch-size` keeps the old behavior: one pytest subprocess per selected file group.

Positive `--test-batch-size` keeps collection and chunk selection unchanged, but it runs each file group as smaller subprocess batches. Batch rows include:

```text
file
selected
nodeids_digest
nodeid_first
nodeid_last
batch_index
batch_total
batch_size
file_selected
```

The batch metadata is explanatory; resume safety still comes from the selected count and exact node-id digest/span.

## Audit result

A bounded 64-chunk aggregate probe with `--test-batch-size 5` was interrupted during batch 5 of `tests/test_editor_fs_open_save.py`. The manifest kept the first four passed five-test batches and marked the interrupted batch partial. A second `--resume` run reused those four passed batches, ran two more five-test batches, and left the remaining four tests as `not_run` after the max-new-tests budget was exhausted. `tools/mxtest.py --verify-current` reported the partial manifest as source/environment-matching and resume-safe.

This is not a full-suite pass. It is a better runway for obtaining one over repeated bounded passes.

## Recommended command

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py   --run-chunks 64   --strategy segment   --isolate-files   --resume   --max-new-tests 120   --max-new-files 8   --test-batch-size 8   --file-timeout 180   --json .artifacts/mxtest-all-64.json   --durations 0
```

Then:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py   --verify-current .artifacts/mxtest-all-64.json
```

The Makefile now routes `make test-all-chunks` through the same bounded/batched lane.
