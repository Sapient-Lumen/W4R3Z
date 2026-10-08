# 766 — Recent-file read authority boundary

Rev808 continues the protected-register audit on the recent-file MRU.  Earlier
revisions protected destructive recent-file mutation, but read surfaces still
returned trusted/user path history to lower-authority scripts.

## Failure mode

The recent-file register carries host paths and editor recovery/navigation
history.  A script that could not clear trusted recent rows could still inspect
or infer them through read-only surfaces such as:

- `ed.recent`;
- `ed.recent-inventory-rows`;
- `ed.recent-detail-row` / slot detail rows;
- recent pickers and section summaries;
- command-palette Recent Files rows;
- numbered `recent N` / `recent #N` open commands;
- path-completion candidates sourced from the recent-file MRU.

That was a privacy and delayed-navigation side channel.  It also weakened the
meaning of the existing recent-file mutation sidecar: protected rows were not
destructible, but they were still visible.

## Change

New policy seam:

`src/micromax_editor/recent_policy.py`

The policy matches the surrounding protected-register model:

- trusted/interactive callers keep normal recent-file visibility;
- script-origin callers can read same-origin recent rows;
- trusted/user, persisted, or other-origin rows are hidden from scripts by
  default;
- `cap.recent-read` / `ed.recent-read` is the explicit unsafe override for
  automation that intentionally inspects protected path history.

The filtering is now applied through `Editor.visible_recent_files()` and the
same authority check backs inventory rows, detail rows, slot addressing,
section/picker rows, command-palette Recent Files rows, numbered
`recent N` reopening, and known-path completion candidates.

`cap.history-clear` remains destructive-history authority only.  It does not
grant read access to protected recent-file paths.

## Validation

Focused validation covered:

- scripts cannot read trusted recent paths through `ed.recent`, inventory,
  detail rows, picker rows, or command-palette file rows;
- `cap.history-clear` does not grant recent read;
- `cap.recent-read` explicitly reveals protected rows;
- same-origin script recent rows remain readable;
- independent script-origin rows stay hidden;
- script-visible slot numbers are visible slots, not raw MRU slots;
- `recent 1` reopens visible slot 1 rather than hidden raw MRU index 0;
- known-path completion no longer leaks hidden recent basenames.

## Remaining risk

This is editor-runtime provenance, not OS-level secrecy.  Trusted interactive
code can still inspect the full MRU, and intentionally enabling
`cap.recent-read` exposes protected recent-file paths to scripts.  Future MRU
persistence/import/export changes should preserve persisted-row provenance and
avoid treating imported path history as fresh trusted user state.
