# DeriveBSD rev0503 risk-first substance audit

Input archive: `DeriveBSD-rev0502-2026.06.04.02.50-cloudtaineraudit-r533idfix-wastebudget-stoneglass.zip`.

This pass deliberately favors executable guardrails and cross-artifact checks over another doctrine/registery expansion.

## What changed

1. **Generated-artifact release IDs are now semantically guarded.** Added `tools/check_generated_artifact_version_ids.py` and a red fixture at `spec/examples/invalid/cube-generated-artifact-version-ids/stale-r533-report-id-r532.json`. The checker scans canonical generated examples and requires durable top-level `*_id` fields to contain the normalized release token from `generated_for_version`, so the r532/r533 skew fixed in rev0502 cannot return as a locally-green stale comparison.

2. **Hygiene can now emit a typed run ledger.** Added `spec/cube.hygiene.run.ledger.schema.json`, `spec/examples/cube.hygiene.run.ledger.json`, and ledger mode in `tools/hygiene.py` via `--ledger` / `--ledger-json` plus `--check-timeout-seconds` / `--timeout-seconds`. Ledger entries include tool, profile, command, return code, elapsed seconds, timeout status, output byte counts, output digests, and best-effort child RSS. Ledger mode rewrites the JSON file after each check so a cloudtainer or CI timeout leaves partial structured evidence.

3. **The removable-media first lane now has a vertical-slice coherence check.** Added `tools/check_removable_media_local_fallback_vertical_slice.py`, which cross-checks existing examples from read-only attach through capture-first import, detach, post-detach constrained launch evidence, and reader admission. This is not a real FreeBSD executable prototype yet, but it is a single guard that fails if the modeled runnable path stops hanging together.

4. **Front-door growth is now ratcheted.** Added `tools/check_frontdoor_budget.py` and `tools/baselines/frontdoor_budget.json` for `README.md`, `docs/00-index.md`, and `docs/99-llm-runbook.md`. The budget does not pretend these surfaces are small; it prevents silent growth without an explicit budget edit.

5. **Cube checker duplication was reduced.** Added `tools/cube_check_lib.py` and refactored the cube audit/backlog/checkset checker cluster onto shared helpers for failure reporting, schema validation, required text-token checks, and generated-artifact ID consistency.


6. **Current cube-generated artifacts now have to match the current cut, not just themselves.** During final validation, the first r534 archive still had self-consistent r533 cube audit/backlog/checkset artifacts. `tools/check_generated_artifact_version_ids.py` now checks the current cube-generated artifact families against the top `CHANGELOG.md` release as well as checking ID-token agreement, and the regenerated cube examples/schemas now carry `2026-06-04r534` plus `20260604-r534` durable IDs.

7. **Cloudtainer waste was corrected instead of hidden.** The work now records bounded hygiene progress as structured evidence instead of relying on scrollback. The included schema-cube hygiene ledger is the durable proof surface for the bounded checks that completed, and the partial release-critical ledger documents where the interrupted broader run stopped.

## Validation performed

Passed in this cloudtainer after the final r534 regeneration/current-cut guard fix:

- `python3 tools/check_generated_artifact_version_ids.py`
- `python3 tools/check_cube_schema_audit_report.py`
- `python3 tools/check_cube_schema_refactor_backlog.py`
- `python3 tools/check_cube_hygiene_checkset_manifest.py`
- `python3 tools/check_cube_hygiene_run_ledger.py`
- `python3 tools/validate_spec_examples.py`
- `python3 tools/lint_spec_schemas.py`
- `python3 tools/check_schema_kind_matches_filename.py`
- `python3 tools/check_spec_example_coverage.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/check_frontdoor_budget.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 tools/check_hygiene_checkset_completeness.py`
- `python3 tools/check_consistency.py`
- `python3 tools/check_validation_logs_clean.py`
- `python3 tools/check_text_files_final_newline.py`
- `python3 tools/check_python_tool_executable_bits.py`
- `python3 tools/check_version.py`
- `python3 tools/check_readme_latest_cut.py`
- `python3 tools/hygiene.py --profile schema-cube-audit --ledger-json session-reviews/DeriveBSD-rev0503-2026.06.04-schema-cube-audit-hygiene-ledger.json --timeout-seconds 60`

The successful schema-cube audit hygiene ledger is included as `session-reviews/DeriveBSD-rev0503-2026.06.04-schema-cube-audit-hygiene-ledger.json`. A release-critical ledger was also attempted and is included as a partial run evidence file at `session-reviews/DeriveBSD-rev0503-2026.06.04-release-critical-hygiene-ledger.json`; it reached the first 12 release-critical checks before the outer cloudtainer command was interrupted, with no failed child check recorded in that partial ledger.

## Remaining risk

The full release-critical wrapper is still not a comfortable single interactive operation in this cloudtainer. The next correction should use the new ledger mode on release-critical and split or optimize whichever checks dominate elapsed time and memory.

The highest-value product cut remains a tiny executable FreeBSD removable-media local fallback harness: probe filesystem, mount read-only with hardening flags, capture one regular file to digest-addressed storage, detach, then launch the post-detach worker with the constrained envelope already modeled by the examples.
