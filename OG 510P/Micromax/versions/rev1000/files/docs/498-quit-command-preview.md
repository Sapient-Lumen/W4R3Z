# Rev556: quit/quit! command rows preview live exit-guard truth

## Why

Micromax already treated editor exit carefully: `quit` warned on unsaved buffers, gave autosave one best-effort pass, and only exited on a second attempt unless the user forced it with `quit -f` or `quit!`. But the command bar still lagged behind the newer trust-first previews for saves, jumps, recents, grouped summaries, close-family commands, and other no-arg editor actions. Right before an exit command ran, plain `quit` and `quit!` still fell back to generic command metadata even though the editor already knew how many buffers existed, how many were still dirty, and whether the dirty-quit guard was already armed.

That left one tiny but high-frequency trust seam harder than it needed to be: humans and future LLMs had to remember hidden dirty state or press Enter once just to learn whether Micromax would stop, quit now, or force quit.

## What changed

- added shared `_prompt_quit_command_preview(...)` and `_prompt_quit_command_row(...)` helpers in `src/micromax_editor/editor.py`
- exact command completion for plain `quit` and `quit!` now replaces generic provenance info with live exit-guard truth
- previews stay deliberately small:
  - `quit` shows the current buffer count plus dirty-count guard truth and whether the guard is already armed
  - `quit!` shows the same live buffer/dirty count but makes the force semantics explicit
- focused tests pin dirty, armed, and force-quit command-row previews in `tests/test_editor_prompt_completion_hostcalls.py`

## Result

Micromax now keeps one more high-value trust seam honest before Enter: if the editor already knows whether a no-arg quit command will warn, quit now, or force quit, the command bar says so directly instead of hiding behind generic command metadata.
