# Rev657 / rev716 — macro replay atomicity trust

Macro replay now treats playback as a tiny transaction over the open editor buffers it can mutate. Before this change, `play_macro()` ignored failed step return values, so a macro whose first step edited text and whose later step failed could leave the earlier edit half-applied while still returning success. That is exactly the kind of automation failure that makes a scriptable editor feel untrustworthy.

The fix stays deliberately editor-local and inspectable:

- `Editor._macro_replay_snapshot()` captures open buffers, active buffer, buffer MRU, cursors, selections, cursor ids, local options, jump/selection stacks, dirty metadata, and the replay input scratch before playback begins.
- `Editor._restore_macro_replay_snapshot()` restores that snapshot if any replayed action or command fails or raises.
- `play_macro()` now checks every replayed step result, reports `macro: aborted at step N: ...`, returns `False`, and keeps the existing success message only for fully successful playback.
- replay still runs with `_macro_playing` true, so replay-triggered commands/actions remain outside live macro recording.

This intentionally does not reuse undo internals or leak rollback semantics into the Micromax VM. The product promise is narrower and clearer: recorded editor automation should either finish or leave the user’s buffer/cursor/selection state where it started.

Pinned tests cover failed command replay, failed action replay, rollback of text/cursor/selection state, and the existing successful playback message.
