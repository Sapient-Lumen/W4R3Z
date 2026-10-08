# Rev795 state-history clear capability and message/help authority

Rev795 finishes the destructive-register audit lane that followed the selection, jumplist, and recent-file authority work.  The remaining high-risk state was not disk or plugin code; it was recovery and evidence state that lower-authority scripts could erase or replay after a failure.

## Failure mode

Editor-local registers are often the only evidence a user has after an automation mistake:

- message logs explain what was denied or what failed;
- help navigation history records where the user was in docs/help;
- recent-file and jumplist registers are recovery routes back to work context.

Earlier revisions protected selections, marks, jumplists, and recent MRU rows.  Message rows and help-history rows needed the same row-level provenance plus a deliberate trusted override for scripts that are intentionally allowed to clear editor history.

## Change

The editor treats message and help-history state as runtime-authority rows:

- `Editor.message_authority` tracks per-message provenance beside `messages`;
- `ed.pop-message` and `ed.clear-messages` preflight target rows before mutation;
- help back/forward/session history rows carry authority and block lower-authority replay or pruning of trusted/user rows;
- legacy/missing authority rows normalize to trusted/user state;
- adjacent rollback helpers preserve sidecars where they snapshot the visible state.

The explicit unsafe capability is:

- feature: `ed.history-clear`
- option: `cap.history-clear`

When enabled by trusted user/config code, script-origin code may clear protected message, recent-file, jumplist, and help-history rows.  Because it is a canonical `cap.*` option, script-origin code cannot grant it to itself.

## Regression coverage

Focused coverage lives in `tests/test_editor_state_clear_authority.py`, `tests/test_editor_message_log_authority.py`, `tests/test_editor_jump_history_authority.py`, `tests/test_editor_recent_register_authority.py`, and `tests/test_editor_capabilities_registry.py`.
