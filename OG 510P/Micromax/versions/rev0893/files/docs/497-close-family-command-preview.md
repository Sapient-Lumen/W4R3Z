# Rev555: close/closeall/only command rows preview live close truth

## Why

Micromax already treated buffer-destruction itself carefully: `close`, `closeall`, and `only` guarded dirty buffers with an explicit double-tap flow, and successful runs already reported landed or kept buffers plainly after Enter. But their own exact command rows still lagged behind nearby trust-first command previews for saves, jumps, recents, and grouped summaries. Right before a destructive no-arg command ran, the command bar still fell back to generic command metadata even though the editor already knew the active target, how many buffers would be closed, whether dirty guards would trip, and which buffer would remain active.

That made one tiny but high-frequency trust seam harder than it needed to be: humans and future LLMs had to remember hidden editor state or press Enter just to learn what `close`, `closeall`, or `only` would do right now.

## What changed

- added shared `_prompt_buffer_target_brief(...)`, `_close_successor_name(...)`, `_prompt_close_command_preview(...)`, and `_prompt_close_command_row(...)` helpers in `src/micromax_editor/editor.py`
- exact command completion for plain `close`, `closeall`, and `only` now replaces generic provenance info with live close-target/count/guard truth
- previews stay deliberately small:
  - `close` shows the current target buffer plus either the dirty confirm hint or the next landed buffer
  - `closeall` shows the total buffer count plus dirty-count confirm truth or the final `*scratch*` landing
  - `only` shows the kept buffer plus how many other buffers would close and whether dirty guards would stop first
- focused tests pin dirty and clean command-row previews in `tests/test_editor_prompt_completion_hostcalls.py`

## Result

Micromax now keeps one more destructive editing loop honest before Enter: if the editor already knows what a no-arg close-family command will target, keep, or refuse to close without confirmation, the command bar says so directly instead of hiding behind generic command metadata.
