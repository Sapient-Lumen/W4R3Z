# Rev796 history-clear capability wiring

Rev796 preserves the rev793 through rev795 destructive-register authority work and finishes the missing capability/registry wiring for the linked handoff.  The code already had the important row-provenance seams for jump history, recent files, message logs, and help navigation; the remaining risk was that the documented broad override, `cap.history-clear`, was not a complete advertised capability in the standard option/feature registry.

## Failure mode

The default behavior should be conservative: lower-authority scripts can clear rows they created, but cannot erase trusted/user history or another script's evidence.  That is now true for jumplist rows, recent-file MRU rows, message-log rows, and docs-help history rows; failed callback rollback restores prior message evidence while preserving new diagnostics.

There is still a legitimate automation case for clearing broader editor history in a controlled environment.  Without a real capability entry, that override is easy to document inconsistently or test only accidentally.  Worse, future code might treat it as a normal option rather than a host-adjacent unsafe capability.

## Change

Rev796 adds the explicit capability surface:

- option: `cap.history-clear`
- feature: `ed.history-clear`

The option is registered with the rest of the unsafe host-adjacent capabilities and appears in `host.capabilities` / `host.feature?` only after trusted code enables it.  Because it is still a canonical `cap.*` option, the existing script option policy blocks scripts from granting it to themselves.

When enabled by trusted user/config code, script-origin destructive history clear paths may clear protected rows for these registers:

- message log rows via `ed.pop-message` / `ed.clear-messages`;
- recent-file rows via `ed.recent-clear`, `ed.recent-clear-count`, and `recent clear`;
- jumplist rows via `ed.clear-jumps` and bounded clear/truncate/evict operations;
- help-history pruning for missing help targets.

Navigation through trusted jumplist rows remains protected by row authority; `cap.history-clear` is a destructive-clear capability, not a general delayed-navigation authority grant.

## Tests

Focused coverage is in:

- `tests/test_editor_state_clear_authority.py`
- `tests/test_editor_message_log_authority.py`
- `tests/test_editor_capabilities_registry.py`
- `tests/test_editor_jump_history_authority.py`
- `tests/test_editor_recent_register_authority.py`

The new/updated coverage verifies the capability registry advertisement and the trusted-code opt-in behavior while keeping default script clears denied.

## Remaining risk

This remains editor-level provenance inside one process, not an OS sandbox.  The next high-leverage audit target is persistence restore: recent/history data loaded from disk should not re-enter with misleading provenance or bypass the runtime sidecars.
