# Archived `docs/43-worklist.md` through rev0855

Preserved during the rev0856 mission/context reset. The corresponding living document now contains only current handoff material.

---

# Worklist

Rev0855 docs-cues pass landed: zero-sized docs-cues payloads now expose the full metric schema, closing a fragile headless/UI consumer edge before any wider parser split.

This is the active worklist. Historical append-only worklist content through rev0822 is preserved in `docs/history/43-worklist-through-rev0822.md`.


## Completed in rev0855

- Added `DOCS_CUE_ZERO_METRIC_KEYS` and `_zero_docs_cue_metrics()` so zero-sized docs-cues payloads keep the same top-level metric schema as normal active payloads.
- Removed the stale hand-maintained initial counter block from `docs_cues_model_from_parts()`, cutting the helper from about 2,081 lines to about 1,928 lines without moving parsing semantics.
- Added focused coverage that compares zero-viewport and active docs-cues key sets and verifies every zero metric is present and zero.
- Added `docs/813-docs-cues-zero-schema-refactor.md` with the audit/refactor note and next-seam guidance.
- Refresh `.artifacts/mxtest-all-64.json` after this runtime/docs/test change before claiming current-source aggregate evidence.

## Completed in rev0854

- Added a strict recent picker submit resolver so changed prompt text must match visible recent-file truth before Enter can open anything.
- Extracted the shared `recentpick` / `recentdirpick` submit body from `Editor.submit_prompt()`.
- Added focused tests proving typed queries re-resolve away from stale selected rows and unmatched typed queries do not create raw buffers.
- Added `docs/812-recent-picker-raw-open-guard.md` with the concrete bug/audit trail and next-seam guidance.
- Refresh `.artifacts/mxtest-all-64.json` after this runtime/docs/test change before claiming current-source aggregate evidence.

## Completed in rev0853

- Added `prompt_refresh.resolve_prompt_row()` for picker submit branches that need the full row, not just the inserted candidate.
- Added `prompt_refresh.parse_prompt_linecol()` and routed helpnav/helpoutline submit branches through it.
- Added focused helper and editor integration tests proving changed prompt text re-resolves away from a previously selected helpnav/helpoutline row.
- Fixed `mxcontext.py` current TODO-section parsing so older completed package bullets no longer make `--check` warn after a new rev heading lands.
- Added `docs/811-helpnav-outline-row-seam-audit.md` with a concrete AST scale audit and next-seam guidance.
- Refreshed `.artifacts/mxtest-all-64.json` after this runtime/docs/test change before claiming current-source aggregate evidence.

## Completed in rev0852

- Added a focused living-doc freshness guard so stale `docs/02-repo-map.md` aggregate commands fail tests instead of surviving a handoff.
- Refactored `tools/mxcontext.py` to derive newest revision docs from `docs/revision-index.json`, trimming the manual newest-doc tail from the static context list.
- Extracted `prompt_refresh.resolve_prompt_target()` and routed topic, binding, buffer, plugin, recent, recentdir, doc, helplink, mark, and jump picker submissions through it.
- Added focused prompt helper, context, and doc hygiene tests.
- Refresh `.artifacts/mxtest-all-64.json` after this runtime/tooling/docs change before claiming current-source aggregate evidence.

## Completed in rev0851

- Audited the incoming rev0850 archive for stale living-doc claims, source/test/doc scale, and cloudtainer waste.
- Rewrote `docs/02-repo-map.md` so evidence commands use `--max-runtime-seconds 25`, installed help is described as curated, and source-dependency partitioning is treated as live.
- Added `docs/809-cloudtainer-deep-audit.md` with missing guardrails, wasteful concentrations, and staged recommendations.
- Brought `tools/mxcontext.py` forward through rev0851 and added a test that top revision-index docs are included in context output.
- Left runtime source untouched; the next runtime seam should still start from focused prompt/provider work, not a broad editor rewrite.
- Refresh `.artifacts/mxtest-all-64.json` after this docs-only change before claiming current-source aggregate evidence.

## Completed in rev0850

- Changed `make doctor-chunked` to forward `MAX_NEW_TESTS`, `MAX_NEW_FILES`, `TEST_BATCH_SIZE`, and `FILE_TIMEOUT` into `mxdoctor --chunked`.
- Added matching direct `mxdoctor --chunked` CLI defaults and override flags.
- Added focused tests for the `mxdoctor` command builder and Makefile target so future workflow edits cannot reintroduce budget-shape drift.
- Refresh `.artifacts/mxtest-all-64.json` after this workflow/tooling/test/docs change before claiming current-source aggregate evidence.

## Completed in rev0849

- Changed `make doctor-chunked` to forward `TEST_MANIFEST` as `mxdoctor --chunked --manifest ...`.
- Changed `make doctor-chunked` to forward `MAX_RUNTIME_SECONDS` as `mxdoctor --chunked --max-runtime-seconds ...`.
- Added focused Makefile coverage so a future workflow edit cannot silently reintroduce a doctor side manifest or budget lane.
- Refresh `.artifacts/mxtest-all-64.json` after this workflow/test/docs change before claiming current-source aggregate evidence.

## Completed in rev0848

- Changed `Makefile` default `MAX_RUNTIME_SECONDS` from 240 to 25 for the archive-carried aggregate lane.
- Made `mxdoctor --chunked` pass a 25-second `--max-runtime-seconds` by default.
- Added override paths so long local runs can still be explicit instead of accidental.
- Added Makefile and mxdoctor coverage for the default and override behavior.
- Fixed runtime-budget-derived child timeouts so graceful budget exhaustion does not masquerade as file/test timeout evidence.
- Fixed combined bounded-stop reasons so later matching passed chunks are still preserved.
- Refresh `.artifacts/mxtest-all-64.json` after this workflow/tooling/docs change before claiming current-source aggregate evidence.

## Completed in rev0847

- Added workflow and test-config token partitions to `tools/mxtest.py` source-dependency inference.
- Made Makefile handoff tests depend on the `workflow` partition.
- Made installed-resource/package-data tests depend on the `test-config` partition.
- Added focused regression tests so Makefile and pyproject/package-data edits change the relevant chunk dependency digest.
- Fixed interrupted-stop handling so later matching passed chunks are preserved instead of replaced by `not_run` records.
- Refresh `.artifacts/mxtest-all-64.json` after this tooling/test/docs change before claiming current-source aggregate evidence.

## Completed in rev0846

- Removed the duplicate hard-coded picker-kind tuple from `Editor.prompt_complete()`.
- Kept command prompt completion as the only special token-completion path.
- Made picker prompt completion eligibility follow `_picker_prompt_refreshers()` membership, so future picker kinds need one dispatch-map edit instead of a second allowlist edit.
- Added a synthetic picker regression test proving `prompt_complete()` accepts dispatcher-provided picker kinds.
- Refresh `.artifacts/mxtest-all-64.json` after this source change before claiming current-source aggregate evidence.

## Completed in rev0845

- Centralized active picker prompt refresh dispatch in `Editor` so prompt text syncing and prompt completion share the same picker-kind map.
- Fixed help link, help outline, and combined help navigation pickers so `prompt_complete()` can reseed rows after suggestions are cleared.
- Added focused coverage for `helplinkpick`, `helpoutlinepick`, and `helpnavpick` Tab reseeding.
- Refresh `.artifacts/mxtest-all-64.json` after this source change before claiming current-source aggregate evidence.

## Completed in rev0844

- Centralized active prompt-kind guarding in `prompt_refresh.refresh_prompt_suggestion_rows()`.
- Ensured wrong-kind refresh attempts do not call the provider or mutate prompt state.
- Kept existing editor refresh method names while moving the guard into the shared seam.
- Refreshed `.artifacts/mxtest-all-64.json` to a full current-source aggregate pass.

## Completed in rev0843

- Added shared prompt row-budget helpers in `prompt_refresh.py` for grouped-section pickers and direct-or-grouped help-style pickers.
- Removed repeated query stripping, positive limit coercion, section flattening, and empty-query browse-budget selection from broad picker row provider methods.
- Added focused helper tests for empty-query browse budgeting, non-empty query linear limits, and direct-vs-grouped routing.
- Refresh `.artifacts/mxtest-all-64.json` after this source change before claiming current-source aggregate evidence.

## Completed in rev0842

- Added `src/micromax_editor/prompt_refresh.py` as the shared picker row-to-suggestion-session boundary.
- Replaced repeated prompt picker refresh mutation blocks in `Editor` with a single `_refresh_picker_prompt_suggestions()` helper while preserving existing private refresh method names.
- Added focused prompt refresh tests covering row application, empty-row no-op behavior, and wrong-kind provider suppression.
- Paid the deliberate runtime invalidation cost only after rev0841 had a full aggregate baseline; refresh `.artifacts/mxtest-all-64.json` after this source change before claiming current-source evidence.

## Completed in rev0841

- Completed `.artifacts/mxtest-all-64.json` as a full current-source aggregate pass: 2,189 passed, zero failures, zero timeouts, zero partials, zero not-run tests.
- Preserved the pass by keeping runtime source untouched during the evidence push, then refreshed docs and re-verified the manifest after the docs-only update.
- Audited the aggregate execution lane: bounded resumes were safer than one large outer-cloudtainer run because they checkpointed evidence after every small batch.

Rev0840 also:

- Hardened `mxdoctor` timeout teardown so it uses `killpg` only after confirming the child has its own process group.
- Added a direct-child fallback for timeout cleanup when process-group identity is unavailable or unconfirmed.
- Removed a duplicate `preflight_command()` docstring line instead of growing the doctor registry.
- Added focused tests for confirmed-group and unconfirmed-group timeout teardown behavior.

## Active lanes

### 1. Evidence manifest handoff

Use the archive-carried merged checkpoint/runtime lane:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```

Or run the explicit command:

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

The current manifest is complete once refreshed for rev0855. After any source edit, treat it as stale until `--verify-current` reports source and environment matches again.

### 2. Prompt seam purification

`prompt_refresh.py` now owns the common picker row-to-suggestion-session mutation path, common picker query/limit/browse-budget policy, active prompt-kind guard, shared target resolution, and shared row resolution; `Editor` now has one active picker refresh dispatch helper, and `prompt_complete()` uses that dispatch helper as the picker allowlist. `prompt_suggestions.py` is extracted and has a table-driven root-command preview map, but it still depends broadly on the editor object. The next prompt pass should shrink that dependency in safe steps:

- keep row providers query-only and prompt mutation centralized;
- inventory/detail formatting second;
- then a narrow protocol if tests make the boundary clear.

### 3. Source-dependency refinement

The first source-dependency cut is live. Keep it conservative even with the full aggregate pass:

- runtime partition changes invalidate all chunks;
- selected test files and `tests/conftest.py` are explicit file dependencies;
- docs/plugins/tools/portability/workflow/test-config sensitivity is inferred from selected test filenames and test-file tokens.

### 4. Installed help diet

Installed help follows `docs/installed-help-manifest.txt`. Add a new doc there only when it is useful as runtime help for installed users. Revision archaeology and cloudtainer audit notes should remain source-archive docs, not installed help.

## Guardrails

- Preserve behavior first; do not rewrite while extracting.
- Do not let archive lineage fork again: every handoff must advance the revision number.
- Keep authority/provenance tests focused and explicit.
- Keep current docs small; put archaeology under `docs/history/` or `docs/revision-index.json`.
- Keep the required archive filename shape: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
