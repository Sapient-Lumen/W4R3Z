# Recent inventory feedback

Micromax's recent trust/flow work has been steadily tightening one small rule: ordinary inventory should not collapse meaningful editor state to lossy labels. Recent revisions already made `open ...`, help/navigation moves, search, macros, clipboard actions, `buffers`, and other everyday loops more explicit.

One plain inspection path still lagged behind: `recent`. The editor already had a useful MRU, grouped `recentpick` / `recentdirpick`, and explicit open feedback, but the plain `recent` command still flattened file history to numbered raw paths. That made it easy to miss which recent files were still open, which one was active, whether an open recent file was dirty or readonly, and where the live cursor currently sat.

Rev345 keeps the implementation deliberately small:

- unopened entries still read as plain `N:path`
- still-open entries now show the same tiny honesty cues the rest of the editor has been converging on
- active recent files get `*`
- non-active open recent files get `open`
- visible `dirty` / `readonly` flags appear when relevant
- open recent files also show the current cursor target as `@ line:col`

So the command now reads more like a true MRU inventory and less like a bare list dump, for example:

- `recent: 1:/tmp/c.txt; 2:*/tmp/b.txt [dirty, readonly] @ 1:1; 3:/tmp/a.txt [open] @ 1:0`

That is still tiny, but it matters. The user should not need to enter `recentpick` or reopen a file just to answer a small question like “which recent file is still open?” or “which one is the active dirty one?”.


Follow-up: rev366 keeps the same plain `recent` surface count-aware too, so the command now starts with `recent: N recent file(s)` in both the empty and non-empty cases instead of falling back to `recent: (none)` when the MRU is empty. See `docs/308-recent-counts.md`.
