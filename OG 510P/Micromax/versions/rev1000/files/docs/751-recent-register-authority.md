# Rev794 recent-file MRU authority boundary

Rev794 continues the destructive-register audit after the jumplist authority work.  The target is the recent-file MRU behind `recent`, `recentpick`, command-palette recent rows, and the hostcalls `ed.recent-clear` / `ed.recent-clear-count`.

## Failure mode

The recent-file list is not a filesystem capability by itself, but it is still long-lived user/editor evidence: it records where the user has been, feeds the command palette, and can disclose or erase path history.  Before this revision, the clear path had only a blunt trusted-state guard, while incidental MRU updates could still reorder or evict trusted entries during lower-authority script open/save flows.

That left two bad shapes:

- a lower-authority script could not honestly own the MRU rows it created, so the guard could not distinguish same-script cleanup from trusted/user cleanup;
- a script opening or saving a new path while the MRU was full could evict a trusted/user row as an incidental side effect.

## Change

`Editor` now carries `recent_files_authority` beside `recent_files`.  Missing legacy rows normalize to trusted authority, matching the safer rule used for marks, selection recovery snapshots, and jumplist rows.

The new recent-file policy is intentionally asymmetric:

- explicit destructive clears (`recent clear`, `ed.recent-clear`, `ed.recent-clear-count`, and `clear_recent_files()`) preflight every row and raise when a lower-authority script would erase trusted or other-origin rows;
- same-origin scripts can clear recent rows they created;
- incidental `_push_recent_file(...)` updates from open/save skip rather than failing the primary operation when they would reorder or evict protected MRU rows;
- bounded-list eviction is preflighted against the original rows that would be dropped, so a denied update leaves the list and authority sidecar unchanged.

The bridge fallback for `ed.recent-clear*` no longer clears the list after a broad exception.  It delegates to `Editor.clear_recent_files()` so the authority check remains the single source of truth.

## Rollback coverage

Recent-file rows and their authority sidecar are now captured by the all-buffer transaction/macro replay snapshot and by plugin callback/runtime snapshots.  A failed grouped operation or failed deferred plugin callback can no longer leave a transient script MRU row behind or launder script-owned MRU rows into trusted rows.

The adjacent cursor-state transaction helper now also preserves selection-stack and jumplist authority sidecars, closing the same rollback-laundering gap for those recovery registers.

## Tests

New focused file:

- `tests/test_editor_recent_register_authority.py`

It covers trusted clear denial, hostcall clear denial without fallback bypass, same-origin clear success, independent-script denial, full-MRU eviction skip, transaction rollback, and plugin-callback snapshot rollback.

Existing jumplist coverage remains in:

- `tests/test_editor_jump_history_authority.py`

## Remaining risk

The destructive-register audit should continue through help navigation history and message-log destructive hostcalls.  Message logs currently have a blunt trusted-state clear guard; that is safer than the old unguarded clear, but it is not yet a per-message authority sidecar like the MRU/jump/selection registers.
