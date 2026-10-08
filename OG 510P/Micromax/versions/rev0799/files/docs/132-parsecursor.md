Rev496 note: parsecursor support now also keeps visible known-path file rows honest about missing-file opens: when a deleted recent path or unsaved open buffer survives as one visible completion candidate, the row now says `new file` and — when no stronger live-buffer answer exists — `empty buffer @ 1:0`.

# Open-target cursor parsing (`parsecursor`) (rev191, relanded in rev192)

Rev191/192 adds a tiny shared `parsecursor` option to the editor core.

## Option

- `parsecursor` (bool, default `false`)

When enabled, open targets like `file:line[:col]` are interpreted as:

- open `file`
- place the primary cursor at `line` / `col` immediately

Rules:

- line numbers are 1-based
- columns are 0-based (`file:42` means line 42, column 0)
- malformed suffixes stay literal paths
- if the literal path already exists, it wins over parsing (so existing colon-containing paths remain openable)
- explicit parsed targets override `savecursor` for that open

## Shared paths

The same policy now flows through:

- interactive `open` / direct `open_file(...)`
- capability-gated `ed.open`
- scripted `open ...` through `ed.command` / prompt submit
- path-style command-palette opens, including typed directory drill-down targets inside `commandpick`

That tradeoff is deliberate: the first pass mirrors micro's small `parsecursor`
idea without inventing a larger session/open-command subsystem.


Rev331 follow-up: explicit command-path `open ...` now also reports the post-open landed target as `opened: path @ line:col`, so parsecursor-driven opens stop being visually correct but verbally silent. The summary is taken from the real editor state after open, so it also covers savecursor-restored and already-open-buffer cases honestly.


Rev486 follow-up: parsecursor-shaped directory targets inside the command palette now stay behaviorally honest too. A typed query like `guide/:2` can still render as `directory | drill down`, and submitting that exact typed `Open` row now reopens the palette inside `guide/` instead of failing against the raw suffixed text.

Rev488 follow-up: parsecursor-shaped relative file targets now still count as path-like inside `commandpick` too. A query like `draft.md:3:7` now reuses `_parse_open_target(...)` before the palette decides whether to show the exact typed `Open` row, so relative file opens with cursor suffixes stop disappearing from the palette even though submit/open already understood them.

Rev489 follow-up: existing extensionless parsecursor targets now keep that same typed row too when Micromax already has enough evidence that the parsed target is real. Queries like `guide:2` and `intro:2` now stay path-like when the parsed target already maps to one open buffer, one exact recent file/directory row, or — under `cap.fs-list` — one existing file or directory on disk, so extensionless parsecursor targets stop vanishing from the palette right before Enter.

Rev490 follow-up: parsecursor-shaped partial file queries now keep visible completion rows aligned with submit/open too. A query like `guide/i:2` now reuses the parsed path when the palette lists filesystem candidates, so Micromax can surface `guide/intro.md:2` as one visible completion target instead of collapsing to one lonely typed `Open` row, and selecting that visible row still opens the completed file at the intended cursor.

Rev491 follow-up: parsecursor-shaped existing-file targets that are not already open now keep one tiny cursor-request cue in those palette rows too. Queries like `guide/intro.md:2`, `intro:2`, and visible completion rows like `guide/intro.md:2` now append `cursor 2:0` when Micromax can see one real existing file target but cannot clamp it exactly through one live buffer yet, while already-open buffer targets still keep the exact `goto line:col` cue.

Rev492 follow-up: parsecursor-shaped new-file targets now keep one tiny exact empty-buffer landing cue too. Queries like `draft.md:3:7` now append `empty buffer @ 1:0` in the exact typed `Open` row when Micromax already knows the file does not exist yet, so the palette stops going silent about the real landing for one brand-new empty buffer.

Rev493 follow-up: parsecursor-shaped partial directory queries now keep visible completion rows aligned with that same submit/drill-down path too. A query like `guide/s:2` now preserves the typed suffix on visible directory candidates, so Micromax can surface `guide/sub/:2` as one completion target instead of hiding that row right before Enter just because the visible candidate dropped `:2`.

Rev494 follow-up: partial extensionless current-directory queries now stay path-like when Micromax can already complete one real candidate from the parsed target's parent directory. Queries like `gu:2` and `intr:2` now let the palette surface `guide/:2` and `intro:2` as visible completion rows instead of disappearing before the path rows render at all.

Rev496 follow-up: those visible known-path file candidates now keep missing-file truth too. A deleted recent path like `old.md:3` or an unsaved open buffer surfaced as `scratch.md:2` now appends `new file`, and when no live open buffer already provides an exact `goto line:col` answer the row also uses the more honest `empty buffer @ 1:0` landing cue instead of pretending Enter will honor the requested cursor against an existing file.

Rev487 follow-up: parsecursor-shaped file targets that already map to an open buffer now keep that last action cue visible too. When a typed query like `guide/intro.md:1:0` would switch to or stay on one live buffer and move its cursor, the exact typed `Open` row now appends `goto 1:0` instead of making the row read like an ordinary static current/open file witness.
