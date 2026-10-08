# Rev703 / rev759 cloudtainer audit and docs-scan cache fix

Rev759 starts a cloudtainer audit lane rather than another narrow feature lane. The immediate code fix is small: docs/topic prompt completion now reuses the docs catalog and the docs picker rows instead of rebuilding them repeatedly while composing command-completion explanation rows. The broader finding is architectural: Micromax has excellent self-describing evidence, but too much of that evidence is produced by one large editor surface and by validation defaults that no longer match the real cost of the suite.

## What went severely wrong

The expensive path was not simply "the repository is large." A single completion for `help phn` rebuilt docs prompt rows many times while decorating candidate rows. The pre-fix profile spent about 12.9 seconds inside one Tab press, made about 8.0 million Python calls, called `doc_prompt_rows()` 80 times, and normalized docs paths about 53,200 times. That made the editor feel hung and made prompt-completion tests look much more expensive than the behavior being tested.

Rev759 adds a process-local docs catalog cache keyed by docs root and a per-editor docs prompt-row cache. After the fix, the same cold completion pays one docs scan once, around 1.4 seconds in the cloudtainer profile, and the focused `help phn` regression test runs in about 0.11 seconds. The full `tests/test_editor_prompt_completion_hostcalls.py` file, which previously did not finish within a 300-second container run, now completes 258 tests in about 10.6 seconds.

## What is still missing

The repository has a validation runway, but the defaults still point at old assumptions. Plain `pytest -q` and `mxdoctor.py` both still try to run the whole suite in one foreground lane. The mxtest manifest/chunk tooling is the right direction, but the default human commands should make the cheap path obvious: smoke checks first, chunked aggregate evidence for the full suite, and a no-run manifest summary for handoff inspection.

The package boundary is also not explicit enough. The wheel contains the runtime packages and `micromax.stdlib/core.mx`, but the datacube itself lives in the source archive: docs, tools, portability ledgers, plugins, examples, and revision manifests. That is fine if the wheel is a runtime product and the zip is the research product, but the README should say so plainly. Installed console entry points are also missing; users need source-tree commands or `python -m ...` incantations instead of stable names such as `micromax-editor`, `mxtest`, and `mxcontext`.

The docs are useful but too append-heavy. `README.md`, `TODO.md`, and `docs/43-worklist.md` are now large enough to behave as logs rather than landing pages. The project should keep the truth trail, but promote the top of each long file into a compact dashboard and move older detail into indexed revision entries.

## What should change next

1. Make `mxdoctor` a fast preflight by default, with a separate `--full` or `make test-all-chunks` lane for complete validation. Doctor should not start a long pytest run without saying that it is entering the expensive lane.
2. Split the editor monolith by stable surfaces: docs index/navigation, prompt completion, prompt row models, screen models, macro state, and action installation. `src/micromax_editor/editor.py` is now about 26.6K lines, with a 24.2K-line `Editor` class; refactors should reduce blast radius before adding more features.
3. Split other installer monoliths: `command_dispatcher.install_default_commands`, `micromax_bridge.install_editor_hostcalls`, and `core.install_core_words` are all single large registration funnels. Keep the registry semantics, but move command/hostcall/word families into small modules.
4. Promote `docs/revision-index.json` into the real datacube index. It should eventually carry compact rows for revision, surface, doc path, code path, validation evidence, and recommended next action, so tools do not need to scan hundreds of Markdown files for every fresh editor/session.
5. Add explicit performance budgets for prompt completion and docs search. The cache regression added in rev759 protects the direct repeated-row bug, but a marked perf suite should guard "one Tab over docs" as a first-class behavior.
6. Add a dependency/host reproducibility story. `pyproject.toml` and `requirements-dev.txt` are useful, but a constraints or lock artifact plus CI matrix would make mxtest environment evidence more actionable.
7. Decide the Python baseline path. The project currently allows Python 3.10+, while Python 3.10 is already in security-only support and reaches end-of-life in 2026-10. A 3.11/3.12+ support plan should be written before the baseline becomes a surprise.

## Speculation for future audits

Micromax has repeatedly added accurate local "truth rows" for commands, docs, hooks, keymaps, and validation manifests. That culture is working: it made this cache bug visible, measurable, and correctable. The risk is that each truth-row producer is being appended to the same large object graph. When a display helper can accidentally trigger a full docs scan 80 times, the data model is telling us that the read paths need declared cost classes: cheap cached row, moderate scan, expensive full parse, external side effect.

The next waste class is probably not another single `Path.resolve()` loop. It is likely coarse invalidation: repository-wide source digests make every docs-only edit stale for every full-suite manifest, and docs search currently treats the whole Markdown tree as one catalog. Partitioned source attestations and a materialized docs index would let the project keep its high-trust handoff style without paying full-tree costs on every move.

## Rev759 validation notes

Focused validation performed in the cloudtainer:

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_doc_prompt_cache.py tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_fuzzy_help_topic_prefers_camel_boundary_match --durations=10` passed: 3 tests in about 0.93 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py --durations=20` passed: 258 tests in about 10.60 seconds.
- `python -m py_compile src/micromax_editor/editor.py tests/test_editor_doc_prompt_cache.py` passed.
- `bash scripts/lint.sh` passed through `mxlint: ok`.

Full-suite validation was not claimed in this revision. A plain `pytest -q` run timed out in the cloudtainer before the cache fix while still early in collection/execution, and a later chunked run attempt was inconclusive under the container command timeout. This is itself part of the audit finding: the project needs default validation commands that fit the current suite shape.
