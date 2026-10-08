# Generation interaction cleanup (rev0892)

Rev0891 stopped retired plugin-generation callbacks before their bodies executed, but the remaining interaction lane was more stateful than a callback row.  Active command prompts, query-replace sessions, pending external-URL confirmations, and capture keymodes can all sit in the editor after plugin code returns.  If a stale copy is reinserted by a test, embedding, or surviving heap reference, it should not borrow user/editor authority or accidentally bind to a replacement plugin generation.

Rev0892 makes those delayed interaction rows generation-scoped.  `RuntimeInteractionGenerationSnapshot` captures only prompt, qreplace, pending-open-url, and active keymode rows owned by a selected plugin root/generation.  `restore_interaction_generation_state()` restores those rows without rewinding unrelated trusted/user interactions, and `Editor.remove_plugin_interaction_generation()` removes matching rows during plugin generation cleanup.

The response path now has an explicit stale authority seam.  `Editor._stale_plugin_authority_reason()` turns a captured plugin root/generation into a human denial such as `stale plugin qreplace: plugin alpha generation N is not loaded`.  `Editor._drop_stale_plugin_interaction()` then removes the matching delayed interaction so repeated responses do not keep hitting the same retired object.  Prompt-origin actions receive the same treatment before submit/navigation work runs.

## Runtime surfaces changed

- `RuntimeInteractionGenerationSnapshot` records generation-owned active keymodes, prompts, query-replace state, qreplace cursor state, and pending external URL confirmations.
- `snapshot_runtime_generation_state()` now includes interaction generation rows alongside recovery, recent, palette, prompt-history, saved-cursor, clipboard, search, help-history, and macro generation state.
- `cleanup_plugin_generation_state()` includes `remove_plugin_interaction_generation` in the generation cleanup sweep.
- `_interaction_response_denial()` rejects stale prompt/qreplace/open-url authorities before lower-authority response policy can fall back to ambient editor/user authority.
- `_run_prompt_origin_callback()` clears stale plugin prompts rather than leaving a dead prompt active after the denial.
- `mxaudit --check` now records `generation-interactions=True` and `retired-interaction-guard=True`.

## Preservation tests

Focused tests now prove that:

- generation snapshots restore only the selected plugin interaction rows and preserve unrelated trusted rows;
- a reinserted retired query-replace session does not modify the buffer and is cleared;
- a reinserted retired external-URL confirmation does not open the URL and is cleared;
- a reinserted retired command prompt does not submit and is cleared.

## Remaining risk

This closes the active interaction lane that bypassed dictionary lookup, direct execution tokens, and the shared callback runner.  The remaining stale-handle search is narrower: enumerate plugin-owned resource handles that are neither executable callbacks nor active interaction rows, then either route them through a live-generation check or document them as metadata-only.
