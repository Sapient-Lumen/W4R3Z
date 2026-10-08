# Rev798 — persisted history provenance boundary

## Audit finding

The destructive-register authority lane had one remaining restore-path problem:
runtime rows could be protected while disk-loaded rows still re-entered as
ambient trusted/editor state.  Recent-file MRU and prompt-history persistence are
explicitly gated by `cap.persist`, but the JSON files are still mutable host
state.  A restored row should not become indistinguishable from a fresh user
interaction when lower-authority script code later tries to recall or clear it.

Prompt history was the sharper risk.  A command/search prompt row can be recalled
into a delayed prompt and later submitted.  Recent work already made prompt
submission preserve script origin, but the history row itself also needs
provenance so a script cannot inspect or reuse persisted command text by walking
history.

## Change

Rev798 adds a small persisted-runtime authority helper:

`Editor._persisted_runtime_authority(kind, path)`

Rows restored from persistence now get lower-authority provenance:

- `load_recent_files()` tags every restored recent-file row as
  `persist:recent:<path>` instead of trusted/editor state.
- `load_prompt_history()` tags every restored prompt-history row as
  `persist:prompt-history:<path>` instead of trusted/editor state.
- Trusted/interactive callers can still use the rows normally.
- Script-origin prompt history recall filters out rows the current script does
  not own, so persisted command/search rows are not script-readable by default.
- Script-origin recent clears still require row ownership or the explicit unsafe
  cleanup capability.

This keeps `cap.persist` as storage authority, not as a laundering mechanism that
turns mutable JSON rows into trusted runtime provenance.

## Rollback fix

Failed deferred plugin callbacks already rolled back dictionary and runtime
registration debris.  Rev798 extends that rollback snapshot to prompt history and
its authority sidecar, so a plugin callback that runs a command and then fails no
longer leaves stray command-history rows behind while the rest of its side
effects roll back.

## Regression coverage

New/extended tests cover:

- persisted prompt-history rows carry `persist:prompt-history` authority;
- lower-authority scripts cannot recall persisted prompt-history rows;
- trusted users can still recall persisted prompt history;
- persisted recent rows carry `persist:recent` authority and are not clearable by
  scripts by default;
- failed plugin command callbacks roll back prompt-history writes.

## Remaining risk

Prompt-history persistence still serializes strings only, not authority metadata;
that is deliberate.  Rows restored in a later session get persistence authority
rather than trying to preserve possibly stale script/plugin identities.  A future
signed profile or per-user trust store could distinguish editor-created stores
from imported stores, but this revision keeps the boundary conservative and
local.
