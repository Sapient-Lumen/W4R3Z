# Archived `TODO.md` through rev0855

Preserved during the rev0856 mission/context reset. The corresponding living document now contains only current handoff material.

---

Rev0855 note: docs-cues risk work landed a zero-viewport schema fix and a smaller initialization seam before attempting any wider parser split.

Latest tiny landing (rev0855): zero-sized docs-cues payloads now expose the same top-level metric keys as active payloads, with every metric zeroed instead of missing newer counters.

# TODO (rev0855)

- [x] Make `mxdoctor` timeout teardown use only a confirmed child process group, with direct-child fallback.
- [x] Keep the rev0840 code change in `tools/` so runtime chunks are not gratuitously invalidated.
- [x] Add focused `mxdoctor` timeout-teardown regression coverage.
- [x] Complete the current-source aggregate manifest.
- [x] Land the first prompt refresh provider seam: centralize picker row application while preserving existing refresh method names.
- [x] Land the second prompt refresh seam: centralize picker query normalization, positive limit coercion, and browse-budget row flattening.
- [x] Land the third prompt refresh seam: centralize active prompt-kind guarding.
- [x] Centralize active picker/prompt refresh dispatch and fix help picker Tab reseeding after suggestions are cleared.
- [x] Remove the duplicate prompt_complete picker-kind allowlist so picker eligibility follows `_picker_prompt_refreshers()`.
- [x] Include workflow/test-config partitions in mxtest source-dependency inference for Makefile and packaging/config-sensitive tests.
- [x] Preserve later matching passed chunks after `interrupted-*` stops, matching the existing max-runtime/max-new budget preservation.
- [x] Make default aggregate handoff commands stop at graceful cloudtainer-safe checkpoints instead of relying on external SIGTERM.
- [x] Make `make doctor-chunked` forward `TEST_MANIFEST` and `MAX_RUNTIME_SECONDS` so doctor chunked runs cannot silently use a side manifest/budget lane.
- [x] Make `make doctor-chunked` forward `MAX_NEW_TESTS`, `MAX_NEW_FILES`, `TEST_BATCH_SIZE`, and `FILE_TIMEOUT` so doctor and aggregate chunked runs use the same budget shape.
- [x] Audit the incoming rev0850 datacube for stale handoff claims, cloudtainer waste, source/test/doc scale, and missing automation guardrails.
- [x] Correct `docs/02-repo-map.md` from the old rev0836/240-second/pending-evidence story to the current rev0851/25-second/current-evidence lane.
- [x] Add `docs/809-cloudtainer-deep-audit.md` as the session audit ledger for missing, wrong, and speculative next cuts.
- [x] Bring `tools/mxcontext.py`'s static docs list forward through rev0851.
- [x] Add a focused `test_mxcontext` guard that the top revision-index docs are included in context output.
- [x] Add a focused living-doc freshness guard so stale aggregate command text in `docs/02-repo-map.md` cannot survive another handoff.
- [x] Extract shared picker submit target resolution without moving picker side effects or adding a broad prompt registry.
- [x] Extract shared helpnav/helpoutline row submit resolution and heading-location parsing without moving navigation side effects.
- [x] Extract shared recent/recentdir submit handling and prevent stale picker suggestions from granting raw `open` fallback.
- [x] Fix docs-cues zero-viewport schema drift and replace the stale hand-maintained initial metric block with a shared zero-metric helper.
- [ ] Continue narrowing picker/prompt submit/refresh seams or docs-cues sub-builders only after re-verifying aggregate evidence; avoid broad prompt/doc registries.
- [ ] Revisit source-dependency sensitivity after more aggregate evidence exists; runtime changes remain intentionally all-chunk invalidating.
- [x] package rev0840 with the required filename structure.
- [x] package rev0841 with the required filename structure and full aggregate evidence.
- [x] package rev0842 with the required filename structure and refreshed current-source evidence.
- [x] package rev0843 with the required filename structure and refreshed current-source evidence.
- [x] package rev0844 with the required filename structure and refreshed current-source evidence.
- [x] package rev0845 with the required filename structure and refreshed current-source evidence.
- [x] package rev0846 with the required filename structure and refreshed current-source evidence.
- [x] package rev0847 with the required filename structure and refreshed current-source evidence.
- [x] package rev0848 with the required filename structure and refreshed current-source evidence.
- [x] package rev0850 with the required filename structure and refreshed current-source evidence.
- [x] package rev0851 with the required filename structure and refreshed current-source evidence.
- [x] package rev0852 with the required filename structure and refreshed current-source evidence.
- [x] package rev0853 with the required filename structure and refreshed current-source evidence.
- [x] package rev0854 with the required filename structure and refreshed current-source evidence.
- [x] package rev0855 with the required filename structure and refreshed current-source evidence.


## Completed in rev0855

- Added `DOCS_CUE_ZERO_METRIC_KEYS` and `_zero_docs_cue_metrics()` so inactive/zero-sized docs-cues payloads expose the same metric keys as normal active payloads.
- Replaced the stale hand-maintained initial docs-cues counter block with the shared zero-metric helper, shrinking `docs_cues_model_from_parts()` without moving row parsing behavior.
- Added regression coverage comparing zero-viewport and active docs-cues key sets and checking all zero-metric counters are present and zero.
- Added `docs/813-docs-cues-zero-schema-refactor.md` as the concrete audit/refactor note for this seam.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this runtime/docs/test change before claiming current-source aggregate evidence.

## Completed in rev0854

- Added `Editor._resolve_recent_prompt_target()` so recent-file pickers submit recent-file truth only, not arbitrary raw text after stale suggestions.
- Added `Editor._submit_recent_prompt()` and routed `recentpick` / `recentdirpick` prompt submissions through the shared body.
- Added focused editor tests covering typed-query re-resolution away from a stale selected recent row and unmatched raw-open prevention for both recent picker modes.
- Added `docs/812-recent-picker-raw-open-guard.md` as the concrete audit/refactor note for this seam.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this runtime/docs/test change before claiming current-source aggregate evidence.

## Completed in rev0853

- Added `prompt_refresh.resolve_prompt_row()` for picker submit branches that need the whole selected row.
- Added `prompt_refresh.parse_prompt_linecol()` and routed helpnav/helpoutline heading jumps through it.
- Added helper and editor integration tests covering selected-row preservation plus typed-query re-resolution for helpnav/helpoutline.
- Added `docs/811-helpnav-outline-row-seam-audit.md` with measured AST risk surfaces for the next runtime cut.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this runtime/docs/test change before claiming current-source aggregate evidence.
- [x] package rev0853 with the required filename structure.

## Completed in rev0852

- Added a living-doc freshness test tying `docs/02-repo-map.md` to the Makefile aggregate lane defaults.
- Changed `mxcontext.py` so newest revision-note docs come from `docs/revision-index.json` instead of a manual tail list.
- Extracted `prompt_refresh.resolve_prompt_target()` and used it for repeated picker-style `submit_prompt()` target selection.
- Added focused helper/context/doc hygiene coverage and reran the prompt/editor picker tests affected by the runtime refactor.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this runtime/tooling/docs change before claiming current-source aggregate evidence.
- [x] package rev0852 with the required filename structure.

## Completed in rev0851

- Audited the incoming rev0850 archive for scale, stale claims, evidence state, and cloudtainer waste.
- Rewrote `docs/02-repo-map.md` so the living repo map no longer contradicts the Makefile/mxtest lane.
- Added `docs/809-cloudtainer-deep-audit.md` with missing guardrails, wasteful seams, and staged recommendations.
- Brought `tools/mxcontext.py` forward through the newest revision notes and repo map and added a guard that top revision-index docs appear in context output.
- Kept runtime source untouched; this revision is a docs/tooling/evidence freshness correction.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this docs change before claiming current-source aggregate evidence.
- [x] package rev0851 with the required filename structure.

## Completed in rev0850

- Changed `make doctor-chunked` to pass `MAX_NEW_TESTS`, `MAX_NEW_FILES`, `TEST_BATCH_SIZE`, and `FILE_TIMEOUT` into `mxdoctor --chunked`.
- Added matching `mxdoctor --chunked` CLI defaults and overrides for max-new-tests, max-new-files, test-batch-size, and file-timeout.
- Added focused `mxdoctor` and Makefile coverage so the doctor chunked lane cannot drift away from the aggregate handoff lane's work slicing.
- Audited the rev0849 command shape: manifest/runtime parity was not enough because same-manifest runs could still use different per-invocation budgets.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this workflow/tooling/test/docs change before claiming current-source aggregate evidence.
- [x] package rev0850 with the required filename structure.

## Completed in rev0849

- Changed `make doctor-chunked` to pass `--manifest "$(TEST_MANIFEST)"` into `mxdoctor --chunked`.
- Changed `make doctor-chunked` to pass `--max-runtime-seconds "$(MAX_RUNTIME_SECONDS)"`, matching the aggregate Makefile runtime knob.
- Added focused Makefile coverage so future handoff edits do not reintroduce a hidden doctor side lane.
- Audited the current rev0848 full-pass manifest before editing; refresh `.artifacts/mxtest-all-64.json` again after this workflow/test/docs change before claiming current-source full evidence.
- [x] package rev0849 with the required filename structure.
- [x] package rev0850 with the required filename structure.

## Completed in rev0848

- Lowered the Makefile aggregate default to `MAX_RUNTIME_SECONDS ?= 25` so `make test-all-chunks` stops at an intentional checkpoint in this cloudtainer.
- Made `mxdoctor --chunked` include the same 25-second runtime budget by default.
- Added explicit override paths: `MAX_RUNTIME_SECONDS=...`, `--max-runtime-seconds 0`, and `MXDOCTOR_CHUNKED_MAX_RUNTIME_SECONDS`.
- Added focused Makefile and mxdoctor tests for the cloudtainer-safe aggregate budget.
- Fixed runtime-budget-derived child timeouts so they leave checkpointed `not_run` remainder rows instead of manifest-poisoning `timed_out` rows.
- Fixed combined bounded-stop skip reasons so later matching passed chunks are preserved after `max-runtime-seconds` plus `max-new-*` stops.
- [x] Refresh `.artifacts/mxtest-all-64.json` after this workflow/tooling/docs change before claiming current-source aggregate evidence.
- [x] package rev0848 with the required filename structure.

## Next up (high leverage)

1. **Evidence lane:** keep `.artifacts/mxtest-all-64.json` current; after any source edit, resume with `make test-all-chunks`, then verify with `make test-verify-current`.
2. **Prompt seam purification:** continue from `prompt_refresh.py` toward narrower provider/detail seams without broad rewrites.
3. **Doctor timeout discipline:** keep bounded child cleanup and Makefile passthrough safe; do not widen the preflight registry unless it saves handoff time.
4. **Mxtest summary discipline:** keep manifest-summary reporting actionable; do not add a new registry/doctrine layer unless it saves handoff time.

## Current known risks

- The aggregate suite manifest must stay current after rev0853 runtime/docs/test changes; verify `.artifacts/mxtest-all-64.json` before packaging and after any further source edit.
- Source-dependency mapping is conservative and heuristic for docs/plugins/tools sensitivity.
- Installed help is curated; source-checkout docs remain complete, but wheel users will not see every revision/audit note in help pickers.

- [x] package rev0850 with the required filename structure and refreshed current-source evidence.
- [x] package rev0851 with the required filename structure and refreshed current-source evidence.
- [x] package rev0852 with the required filename structure and refreshed current-source evidence.
