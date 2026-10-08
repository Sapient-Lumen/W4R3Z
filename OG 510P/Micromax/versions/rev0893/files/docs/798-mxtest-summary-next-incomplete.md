# rev0839 mxtest summary next-incomplete chunks

## Why

The aggregate evidence lane is still partial, so the most useful handoff view is not just the slowest chunks. Operators need to see the earliest incomplete chunk(s) and whether a partial chunk already contains useful passed file/test-span evidence.

## Change

`python tools/mxtest.py --manifest-summary .artifacts/mxtest-all-64.json` now includes a `next incomplete chunks` section. The summary payload also exposes:

- `next_incomplete_count`
- `next_incomplete_chunks`
- per-row `file_status_counts` when a partial chunk has file/test-span rows

This is intentionally a reporting change. It does not alter collection, chunking, source-dependency matching, or resume semantics.

## Current audit note

The rev0838 handoff manifest showed chunk 15 as the earliest partial chunk and chunks 16+ as not run. The new summary makes that visible without hand-parsing `.artifacts/mxtest-all-64.json`.

## Guardrail

Keep this as an evidence-navigation helper, not a new doctrine layer. The authoritative way to continue remains the same resume-safe command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```
