Rev401 note: docs fragment/footnote jump misses now keep the jump surface visible too — failed same-page `#fragment` or `[^footnote]` navigation reports `helpjump: no section or footnote: #target` instead of falling back to a generic `help:` line, so docs-link jumps stay typed on both success and failure; `docs/343-helpjump-fragment-miss-feedback.md` records why that tiny trust/flow follow-up matters.

Rev400 note: explicit `help docs TOPIC` opens now keep the command family visible on success too — successful direct docs lookup reports `help docs: topic @ line:col` instead of falling back to the broader `help:` success prefix, so one tiny docs-discovery path now names itself on both success and failure; `docs/342-helpdocs-open-feedback.md` records why that trust/flow follow-up matters.

Rev398 note: `helpfollow` now names itself on its two common miss paths too — `helpfollow: not in a docs buffer` and `helpfollow: no link under cursor` — so docs navigation no longer falls back to generic `help:` wording before a target is even resolved; `docs/340-helpfollow-miss-feedback.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev398): this is a small trust/flow follow-up to rev335/rev389/rev397's docs-navigation cleanup. The editor already had the right tiny docs-follow loop: `helpfollow` could jump to internal docs, hand external URLs off to the same capability-gated open-url boundary as `urlopen`, and after rev397 its successful/capability-gated link actions already spoke in the newer typed dialect. But one wording seam still lingered before any target was resolved: the two most common miss paths still fell back to generic `help: not in a docs buffer` / `help: no link under cursor` lines, which were accurate but weaker than nearby `helplinkcopy`, `helpjump`, `help docs`, and typed URL feedback. Rev398 keeps the implementation deliberately small while tightening that seam exactly where users and future LLMs inspect it: `helpfollow` now names itself on both pre-target miss paths, focused tests pin the exact wording, `docs/98-help-browser.md` / `docs/50-editor-behaviors.md` record the new dialect, and `docs/340-helpfollow-miss-feedback.md` records the intent. The goal is simple: follow-link failures should identify the action that failed before any navigation happens.

Rev397 note: docs-help link actions now report typed, self-identifying feedback too — `helplinkcopy` says `helplinkcopy: target`, external `helpfollow` opens say `helpfollow: URL`, and confirmation-copy now reuses the same command-specific prefixes instead of drifting into older `help: copied link target`, `help: opened external link`, or generic `copied link` wording; `docs/339-help-link-action-feedback.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev397): this is a small trust/flow follow-up to rev88/rev89's safe external-link support, rev335/rev389's docs-browser polish, and rev395's typed URL-command cleanup. The editor already had the right tiny docs/help link loop: `helpfollow` could jump to internal docs or hand external URLs off to the same capability-gated open-url boundary as `urlopen`, `helplinkcopy` could copy markdown link targets directly from docs buffers, and confirmation mode already carried the source (`help`, `cursor`, or `command`) through the prompt model. But one wording seam still lingered at that exact boundary: docs-buffer link copy still fell back to `help: copied link target`, confirmed external opens still collapsed to `opened external link`, and confirmation-copy still used a generic multi-line `copied link` block. Rev397 keeps the implementation deliberately small while tightening that drift where people and future LLMs actually inspect it: docs-buffer copy now reports `helplinkcopy: ...`, confirmed external opens from docs now report `helpfollow: URL`, confirmation-copy reuses `helplinkcopy:` for help and `urlcopy:` elsewhere, focused tests pin down the docs/help and generic confirmation paths, `docs/98-help-browser.md` / `docs/101-open-url-under-cursor.md` record the new wording, and `docs/339-help-link-action-feedback.md` records the intent. The goal is simple: docs-browser link actions should speak as plainly as the URL commands and help navigation around them.

Rev396 note: option-edit commands now report typed, self-identifying feedback too — `set` says `set: name=value`, `setlocal` says `setlocal: name(local)=value`, `toggle` says `toggle: name=value`, and `togglelocal` says `togglelocal: name(local)=value`, so small configuration edits stay searchable and attributable in logs, tests, and future LLM traces; `docs/338-option-command-feedback.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev396): this is a small trust/flow follow-up to Micromax-editor's long run of typed command-surface cleanup and the existing headless-first options model. The editor already had the right tiny configuration loop: `set`, `setlocal`, `toggle`, `togglelocal`, and `show` all acted through the same shared option registry, capability flips like `cap.open-url` and `cap.fs-*` refreshed the active capability snapshot immediately, and option changes were already easy to test before any TUI commitments. But one tiny wording seam still lingered on the success side of that same loop: successful option edits fell back to bare `name=value` / `name(local)=value` lines, which were readable in the moment but weaker in logs, prompts, and future LLM traces because they hid which command actually made the change. Rev396 keeps the implementation deliberately small while tightening that drift: `set`, `setlocal`, `toggle`, and `togglelocal` now all report typed, self-identifying feedback, focused tests pin down both global and local edit paths, `docs/50-editor-behaviors.md` / `docs/55-editor-command-bar.md` record the new dialect, and `docs/338-option-command-feedback.md` records the intent. The goal is simple: tiny configuration edits should speak as plainly as the rest of the command bar.

Rev395 note: `urlopen` / `urlcopy` now report typed, command-specific feedback too — opening a URL now says `urlopen: URL`, copy says `urlcopy: URL`, and the under-cursor path no longer drifts into older `openurl: ...`, `opened url`, or `copied url` wording, so explicit URL commands and under-cursor URL actions read as one small self-identifying surface; `docs/337-url-command-feedback.md` records why that tiny trust/flow follow-up matters.

# Editor behaviors we adore (target UX)

This is the “north star” list. It’s intentionally opinionated.

Each item should eventually map to:
- one or more editor primitives
- one or more micromax words
- tests (behavioral + property-style)

The current prioritization lens for this north star is:

- **Taste**: make the TUI, prompts, pickers, and docs/help surfaces feel visually deliberate.
- **Trust**: make startup, save/open, replace, and plugin/error behavior feel boringly honest.
*(rev360: `plugin info NAME` now keeps dependency inventory count-aware too — it always says `requires: N`, so empty and non-empty dependency detail use one tiny inspectable shape. Rev366 applies the same tiny structural rule to plain `recent`, which now starts with `recent: N recent file(s)` before the existing MRU entry detail. Rev372 gives `prevbuf` the same plain-spoken empty-case honesty by making the no-target path say `prevbuf: no previous buffer` instead of a raw placeholder. Rev377 applies that same typed-miss rule to named `buffer NAME` / `close NAME`, which now identify the command family when a target buffer does not exist. Rev381 carries that same trust-first rule one layer outward into the headless REPL, which now says `repl: no such command: LINE` instead of a bare `unknown command`. Rev389 applies the same rule back inside docs navigation itself, so stale `helpback` targets and missing internal docs links now say `help docs: no such doc: TOPIC` instead of older `help: no doc for ...` prose.)*
- **Flow**: make navigation, editing loops, and recovery loops keep the user moving.

Not every feature here matters equally right now. The more detailed sequencing and rationale live in `docs/269-editor-goals-taste-trust-flow.md`.

## Editing fundamentals

1) **Always-available undo/redo**
- unlimited, fast
- doesn’t lose history on save
- (later) supports undo across multiple cursors
*(v15: `ed.with-undo` hostcall groups scripted edits into a single undo step; undo is currently linear.)*
*(rev342: the recovery loop is now explicit too — key-driven `Undo` / `Redo` plus command-bar `undo` / `redo` now report the edit description and touched target as `undo: DESC -> name @ line:col` / `redo: ...`, and empty-stack retries now say `nothing to undo` / `nothing to redo` instead of failing quietly.)*

2) **Predictable clipboard/yank behavior**
- separate kill-ring vs system clipboard is optional
- paste is always what you expect
*(v15: internal clipboard supports multi-item and linewise kinds; hostcalls expose it; system clipboard integration later.)*
*(v9: internal clipboard + Copy/Cut/Paste/CutLine/DuplicateLine implemented; system clipboard integration later.)*
*(rev343: the ordinary clipboard loop is now explicit too — `Copy` / `Cut` report selection counts and copied chars, successful `Paste` reports cursor count, inserted chars, and the landed target, and empty internal-clipboard `Paste` now says `paste: clipboard empty` instead of failing silently.)*
*(rev355: searchable `pluginpick` buckets are glanceable now too — visible section labels and previews carry tiny count-aware labels like `Errors (1)` / `Loaded (2)`, so filtered plugin inspection stops making users count rows by hand.)*

3) **Incremental search that never lies**
- highlights matches as you type
- can jump next/prev without leaving search mode
- search can be literal or regex

4) **Replace that is safe**
- preview count and/or diff of replacements
- confirm-each as a mode

*(v9: `replace` / `replaceall` commands implemented; rev329 adds explicit replaced-count / not-found feedback, rev330 makes ordinary `save` feedback equally explicit by reporting the target path plus any save-time normalization steps, rev331 makes explicit command-path `open` report the real landed `path @ line:col`, and rev334 extends that same orientation rule into picker-driven navigation such as `jumppick`, `helpoutlinepick`, and internal docs-link picks, but there is still no preflight preview or diff yet.)*

*(v86: added `qreplace` / `queryreplace` — an interactive confirm-each loop (`y`/`Enter` replace, `n` skip, `a` all, `l` last, `q`/`Esc` quit). It already exposes a small progress count during the loop, but there is still no preflight diff/count preview yet.)*

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

*(v18: implemented a per-buffer jumplist with `PushJump` / `JumpBack` / `JumpForward` and hostcalls; rev341 makes actual back/forward traversal explicit too, so `JumpBack` / `jumpback` and `JumpForward` / `jumpforward` now report the real landed target or say `no earlier jump` / `no later jump`; see `docs/63-editor-jumplist.md`.)*

7) **Fast file switching**
- fuzzy open
- recent files list

*(v74: added a headless recent-files MRU, `recent` / `recentpick`, and `ed.recent` hostcalls; persistence + project-aware recents later. Rev331 also makes explicit `open ...` say where it actually landed (`opened: path @ line:col`), rev332 extends that same honesty/orientation rule to ordinary buffer movement (`buffer`, `prevbuf`, `bufferpick`, `close`, `only`, `closeall`), rev333 applies it to jump-style cursor movement (`goto`, `jump`, `helpjump`, `markjump`), rev334 extends it into searchable picker-driven navigation, rev335 closes the same gap for ordinary docs browsing (`help ...`, `helppick`, `helpfollow`, `helpback`), rev336 carries the same rule into command-palette file picks (`recentfile` / `openpath` rows now report `opened: path @ line:col`), rev337 applies it to mark placement itself (`mark set: name -> buffer @ line:col`), rev340 carries the same rule into committed search movement (`find`, `findnext`, `findprev`) together with the existing tiny `i/n` summary, rev341 closes the same gap for jumplist back/forward traversal (`JumpBack` / `jumpback`, `JumpForward` / `jumpforward`), rev344 makes the plain `buffers` inventory stop flattening open state to raw names by showing the active marker, `dirty` / `readonly` flags, and current cursor target for each buffer, and rev345 gives the plain `recent` command the same honesty by showing open/active state, visible flags, and current cursor targets for still-open recent entries, and rev346 brings plain `marks` up to the same standard by showing active-buffer ownership plus a tiny `[here]` cue for the mark under the current primary cursor; rev365 adds one more tiny glanceability follow-up by making plain `buffers` / `marks` start with count-aware `N` prefixes too, rev379 makes missing `markjump NAME` targets fail plainly as `markjump: no such mark: NAME` instead of the older `unknown mark` wording, and rev387 makes successful `close` / `closeall` actions identify themselves too (`close: ...`, `closeall -> ...`) instead of falling back to the older `closed...` dialect, and rev391 keeps the unexpected bulk-close failure side in the same family by making raised `only` / `closeall` faults report `only: error: ...` / `closeall: error: ...`, and rev399 applies that same self-identifying rule back to docs back-navigation itself so successful returns say `helpback: ...` and empty history says `helpback: back stack empty`, and rev401 closes the tiny remaining fragment-jump miss seam in that same docs loop by making unresolved same-page `#fragment` / `[^footnote]` jumps say `helpjump: no section or footnote: #target` instead of falling back to generic `help:` prose, so navigation/help/file-open/mark/search/jumphistory/buffer/recent/mark-inventory/docs-back/docs-fragment-jump flows keep the responsible command visible on both success and failure instead of switching dialects at the worst moment.)*

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
*(v373: `showcmd NAME` / `showword NAME` now fail plainly as `showcmd: no such command: NAME` / `showword: no such word: NAME`, so inspection misses stop speaking in raw placeholder dialects.)*

*(rev380: ordinary typed command-bar misses now fail plainly as `command: no such command: NAME` instead of the older `Unknown command: NAME`, so the first command-entry failure now matches the newer command/help/navigation miss dialect too.)*
*(rev388: once a command exists, unexpected dispatcher faults now keep that command visible too as `command NAME: error: DETAILS` instead of a generic capitalized `Command error: ...`, so plugin/dev-command failures stay inspectable in the same message log.)*
*(rev392: Micromax-defined commands registered through `ed.cmd-add` now keep that same `command NAME: error: DETAILS` prefix on Micromax/runtime faults too, so the live-scripting path no longer falls back to a weaker bridge-specific dialect.)*
*(rev381: the tiny headless REPL in `python -m micromax_editor` now makes its own top-level misses equally explicit as `repl: no such command: LINE`, so the headless-first validation surface does not fall back to a weaker generic sentence when the REPL layer itself rejects input.)*

10) **Keybinding layers/modes without pain**
- global bindings + mode bindings + transient bindings
- transparent introspection: “what does this key do right now?”

*(v30: bindings now carry best-effort provenance; `showkey` can report where a micromax-defined binding came from, and `ed.bindings` returns a machine-readable binding table.)*

*(v34: commands and bindings can now be tagged with a registration group for reload-safe cleanup; `showcmd` / `showkey` surface group metadata and plugin unload removes grouped registrations.)*

*(v35: keybindings can now live in named keymodes with global fallback.)*

*(v36: keymodes can also be **one-shot**, enabling small transient/prefix-style layers; `dispatch_key()` / `ed.press-key` centralize lookup so future UIs do not bypass those semantics.)*

*(v37/v367: keymap discovery has a headless surface; `showbindings` / `whichkey` and `ed.available-bindings` answer “what can I press right now?” without scraping UI, and the plain command-bar discovery paths now keep empty/non-empty results count-aware too.)*

*(v38: bindings can now carry human descriptions/docstrings, `whichkey` prefers those labels, and description-rich rows are available through `ed.binding-info-for` / `ed.available-binding-info` / `ed.resolve-key-info`.)*

*(v35: mode-aware keybindings now exist with global fallback; `showkey` resolves through the active keymode stack, `showkeymodes` exposes state, and `ed.status` now reports `keymode`.)*

*(rev374: key-binding inspection/edit misses now fail plainly as `...: no such binding: ...` for `showkey`, `binddoc`, `bindmodedoc`, `unbind`, and `unbindmode`, so missing-keymap targets stop collapsing to raw `(unbound)` placeholders.)*

*(rev385: successful `unbind` / `unbindmode` edits now report `unbind: KEY` / `unbindmode: KEY@MODE`, so small keymap surgery stays typed and easy to scan in headless logs too.)*
*(rev386: successful `bind` / `bindmode` / `bindprefix` / `bindmodeprefix` edits now report `bind: KEY -> ACTIONSPEC`, `bindmode: KEY@MODE -> ACTIONSPEC`, `bindprefix: KEY -> MODE`, and `bindmodeprefix: KEY@OWNERMODE -> MODE`, so keymap creation logs stay just as self-identifying as keymap removal.)*
*(rev394: successful `binddoc` / `bindmodedoc` edits now report `binddoc: KEY -> DOC...` / `bindmodedoc: KEY@MODE -> DOC...`, so description edits speak in the same typed dialect as bind/unbind itself.)*

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
- plain `plugin list` inventory is legible enough to debug plugin health without entering `pluginpick` or `plugin info/errors` first, and it now starts with a tiny count-aware summary so broad plugin health is glanceable before you read the per-plugin entries
- successful `plugin reload NAME` confirms the resulting plugin state instead of only reporting that reload ran
- the live Micromax `plugin.reload` hostcall now reuses that same reload-feedback helper too, so script-driven reloads no longer fall back to an older generic error dialect
- failed `plugin reload NAME` now keeps that same honest dialect too: broken known plugins start with the same explicit plugin-state summary and list their current recorded load errors directly, while unknown names fail plainly as `plugin reload: no such plugin: NAME`
- `plugin info NAME` starts with the same explicit plugin-state summary used by `plugin list` / `plugin reload`, unknown plugin names fail plainly, healthy plugins say `errors: 0`, broken plugins list their current recorded error lines directly, dependency rows now distinguish loaded / available / error / missing states instead of flattening everything to `loaded` or `missing`, and the `requires: N` line can summarize the dependency-state shape up front so plugin detail stays glanceable before you read every row
- filtered `plugin errors NAME` starts with that same summary, makes `no such plugin` explicit, and keeps that same count-aware detail shape when a known plugin currently has no recorded errors (`errors: 0`)
- plain `plugin errors` groups current load failures by plugin, starts with a tiny plugin/error count summary, keeps `plugin errors: 0 plugin(s), 0 error(s)` in the empty case instead of falling back to a special `(none)` shape, and keeps per-plugin detail under the same summary dialect so broad broken-plugin inspection reads like inventory instead of a log dump
- `pluginpick` now routes broken plugins to filtered `plugin errors NAME`, so searchable selection from the `Errors` section opens failure detail directly instead of generic metadata
- `pluginpick` row labels and previews now reuse the same bracketed state/version/dependency summaries as `plugin list` / `plugin reload` / `plugin info` / `plugin errors`, so searchable plugin inspection no longer falls back to older free-form status labels

15) **Errors are friendly**
- show file/line + trace
- “disable plugin” is a first-class action

*(v31: `showhook NAME` + `hook-rows` make event wiring inspectable without UI-specific tooling.)*

*(v369: `showhook NAME` now keeps that hook inventory count-aware too, so empty and non-empty handler chains share one tiny inspectable dialect.)*
*(v378: `showhook NAME` also fails plainly on non-hook targets now, reporting `showhook: not a hook: NAME` instead of a placeholder-style line.)*

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

Recent small trust/flow work also keeps command-bar feedback plain, typed, count-aware, and landed-target-oriented wherever the editor already knows the exact state. The `help` command now follows that same rule on direct docs opens and misses too: explicit `help docs TOPIC` lookup reports `help docs: TOPIC @ line:col` on success and `help docs: no such doc: TOPIC` on miss, while general `help QUERY` misses still report `help: no such topic: QUERY` and keep any `Try: ...` preview under the same typed prefix.

- `macro play NAME` now fails as `macro play: no such macro: NAME`, so missing named playback targets stay in the same plain, typed dialect as the rest of the command/help/inspection loop.


Rev393 follow-up: editor lifecycle hook failures now keep the hook surface visible too, reporting `hook NAME: error: DETAILS` instead of the older `hook NAME error: ...` wording.
