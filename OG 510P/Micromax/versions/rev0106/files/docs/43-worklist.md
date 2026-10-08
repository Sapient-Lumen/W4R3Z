# Worklist (rev106)
This is the **living, prioritized worklist** for Micromax + the micro-esque editor core.

It is intentionally practical:
- describes *what users actually feel* (keybindings, editing loops)
- breaks work into pieces small enough to land with tests
- records **status** and **pointers** (files/tests) so future humans/LLMs can pick up the thread quickly

## Status legend

- ✅ **DONE** — implemented + covered by tests
- 🧪 **VERIFY** — exists, but needs an end-to-end test or audit
- 🧱 **TODO** — not implemented yet
- 💤 **DEFER** — postponed intentionally (needs UI layer or bigger design)
- 💡 **IDEA** — plausible, but not currently committed

## A gentle argument against “Tier 6 is late”

The list below is excellent, but there’s one strategic twist:

> **A minimal TUI loop should *not* wait until Tier 6.**

Even a 200-line curses wrapper (input → `ed.press-key` → render) is a multiplier:
- it will expose subtle movement/editing bugs immediately
- it makes it easier to judge what headless APIs are missing
- it prevents the “1000 perfect headless features, 0 usability” trap

So: we keep most rendering sophistication late, but we try to get a *tactile* loop early.

## Tier 0 — Editor must be functional

1. **Verify `save` writes to disk.** ✅ DONE (rev61): `Editor.save()` writes `Buffer.path` to disk and clears `dirty`. Tests: `tests/test_editor_tier0_basics.py::test_open_and_save_round_trip`.

2. **Verify `open` loads a file.** ✅ DONE (rev61): `Editor.open_file()` reads UTF-8 or starts empty if missing. Same test as above.

3. **`quit` warns on unsaved changes.** ✅ DONE (rev61): `quit` arms once when any buffer is dirty, then quits on second attempt; `quit -f` / `quit!` force. Code: `src/micromax_editor/command_dispatcher.py`. Tests: `tests/test_editor_tier0_basics.py::test_quit_warns_on_dirty_buffers_and_can_force`.

3b. **Close buffer (`close`, `close!`).** ✅ DONE (rev74): close current or named buffer with a dirty-buffer double-tap guard (mirrors `quit`). Code: `src/micromax_editor/editor.py::close_buffer`, `src/micromax_editor/command_dispatcher.py`. Tests: `tests/test_editor_buffer_lifecycle_recent.py`.

3c. **Bulk buffer close + previous buffer MRU.** ✅ DONE (rev75): `closeall`, `only`, and `prevbuf`, plus MRU-based active-buffer selection after close. Code: `src/micromax_editor/editor.py` (MRU), `src/micromax_editor/command_dispatcher.py`. Tests: `tests/test_editor_buffer_mru_and_closeall.py`.

4. **Forward delete (`Delete` key).** ✅ DONE (rev61): new action `Delete` + keybinding. Code: `src/micromax_editor/editor.py` and `plugins/core/init.mx`. Tests: `tests/test_editor_tier0_basics.py::test_delete_forward_deletes_chars_and_joins_lines`.

5. **Word-jump movement (`Ctrl-Left`, `Ctrl-Right`).** ✅ DONE (rev61): actions `WordLeft`/`WordRight` using `Buffer.word_boundary_left/right()`. Code: `src/micromax_editor/buffer.py`, `src/micromax_editor/editor.py`, bindings in `plugins/core/init.mx`. Tests: `tests/test_editor_tier0_basics.py::test_word_movement_and_selection`.

6. **Word-select (`Shift-Ctrl-Left/Right`).** ✅ DONE (rev61): actions `SelectWordLeft`/`SelectWordRight`. Same code/tests as above.

7. **`PageUp` / `PageDown`.** ✅ DONE (rev61): actions `PageUp`/`PageDown` use option `page.height` (default 30). Code: `src/micromax_editor/editor.py`. Tests: `tests/test_editor_tier0_basics.py::test_doc_top_bottom_and_page_moves`.

8. **`Ctrl-Home` / `Ctrl-End`.** ✅ DONE (rev61): actions `DocTop`/`DocBottom`. Same test as above.

9. **Go-to-line command (`goto` / `Ctrl-L`).** ✅ DONE: command `goto line[:col]` existed; rev61 adds default binding `Ctrl-l` → `command-edit:goto `.

9b. **Prompt typing/editing works.** ✅ DONE (rev63): unbound printable keys insert text; when a prompt is active, they edit the prompt instead of the buffer. Prompt mode bindings override arrows/backspace/delete. Tests: `tests/test_editor_viewport_and_typing.py`.

9d. **Picker prompt UX: selection, paging, copy, and section stability.** ✅ DONE (rev93): in picker-style prompts (buffer/doc/help pickers, palette, etc.), Up/Down moves the highlighted selection without mutating the typed query, PageUp/PageDown jumps selection by a small window (option: `prompt.page`), `Ctrl-y` copies the selected row (for links: copies the target), `Ctrl-Home`/`Ctrl-End` jumps to first/last selection, `Alt-Up`/`Alt-Down` jumps between section headers, and option `prompt.wrap` controls wrap vs clamp at ends. The minimal TUI repeats the active section header as a sticky header when paging through long mixed sections. Tests: `tests/test_editor_prompt_picker_navigation.py`, `tests/test_editor_prompt_picker_navigation_page.py`, `tests/test_editor_prompt_picker_navigation_home_end.py`, `tests/test_editor_prompt_picker_navigation_wrap.py`, `tests/test_editor_prompt_picker_navigation_sections.py`, `tests/test_tui_prompt_display_lines_sticky_header.py`.

9e. **Docs markdown: shortcut reference links.** ✅ DONE (rev94): help/docs pages can use shortcut reference links (`[id]` with a matching `[id]: target`), and the minimal TUI underlines inline/reference/shortcut/autolinks consistently. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_shortcut_reference_link`, `tests/test_tui_md_link_label_spans.py`.

9c. **Jumplist picker (`jumppick`).** ✅ DONE (rev64): searchable prompt over the current buffer's navigation history. Code: `src/micromax_editor/editor.py`, `src/micromax_editor/command_dispatcher.py`. Docs: `docs/63-editor-jumplist.md`. Tests: `tests/test_editor_jumppick.py`.

10. **Line wrapping awareness in Up/Down.** 💤 DEFER: needs a UI-provided viewport width + “visual line” model (or a future layout engine). This should be designed alongside the first TUI renderer.

## Tier 6 — TUI (the actual rendering layer)

47. **Pick a terminal library.** 🧱 TODO: Python `curses` is the fastest universal MVP; `prompt_toolkit` later if we want richer line editing.

48. **Minimal TUI loop.** ✅ DONE (rev63): `micromax-editor --tui` runs a tiny curses loop (input → `ed.dispatch_key` → render). Requirements:
- translate terminal keys → the same key strings used in `plugins/core/init.mx`
- render buffer lines + statusline + command bar
- support a fixed viewport height/width (no softwrap yet)

   - *(rev95)* Picker suggestion rows now highlight query-token substring matches

   - *(rev104)* The curses TUI enables bracketed paste mode (CSI ? 2004) and inserts bracketed pastes as a single chunk (plus a micro-esque `paste` option to aggregate non-bracketed paste bursts). (UI-only polish that makes long pickers feel much closer to fzf/micro).

49. **Color/style model.** 💤 DEFER until syntax highlighting exists; but define the *shape* early: per-line spans with style tags.

50. **Scrolling / viewport management.** ✅ DONE (rev63): headless viewport stored on Editor; exposed via `ed.viewport` / `ed.viewport!` and status model fields. Tests: `tests/test_editor_viewport_and_typing.py`.

## Tier 1 — Plugin-writing blocks (language + hostcalls)

11. **String primitives as hostcalls.** ✅ DONE (rev63): hostcalls installed by editor bridge + convenience words defined in `forth`.
   - Host impl: `src/micromax/host_strings.py`
   - Installation: `src/micromax_editor/micromax_bridge.py`
   - Words: `s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower`
   - Tests: `tests/test_string_hostcalls.py`

12. **String concatenation with `+`.** 💤 DEFER: prefer `s+` for clarity + Rust port discipline.

13. **String comparison ops.** ✅ DONE (rev63): typed `s=` and `s<` primitives.
   - Core primitives: `src/micromax/core.py`
   - Tests: `tests/test_type_predicates_and_conversions.py`

14. **Type-checking words.** ✅ DONE (rev63): `int?`, `str?`, `list?`, `map?`, `quote?`, `xt?`.
   - Core primitives: `src/micromax/core.py`
   - Tests: `tests/test_type_predicates_and_conversions.py`

15. **`to-str` / `to-int`.** ✅ DONE (rev63): `to-int` parses decimal; `to-str` provides a stable-ish representation for non-strings.
   - Core primitives: `src/micromax/core.py`
   - Tests: `tests/test_type_predicates_and_conversions.py`

16. **`cr` and `.` portable.** ✅ DONE: core defines `.` and `cr` as primitives (see `src/micromax/core.py`).

17. **`s-format` / interpolation.** ✅ DONE (rev63): hostcall `s-format` + word alias `format` (`( ... fmt n -- s )`). Tests: `tests/test_string_hostcalls.py`.

## Tier 2 — Micro parity (selected)

18. **Syntax highlighting model.** ✅ DONE (rev66): span model + hostcall surface.
   - Hostcall: `"ed.highlight" hostcall` returns per-line spans `[[start end tag] ...]`.
   - Tags: `"ed.highlight-tags" hostcall`.
   - Default micromax highlighter (line-local): `src/micromax_editor/highlight.py`.
   - Tests: `tests/test_editor_highlight_and_timers.py::test_ed_highlight_spans_for_micromax_lines`.


19. **Line numbers gutter.** 💤 DEFER until TUI exists.

20. **Tab width / tabs-to-spaces.** ✅ DONE (rev65): editor options `tabsize` + `tabstospaces` + visual-column-aware `InsertTab`.
   - Options: `src/micromax_editor/editor.py::_install_default_options`
   - Action: `src/micromax_editor/editor.py::a_insert_tab`
   - Tests: `tests/test_editor_autoindent_tabs.py::test_insert_tab_respects_tabstospaces_and_tabsize`

21. **Auto-indent on newline.** ✅ DONE (rev65): `InsertNewline` preserves current-line indentation without doubling when splitting inside the indent prefix.
   - Action: `src/micromax_editor/editor.py::a_insert_newline`
   - Tests: `tests/test_editor_autoindent_tabs.py::test_insert_newline_preserves_current_line_indentation`

22. **`replace` / `replaceall` integration.** ✅ DONE (rev85): core commands existed; rev85 adds default `Ctrl-r` → `command-edit:replace ` binding and makes Alt/Meta chords work in the TUI so the rest of the micro-esque keymap is actually reachable. Tests: `tests/test_editor_default_keybindings_core.py`.

22b. **Interactive query-replace (`qreplace`).** ✅ DONE (rev86): added micro/Emacs-style confirm-each loop (`y`/`Enter` replace, `n` skip, `a` all, `l` last, `q`/`Esc` quit) implemented as a capture keymode so global bindings can't fire accidentally. Command: `qreplace` / `queryreplace`. Tests: `tests/test_editor_query_replace.py`.

22c. **Replace respects ignorecase.** ✅ DONE (rev87): `replace` / `replaceall` and `qreplace` now follow the editor's `ignorecase` option (like `find`), so case-insensitive workflows are consistent. Tests: `tests/test_editor_core.py`, `tests/test_editor_query_replace.py`.

23. **Mouse support model.** 💤 DEFER until TUI.

24. **Soft-wrap vs horizontal scroll.** ✅ DONE (rev71): `softwrap` option + core `view_rows`/`cursor_view_pos` rendering model + visual-row motion/scrolling (`CursorUp`/`CursorDown`/`PageUp`/`PageDown`) with `top_subline` viewport offset.

25. **Status bar model + format strings.** ✅ DONE (rev72): status model includes `encoding`, `fileformat`, `percentage`, and summary strings; statusline is now configurable via micro-esque `statusformatl`/`statusformatr` templates.
   - Options: `statusline`, `statusformatl`, `statusformatr` (`src/micromax_editor/editor.py::_install_default_options`)
   - Template renderer: `src/micromax_editor/statusformat.py`
   - Docs: `docs/97-statusline.md`
   - Tests: `tests/test_statusformat_templating.py`, `tests/test_statusline_strings.py`

26. **Buffer management UX bindings.** ✅ DONE (rev85): core plugin binds `Ctrl-b` → `bufferpick` and `Ctrl-o` → `open` (prefilled). Tests: `tests/test_editor_default_keybindings_core.py`.

26b. **Recent files list + picker.** ✅ DONE (rev75): MRU list + picker, optional persistence (`recent.persist`/`recent.file`), grouped section rows (`ed.recent-section-rows` / `ed.recent-dir-section-rows`), and a `Recent Files` bucket inside `commandpick`. Tests: `tests/test_editor_buffer_lifecycle_recent.py`, `tests/test_editor_buffer_mru_and_closeall.py`.

27. **Splits.** 💤 DEFER.

## Tier 3 — Plugin ecosystem ergonomics

28. **`require`/`include` path convention.** ✅ DONE (rev64): relative-to-caller + `$MICROMAX_PATH` + host `vm.load_paths`. See `docs/88-require-and-paths.md`. Code: `src/micromax/vm.py::resolve_load_path`, `src/micromax/core.py::{include,require,reload,unrequire}`. Tests: `tests/test_vm_require_paths.py`.

29. **Error recovery in plugins.** ✅ DONE (rev64): plugin init failures do not abort loading; errors are recorded and best-effort cleanup removes leaked hooks/commands/bindings. Code: `src/micromax_editor/plugins.py`. Tests: `tests/test_plugin_load_errors.py`.

30. **`timer` / `after` hostcall.** ✅ DONE (rev66): deterministic, no threads.
   - Hostcalls: `"ed.after"`, `"ed.cancel-timer"`, `"ed.pump-timers"`.
   - Core queue: `src/micromax_editor/timers.py`.
   - Execution + stack isolation: `Editor.pump_timers()`.
   - Plugin unload cleanup: timers are canceled by plugin group.
   - Tests: `tests/test_editor_highlight_and_timers.py`.


31. **`plugin.json` metadata schema.** ✅ DONE (rev71): validated metadata + optional `entry` + `requires` dependency ordering, plus `plugin.list`/`plugin.reload`/`plugin.errors` hostcalls and basic UI surfacing of load errors. Docs: `docs/95-plugin-json.md`.

32. **Hook documentation.** ✅ DONE (rev63): doc now specifies per-handler stack isolation + editor hook contracts.

33. **Lifecycle hooks (`on-save`, `on-open`, `on-change`).** ✅ DONE (rev63): `ed.on-open`, `ed.on-save`, `ed.on-change`.
   - Emit points: `Editor.open_file`, `Editor.save`, and `Editor.run_action` (buffer version bump).
   - Tests: `tests/test_editor_lifecycle_hooks.py`

34. **Filetype detection.** ✅ DONE (rev63): extension + shebang; exposed via `ed.filetype` and status model field.
   - Code: `src/micromax_editor/filetypes.py`, `Editor.filetype()`
   - Tests: `tests/test_editor_filetypes.py`

## Tier 4 — VM/language maturity

35. **Stack effect checking (dev-mode).** ✅ DONE (rev67): starter kit.
   - Toggle: `stackcheck!` / `stackcheck@` (0 off, 1 warn, 2 error)
   - Tools: `infer-effect`, `check-effect`
   - Runtime: closed-effect words/quotes checked by observed stack delta
   - Define-time: closed-effect colon defs verified when inference is possible
   - Quote annotation: leading paren-comment inside `[...]` is preserved and used as an effect
   - Implementation: `src/micromax/vm.py` (EffectSig + inference + runtime checks), `src/micromax/core.py` (tool words)
   - Docs: `docs/91-stack-effect-checking.md`
   - Tests: `tests/test_stack_effect_checking.py`

36. **Richer `see` / decompiler.** ✅ DONE (rev68): `see` now includes disasm + const pool; added `disasm-rows` for UI tooling.
   - Code: `src/micromax/core.py`
   - Docs: `docs/92-decompiler-and-disasm.md`
   - Tests: `tests/test_disasm_rows.py`

37. **`recurse` / tail-call support.** 💡 IDEA (may be a compiler-tier concern).

38. **Float support.** 💡 IDEA.

39. **Regex support hostcalls.** ✅ DONE (rev68): `re.search`/`re.findall`/`re.sub`/`re.subn`/`re.escape` hostcalls + shared replacement-template conversion.
   - Code: `src/micromax/host_regex.py`, `src/micromax/regex_tools.py`
   - Editor alignment: `src/micromax_editor/command_dispatcher.py`
   - Docs: `docs/93-regex-hostcalls.md`
   - Tests: `tests/test_regex_hostcalls.py`

40. **`try`/`catch` ergonomics + cleanup.** ✅ DONE (rev72): stdlib `try?`, `try`, `recover`, plus `ensure`/`finally` cleanup combinators built on `catch`/`throw`.
   - Stdlib: `src/micromax/stdlib/core.mx`
   - Docs: `docs/96-try-catch.md`
   - Tests: `tests/test_try_combinator.py`, `tests/test_ensure_finally.py`

41. **Cooperative tasks / `yield`.** 💤 DEFER.

## Tier 5 — Rust/WASM transition

42. **Portability test suite.** 🧱 TODO.

43. **Minimal Rust VM spike.** 🧱 TODO.

44. **Binary bytecode format.** 💤 DEFER.

45. **Hostcall ABI for WASM.** 💤 DEFER.

46. **TiddlyWiki integration spike.** 💡 IDEA.

## Tier 7 — Nice-to-haves and polish

51. **`ed.config` / RC file loading.** ✅ DONE (rev64): editor loads `~/.config/micromax/init.mx` (override: `$MICROMAX_INIT`) at startup after plugins. Docs: `docs/87-editor-config.md`. Tests: `tests/test_editor_user_init.py`.

52. **Comment toggling.** 💤 DEFER (filetype-aware).

53. **Bracket matching / pair highlighting.** 💤 DEFER (needs renderer span model).

54. **Trailing whitespace visualization / cleanup.** 💤 DEFER.

55. **`ed.exec` hostcall (run shell command).** 💤 DEFER: capability-gated; useful but security-sensitive.

56. **Scrollbar model for the TUI.** 💤 DEFER.

57. **Mouse-drag selection.** 💤 DEFER.

58. **Multi-buffer tab bar or buffer list in statusline.** 💤 DEFER.

59. **Help system loaded from docs.** ✅ DONE (rev76): `help TOPIC` falls back to opening a matching `docs/*.md` page into a protected read-only buffer; includes a docs picker (`helppick`).

    - *(rev77)* Added docs navigation helpers: `helpfollow` (follow markdown link under cursor) and `helpback` (return to previous docs page).
    - *(rev84)* Added a combined page navigator picker: `helpnavpick` merges headings + links.

60. **Plugin manager.** 💤 DEFER: late-stage; design `plugin.json` schema first.

61. **Open URL under cursor.** ✅ DONE (rev89): added `urlopen` / `urlcopy` commands and default `Alt-o`/`Alt-y` bindings to open/copy URLs under cursor, capability-gated by `cap.open-url` and confirmed by default via `open-url.confirm`.
   - Code: `src/micromax_editor/editor.py` (`url_under_cursor`, `open_url_under_cursor`, `copy_url_under_cursor`)
   - Commands: `src/micromax_editor/command_dispatcher.py` (`urlopen`, `openurl`, `urlcopy`)
   - Keybinds: `plugins/core/init.mx`
   - Tests: `tests/test_editor_url_under_cursor.py`
