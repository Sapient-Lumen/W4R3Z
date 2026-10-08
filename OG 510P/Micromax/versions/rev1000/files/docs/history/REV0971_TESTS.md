# Revision 0971 test evidence

This file records scoped evidence from the final source generation. It is not a complete repository-suite claim.

## Pure planner and prompt policy

```bash
pytest -q tests/test_prompt_refresh.py tests/test_project_picker_model.py --durations=8
```

Result: **19 passed in 0.42s**.

This covers deterministic project-row planning, complete-inventory query search, exact dedupe and metadata rejection, one inventory-normalization pass over 4,096 members, context capping, section labels, and preferred/avoided prompt selection including the honest row-zero fallback.

## Navigation journeys

```bash
pytest -q tests/test_editor_picker_mru_return.py --durations=8
```

Result: **6 passed in 15.84s**.

```bash
pytest -q tests/test_editor_navigation_picker_retry.py --durations=8
```

Result: **5 passed in 16.54s**.

These slices prove buffer/recent MRU return, active-target avoidance, query ranking after typing, one visible-recent register read for return-target planning, stale recent-row refusal, retained failed-submit query/cursor/keymode, exact project snapshot reuse without rescan, successful correction after failure, and script-origin retention without `cap.fs-open` laundering.

## Project scanner and picker boundary

The 18 tests in `tests/test_editor_project_file_picker.py` were run as three independently bounded six-test slices so worker cleanup could not outlive the command window:

- scanner determinism, budgets, timeout cleanup, and large payload ordering — **6 passed in 0.36s**;
- immutable snapshot, two-file toggle, dirty/context cues, script non-disclosure, member-only open, and stale/symlink rejection — **6 passed in 16.31s**;
- hidden-file policy, delayed script authority, deep-copied prompt lifecycle, and finite malformed-limit handling — **6 passed in 3.51s**.

## Modified lifecycle, status, and TUI projections

Each changed legacy/UI case passed independently:

- `test_recent_tracks_open_and_save_and_picker_opens` — **1 passed in 7.51s**;
- `test_recentdirpick_groups_rows_by_directory_and_keeps_literal_details` — **1 passed in 8.53s**;
- `test_recentpick_status_summary_exposes_grouped_preview` — **1 passed in 6.13s**;
- `test_recentpick_render_shows_prompt_position_summary` — **1 passed in 4.78s**.

## Living docs, generated contracts, and metadata

```bash
pytest -q -p no:cacheprovider tests/test_revision_index.py tests/test_mxcontext.py tests/test_docs_living_hygiene.py
```

Result: **12 passed in 3.07s**. The slice verifies the current `Latest substantive landing` handoff, historical `Latest tiny landing` compatibility, and continued orphan/revision-mismatch rejection. The living-doc checks had already caught and verified the correction of a case-sensitive installed-roadmap anchor rather than suppressing the contract. A final release audit then exposed 68 inlined docs and 65 code paths; after moving rev0961–rev0962 evidence triplets to `docs/history/` and removing two unchanged tests from rev0971's touched-code ledger, the regenerated handoff contains exactly **64 docs** and **63 code paths**.

```bash
pytest -q tests/test_effect_contracts.py --durations=8
```

Result: **5 passed in 22.87s**.

## Static and generated checks

- `python -m py_compile` over the changed runtime, planner, context-currentness, and focused test modules — passed.
- `bash scripts/lint.sh` — passed (`mxlint: ok`).
- `python tools/mxeffects.py --check` — passed with 23 live rows at rev0971.
- `python tools/mxaudit.py --check` — passed; curated entrypoints, installed help, release hygiene, and high-risk boundaries are current.
- `python tools/mxcontext.py --check` — passed before final sealing and is rerun after context regeneration.

```bash
pytest -q tests/test_mkrevzip.py --durations=10
```

Result: **52 passed in 18.54s** with one intentional `zipfile` warning from the duplicate-member rejection fixture. Coverage includes byte reproducibility, package-input mutation refusal, canonical names and timestamps, embedded context/provenance, member hashes, duplicate/path/mode rejection, lineage assertions, and verifier CLI output.

The exact archive receives a final context regeneration, cache cleanup, provenance verification, and `unzip -t` check before publication.
