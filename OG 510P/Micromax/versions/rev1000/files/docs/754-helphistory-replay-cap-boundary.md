# Rev797 help-history replay capability boundary

Rev797 tightens the final edge of the destructive-register authority lane.  The worktree already contained the rev793 through rev796 register sidecars for jumplists, recent files, message logs, and help history.  The risky remaining detail was semantic: the broad `cap.history-clear` override must stay a destructive-clear/prune capability, not become a general delayed-navigation authority grant.

## Failure mode

`helpback` and `helpforward` are not mere clears.  They consume a history row, switch the visible help buffer, and restore a saved cursor target.  Treating replay as just another history clear would let a script with history-cleanup authority navigate through trusted/user docs-help state.  That is the same class of delayed-authority problem that earlier revisions fixed for jumplist navigation and key/prompt callbacks.

## Change

Help-history rows now keep the row-authority sidecar behavior, but the capability bypass is narrower:

- `cap.history-clear` may allow script-origin clearing/pruning of protected message/recent/jump/help-history rows where the operation is destructive cleanup;
- `helpback` / `helpforward` replay through trusted help-history rows still requires ownership of those rows;
- same-origin script help-history replay remains allowed;
- trusted replay denial is preflighted before opening or switching help buffers, so a refused script cannot partially navigate first and fail later.

This preserves the documented rev796 distinction: `ed.history-clear` is an unsafe cleanup capability, not a navigation or delayed-authority capability.

## Tests

`tests/test_editor_state_clear_authority.py` now covers:

- script denial when replaying trusted help history;
- same-origin script helpback success;
- script denial when pruning trusted help history by default;
- trusted `cap.history-clear` allowing prune cleanup;
- trusted `cap.history-clear` **not** allowing helpback replay through trusted rows.

Existing help-history/navigation suites continue to cover ordinary user behavior.

## Remaining risk

The next adjacent audit target is persisted-history restore provenance: history loaded from disk should not re-enter as misleadingly trusted or script-owned rows.  That is a persistence-boundary issue rather than another runtime-list mutation fix.
