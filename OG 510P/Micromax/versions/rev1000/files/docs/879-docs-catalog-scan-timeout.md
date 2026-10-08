# Rev0921 — docs catalog scan timeout

## What changed

The docs/help catalog is now built from a bounded top-level docs-root inventory instead of direct `Path.glob("*.md")`, per-path `is_file()`, repeated `stat()`, and full-file `read_text()` calls.

`src/micromax_editor/docs_index.py` now owns a small docs scan worker with explicit row, per-file prefix-byte, total-byte, and wall-clock budgets:

- `DOCS_SCAN_MAX_FILES`
- `DOCS_SCAN_MAX_FILE_BYTES`
- `DOCS_SCAN_MAX_TOTAL_BYTES`
- `DOCS_SCAN_TIMEOUT_SECONDS`

The worker uses the existing fd-contained filesystem family for directory listing and metadata, then reads only a bounded prefix of each direct Markdown child for title and summary extraction. The parent process still runs the Markdown heading/summary extraction, so the scanner does not pickle editor callbacks or move docs parsing policy into a subprocess.

`src/micromax_editor/file_access.py` adds `read_file_prefix_contained()`: an fd-bound, containment-checked read helper for preview/catalog surfaces that need the first bytes of a regular file without rejecting the file merely because its full size is larger than the preview budget.

## Why this was next

Plugin discovery and package fingerprinting were fixed in rev0920, but the docs/help catalog was the next hot discovery surface. Prompt suggestions, help lookup, `showdocs`, and docs pickers can rebuild or refresh docs metadata frequently in long editor sessions. The repository docs tree already has hundreds of direct Markdown children, so the waste risk was real even without a malicious tree.

The important correction is not another registry row. It is making the remaining high-frequency inventory path explicit and killable:

1. one top-level docs-root scan,
2. bounded file count,
3. bounded per-file prefix read,
4. bounded aggregate bytes,
5. process timeout and terminate/kill cleanup,
6. process-local record and row cache reuse for the hot path.

During validation, this revision also caught and fixed the important waste regression: the first bounded implementation could still rescan the whole docs root repeatedly inside one long help/status render when the TTL expired during the render. `docs_root_cache_token()` now reuses the recent large-root scan-record fingerprint before spawning another worker, so the boundary is not merely safe but cheap enough for hot UI paths.

## Online research used

- Python's `subprocess` documentation says timeout handling kills and waits for the child process, while process creation itself may not be interruptible on all platforms. That supports killable process boundaries for filesystem work that might block.
- Python's `concurrent.futures` documentation says running futures are not cancelled by `shutdown(cancel_futures=True)`, which reinforces avoiding thread-pool cancellation as a containment story for blocking filesystem calls.
- OWASP API4:2023 names missing execution timeouts, memory, file-descriptor, process, payload, operation, and record limits as resource-consumption risk. The docs catalog is not an API endpoint, but the same missing-limit shape applies to a prompt surface that walks and reads many files.
- VS Code's extension-host documentation frames extension isolation partly around startup and UI performance, while Workspace Trust is explicitly motivated by unintended code execution when opening a workspace. Micromax's docs catalog is not executing docs, but it sits in the same product zone: workspace-supplied trees should not be able to stall or unexpectedly expand editor startup/help behavior.

Sources: <https://docs.python.org/3/library/subprocess.html>, <https://docs.python.org/3/library/concurrent.futures.html>, <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>, <https://code.visualstudio.com/api/advanced-topics/extension-host>, <https://code.visualstudio.com/api/extension-guides/workspace-trust>.

## Tests and audit

New focused tests in `tests/test_docs_index.py` assert that `scan_docs()` no longer needs direct `Path.glob()` or `Path.read_text()`, that a large docs file remains discoverable from a byte prefix, and that recent large-root scan records are reused between token checks and row building instead of spawning repeated workers. `tools/mxaudit.py --check` now hard-checks `docs_catalog_scan_timeout_boundary` so the direct hot docs catalog shape does not quietly return.

Focused validation run for this revision:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_docs_index.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_docs_index.py tests/test_mxaudit.py tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_tui_md_definitions.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showdocs_uses_doc_section_summary_metadata tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showdoc_and_help_docs_use_doc_metadata tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_help_and_apropos_include_doc_topics tests/test_editor_help_docs_buffers.py tests/test_editor_help_docs_boundary.py
PYTHONPATH=src python tools/mxlint.py
PYTHONPATH=src python tools/mxaudit.py --check
PYTHONPATH=src python tools/mxcontext.py --check
```

## Remaining risk

This is still a catalog scan, not an OS sandbox. The worker can be killed after the configured timeout, but process creation itself can still take nonzero time on some platforms. The scan intentionally reads only direct Markdown children; recursive docs trees remain out of scope for the live help catalog.

The next concrete survivor is project-root discovery. `_project_root_for_path()` still walks parent directories with ordinary marker probes. That path is not as broad as docs or plugin discovery, but it is a precise ambient helper worth converting to bounded/batched marker checks before generating another effect table.
