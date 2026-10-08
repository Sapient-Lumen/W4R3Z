# Archived `docs/02-repo-map.md` through rev0855

Preserved during the rev0856 mission/context reset. The corresponding living document now contains only current handoff material.

---

Rev0855 note: this living repo map remains guarded against stale aggregate lane text and now records the docs-cues zero-schema guard.
# Repo map (rev0855)

```text
docs/                    current design docs and recent revision notes
docs/history/            archived append-only handoff ledgers through rev0822
examples/                small Micromax language examples
plugins/                 bundled editor plugins
portability/             replayable VM portability corpus
scripts/                 shell helpers
src/micromax/            VM, core language, stdlib, REPL
src/micromax_editor/     editor substrate, policies, prompts, commands, hostcalls, TUI
tests/                   headless unit/regression tests
tools/                   lint/context/doctor/pack/test utilities
```

## Important current seams

- `tools/mxtest.py` owns deterministic collection, chunking, aggregate manifests, resume, bounded file/node/batch/runtime progress, per-test checkpoint evidence, selected-test progress counts, signal-safe interruption rows, source-dependency partitioning, and source/environment verification.
- `Makefile` owns the default handoff manifest path through `TEST_MANIFEST ?= .artifacts/mxtest-all-64.json`; `make test-all-chunks`, `make test-verify-current`, summary targets, and `make doctor-chunked` now follow that archive-carried manifest and the same aggregate budget shape by default.
- `tools/mxtest_progress_plugin.py` is the pytest child plugin used only by `mxtest --checkpoint-tests` to write resume-safe per-test JSONL progress.
- `tools/mxdoctor.py` owns preflight orchestration. Its default/checkpointed lanes are bounded; `--chunked` forwards the same manifest, runtime, new-test, new-file, batch, and file-timeout knobs as the aggregate handoff lane.
- `tools/mxcontext.py` owns the compact handoff context. Rev0852 derives newest revision-note docs from `docs/revision-index.json`, keeping the static context list focused on stable design/history anchors while tests require recent revision docs to appear in context output.
- `src/micromax_editor/command_dispatcher.py` is registration-only after rev0828. Command behavior lives in `buffer_commands.py`, `show_commands.py`, `plugin_commands.py`, `macro_commands.py`, `replace_commands.py`, `help_commands.py`, `binding_commands.py`, `keymode_commands.py`, `picker_commands.py`, `option_commands.py`, and `session_commands.py`.
- `src/micromax_editor/buffer_commands.py` owns the extracted file/buffer/navigation commands. Its scripted `open` path intentionally resolves `checked_sandbox_path` through `command_dispatcher` for compatibility with the late-bound monkeypatch seam restored in rev0830.
- `src/micromax_editor/prompt_suggestions.py` owns the extracted command-ish prompt candidate logic, but still takes a broad editor object. It remains a good narrow seam to purify.
- `src/micromax_editor/prompt_refresh.py` owns the current picker row application, query/limit/browse-budget policy, active-kind guard, shared refresh dispatch seams, shared picker submit target resolution, and row-level helpnav/helpoutline submit resolution. `Editor._submit_recent_prompt()` remains deliberately editor-local because it performs recent-file authority checks plus open/message side effects.
- `src/micromax_editor/docs_index.py`, `markdown_docs.py`, and `docs_cues.py` own docs/help parsing and cues. Rev0855 centralizes the docs-cues zero-metric schema so zero-sized viewports and active viewports expose the same metric keys. Installed help is curated through `docs/installed-help-manifest.txt` and package-data tests; source archives still carry the larger docs cube.
- `src/micromax_editor/micromax_bridge.py` remains a large hostcall installer and is a good future subfamily split target.
- `src/micromax_editor/editor.py` remains the large coordination object and should receive fewer new behaviors over time.

## Useful evidence commands

```bash
python tools/mxlint.py
python tools/mxcontext.py --check
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_docs_living_hygiene.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```

Equivalent explicit aggregate commands:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --checkpoint-tests \
  --max-new-tests 120 \
  --max-new-files 8 \
  --test-batch-size 0 \
  --file-timeout 180 \
  --max-runtime-seconds 25 \
  --json .artifacts/mxtest-all-64.json \
  --durations 0
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --verify-current .artifacts/mxtest-all-64.json
```

## Cloudtainer audit watch-list

- Keep `.artifacts/mxtest-all-64.json` current after every source/doc/workflow/tooling edit; the carried manifest should verify source, environment, completeness, and resume-safety before packaging.
- Keep the living-doc freshness guard for this file focused and current. Old runtime-budget values, side-manifest paths, stale rev headings, or stale aggregate command text should fail `tests/test_docs_living_hygiene.py`.
- Source-dependency partitioning is live and avoids many docs-only/runtime-only invalidations, but it remains heuristic rather than dynamic tracing.
- Installed help is intentionally curated. Do not re-expand wheel help to all root docs just because the source archive carries every revision note.
- The largest waste/risk concentration is still structural: `src/micromax_editor/editor.py`, `src/micromax_editor/micromax_bridge.py`, `src/micromax_editor/docs_cues.py`, and `tools/mxtest.py` are large enough that future changes should prefer extraction seams with focused tests. Rev0854 reduced `Editor.submit_prompt()` to roughly 355 lines and fixed a real stale-suggestion raw-open bug. Rev0855 reduced `docs_cues_model_from_parts()` to roughly 1,928 lines by centralizing zero-metric initialization and fixing zero-viewport schema drift; any deeper split there must be model-output-preserving.
- Duplicate numeric doc prefixes still exist and should be either renumbered or documented as intentional before adding more ambiguous numbered notes.
