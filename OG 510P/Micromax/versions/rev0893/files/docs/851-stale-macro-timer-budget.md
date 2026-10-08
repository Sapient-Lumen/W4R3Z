# Stale macro playback and timer pending-work budget (rev0893)

Rev0890 removed retired plugin wordlists from live dictionary lookup, rev0891 blocked generated callbacks from retired plugin generations, and rev0892 cleared active prompt/query/open-url interaction rows.  One remaining delayed-execution lane was saved macro slots: a macro step can hold plugin root/generation provenance and later replay a command or action without first touching dictionary lookup.

Rev0893 makes saved macro slots participate in the same live-generation rule.  `Editor._stale_plugin_macro_reason()` derives a stale denial from the macro slot authority, `Editor._drop_stale_plugin_macro()` removes one retired slot, and `Editor._prune_stale_plugin_macros()` keeps macro inventory from advertising non-runnable plugin-owned rows.  Playback, raw macro read, and macro detail/list surfaces now drop stale retired plugin macro slots before they can execute or be reported as live automation.

The revision also adds a concrete pending-work budget for delayed callbacks.  `ed.after` now routes through `Editor.schedule_timer_checked()` instead of scheduling directly into `TimerQueue`; the editor refuses new delayed callback work when `max_pending_timers` is reached.  This does not pretend to be process isolation, but it closes an easy in-process memory/cleanup-pressure path where a legitimate hostcall could enqueue unbounded timer work.

## Runtime surfaces changed

- Macro slot storage/clearing now goes through `_replace_macro_slot()` and `_clear_macro_slot()` so cleanup paths preserve the stable `last` alias instead of open-coding slot mutation.
- `play_macro()` refuses retired plugin macro slots with `macro play: stale plugin macro: ...` and clears the slot.
- `macro_names()`, `macro_detail_row()`, and `get_macro()` prune retired plugin macro slots before reporting or returning their step payloads.
- `hc_ed_after` calls `Editor.schedule_timer_checked()`; the helper enforces `max_pending_timers` before appending to the timer queue.
- `mxaudit --check` now guards retired macro playback refusal and the timer pending-work budget seam.

## Preservation tests

Focused tests prove that:

- generation cleanup removes plugin-owned saved macro slots as before;
- a reinserted saved macro step from a retired plugin generation is refused before playback and removed from later inventory;
- `ed.after` refuses scheduling when the pending-timer budget is full;
- canceling a timer frees budget for a later delayed callback.

## Remaining risk

This closes the saved-macro stale-execution lane, but the larger resource-handle audit is not complete.  The next pass should enumerate remaining plugin-owned objects that are neither dictionary words, generated callbacks, active interactions, nor macro steps, then either route them through a live-generation check, clean them by generation, or mark them as metadata-only.
