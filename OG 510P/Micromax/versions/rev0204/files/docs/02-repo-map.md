# Repo map (rev188)

Latest tiny landing (rev202): the shared editor core now treats `fastdirty` as a real ordinary option, so buffers can either keep the cheap modified-flag rule or accurately clear `dirty` again when their text returns to the last clean baseline; the handoff note is `docs/143-fastdirty.md`, the focused editor coverage lives in `tests/test_editor_fastdirty.py`, `tests/test_editor_fs_open_save.py`, and `tests/test_editor_statusline.py`, and the portability corpus now also covers merging into an empty destination map adopting the source pairs in `portability/kernel_cases.json`.


## Key files

### Priorities
- `TODO.md` — current priorities
- `docs/43-worklist.md` — detailed tiered worklist (living)

### Language / VM
- `src/micromax/vm.py` — tokenizer, VM, wordlists, locals, budgets, tier-2 scaffolding
- `src/micromax/core.py` — core words (portable kernel + a little debug tooling)
- `src/micromax/stdlib/core.mx` — boot stdlib (convenience words; includes `try`/`recover` + `ensure`/`finally` helpers)
- `docs/96-try-catch.md` — stdlib `try?`/`try`/`recover` + `ensure`/`finally` patterns and examples
- `src/micromax/host_strings.py` — reference string helpers (installed as hostcalls)
- `src/micromax/host_regex.py` — reference regex helpers (installed as hostcalls)
- `src/micromax/regex_tools.py` — shared replacement-template conversion + flag parsing
- `src/micromax/portability_suite.py` — JSON portability corpus runner for future Rust/WASM hosts
- `portability/kernel_cases.json` — small cross-host semantic corpus for the portable kernel / boot stdlib
- `docs/102-portability-suite.md` — what belongs in the portability corpus and how to run it

### Editor core
- `src/micromax_editor/editor.py` — buffers, actions, keymaps, search, selections, multicursor, macros, status model + viewport/softwrap rendering helpers (`statusline_text`)
- `src/micromax_editor/statusformat.py` — micro-esque statusformat template renderer (`$()` directives)
- `docs/97-statusline.md` — status model fields + statusformat templating + reference formatter
- `docs/116-scrollmargin.md` — shared `scrollmargin` viewport/context policy
- `docs/126-pageoverlap.md` — shared `pageoverlap` paging/context policy
- `docs/127-rmtrailingws.md` — shared save-time trailing-whitespace cleanup policy
- `docs/128-eofnewline.md` — shared save-time final-newline normalization policy
- `docs/129-mkparents.md` — shared save-time parent-directory creation policy
- `docs/117-cursorline.md` — tiny `cursorline` current-row policy for the curses TUI
- `docs/118-hltrailingws.md` — tiny `hltrailingws` trailing-whitespace policy for the curses TUI
- `docs/119-hltaberrors.md` — tiny `hltaberrors` indentation-mismatch policy for the curses TUI
- `docs/120-colorcolumn.md` — tiny `colorcolumn` guide-column policy for the curses TUI
- `docs/121-scrollbar.md` — tiny `scrollbar` thumb policy for the curses TUI
- `docs/122-scrollbarchar.md` — tiny `scrollbarchar` thumb-glyph policy for the curses TUI
- `docs/113-search-highlighting.md` — tiny `hlsearch` rendering policy for the curses TUI
- `docs/114-search-position-summary.md` — shared whole-buffer search-position/status contract (`i/n`)
- `src/micromax_editor/buffer.py` — line-based buffer operations (easy to swap later)
- `src/micromax_editor/filetypes.py` — tiny filetype detection (extension + shebang)
- `src/micromax_editor/undo.py` — tiny linear undo stack
- `src/micromax_editor/micromax_bridge.py` — hostcalls (stable scripting surface)
- `src/micromax_editor/highlight.py` — syntax highlight span model + micromax line highlighter
- `src/micromax_editor/timers.py` — deterministic timer queue (after/cancel/pump)


- `docs/81-editor-marks.md` — named marks + buffer switching (navigation primitives)
- `docs/86-editor-lifecycle-hooks.md` — editor hook names + stack contracts
- `docs/87-editor-config.md` — rc/init loading conventions
- `docs/88-require-and-paths.md` — `include`/`require` search convention
### Example scripts
- `examples/combinators.mf` — small quotation combinator examples
- `examples/editor_completion_rows.mf` — custom editor command completion with richer suggestion rows

## Tests
- `tests/test_smoke.py` — basic language smoke tests
- `tests/test_features.py` — lists/hooks/modules/locals/host API features
- `tests/test_editor_core.py` — editor behaviors without any UI
- `tests/test_maps.py` — portable map/dict primitives
- `tests/test_portability_suite.py` — verifies the JSON portability corpus stays runnable and useful
- `tests/test_tui_hltrailingws.py` — renderer-local trailing-whitespace cue under plain/softwrapped views
- `tests/test_tui_hltaberrors.py` — renderer-local tab/indentation-mismatch cue under plain/fragmented views
- `tests/test_tui_colorcolumn.py` — renderer-local guide-column cue under plain/scrolled/softwrapped/help views
- `tests/test_tui_scrollbar.py` — renderer-local right-edge scrollbar cue under plain/softwrapped/help views
- `tests/test_tui_hlsearch.py` — renderer-local `hlsearch` spans + find-prompt search-position summary
- `tests/test_tui_cursorline.py` — tiny `cursorline` current-row rendering policy
- `tests/test_xt_span.py` — spans + xt-span introspection
- `tests/test_editor_prompt_completion_hostcalls.py` — prompt completion via hostcalls, including fuzzy fallback for command-ish tokens and richer argument completion (option values / keymodes / hook topics)
- `tests/test_editor_prompt_path_completion.py` — prompt completion for filesystem paths (open/save/cd), including quote-aware completion for spaces and embedded quotes
- `tests/test_editor_mx_commands_and_completion.py` — micromax-defined command-bar commands + completion hooks, including plugin-provided suggestion metadata rows
- `tests/test_here_span.py` — here-span + vm.last_span provenance
- `tests/test_stack_effect_checking.py` — dev-mode stack effect checking + inference tools
- `tests/test_editor_keybinding_provenance.py` — keybinding provenance, `showkey`, `ed.bindings`, `ed.unbind`
- `tests/test_hook_provenance.py` — hook definition/handler provenance, `hook-rows`, `xt-span` for hooks
- `tests/test_editor_showhook.py` — editor command-bar hook inspection
- `tests/test_editor_statusline.py` — portable statusline/infobar model + `showstatus`
- `tests/test_editor_softwrap.py` — visual-row movement/scrolling + wrapped `scrollmargin` / `pageoverlap` behavior
- `tests/test_hook_groups.py` — hook groups, `hook-detail`, and plugin-reload hook cleanup
- `tests/test_editor_registration_groups.py` — grouped editor commands/keybindings and plugin reload cleanup
- `tests/test_editor_keymap_modes.py` — mode-aware keybindings, keymode stack, and plugin reload cleanup for mode bindings
- `tests/test_editor_transient_keymodes.py` — one-shot keymodes, centralized key dispatch, and fallthrough semantics
- `tests/test_editor_keymap_discovery.py` — resolved keymap discovery, filtered binding rows, and `whichkey`/`showbindings`
- `tests/test_editor_keybinding_docs.py` — derived/custom binding descriptions and machine-readable keymap info rows
- `tests/test_editor_tier0_basics.py` — Tier-0 editor basics (open/save/quit/delete/word/page, including shared `pageoverlap`)
- `tests/test_editor_viewport_and_typing.py` — viewport model + unbound typing + prompt-mode editing
- `tests/test_string_hostcalls.py` — string hostcall MVP
- `tests/test_type_predicates_and_conversions.py` — typed predicates + conversions (`to-int`/`to-str`)
- `tests/test_editor_filetypes.py` — filetype detection
- `tests/test_editor_lifecycle_hooks.py` — open/save/change hooks
- `tests/test_editor_prefix_maps.py` — one-shot prefix-mode helpers (`prefixmode`, `bindprefix`, `bindmodeprefix`, `ed.bind-prefix`, `ed.bind-mode-prefix`)
- `tests/test_editor_highlight_and_timers.py` — syntax highlight spans + deterministic timers
- `tests/test_statusformat_templating.py` — statusformat directive rendering (opt/bind/escaping)
- `tests/test_ensure_finally.py` — `ensure`/`finally` cleanup combinators

## Docs worth skimming
- `docs/20-language-design.md`, `docs/21-language-spec-sketch.md`
- `docs/24-bytecode-format.md`, `docs/25-inline-caching.md`
- `docs/31-host-api.md`
- `docs/61-editor-cursorstate.md`
- `docs/63-editor-jumplist.md`
- `docs/64-editor-prompt-completion.md`
- `docs/65-debugging-spans.md`
- `docs/66-editor-micromax-commands.md`
- `docs/67-editor-keybinding-provenance.md`
- `docs/68-hook-provenance.md`
- `docs/69-editor-statusline-model.md`
- `docs/73-hook-groups.md`
- `docs/74-editor-registration-groups.md`
- `docs/75-editor-keymap-modes.md`
- `docs/76-editor-transient-keymodes.md`
- `docs/77-editor-keymap-discovery.md`
- `docs/78-editor-binding-descriptions.md`
- `docs/79-editor-prefix-maps.md`
- `docs/80-editor-mode-prefix-maps.md`
- `docs/89-syntax-highlight-spans.md`
- `docs/90-timers.md`
- `docs/91-stack-effect-checking.md`
- `docs/57-editor-multicursor.md`

## Tools (for future LLMs + humans)

- `tools/mxdoctor.py` — run lint + tests; emits archive hygiene warnings
- `tools/mxcontext.py` — print a curated “project context” snapshot
- `tools/mxpack.py` — build a clean zip archive (excludes caches)

- `tests/test_vm_require_paths.py` — include/require path resolution (caller-relative, MICROMAX_PATH, host load_paths)
- `tests/test_editor_user_init.py` — user init loading via MICROMAX_INIT
- `tests/test_editor_jumppick.py` — jumplist picker behavior
- `tests/test_plugin_load_errors.py` — plugin load error recovery + cleanup


## rev72 notes
- Statusline is now configurable via `statusformatl`/`statusformatr` templates (micro-esque `$()` directives).
- Stdlib now includes `ensure`/`finally` for always-run cleanup.
- `docs/123-matchbrace.md` — tiny visible match-brace cue in the curses TUI (`matchbrace`, `matchbraceleft`)

- `docs/125-statusline-bufferpos.md` — shared current-buffer position model + `$(bufpos)` statusline cue
- `docs/126-pageoverlap.md` — shared `PageUp` / `PageDown` overlap policy
