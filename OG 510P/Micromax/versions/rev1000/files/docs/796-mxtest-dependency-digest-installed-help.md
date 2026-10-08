# Rev0837: chunk source-dependency digests and installed-help diet

## Why

Rev0836 found two wastes that directly threatened cloudtainer progress:

1. one repo-wide source digest made a docs-only or tooling-only handoff edit look identical to runtime/test drift, so previously passed aggregate chunks were too easy to throw away;
2. the installed wheel shipped every root `docs/*.md` file as runtime help, including revision archaeology and cloudtainer audit notes that are useful in source archives but noisy in installed help.

This revision makes both boundaries concrete without trying to finish the full aggregate pass in the same step.

## Source evidence change

`tools/mxtest.py` still writes the old whole-tree `source_digest` for compatibility, but source manifests now also carry partition summaries:

- `runtime` for `src/`;
- `tests` for test files;
- `docs` for root docs, README, and TODO;
- `tooling` for `tools/`;
- `test-config` for pytest/build/lint config;
- plus smaller buckets such as plugins, portability, scripts, workflow, examples, and repo.

Each aggregate chunk now records a `source_dependency` object with its own digest. The dependency is narrower than the whole tree: runtime partition, shared pytest config, selected test files, and only the extra partitions visibly touched by the selected tests. For example, docs-sensitive tests include the docs partition; ordinary test chunks do not. Old manifests that lack per-chunk dependency records can still derive dependency digests from their embedded source manifest, so a future resume can reuse old passed chunks when only irrelevant partitions changed.

This is not a claim that source mapping is perfect. It is a conservative first cut that stops docs/tooling churn from being automatically equivalent to all-runtime drift. Runtime changes still invalidate every chunk.

## Installed help change

`docs/installed-help-manifest.txt` is now the curated source of truth for docs bundled into installed wheels / `pip --target` help resources. `pyproject.toml` data-files now list those docs explicitly instead of `docs/*.md`.

The initial manifest ships 33 user-facing/core docs, including vision, language design, editor integration, command bar, prompt completion, help browser, query replace, portability suite, and headless/context CLI docs. It intentionally excludes cloudtainer audit notes and revision archaeology.

The source checkout still has the full docs cube. Only installed runtime help is dieted.

## Tests added or changed

- `tests/test_mxtest.py` covers source partitions, chunk dependency digests, docs-insensitive resume across docs partition drift, and docs-sensitive refusal when docs drift.
- `tests/test_installed_runtime_resources.py` now checks that pyproject bundled docs exactly match `docs/installed-help-manifest.txt` and are a strict subset of root docs.
- `tests/test_packaging_stdlib.py` now builds a wheel and asserts installed docs follow the curated manifest and do not ship cloudtainer notes.

## Validation

Targeted validation run in this revision:

```text
python tools/mxlint.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_mxtest.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_installed_runtime_resources.py tests/test_packaging_stdlib.py
```

The aggregate `.artifacts/mxtest-all-64.json` still needs bounded continuation after this source/docs change. The point of this revision is to make that continuation less wasteful and to stop installed help from growing with every audit note.

## Remaining risk

- The source-dependency scanner uses selected test files plus token/filename heuristics for docs/plugins/tools/portability sensitivity. That is intentionally conservative but not a full dynamic dependency tracer.
- The installed-help manifest is curated manually and duplicated into `pyproject.toml`; tests enforce alignment, but future docs authors still need to decide whether a new help topic belongs in installed help.
- Full aggregate evidence is still not complete; use `make test-all-chunks` and `make test-verify-current` as the next handoff lane.
