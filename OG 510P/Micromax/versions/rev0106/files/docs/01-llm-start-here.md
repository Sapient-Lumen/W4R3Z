# LLM start here (rev106)
If you're an automated assistant (or a human who wants the shortest on-ramp), read in this order:

0) `TODO.md` + `docs/43-worklist.md` — what to do next (living priorities)
   - new: curses TUI pickers now preserve minimal row metadata (via `PromptDisplayItem` + `_prompt_display_items`) so suggestion rows can be styled by kind (actions/files/links/headings) without re-parsing strings, and help/docs buffers now dim inline markdown code spans (`` `code` ``) for scanability (rev106)
   - new: fixed a capability bypass where scripts could open files via the command palette openpath row (\`ed.command-palette\` + \`ed.prompt-submit\`) without \`cap.fs-open\`; palette opens now require \`cap.fs-open\` in script context and respect \`cap.fs-root\` for both openpath and recentfile rows, helpnav link rows now include nearest heading breadcrumb context, and the minimal TUI dims picker “detail” suffixes after \`—\` for scanability (rev101)
   - new: `clipboard=external` Paste (Ctrl-v) now best-effort imports from the system clipboard via wl-paste/xclip/xsel/pbpaste/powershell (fallback to internal clipboard when unavailable); script-originated reads are gated by new `cap.clipboard-read` advertised as `ed.clipboard-import`, with a matching `( -- ok text err )` hostcall `ed.clipboard-import` (rev105)
   - new: scripts can no longer bypass `cap.fs-open`/`cap.fs-save` by running `open`/`save` through `ed.command` or `ed.prompt-submit` (script context now propagates through those hostcalls and the command dispatcher enforces caps + `cap.fs-root` in that context), and the minimal TUI picker match highlighting now falls back to fzf-style subsequence character matches when no substring hit exists (rev100)
   - new: capability-gated `ed.open`/`ed.save` hostcalls (`cap.fs-open`/`cap.fs-save`) to avoid ambient filesystem authority from scripts, `cd` now expands `~` and reports errors cleanly, and the minimal TUI picker list now shows per-section counts plus rough "more" counts (rev99)
   - new: optional filesystem sandbox root `cap.fs-root` now constrains the capability-gated filesystem helpers (`ed.fs-read`/`ed.fs-list`/`ed.fs-stat`) *and* command-palette path completions/drill-down; also added VM debugging word `callstack` (alias `trace`) (rev98)
   - new: docs link picker sections can optionally group by nearest markdown heading via `set help.linksections heading` (default remains Docs/Files/External), and the host adds capability-gated `ed.fs-stat` (plus a small `tools/mkrevzip.py` helper to build standard-named archives) (rev97)
   - new: picker suggestion lists highlight query-token substring matches in the minimal TUI, and the `Makefile` now invokes scripts via `bash` so `make test` works even when executable bits are lost in archive checkouts (rev95)
   - new: docs help browser now supports shortcut reference links (`[id]` with a matching `[id]: target`), and the minimal TUI underlines reference/shortcut/autolinks (rev94)
   - new: picker prompts now support `Alt-Up`/`Alt-Down` to jump between section headers (and `Alt-Up` jumps to the start of the current section when used inside a section) (rev93)
   - new: picker prompts now have `prompt.wrap` (wrap vs clamp), support `Ctrl-Home`/`Ctrl-End` to jump to first/last selection, and the minimal TUI repeats the active section header as a sticky header while paging through long mixed sections (rev92)
   - new: picker-style prompts now support `PageUp`/`PageDown` selection jumps (option: `prompt.page`, default 8), in addition to `Up`/`Down` selection (without clobbering the typed query) and `Ctrl-y` to copy the selected row (for links: copies the target) (rev91)
   - new: `urlopen` / `urlcopy` commands and default `Alt-o`/`Alt-y` bindings to open/copy URLs under cursor (capability-gated by `cap.open-url`, confirmed by default via `open-url.confirm`) (rev89)
   - new: docs buffers support `y` (and `helplinkcopy`) to copy the link target under cursor; external links now confirm by default when `cap.open-url` is enabled (rev88)
   - new: `replace` / `replaceall` and `qreplace` now follow `ignorecase` (like `find`), and `qreplace` shows a small `match i/N` progress hint when it can pre-count matches (rev87)
   - new: interactive query-replace (`qreplace` / `queryreplace`) with a capture keymode (y/n/a/q) so global bindings can't accidentally fire (rev86)
   - new: shared Cursor↔offset helpers (`src/micromax_editor/textpos.py`) used by search + replace to avoid drift (rev86)
   - new: TUI now supports ESC-prefixed **Alt/Meta chords** and maps **Ctrl-Space** (NUL) to `Ctrl-Space`, so the default `Alt-*` keymap is reachable (rev85)
   - new: core defaults include `Ctrl-b` buffer picker, `Ctrl-o` open (prefilled), `Ctrl-r` replace (prefilled), `Ctrl-Space` command palette, and `Alt-g` binding discovery (rev85)
   - new: `docs/99-tui-key-decoding.md` (Alt/Meta ESC-prefix chords + Ctrl-Space mapping + rawkeys tips)
   - new: `helpnavpick` merges docs headings + links into one page navigator, and the host exposes `ed.helpnav-section-rows` (rev84)
   - new: docs help browser recognizes reference links (`[text][id]` + `[id]: target`) and autolinks (`<https://...>`) (rev83)
   - new: `docs/91-stack-effect-checking.md` (dev-mode checker starter kit)
   - new: `docs/94-softwrap.md` (softwrap + visual-row movement + top_subline)
   - new: `docs/97-statusline.md` (statusformat templating + reference formatter)
   - new: `docs/96-try-catch.md` (now includes `ensure`/`finally` cleanup)
   - new: `plugin.list` / `plugin.reload` / `plugin.errors` hostcalls (see `docs/31-host-api.md` and `docs/95-plugin-json.md`)
   - new: `ed.statusfmt` / `ed.statusline-text` (statusformat rendering) + `ed.with-buffer` helper hostcall
   - new: `ed.with-viewport` and `ed.recent` / `ed.recent-clear` hostcalls + `recent` / `recentpick` and `close` / `close!` commands (rev74)
   - new: `pluginpick` searchable plugin picker + richer `plugin info/errors` + completion for `plugin info/errors` (rev73)
   - also see `docs/89-syntax-highlight-spans.md` (highlight span model), `docs/90-timers.md` (after/cancel/pump),
     `docs/92-decompiler-and-disasm.md` (see/disasm/disasm-rows), and `docs/93-regex-hostcalls.md` (regex hostcalls), `docs/94-softwrap.md` (softwrap rendering model), and `docs/95-plugin-json.md` (plugin.json schema)
   - also see `docs/87-editor-config.md` and `docs/88-require-and-paths.md` for rc/init + module path conventions
1) `docs/00-vision.md` — why this exists and what “success” looks like
2) `docs/42-portability-ledger.md` — the contract that keeps us port-able to Rust/WASM
3) `docs/22-two-tier-execution.md` — interpreter vs compiled execution plan
   - also see `docs/24-bytecode-format.md`, `docs/25-inline-caching.md`, and `docs/27-bytecode-serialization.md` for tier-2 details
4) `docs/50-editor-behaviors.md` + `docs/57-editor-multicursor.md` — the editor’s core invariants
   - also see `docs/61-editor-cursorstate.md` for save/restore cursor state patterns
   - also see `docs/64-editor-prompt-completion.md` for command bar completion/session modeling
   - also see `docs/75-editor-keymap-modes.md` for mode-aware keybindings and active keymode state
   - also see `docs/76-editor-transient-keymodes.md` for one-shot keymodes and centralized key dispatch
   - also see `docs/77-editor-keymap-discovery.md` for resolved keymap inspection / `whichkey`-style discovery
   - also see `docs/78-editor-binding-descriptions.md` for human-friendly binding labels / whichkey descriptions
   - also see `docs/79-editor-prefix-maps.md` for tiny first-class prefix-key helpers built on one-shot keymodes
   - also see `docs/80-editor-mode-prefix-maps.md` for mode-local prefix helpers / nested prefix layers
   - command-bar completion also has a small fuzzy fallback for command-ish tokens, small argument completion for option values/keymodes/inspection topics, action-spec completion for `bind` / `bindmode`, best-effort suggestion metadata rows for future UIs/scripts, a tiny `apropos` search surface over command/action/word topics, and now a dedicated searchable `topic` prompt / `topicpick` surface built on the same rows; that prompt now live-refreshes ranked topics as its query changes, exposes the active row through `ed.prompt-current-row`, and also exposes grouped topic sections plus compact current-item previews for future UIs/statuslines; there is now also a parallel searchable `binding` prompt / `bindingpick` surface over the currently reachable keymap, with `ed.binding-prompt` and `ed.binding-prompt-rows`; there is also now a searchable command/action palette via `commandpick`, `CommandPalette`, and `ed.command-palette`, which executes actions directly and opens the ordinary command bar prefilled when a command is chosen; that palette now keeps a tiny MRU of palette selections, surfaces those recents first for empty queries, and exposes grouped sections through `ed.command-palette-section-rows`; topic, binding, and command-palette discovery all support small multi-term / out-of-order matching across names plus summary/description metadata; see `docs/64-editor-prompt-completion.md`
5) `docs/71-cookbook.md` — practical language snippets

## Repo invariants (do not break casually)

### VM invariants
- The Python VM is the **reference implementation** and **test oracle**.
- New convenience words should land in **stdlib** first (`src/micromax/stdlib/core.mx`).
- The stdlib now includes small quotation combinators (`dip`, `keep`, `2dip`, `2keep`, `bi`, `tri`); prefer composing with those before adding new primitives.
- If you add VM surface area, update the **portability ledger**.
- Stack effects are now explicitly **doc-first metadata**, not a checker contract: use `xt-effect`, `xt-doc`, `words-rows`, and `wid-word-rows` before proposing validation machinery.

### Two-tier invariants
- Tier-2 must preserve tier-1 semantics.
- Tier-2 name dispatch uses per-call-site caches invalidated by `dict-version`.
- Compiled code currently rejects **token-stream parsing words** (see `docs/22-two-tier-execution.md`).

### Editor invariants
- Editor core is **headless-first** and **unit-testable**.
- Multi-cursor behavior must stay deterministic (ordering, selection semantics).
- Editor scripting should use `ed.with-undo` to group multi-step edits into one undo entry.
- Clipboard is exposed via hostcalls (`ed.clipboard*`) and supports multi-item and linewise kinds.
- Micromax-defined command-bar commands are registered via `ed.cmd-add`; prompt completion can be extended via `ed.complete.*`, which now supports optional plugin-provided metadata rows in the same `[insert kind menu info]` shape used by built-ins; active suggestion rows are visible through `ed.prompt-suggestion-rows`, `ed.prompt-current-row`, `ed.prompt-current-section`, and `ed.prompt-current-preview`; the editor also exposes searchable topic rows through `apropos QUERY`, `ed.topic-rows`, `ed.apropos-rows`, grouped section views via `ed.topic-section-rows` / `ed.apropos-section-rows`, and the `topicpick` / `ed.topic-prompt` surface alongside `help NAME` / `showword NAME`; `apropos` now searches topic summaries/docs as well as names, failed `help` calls surface a few likely matches, multi-term/out-of-order queries can match across topic names + summaries and binding keys + descriptions, the topic prompt reuses the same ranking/row substrate while live-refreshing as the query changes, the same prompt/session contract now also powers searchable current-binding discovery through `bindingpick` / `BindingPrompt` / `ed.binding-prompt`, and a parallel command/action palette through `commandpick` / `CommandPalette` / `ed.command-palette`; that palette now also exposes grouped `Recent` / `Commands` / `Actions` sections via `ed.command-palette-section-rows` and marks current-item previews/status with `Recent` when appropriate (see `docs/66-editor-micromax-commands.md`).

## Where to change things

- Language core primitives: `src/micromax/core.py`
- VM execution + compiler scaffolding: `src/micromax/vm.py`
- Stdlib: `src/micromax/stdlib/core.mx`
- Editor core: `src/micromax_editor/editor.py`
- Editor↔VM hostcalls: `src/micromax_editor/micromax_bridge.py`
- Tests: `tests/`

## Running the suite

```bash
make test
```

## Adding a word (suggested process)

1) Write the word in micromax stdlib first (if possible).
2) Add 2+ focused tests.
3) If you must add a primitive, record the decision + update `docs/42-portability-ledger.md`.
