# Rev0854 recent-picker stale-selection raw-open guard

## What changed

Rev0854 continues the prompt-submit seam from rev0852-rev0853, but focuses on a concrete correctness bug rather than a new registry. `recentpick` and `recentdirpick` used the generic picker target resolver. When a prompt still had old suggestions and the user typed a new non-matching query before pressing Enter, that generic resolver treated the typed text as the target. For a recent-file picker, that meant a stale suggestion session could accidentally run `open unmatched-recent-query` and create/switch to a raw path that was never a recent-file match.

The fix is deliberately local:

- `Editor._resolve_recent_prompt_target()` now resolves recent picker submissions through recent-file truth only.
- `Editor._submit_recent_prompt()` owns the shared `recentpick` / `recentdirpick` body: target resolution, exact slot-miss wording, zero-match wording, open dispatch, and recent-aware feedback replacement.
- `submit_prompt()` now delegates both recent branches to that helper instead of duplicating the body twice.

## Guarded behavior

The new focused tests cover two high-risk stale-row cases for both `recentpick` and `recentdirpick`:

1. A selected stale row plus typed query `a.txt` re-resolves to the matching recent file and reports the original stable MRU slot.
2. A selected stale row plus typed query `unmatched-recent-query` returns `0 recent file(s)` and does **not** open or create a raw buffer for that text.

This closes a real authority leak in the picker semantics: recent-file pickers should submit recent-file targets, not silently degrade into arbitrary raw `open` when prompt text diverges from the selected suggestion.

## Measured risk movement

The extraction reduces `Editor.submit_prompt()` from roughly 411 lines in rev0853 to roughly 355 lines in rev0854. The large remaining hotspots are still unchanged in priority order:

- `docs_cues_model_from_parts()` remains about 2,081 lines and needs exact model-output preservation before a split.
- `install_editor_hostcalls()` remains a large future hostcall-family split target.
- `tools/mxtest.py::run_all_chunks()` remains a large evidence-lane coordinator but should not be rewritten while the checkpoint lane is actively protecting handoffs.

## Next cut

The next runtime cut should stay in this style: identify one stale-authority or duplicated side-effect seam, add focused regression coverage first or alongside the change, and only then refresh the aggregate manifest. Avoid broad prompt registries until repeated, tested branches demand one.
