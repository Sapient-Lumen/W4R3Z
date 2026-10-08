# Rev0853 helpnav/outline row seam and risky-surface audit

Rev0853 keeps the work in the runtime seam already opened by rev0852 instead of adding another registry layer.

## What changed

- Added `prompt_refresh.resolve_prompt_row()` for picker submissions that need the whole selected row rather than only the inserted candidate.
- Added `prompt_refresh.parse_prompt_linecol()` for the 1-based `line[:col]` heading-location fields used by help navigation and outline rows.
- Routed `Editor.submit_prompt()` helpnav and helpoutline branches through those helpers, removing their duplicate selected-suggestion / typed-query / first-apropos row resolution and duplicate line-location parsing.
- Added focused helper tests plus editor integration tests proving helpnav/helpoutline submissions re-resolve after the user types past the original selected suggestion.
- Fixed `mxcontext.py` TODO-section parsing so older `## Completed` package bullets no longer override the current `# TODO (revN)` package handoff check.

## Why this was the right risk lane

`Editor.submit_prompt()` is one of the highest-risk coordination methods because it mixes prompt authority, history, picker resolution, command dispatch, filesystem opening, help navigation, and status messages. Rev0852 extracted simple target resolution for picker branches. The remaining helpnav/helpoutline branches still repeated a row-oriented variant of that same rule and parsed heading locations inline. Rev0853 extracts that row-oriented rule without moving help-following, jump side effects, history writes, or user-facing messages.

## Audit snapshot

A small AST scale audit after the refactor still shows the main concentration points:

```text
src/micromax_editor/editor.py: Editor class ~23129 lines; submit_prompt ~411 lines
src/micromax_editor/docs_cues.py: docs_cues_model_from_parts ~2081 lines
src/micromax_editor/prompt_refresh.py: largest helper resolve_prompt_target ~43 lines; resolve_prompt_row ~33 lines
src/micromax_editor/micromax_bridge.py: hostcall installer remains a large future split target
tools/mxtest.py: run_all_chunks ~469 lines; main ~418 lines
```

The severe waste risk is still broad runtime invalidation from edits to the million-byte editor file, not the small prompt helper module. Future runtime changes should keep moving repeated side-effect-light picker/plumbing policy into tested helper modules and leave side effects in `Editor` until the boundary is proven.

## Focused evidence

- `python tools/mxlint.py`
- `python tools/mxcontext.py --check`
- `pytest -q tests/test_prompt_refresh.py tests/test_editor_helpnavpick.py tests/test_editor_helpoutlinepick.py tests/test_editor_help_picker_browse_budget.py tests/test_mxcontext.py`
- `.artifacts/mxtest-all-64.json` refreshed and verified for the final source tree.

## Remaining watch-outs

- `submit_prompt()` is smaller but still too broad. The next safe cut is likely a tiny helper for palette target-kind resolution or recent/recentdir feedback sharing, not a full prompt registry.
- `docs_cues_model_from_parts()` is a larger structural risk than the prompt helpers, but it should be split only with exact model-output equivalence tests because it owns many counter fields.
- Any runtime source edit invalidates the carried aggregate manifest until `.artifacts/mxtest-all-64.json` is refreshed and `make test-verify-current` passes.
