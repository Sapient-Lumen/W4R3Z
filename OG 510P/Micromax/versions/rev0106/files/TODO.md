# TODO (rev106)
If you want the **current priorities**, start here.

The detailed, tiered list lives in: `docs/43-worklist.md`.



## Next up (high leverage)

1. **Recent UX polish**: keep iterating on picker rendering (colors, scroll windowing, and more section types).
2. **Docs browser polish**: deeper markdown affordances (link list sections, headings outline, and “open external” UX).
3. **Safety boundaries**: keep expanding capability-gated surfaces (jobs, filesystem, UI integration), keeping defaults safe.

## Recently completed

- **TUI picker styling + docs inline-code styling:** the curses TUI now preserves minimal row metadata for picker suggestion lines (via `PromptDisplayItem` + `_prompt_display_items`) so it can style rows by kind (actions/files/links/headings) without re-parsing rendered strings, while keeping `_prompt_display_lines` stable for tests. Help/docs buffers now also dim inline markdown code spans (`` `code` ``) for scanability. ✅ (rev106).

- **External clipboard import + script-gated system clipboard reads:** implemented `clipboard=external` *read* support via wl-paste/xclip/xsel/pbpaste/powershell and made `Paste` (Ctrl-v in core plugin) best-effort import from the system clipboard when `clipboard.external.import=true`. Added new script capability `cap.clipboard-read` advertised as `ed.clipboard-import`, plus hostcall `ed.clipboard-import` returning `( -- ok text err )` ✅ (rev105).

- **Bracketed paste + external clipboard export + paste-burst aggregation:** added bracketed paste mode support in the curses TUI (enable/disable CSI ? 2004 h/l) so pastes arrive as ESC[200~ ... ESC[201~ and are inserted as a single undoable chunk (no autoindent corruption). Also implemented `clipboard=external` export (best-effort piping to wl-copy/xclip/xsel/pbcopy/clip with override options), and added a micro-esque `paste` option that aggregates rapid character bursts into a single insert for terminals that don't support bracketed paste. Clipboard exports remain script-safe via `cap.clipboard-write` ✅ (rev104).

- **Terminal clipboard export (OSC 52) + script-safe clipboard exports:** added best-effort OSC 52 clipboard export in the curses TUI when `clipboard=terminal` (with `clipboard.osc52` + `clipboard.osc52.max` options), plus capability-gated script-originated exports via new `cap.clipboard-write` advertised as `ed.clipboard-export`. Clipboard changes now track a serial + script origin so UIs can reason about side effects ✅ (rev103).

- **Option helper words + persistence gate + prompt history persistence:** editor host now installs micromax-friendly option words `set`/`show`/`toggle` (plus stack synonyms `opt@`/`opt!`) so init/plugins can use micro-esque config lines like `set cap.shell true`. `ed.opt-set` now sets *global* options by default, capability options refresh `host.feature?` immediately, and a new `ed.opt-set-local` hostcall supports buffer-local overrides. Added a new safety boundary `cap.persist` + optional sandbox `cap.persist-root` for editor-owned persistence files, and implemented opt-in prompt history persistence (`history.persist`/`history.file`/`history.limit`) alongside the existing recent-file MRU persistence ✅ (rev102).

- **Script-context palette open safety + helpnav breadcrumbs + TUI scanability:** fixed a capability bypass where scripts could open files via the command palette openpath row (`ed.command-palette` + `ed.prompt-submit`) without `cap.fs-open`; palette opens now require `cap.fs-open` in script context and respect `cap.fs-root` for both openpath and recentfile rows. Help navigator link rows now include the nearest heading breadcrumb in their info for easier scanning/searching, and the minimal TUI dims the “detail” suffix after `—` in picker rows (while still highlighting query matches) ✅ (rev101).

- **Script-context filesystem gates + fuzzy picker highlights:** prevented scripts from bypassing `cap.fs-open`/`cap.fs-save` by running `open`/`save` through `ed.command` or `ed.prompt-submit` (script context now propagates through those hostcalls and the command dispatcher enforces caps + `cap.fs-root` in that context), and improved the TUI picker match highlighting to fall back to fzf-style subsequence character matches when no substring hit exists ✅ (rev100).

- **Capability-gated `ed.open`/`ed.save` + picker section counts + `cd` tilde fix:** made VM-exposed `ed.open`/`ed.save` capability-gated (`cap.fs-open` / `cap.fs-save`) so scripts don't gain ambient filesystem read/write authority by default (both also respect `cap.fs-root`), improved the minimal TUI picker list to show per-section counts and rough hidden-row counts in "more" markers, and fixed the `cd` command to actually expand `~` and report missing-path errors cleanly ✅ (rev99).

- **Filesystem sandbox root + VM callstack introspection:** added option `cap.fs-root` (empty=unrestricted) that constrains the capability-gated filesystem helpers (`ed.fs-read`/`ed.fs-list`/`ed.fs-stat`) and the command palette path-completion/drill-down flow; also added core VM debugging word `callstack` (alias `trace`) returning the current word call chain as a plain list for UIs/tooling ✅ (rev98).



- **Docs link picker sections by heading + new `ed.fs-stat` helper + mkrevzip tool:** `helplinkpick` (and `ed.helplink-section-rows`) can now optionally group links by the nearest markdown heading via `set help.linksections heading` (default remains Docs/Files/External), the host gains capability-gated `ed.fs-stat` (and `fs-stat`) for portable path metadata, and the repo ships `tools/mkrevzip.py` to create standard-named release zips from an offline checkout ✅ (rev97).


- **Capability-gated filesystem listing + command palette path completion:** added `ed.fs-list` behind `cap.fs-list` and, when enabled, the command palette (`commandpick`) now offers best-effort filesystem path completions (dirs and files) with Enter-to-drill-into-directories behavior ✅ (rev96).


- **Picker query match highlighting + archive-friendly Makefile:** picker suggestion lists now highlight query-token substring matches in the minimal TUI, and the `Makefile` now invokes scripts via `bash` so `make test` works even when executable bits are lost in a zip checkout ✅ (rev95).


- **Docs browser markdown (shortcut reference links):** help/docs parsing now recognizes shortcut reference links (`[id]` when a matching `[id]: target` definition exists), and the TUI underlines reference/shortcut/autolinks consistently ✅ (rev94).
- **Picker prompt UX (section jumps):** in picker-style prompts, `Alt-Up` / `Alt-Down` jumps between section headers (and `Alt-Up` also jumps to the start of the current section when used inside a section). Implemented as `PromptSuggestPrevSection` / `PromptSuggestNextSection` and surfaced in both built-in prompt bindings and the core plugin ✅ (rev93).

- **Picker prompt UX (sticky headers + clamp option + first/last):** picker-style prompts gained option `prompt.wrap` (wrap vs clamp), support `Ctrl-Home`/`Ctrl-End` to jump to first/last selection, and the minimal TUI repeats the active section header as a sticky header while paging through long mixed sections ✅ (rev92).
- **Picker prompt UX (page jumps):** in picker-style prompts, `PageUp`/`PageDown` now jumps selection by a small window (option: `prompt.page`, default 8) without mutating the typed query ✅ (rev91).

- **Picker prompt UX:** Up/Down now moves the highlighted selection in picker-style prompts (buffer/doc/help pickers, palette, etc.) without clobbering the typed query, and `Ctrl-y` copies the selected row (for links: copies the target) ✅ (rev90).

- **Open URL under cursor (safe-by-default):** added `urlopen`/`urlcopy` commands and default `Alt-o`/`Alt-y` bindings to open/copy `http(s)`/`mailto:` URLs under the cursor, reusing the capability gate (`cap.open-url`) and confirmation keymode (`openurl`) ✅ (rev89).

- **Docs browser safety + ergonomics:** added `helplinkcopy` (and docs-buffer `y`) to copy link targets under cursor, plus an external-link confirmation keymode (`openurl`) enabled by default when `cap.open-url` is on ✅ (rev88).

- **Replace ignorecase parity:** `replace` / `replaceall` and `qreplace` now follow the editor's `ignorecase` option (case-insensitive by default), and `qreplace` shows a small `match i/N` progress hint when it can count matches up front ✅ (rev87).
- **Interactive query-replace (`qreplace`).** Added micro/Emacs-style confirm-each replacement loop with a capture keymode (`y`/`Enter` replace, `n` skip, `a` all, `l` last, `q`/`Esc` quit) and a default `Alt-%` prefill binding ✅ (rev86).
- **Keymode capture semantics.** Added `ActiveKeyMode.capture` so modal flows can prevent accidental fallthrough to global bindings ✅ (rev86).
- **Shared Cursor↔offset helpers.** Introduced `micromax_editor.textpos` and used it in search + replace to avoid drift ✅ (rev86).

- **TUI Alt/Meta chords + Ctrl-Space:** curses UI now interprets ESC-prefixed Alt chords (so default `Alt-*` bindings work) and maps NUL to `Ctrl-Space` for command palette muscle memory ✅ (rev85).
- **Default buffer/replace/open/binding discoverability binds:** core plugin now binds `Ctrl-b` → `bufferpick`, `Ctrl-o` → `open` (prefilled), `Ctrl-r` → `replace` (prefilled), `Ctrl-Space` → command palette, and `Alt-g` → binding prompt ✅ (rev85).

- **Docs browser navigator picker:** `helpnavpick` merges headings + links into one “go to something on this page” picker; exposed via `ed.helpnav-section-rows` for scripts/UIs ✅ (rev84).
- **Docs browser markdown affordances:** `helpfollow`/`helplinkpick` now understand reference-style links (`[text][id]` + `[id]: target`) and autolinks (`<https://...>`) ✅ (rev83).
- **Docs browser polish:** link picker now groups Docs/Files/External (also surfaced via `ed.helplink-section-rows`), and external-link follow gives an explicit `cap.open-url` enable hint ✅ (rev82).
- **Picker UX polish:** TUI now uses minimal colors for section headers/links/"more" markers when the terminal supports it ✅ (rev82).
- **micro-inspired TUI debugging:** `rawkeys` toggles a raw-key event view so you can discover what your terminal sends for odd key combos ✅ (rev82).

- **Capability-gated filesystem read** ✅ (rev81): added `ed.fs-read` behind `cap.fs-read` with size limits + tests.
- **Docs browser quick jump** ✅ (rev81): `helpjump` jumps to headings (or opens the outline picker).
- **Picker section grouping** ✅ (rev81): buffer/plugin prompts are grouped (help/scratch/dirs; errors/loaded/available); TUI indents help outline items.

- **Docs browser keybindings** ✅ (rev80): in help/docs buffers, `Enter` follows link and `Backspace` goes back.
- **Docs browser outline** ✅ (rev79): headings list (`helpoutlinepick`) + `ed.help-outline-rows`; TUI renders markdown headings in bold.
- **Docs browser polish** ✅ (rev78): link underline highlighting in the TUI; `helplinkpick` lists links on the current docs page.
- **Open external links (gated)** ✅ (rev78): external docs links can open via `cap.open-url`.
- **Capability registry + shell exec (gated)** ✅ (rev78): `host.capabilities` registry; `ed.shell` behind `cap.shell`.

- **Docs browser navigation** ✅ (rev77): `helpfollow` follows markdown links under the cursor; `helpback` returns to the previous docs page.
- **Picker UX polish** ✅ (rev77): curses suggestion list gained scroll windowing with "more" markers + basic attributes (reverse for selection, bold for headers).

- **Help buffer loaded from docs** ✅ (rev76): `help TOPIC` falls back to opening `docs/*.md` into a protected read-only buffer; added `helppick` (docs picker) + hostcalls `ed.doc-rows` / `ed.help-doc`.
- **Picker list in the TUI** ✅ (rev76): shows prompt suggestions under the prompt line with section headers when available.
- **Command palette path-aware open** ✅ (rev76): path-like queries produce an `openpath` row that opens the file directly.

- **Buffer MRU + prev buffer + bulk close** ✅ (rev75): `prevbuf`, `only`, `closeall`, and MRU-based active selection after close.
- **Recent files polish** ✅ (rev75): optional persistence (`recent.persist`/`recent.file`), grouped section rows hostcalls, and a `Recent Files` bucket in `commandpick`.
- **Safety demo plugin** ✅ (rev75): `plugins/capdemo` shows `host.feature?` capability checks.

- **Softwrap follow-on:** continuation indent (`softwrap.contindent`) + visual-row Home/End 🧪✅ (rev73): docs+tests landed.
- **Plugin UX follow-on:** `pluginpick` prompt + `plugin info/errors` details + completion for info/errors 🧪✅ (rev73).
- **Statusline follow-on:** `$(if:...)` conditional directive + hostcalls `ed.statusfmt` / `ed.statusline-text` 🧪✅ (rev73).

- **`ed.statusformatl`/`ed.statusformatr`-style templating** ✅ (rev72): micro-esque $() directives with a tiny renderer.
- **`finally`/`ensure` combinator** ✅ (rev72): stdlib cleanup combinator built on `catch`/`throw`.

- **Softwrap visual-line movement + wrap scrolling** ✅ (rev71): CursorUp/Down/PageUp/Down move by visual rows under softwrap; viewport gains `top_subline`.
- **Plugin manager UX follow-on** ✅ (rev71): surfaced load/requires errors in `plugin list`, improved reload errors, and added hostcalls `plugin.list`/`plugin.reload`/`plugin.errors`.

- **`try`/`catch` ergonomics combinators** ✅ (rev70): `try?`, `try`, and `recover` in stdlib.
- **Richer editor statusline strings** ✅ (rev70): added encoding/fileformat/percentage + a reference `statusline_text` formatter used by TUI.

- **Softwrap option + rendering model** ✅ (rev69): `softwrap` option + `Editor.view_rows` / `Editor.cursor_view_pos` used by TUI.
- **`plugin.json` schema + dependency-aware load order** ✅ (rev69): validated metadata + `entry` + `requires`-based toposort.

- **Richer `see` / decompiler** ✅ (rev68): `see` now includes disasm + const pool; added `disasm-rows` structured output.
- **Regex support hostcalls** ✅ (rev68): `re.search`/`re.findall`/`re.sub`/`re.subn`/`re.escape` + shared replacement templates.

- **Dev-mode stack effect checking (starter kit)** (rev67):
  - `stackcheck!` warn/error modes for closed effects
  - `infer-effect` + `check-effect` tools for straight-line code
  - quotation effect annotations via leading paren-comment are now preserved
  - docs: `docs/91-stack-effect-checking.md`

- **Syntax highlight span model surface**: `ed.highlight` hostcall + minimal micromax line highlighter (rev66).
- **Timer/after hostcall**: `ed.after` + `ed.pump-timers` + cancel + deterministic clock + plugin-group cleanup (rev66).

- Viewport model + minimal curses TUI + prompt editing + `s-format` (rev63).
- **Jumplist picker**: `jumppick [QUERY]` (rev64).
- **User init/rc loading**: `~/.config/micromax/init.mx` (override: `$MICROMAX_INIT`) (rev64).
- **`include`/`require` search convention**: relative-to-caller + `$MICROMAX_PATH` + host `vm.load_paths` (rev64).
- **Plugin load error recovery**: failing plugins don't crash loading; errors recorded (rev64).
- TUI prompt line now shows the **current picker selection preview** (rev64).

- **Auto-indent on newline**: `InsertNewline` preserves current-line indentation (rev65).
- **Tabs options**: `tabsize` + `tabstospaces` + visual-column-aware `InsertTab` (rev65).
