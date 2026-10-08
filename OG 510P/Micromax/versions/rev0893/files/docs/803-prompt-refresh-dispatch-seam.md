# Rev845 - Prompt refresh dispatch seam

## Why this matters

Rev0842 moved full-row prompt suggestion mutation into `prompt_refresh.py`.
Rev0843 moved picker query/limit/browse-budget policy into that seam. Rev0844
moved the active prompt-kind guard there. One repetition still mattered in
`Editor`: active picker refresh dispatch was copied across prompt text syncing
and prompt completion.

That repetition hid a concrete bug: `helplink`, `helpoutline`, and `helpnav`
prompts were listed as completable prompt kinds, but `prompt_complete()` did not
route them through picker refresh. If their initial suggestion session was
cleared, pressing Tab fell into command-style completion and returned `False`
instead of reseeding the help picker rows.

## What changed

`Editor` now has one active picker refresh dispatch helper:

- `_picker_prompt_refreshers()` maps prompt kinds to refresh callbacks.
- `_refresh_active_picker_prompt_suggestions()` refreshes the current picker
  prompt when a registered kind is active.
- `_sync_prompt_after_text_change()` uses that helper instead of a long
  picker-kind `elif` chain.
- `prompt_complete()` uses that helper for non-command picker prompts after the
  topic/binding preview-message special cases.

The command completion path remains unchanged. The prompt refresh seam is still
incremental; this is not a broad command/prompt registry rewrite.

## Tests

`tests/test_editor_help_picker_browse_budget.py` now covers the bug directly:
`helplinkpick`, `helpoutlinepick`, and `helpnavpick` all refresh suggestions via
`prompt_complete()` after their initial suggestions are cleared.
