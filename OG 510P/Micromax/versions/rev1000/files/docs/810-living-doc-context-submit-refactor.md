# Rev0852 living-doc guard, context-doc derivation, and prompt submit target seam

Rev0852 deliberately favored small enforceable changes over another registry layer.

## What changed

- Added a focused living-doc freshness test for `docs/02-repo-map.md`. The test derives the current aggregate lane from `Makefile` defaults and requires the repo map to show the matching chunk count, budget knobs, manifest path, and verify command. It also rejects the old 240-second command and side-manifest path that caused the rev0851 handoff drift.
- Changed `tools/mxcontext.py` so the newest revision-note docs are derived from `docs/revision-index.json` instead of hand-maintained in the static docs list. The static list now stays focused on stable design/history anchors; the current handoff trail follows the authoritative revision index.
- Extracted `prompt_refresh.resolve_prompt_target()` and routed repeated picker-style `submit_prompt()` branches through it. Topic, binding, buffer, plugin, recent, recentdir, doc, helplink, mark, and jump submissions now share one selected-suggestion / typed-exact / apropos fallback rule instead of open-coding it repeatedly inside the broad editor method.

## Why this was the right risk lane

The rev0851 audit found that the project was losing time to stale handoff truth and hand-maintained context lists. The new doc guard and context-doc derivation directly reduce that recurring waste. The prompt target resolver is a narrow runtime refactor in the already-open prompt seam: it cuts repeated branch plumbing without moving command side effects, picker feedback, authority checks, or file-opening behavior.

## Focused evidence

- `python tools/mxlint.py`
- `python tools/mxcontext.py --check`
- `pytest -q tests/test_prompt_refresh.py tests/test_editor_mx_commands_and_completion.py tests/test_editor_help_docs_navigation.py tests/test_editor_help_picker_browse_budget.py tests/test_editor_prompt_completion_hostcalls.py tests/test_editor_pluginpick.py tests/test_editor_macros_named.py`
- `pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_docs_living_hygiene.py tests/test_prompt_refresh.py`

## Remaining watch-outs

`submit_prompt()` is still too large. The next safe cut is not a broad prompt registry; it is another side-effect-light helper around helpnav/helpoutline row resolution or a per-picker submit handler only when tests prove the boundary. Runtime-source edits still invalidate all chunks, so aggregate evidence must be refreshed before packaging.
