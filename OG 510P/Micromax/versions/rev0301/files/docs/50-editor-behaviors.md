# Editor behaviors we adore (target UX)

This is the “north star” list. It’s intentionally opinionated.

Each item should eventually map to:
- one or more editor primitives
- one or more micromax words
- tests (behavioral + property-style)

## Editing fundamentals

1) **Always-available undo/redo**
- unlimited, fast
- doesn’t lose history on save
- (later) supports undo across multiple cursors
*(v15: `ed.with-undo` hostcall groups scripted edits into a single undo step; undo is currently linear.)*

2) **Predictable clipboard/yank behavior**
- separate kill-ring vs system clipboard is optional
- paste is always what you expect
*(v15: internal clipboard supports multi-item and linewise kinds; hostcalls expose it; system clipboard integration later.)*
*(v9: internal clipboard + Copy/Cut/Paste/CutLine/DuplicateLine implemented; system clipboard integration later.)*

3) **Incremental search that never lies**
- highlights matches as you type
- can jump next/prev without leaving search mode
- search can be literal or regex

4) **Replace that is safe**
- preview count and/or diff of replacements
- confirm-each as a mode

*(v9: `replace` / `replaceall` commands implemented; still non-interactive and no preview yet.)*

*(v86: added `qreplace` / `queryreplace` — an interactive confirm-each loop (`y`/`Enter` replace, `n` skip, `a` all, `l` last, `q`/`Esc` quit). Still no diff/count preview yet.)*

*(v62: Tier-0 editing/navigation basics + scripting enablers landed: forward delete (`Delete`), word jumps/select (Ctrl-Left/Right + Shift), page/document jumps (PageUp/Down, Ctrl-Home/End), `quit` warns on unsaved buffers, string helpers (`s+`, `s-split`, ...), lifecycle hooks (`ed.on-open`/`ed.on-save`/`ed.on-change`), and filetype detection (`ed.filetype`). Rev185 adds shared `pageoverlap` paging context so PageUp/PageDown can keep a few rows from the previous view visible in both ordinary and softwrapped views, rev186 adds shared save-time `rmtrailingws` cleanup so manual saves can strip trailing spaces/tabs without hiding the change from undo or future frontends, rev187 adds optional shared `eofnewline` normalization so non-empty saves can end with one final `\n` through that same honest save path, and rev188 adds optional shared `mkparents` so those same manual saves can create missing parent directories already implied by the target path.)*

*(v63: made the core tactile: unbound printable keys insert text (prompt-aware), prompt editing overrides via a reserved `prompt` keymode, a shared viewport model, `s-format`/`format`, and a minimal curses TUI.)*

5) **Selections behave consistently**
- selection expansion/shrink
- rectangular selection (optional)

*(v9: selection anchor + Shift-arrow style selection movement implemented.)*
*(v15: added a small selection recovery stack (`ed.push-selections`/`ed.pop-selections`) for "oops I cleared my cursors" moments.)*

## Navigation

6) **Jump stack**
- “go to definition”, “go back”, “go forward”

*(v18: implemented a per-buffer jumplist with `PushJump` / `JumpBack` / `JumpForward` and hostcalls; see `docs/63-editor-jumplist.md`.)*

7) **Fast file switching**
- fuzzy open
- recent files list

*(v74: added a headless recent-files MRU, `recent` / `recentpick`, and `ed.recent` hostcalls; persistence + project-aware recents later.)*

8) **Go to line / symbol**
- quick prompts with live feedback

## Ergonomics

9) **Command palette**
- every action is a command
- searchable, discoverable

*(v25: command-bar prompt completion modeled headlessly; see `docs/64-editor-prompt-completion.md`.)*

*(v41: built-in command-bar completion now falls back to tiny deterministic fuzzy matching for command-ish tokens when exact-prefix completion finds nothing; filesystem path completion remains explicit/prefix-based.)*

*(v42: command-bar completion also covers a few stable argument surfaces — built-in bool/enum option values, keymode names, and inspection topics like `showcmd` / `showhook` — while keeping the same headless suggestion-session model.)*

*(v47: editor `help` now falls back to visible Micromax words when no editor command/action topic matches, and `showword` exposes the same live word metadata explicitly.)*

10) **Keybinding layers/modes without pain**
- global bindings + mode bindings + transient bindings
- transparent introspection: “what does this key do right now?”

*(v30: bindings now carry best-effort provenance; `showkey` can report where a micromax-defined binding came from, and `ed.bindings` returns a machine-readable binding table.)*

*(v34: commands and bindings can now be tagged with a registration group for reload-safe cleanup; `showcmd` / `showkey` surface group metadata and plugin unload removes grouped registrations.)*

*(v35: keybindings can now live in named keymodes with global fallback.)*

*(v36: keymodes can also be **one-shot**, enabling small transient/prefix-style layers; `dispatch_key()` / `ed.press-key` centralize lookup so future UIs do not bypass those semantics.)*

*(v37: keymap discovery now has a headless surface; `showbindings` / `whichkey` and `ed.available-bindings` answer “what can I press right now?” without scraping UI.)*

*(v38: bindings can now carry human descriptions/docstrings, `whichkey` prefers those labels, and description-rich rows are available through `ed.binding-info-for` / `ed.available-binding-info` / `ed.resolve-key-info`.)*

*(v35: mode-aware keybindings now exist with global fallback; `showkey` resolves through the active keymode stack, `showkeymodes` exposes state, and `ed.status` now reports `keymode`.)*

11) **Macros feel native**
- record / replay / name macros
- macros are just quotations

12) **Multiple cursors (but sane)**
- add next match
- edit all cursors
- a clean escape hatch back to one cursor

## Extensibility (the big one)

13) **Everything is scriptable**
- editor actions are words
- keymaps bind to quotations
- config is micromax

14) **Plugins are isolated by default**
- each plugin has its own wordlist
- plugin loading doesn’t pollute global namespace
- plugins declare required host capabilities
- hooks/commands/bindings are inspectable enough to debug live systems

15) **Errors are friendly**
- show file/line + trace
- “disable plugin” is a first-class action

*(v31: `showhook NAME` + `hook-rows` make event wiring inspectable without UI-specific tooling.)*

*(v33: hook handlers can be grouped for reload-friendly cleanup; `showhook NAME` surfaces group + provenance.)*

## UI/terminal

16) **Terminal UI is calm**
- minimal chrome
- status line that is informative but not noisy

*(v32: the headless core exposes a shared `ed.status` / `showstatus` model so future UIs render the same semantics instead of inventing their own.)*

17) **Mouse is optional**
- everything works without it
- mouse support is additive


*(v39: prefix maps now have a tiny first-class helper; `prefixmode` and `ed.bind-prefix` enter one-shot keymodes and immediately surface reachable bindings via `whichkey`.)*

*(v40: prefix helpers now have a mode-local sibling; `bindmodeprefix` / `ed.bind-mode-prefix` let one active mode enter another temporary key layer without inventing a second binding class.)*
