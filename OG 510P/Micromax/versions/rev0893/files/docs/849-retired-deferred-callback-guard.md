# Retired deferred callback guard (rev0891)

Rev0890 removed replaced/unloaded plugin wordlists from the live VM dictionary and marked direct saved execution tokens as retired.  That closed the measured wordlist-retention leak, but it left a narrower stale-reference lane: a delayed object could still carry a retired plugin root/generation and later run an action spec, hook quotation, timer quotation, macro step, prompt action, or keymode response under ambient authority.

Rev0891 adds a generation-scoped guard at the shared deferred-callback runner.  When a delayed script callback carries a plugin root and generation, `Editor.run_script_origin_callback()` now verifies that the same plugin generation is still loaded before running the callback body.  If the generation is gone, the runner records a clear `stale plugin callback: ... is not loaded` message and returns `False` without executing the callback.

The guard is intentionally scoped to callbacks that actually carry a generation.  Older or malformed rows that only carry a root still retain the existing fail-closed behavior: `plugin_callback_context()` withholds the package-local load root, so package includes fall back to ordinary script filesystem policy and require `cap.fs-require`.  This preserves compatibility with existing low-level tests while closing the stale-generation path created by current plugin-origin registrations.

## Runtime surfaces changed

- `Editor._stale_plugin_callback_reason()` centralizes the live-generation check.
- `Editor.run_script_origin_callback()` refuses retired plugin generations before opening plugin/root/script contexts.
- `Editor.pump_timers()` now uses the same runner for script-originated timers instead of duplicating context setup.
- `HookWord.execute()` delegates script-originated hook handlers to the editor runner when available, so hooks and timers share the same stale-generation semantics as keybindings, prompts, macros, and action-chain callbacks.
- `mxaudit --check` now has a `retired_deferred_callbacks_reject_execution` seam and human output shows `retired-callback-guard=True`.

## Preservation tests

`tests/test_plugin_retired_wordlists.py` now covers three stale deferred references that bypass normal registry cleanup by reusing captured objects:

- a captured keybinding from a retired generation does not run after reload;
- a reinserted old hook handler does not run after reload;
- a reinserted old timer task does not run after reload.

Existing containment tests still prove that malformed legacy rows without a generation do not gain package-local include authority.

## Remaining risk

The guard stops callback bodies from executing when their captured plugin generation is retired.  It does not yet enumerate every possible resource handle or durable object that might contain plugin-owned data.  The next practical lane is smaller than before: find handles that are not routed through `run_script_origin_callback()` or retired `Word` execution, then either route them through a live-generation check or document why they are metadata-only.
