# Rev795 help/message register authority

Rev795 pulls the remaining message-log and docs-help history pieces into the destructive-register authority lane opened by selection, jumplist, and recent-file MRU work.

Docs-help history and messages are not filesystem or shell authority, but they are user-facing evidence and recovery state. A lower-authority script that can erase trusted messages or replay/prune trusted help navigation can hide why a command failed or distort where `helpback` / `helpforward` should return.

Message rows carry `message_authority`, and destructive message operations route through `pop_message()` / `clear_messages()` instead of direct list mutation.

Help-history rows carry authority sidecars for back, forward, and session targets. Replay and prune operations preflight row authority before mutating history. Same-origin script rows remain usable by the script that created them, while legacy/missing sidecar rows normalize to trusted/editor authority.

The explicit unsafe escape hatch is `cap.history-clear` / `ed.history-clear`, which trusted code can enable for automation that is intentionally allowed to clear broader editor history.

Coverage is split across `tests/test_editor_message_log_authority.py`, `tests/test_editor_state_clear_authority.py`, and the existing help-history/navigation suites.
