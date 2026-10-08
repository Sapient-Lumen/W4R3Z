# Rev760 docs-index extraction, doctor preflight, and entry points

Rev760 turns the rev759 audit into code movement rather than another registry pass. The risky area was the docs/help prompt path: rev759 made it fast by caching, but that left the obvious next correctness hazard—long-lived Python processes could keep a stale docs catalog after a docs edit. The fix is to move the docs catalog work out of `editor.py` into `src/micromax_editor/docs_index.py` and make the caches depend on a cheap docs-root signature.

## What changed

- `src/micromax_editor/docs_index.py` now owns docs-root resolution, top-level Markdown scanning, title/summary extraction, catalog key expansion, numbered docs section labels, and docs prompt-state materialization.
- `Editor._scan_docs()`, `_docs_catalog()`, and `doc_prompt_rows()` are now thin adapters that cache by a docs-root freshness token rather than by path alone.
- The process-local scan cache still avoids rereading every Markdown file for every fresh `Editor`, while docs edits invalidate cached rows when file name, size, or `st_mtime_ns` changes. Large docs roots reuse a fresh signature briefly so hot completion paths do not regress into hundreds of repeated `stat()` calls; `Editor.refresh_docs_cache()` remains the explicit escape hatch.
- `tools/mxdoctor.py` no longer launches the whole pytest suite by default. Its default lane is stdlib health + lint + a bounded smoke pytest set; `--full` keeps the old single-process full pytest lane; `--chunked` points at the resumable `mxtest` aggregate lane.
- `Makefile` now exposes `doctor-full` and `doctor-chunked` so the fast and expensive lanes are not hidden behind prose.
- `pyproject.toml` now installs `micromax` and `micromax-editor` console entry points; the packaging smoke test verifies the wheel metadata.
- `mxlint` and `mxformat` now treat generated `.egg-info` metadata as transient, so the wheel smoke test does not leave behind a lint failure for the next doctor run.

## Why this is higher leverage than more bookkeeping

The editor is still a monolith, but this change removes one complete cost class from it: docs indexing is now a separately testable module with its own row state. That gives future work a clean place to add materialized docs/revision-index data, prompt-completion budgets, or richer docs metadata without threading more mutable caches through the 26K-line editor file.

The doctor change also fixes a workflow trap called out in the rev759 audit. A command named `doctor` should be a preflight that finishes quickly enough to run often. Full-suite evidence is still available, but it now has explicit names and a chunked/resumable option.

## Remaining risk

The docs signature is deliberately cheap: it tracks top-level `.md` file names, sizes, and nanosecond mtimes, and very large roots throttle signature refresh for a short window. That is the right default for a source archive and a local editor loop, but it is not a cryptographic content digest. If Micromax eventually uses a materialized docs index as a trust artifact, that artifact should carry content hashes and a source-manifest partition instead of relying on filesystem metadata.

`editor.py` is smaller at this seam but still much too large. Good next splits are prompt completion, prompt row grouping/formatting, help navigation, screen models, and action installation. The most important discipline is to keep hot UI paths from calling moderate/expensive scans while formatting explanatory rows.

## Validation notes

Focused validation in this cloudtainer:

- `python -m py_compile src/micromax_editor/docs_index.py src/micromax_editor/editor.py tools/mxdoctor.py tests/test_docs_index.py tests/test_editor_doc_prompt_cache.py tests/test_mxdoctor.py tests/test_packaging_stdlib.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_docs_index.py tests/test_editor_doc_prompt_cache.py tests/test_prompt_grouping_sections.py::test_doc_prompt_rows_empty_query_budget_across_numbered_families tests/test_editor_help_docs_buffers.py::test_doc_prompt_rows_and_helppick_command tests/test_mxdoctor.py tests/test_packaging_stdlib.py tests/test_mxlint.py tests/test_mxformat.py --durations=20` passed: 25 tests in 15.41 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py --durations=10` passed: 8 tests in 9.52 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py --durations=20` passed: 258 tests in 7.98 seconds.
- `python tools/mxdoctor.py` passed: stdlib health, `mxlint`, and 39 fast preflight tests in 4.43 seconds.
- `bash scripts/lint.sh` and `python tools/mxcontext.py --check` passed for the final rev760 tree.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0760_mxtest_plan.json` collected 1536 tests into eight 192-test chunks with source digest `0eb714c64c76`.

Full-suite validation is still not claimed here; rev760 makes the default preflight honest and keeps the chunked evidence lane explicit.
