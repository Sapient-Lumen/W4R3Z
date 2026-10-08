# Exact recent-directory sample truth

Rev504 closes one small trust/flow seam left behind by rev502/rev503.

Micromax already had the important nearby pieces:

- `recentdirpick` rows now reuse exact recent-file metadata/truth, so one visible
  row can already say `name #N [flags] @ line:col` plus tiny disk/action cues
- project-grouped `recentpick` rows keep the same menu-side MRU/state suffix
  after the project-label rewrite
- exact `showrecent PATH` / `ed.recent-detail-row` inspection already kept the
  same `existing file` / `new file` plus `current buffer` / `switch buffer` /
  `empty buffer @ 1:0` truth dialect as adjacent recent-file rows

But one adjacent exact-inspection seam still lingered in the same reopen loop:
`showrecentdir DIR` / `ed.recent-dir-detail-row` still flattened back to counts
plus one thin `sample_path`, which meant the explicit directory-bucket
inspector was now less honest than the visible `recentdirpick` row beside it.

Rev504 keeps the fix deliberately small:

- `ed.recent-dir-detail-row` now appends the sample row's visible `menu` / `info`
  after the existing stable prefix
- plain `showrecentdir DIR` formats that richer sample truth for humans
- exact `showrecentdir` completion rows now reuse the same richer sample row too
- the older stable prefix stays intact:
  `[query directory count active_count open_count dirty_count readonly_count sample_path sample_detail ...]`

That keeps the exact recent-directory inspector aligned with the visible picker
row it is meant to explain.

Focused coverage:

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

Files touched:

- `src/micromax_editor/editor.py`
- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `docs/31-host-api.md`
- `docs/55-editor-command-bar.md`
- `docs/64-editor-prompt-completion.md`
- `docs/66-editor-micromax-commands.md`
- `README.md`
- `TODO.md`
- `docs/01-llm-start-here.md`
- `docs/02-repo-map.md`
- `docs/43-worklist.md`
- `tools/mxcontext.py`
