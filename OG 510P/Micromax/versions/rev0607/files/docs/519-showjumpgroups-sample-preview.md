# Rev577: showjumpgroups command preview keeps sample-row truth

## What changed

- plain `showjumpgroups` command-bar completion now reuses the shared `_prompt_section_summary_command_row(...)` helper
- the no-arg row now previews grouped jumplist state as `N section(s), M jumps · Current: 1 | e.g. #2 — a @ 2:1 — two`
- empty jumplists still preview as `0 section(s), 0 jumps`
- focused prompt-completion tests pin the richer preview and neutral wording

## Why it matters

Micromax already knew more than the old no-arg `showjumpgroups` preview admitted.
After Enter, `showjumpgroups [QUERY]` already exposed stable
`[[label count sample_name sample_detail] ...]` rows. During query-time
completion, `showjumpgroups QUERY` already reused that same grouped metadata.
But the exact `showjumpgroups` entry point itself still flattened that visible
section back to counts-only `Current 1 · Back 1 · Forward 1`.

That was a small trust/flow mismatch:

- the command bar already knew one representative visible jump row
- neighboring grouped inspectors already used the calmer neutral `LABEL: N | e.g. ...` dialect
- the jumplist preview was slightly less informative and slightly more special-case than the surfaces around it

Reusing the shared grouped-summary helper fixes that seam without widening the
host boundary or inventing one more preview formatter.

## Examples

- before: `3 section(s), 3 jump(s) · Current 1 · Back 1 · Forward 1`
- after: `3 section(s), 3 jumps · Current: 1 | e.g. #2 — a @ 2:1 — two`
- empty: `0 section(s), 0 jumps`

## Files touched

- `src/micromax_editor/editor.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `README.md`
- `TODO.md`
- `docs/01-llm-start-here.md`
- `docs/43-worklist.md`
- `docs/55-editor-command-bar.md`
- `docs/63-editor-jumplist.md`
- `docs/64-editor-prompt-completion.md`
- `docs/66-editor-micromax-commands.md`
- `tools/mxcontext.py`
