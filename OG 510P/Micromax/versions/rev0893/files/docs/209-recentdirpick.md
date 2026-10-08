# Rev502: recentpick / recentdirpick rows keep exact recent-file truth

Rev267 gave Micromax a first-class directory-grouped recent picker, and later
revisions taught adjacent recent-file surfaces to tell the truth about saved vs
missing paths plus live-buffer action. But one small drift lingered: the
dedicated `recentpick` / `recentdirpick` prompts were still built from the old
thin `recent_prompt_rows()` shape, so the most direct MRU picker could still be
less honest than both `showrecent PATH` and palette `Recent Files`.

Rev502 keeps the follow-up deliberately small:

- `recent_prompt_rows()` now reuses exact recent-file row state/truth instead of
  collapsing back to basename + parent
- `recentpick` project-row rewriting still shows `project-name` + project-
  relative path, and after rev503 it also preserves the rich MRU/state suffix
  on the menu itself (`#N`, flags, `@ line:col`) instead of collapsing back to
  bare project names
- `recentdirpick` keeps literal parent-directory grouping while visible row text
  now also carries MRU index, flags, and the same disk/action truth

That keeps the dedicated recent-file prompts aligned with the exact
side-effect-free inspector and the adjacent palette rows, which matters because
these prompts are the boring daily reopen/switch loop future humans and LLMs
will reach for first.

Focused coverage:

- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_statusline.py`
- `tests/test_tui_prompt_display_lines_sticky_header.py`
- `tests/test_prompt_grouping_sections.py`

Files touched:

- `src/micromax_editor/editor.py`
- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_statusline.py`
- `docs/55-editor-command-bar.md`
- `docs/64-editor-prompt-completion.md`
- `docs/66-editor-micromax-commands.md`
- `docs/209-recentdirpick.md`
- `docs/43-worklist.md`
- `README.md`
- `TODO.md`
- `tools/mxcontext.py`

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
