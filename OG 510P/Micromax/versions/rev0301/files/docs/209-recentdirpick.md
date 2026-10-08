# Rev267: live directory-grouped recent picker

This revision closes a small but real drift in the recent-files surface:
Micromax already exposed `recent_section_rows_by_dir(query)` /
`ed.recent-dir-section-rows` for scripts and future UIs, but the live editor
still only had the project-root flavored `recentpick` prompt.

Rev267 adds a sibling command and prompt kind:

- `recentdirpick [QUERY]`

That prompt reuses the existing directory-grouped recent rows directly, so the
live picker now agrees with the existing headless grouped shape:

- empty-query browse windows flatten the same grouped directory sections
- sticky headers / `Alt-Up` / `Alt-Down` reuse those same directory labels
- `prompt_current_section`, preview text, and status surfaces now tell the same
  directory story the hostcall already exposed
- submission still opens the chosen file through the ordinary shared `open` path

The split is intentionally small and useful:

- `recentpick` stays optimized for project-root scanning, rewriting row detail to
  `project-name` + project-relative path
- `recentdirpick` stays optimized for literal parent-directory scanning, keeping
  row detail as `basename` + directory

That mirrors the way other editors treat pickers as first-class interaction
surfaces with distinct grouping strategies rather than one monolithic MRU list.
For Micromax, the important part is not adding a richer picker framework; it is
keeping the live prompt honest with the shared grouped data the repo already had.

Focused coverage:

- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_buffer_mru_and_closeall.py`

Files touched:

- `src/micromax_editor/editor.py`
- `src/micromax_editor/command_dispatcher.py`
- `docs/55-editor-command-bar.md`
- `docs/64-editor-prompt-completion.md`
- `docs/66-editor-micromax-commands.md`
- `docs/31-host-api.md`
- `docs/43-worklist.md`
- `docs/41-decisions-log.md`
- `README.md`
- `TODO.md`
- `tools/mxcontext.py`
