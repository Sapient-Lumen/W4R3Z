# Rev805 command-palette recent authority

The command palette MRU is tiny, but it is still delayed user intent: it records which command/action a user selected recently and it affects ranking the next time the palette is opened. Before this revision, `_palette_recent` had no provenance sidecar. Script-origin code could read trusted palette-recency rows through `ed.command-palette-rows` / section rows and, by recording its own palette selections, could evict or reorder trusted rows in the bounded MRU.

Rev805 adds `_palette_recent_authority` beside `_palette_recent` and routes palette MRU reads/ranking/recording through runtime-authority checks. Trusted interactive code still sees the normal palette. Script-origin code sees same-origin palette recency only; trusted/user rows and independent script/plugin rows do not appear in the `Recent` bucket and do not boost fuzzy ranking. Incidental script palette recording skips rather than evicting or reordering protected rows.

The plugin-callback rollback snapshot also now captures/restores palette MRU rows and their authority sidecar. A failed deferred plugin callback cannot leave behind palette-recency debris or launder row provenance.

This revision intentionally did **not** add a broad read/replay capability for palette recency. Command names and action names remain discoverable through the ordinary command/action inventories; the protected state here is the user's recency/order signal. `cap.history-clear` also does not grant palette-recency read access.

Focused coverage lives in `tests/test_editor_palette_recent_authority.py`. Default `mxdoctor` now includes that focused file while keeping the preflight bounded and risk-focused.

Remaining risk: the protected-register audit should continue looking for unguarded direct mutations of sidecar-backed state, especially in future UI/session helpers that add new MRU-like or delayed-execution registers.
