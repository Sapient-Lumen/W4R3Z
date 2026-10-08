# Rev795 message-log authority boundary

Rev795 continues the destructive-register audit after the jumplist and recent-file MRU work.  The target is the editor message log behind `ed.msg`, `ed.messages`, `ed.pop-message`, `ed.clear-messages`, and the scoped helpers `ed.with-messages` / `ed.capture-messages`.

The message log is recovery and audit evidence. It can contain save-conflict warnings, file-capability denials, plugin load errors, command feedback, and clues that explain why the editor refused or changed something.

`MessageLogSnapshot` captures both visible message strings and the `message_authority` sidecar. `capture_messages(...)` normalizes legacy/missing sidecar rows before snapshotting, and `restore_messages(...)` restores both strings and authority metadata before normalizing again. `ed.capture-messages` clears the message-authority sidecar while the temporary capture log is active, and plugin callback/runtime snapshots include the message log snapshot.

Trusted/user messages normalize to trusted authority. Script-origin messages carry current script/plugin authority. Same-origin scripts can pop or clear their own rows, while independent scripts cannot clear each other's rows and lower-authority scripts cannot pop or clear trusted rows unless trusted code explicitly enables `cap.history-clear`.

Focused coverage lives in `tests/test_editor_message_log_authority.py` and `tests/test_editor_state_clear_authority.py`.
