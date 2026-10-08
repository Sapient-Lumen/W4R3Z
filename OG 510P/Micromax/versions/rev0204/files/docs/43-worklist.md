# Worklist (rev202)
This is the **living, prioritized worklist** for Micromax + the micro-esque editor core.

- Tiny `showchars` TUI pass + missing-map-predicate portability follow-up (rev203): the minimal curses TUI now honors a tiny micro-esque `showchars` option so ordinary and help/docs buffers can display visible one-cell replacements for spaces/tabs (with `ispace` / `itab` overrides in the leading indent run) without mutating buffer text or promoting invisible-character spans into the headless editor model; the portability corpus now also covers `m?` returning `0` for a missing key.
- Shared `fastdirty` modified-state policy + portability follow-up (rev202): the shared editor core now treats `fastdirty` as a real ordinary option, so buffers can either keep the cheap “edited once means dirty” rule or accurately clear `dirty` again when the text returns to the last clean baseline; command-bar / Micromax option paths resync existing buffers immediately, and the portability corpus now also covers merging into an empty destination map adopting the source pairs.
- Shared `autosave` timed save path + portability follow-up (rev201): the shared editor core now treats `autosave` as a real ordinary option, so dirty path-backed buffers can save through the same headless save path after N seconds, `quit` can reuse that same autosave path for eligible dirty buffers, and the portability corpus now also covers merging an empty source map preserving destination pairs.
- Shared `basename` display-path option + portability follow-up (rev200): the shared editor core now treats the visible filename as real status/display state instead of a hardcoded basename, so `status_model()` carries both raw `file_name` and effective `display_name`, `$(filename)` / `showstatus` honor a tiny `basename` option, and the portability corpus now also covers `m-items` returning `[]` for an empty map.
- Real `encoding` open/save behavior + portability follow-up (rev199): the shared editor core now treats text encoding as a real per-buffer option instead of a hardcoded `utf-8` status token, so `open_file(...)` decodes with the configured encoding, `save()` writes with the effective buffer encoding, and status/config surfaces report the same user-facing value; the portability corpus now also covers `m-keys` returning `[]` for an empty map.
- Micro-esque `savehistory` option alias + portability follow-up (rev197): the editor's existing prompt-history persistence can now be enabled through `savehistory`, backed by a tiny alias-aware option registry so reads/writes/toggles and command-bar completion all resolve to the same canonical `history.persist` state; the portability corpus now also covers `m@` returning `0` for a missing key.
- Real `fileformat` open/save behavior + portability follow-up (rev196): the shared editor core now treats line endings as a real per-buffer option instead of a status-model placeholder, so `open_file(...)` best-effort detects CRLF files as `dos`, normalizes buffer text internally to `\n`, and `save()` writes LF or CRLF from the effective option value; the portability corpus now also pins down that *missing* `host.feature?` probes stay lookup-only with respect to `dict-version`.
- Leading-indent cursor stepping + portability follow-up (rev194): the shared editor core now honors a tiny `tabmovement` option so `CursorLeft` / `CursorRight` and `SelectLeft` / `SelectRight` can treat leading runs of `tabsize` spaces like one tab stop when `tabstospaces` is enabled, mirroring micro's conservative indent-only rule without promoting a richer visual-column subsystem; the portability corpus now also covers `host.api-version` staying lookup-only with respect to `dict-version`.
- Protected-buffer option + portability follow-up (rev193): the editor's existing protected-buffer path is now available through a tiny ordinary `readonly` option, so `setlocal readonly true` can block edits and saves in ordinary buffers while reusing the same shared behavior as help/docs buffers; the portability corpus now also covers `host.features` staying lookup-only with respect to `dict-version`.
- Whitespace-only autoindent cleanup + shared open-target parsing (rev192): the shared editor core now honors a tiny `keepautoindent` option so pressing Enter again on a whitespace-only autoindented line can either clear or keep that previous indent through the same headless `InsertNewline` path, and the rebuilt shared `parsecursor` path again understands `file:line[:col]` across interactive, capability-gated/scripted, persistence-aware, and path-palette opens.

- Smart multiline paste indentation + host-inventory portability follow-up (rev190): the shared editor core now honors a tiny `smartpaste` option so multi-line `Paste` can reuse the current line's existing whitespace prefix for otherwise-unindented blocks, keeping the behavior headless-first across ordinary, multi-cursor, and external/internal clipboard pastes without inventing a formatter; the portability corpus now also covers seeded `host.features` inventory deduplicating repeated feature names while staying sorted.

- Shared page-overlap paging + dictionary-version portability follow-up (rev185): the editor core now honors a tiny `pageoverlap` option so `PageUp` / `PageDown` keep a few rows from the previous view visible in both ordinary and softwrapped views, with overlap measured in visual rows under `softwrap`; the portability corpus now also covers `dict-version` staying stable across lookup-only `get-current`.

- Overflow-marker cue + dictionary-version portability follow-up (rev183): the minimal curses TUI now honors a tiny `overflowmarkers` option by drawing bold+dim `<` / `>` cues at the visible edges of horizontally clipped rows in ordinary buffers and docs/help buffers while intentionally suppressing them under `softwrap`, and the portability corpus now also covers `dict-version` staying stable across lookup-only `find`.

- Trailing-whitespace cue + search-order portability follow-up (rev177): the minimal curses TUI now honors a tiny `hltrailingws` option by reverse-dimming visible trailing spaces/tabs in ordinary buffers, docs/help buffers, and softwrapped final fragments without promoting whitespace-warning spans into the headless editor model, and the portability corpus now also covers `previous` dropping the top search-order entry.
- Tiny `cursorline` TUI pass + namespace portability follow-up (rev176): the minimal curses TUI now honors a tiny `cursorline` option by underlining the current visible buffer row (including the active wrapped screen row under `softwrap`) without promoting row-highlighting into the headless editor model, and the portability corpus now also covers `definitions` following the top of the current search order.
- Shared scrollmargin viewport pass + tiny portability follow-up (rev175): the editor core now honors a tiny `scrollmargin` option inside the shared viewport contract, keeping vertical context rows around the primary cursor in both ordinary and softwrapped views, and the portability corpus now also covers `compiled?` returning `0` for a primitive XT.

- Scrollbar thumb-character follow-up + search-order portability case (rev181): the minimal curses TUI now honors a tiny `scrollbarchar` option so the existing right-edge scrollbar cue can render a user-chosen one-cell glyph (default `|`, empty falls back to `|`, longer strings use their first character) without promoting new scrollbar state into the headless editor model, and the portability corpus now also covers search-order conflict precedence so future hosts can validate that the first search-order entry wins on duplicate names from JSON alone.

- Scrollbar cue + host-feature portability follow-up (rev180): the minimal curses TUI now honors a tiny `scrollbar` option by reserving one right-edge column for a proportional thumb in ordinary and softwrapped views without promoting scrollbar state into the headless editor model, and the portability corpus can now seed per-case `host_features` so future hosts can validate positive host-boundary probes directly from JSON.

- Statusline search-count cue + tiny portability follow-up (rev174): the reference statusline formatter now understands `$(searchpos)` / `$(searchcount)` / `$(search)` as a compact ` [i/n]` token built from the shared search-position model, the default right-side status format now includes that token so ordinary TUI/statusline rendering exposes active search position outside the transient find prompt too, and the portability corpus now also covers missing-word `find` returning `0`.

- Search-position/statusline win (rev173): the editor now exposes one shared whole-buffer search-position model through `status_model()` / `ed.status` (`search_query`, `search_literal`, `search_case_sensitive`, `search_match_index`, `search_match_count`, `search_summary`), the minimal TUI now shows the same compact `[i/n]` summary right in the find prompt, and future statuslines/UIs/LLMs can reuse that same tiny contract instead of re-counting matches themselves.

- Portability host-boundary follow-up (rev173): `portability/kernel_cases.json` now also covers bare-VM `host.feature?` for a missing feature, giving future Rust/WASM hosts one more tiny host-introspection contract point alongside `host.api-version` and bare-VM `host.features`.

- Portability exact-slice + missing-kernel-contract win (rev170): the tiny JSON portability suite now covers a few more missing but very contract-like kernel behaviors — `0=`, successful `catch`, list clone/pop isolation, `m-keys`, `m-items`, session-local query/removal, and `set-current` round-tripping — and `mxportable` / `portability_suite.py` now support exact case-name filtering so future hosts and future LLMs can ask for precise slices without fuzzy substring matching.

- Portability inventory + kernel-coverage win (rev169): the tiny JSON portability suite now covers a few more portable kernel behaviors Micromax already relies on — `when`, `to-int`, `to-str`, `m-del`, `m-merge` — and `mxportable` can now emit a lighter-weight inventory of matching categories/tags/case names so future hosts and future LLMs can inspect the contract without pulling full case bodies.

- Portability inspectability win (rev168): the tiny JSON portability suite now covers a few more missing portable kernel behaviors — `while`, `constant`, `variable`, locals shadowing — carries broader tags across the corpus, and `mxportable` can now emit machine-readable JSON summaries/results so future hosts and future LLMs can inspect slices without scraping human text.

- Portability contract/tooling win (rev167): the tiny JSON portability suite now covers more missing portable kernel/boot-stdlib ground — return-stack basics, `execute`, wordlist/search-order lookup, `in`, `2dip`, `recover`, and `finally` — and the shared runner/CLI now validate case shape plus support category/tag/name filtering for targeted cross-host runs.

- Portability-corpus coverage win (rev166): the tiny JSON portability suite now covers more of the portable language surface Micromax actually uses in anger — quotation combinators (`dip`, `2keep`, `tri`), recovery/cleanup helpers (`try?`, `try`, `ensure`), and budget exhaustion under `catch` — so future Rust/WASM hosts can validate more than arithmetic + one `bi` example against the Python oracle.

- Docs/help multi-line footnote-definition render-parity win (rev165): tiny indented continuation lines under markdown footnote definitions now also render dim in the live docs/help TUI, while visible `[^id]:` starter markers keep their existing dim+bold treatment, all through the same shared definition-line roles instead of another parser path.

- Docs/help escaped-markdown source-view cue win (rev164): visible backslash-escaped markdown punctuation pairs like `\[` / `\!` / `\<` / `\*` / `\_` / `\~` / ``\``` now also read a little more like deliberate source in the live docs/help TUI: the visible two-character escape pair renders dim while the escaped form still stays literal and non-navigable, all through one tiny helper layered on the existing shared backslash-escape policy instead of another parser path.

- Docs/help inline-code delimiter cue win (rev163): visible markdown inline-code backtick delimiters now also read a little more like deliberate source in the live docs/help TUI: opening/closing backtick runs render bold+dim while the already-dim code body styling stays intact, all through one tiny shared helper layered on the existing equal-length backtick scan instead of another parser path.
- Docs/help live-link source-scaffolding cue win (rev161): visible supported ordinary markdown links like `[Vision](00-vision.md)` / `[Vision ref][visionref]` / `[Vision shortcut]` now also read a little more like deliberate source in the live docs/help TUI: the non-label scaffolding (`[` / `](` + destination or reference tail / `]`) renders dim while the live label stays underlined, all through one tiny helper layered on the existing shared link matcher instead of another parser path.
- Docs/help inline raw-HTML source-view cue win (rev160): visible inline raw HTML tags like `<kbd>` / `</kbd>` / `<a name=...>` now also read a little more like deliberately inert source in the live docs/help TUI: whole tag tokens render dim through one tiny helper layered on the existing shared inline raw-HTML span helper, while supported autolinks keep their separate bold whole-token cue.

- Docs/help inline-emphasis delimiter cue win (rev162): visible markdown emphasis delimiters like `**` / `*` / `_` / `~~` now also read a little more like deliberate source in the live docs/help TUI: delimiter tokens render dim while the existing strong/emphasis/strike body styling stays intact, all through one tiny helper layered on the existing inline-emphasis regex helpers instead of another parser path.

It is intentionally practical:
- describes *what users actually feel* (keybindings, editing loops)
- breaks work into pieces small enough to land with tests
- records **status** and **pointers** (files/tests) so future humans/LLMs can pick up the thread quickly

- Docs/help image-token inert-source cue win (rev159): visible supported markdown image forms like `![alt](dest)` / `![alt][id]` now also read a little more like deliberately inert source in the live docs/help TUI: the whole token renders dim, all through one tiny helper layered on the existing shared markdown destination/reference helpers instead of another parser path.
- Docs/help autolink-token source-view cue win (rev158): visible supported angle-bracket autolinks like `<https://...>` now also read a little more like autolink tokens in the live docs/help TUI: the whole token renders bold while the inner URL still keeps the ordinary docs-link underline, all through one tiny helper layered on the existing shared autolink matcher instead of another parser path.
- Docs/help footnote-reference source-view cue win (rev157): visible markdown footnote references like `[^note]` now also read a little more like footnote tokens in the live docs/help TUI: the whole token renders bold while the inner `^note` still keeps the ordinary docs-link underline, all through one tiny helper layered on the existing shared footnote matcher instead of another parser path.
- Docs/help nested-list scanability win (rev155): the live docs/help TUI now opts into deeper indentation for nested list/task markers only after the shared indented-code check has already ruled out real top-level code blocks, so nested worklist bullets finally read like lists in source view without reclassifying literal code examples.
- Docs/help definition render-parity win (rev154): reference-style definition starter lines now render dim with a bold `[id]:` token, tiny wrapped reference-definition continuation lines render dim too, and footnote-definition starter lines get the same dim+bold treatment in the live docs/help TUI — all through one shared definition-line helper reused from the docs-browser side instead of another render-only parser.
- Docs/help raw-HTML render-parity win (rev153): raw HTML comments and raw HTML block lines were already inert for docs navigation, definition parsing, and link underlining; the live docs/help TUI now dims those existing comment spans / block lines too, so commented-out notes and embedded HTML examples read less like ordinary prose without adding another parser path.
- Docs/help indented-code parity win (rev152): blank-separated top-level indented code-ish lines now stay inert for `helpfollow`, `helplinkpick`, and TUI docs-link underlining too, while the live docs/help TUI dims those lines via one tiny shared helper so source-view examples read like code instead of accidentally clickable prose.
- Docs/help fenced-code render-scanability win (rev151): docs/help rendering now reuses one tiny shared fenced-code line-role helper, so fenced markdown examples finally look visibly code-ish in the live TUI too: opening/closing fence lines render bold+dim while fenced body lines render dim, staying aligned with the same fence precedence already trusted for docs-link actions and definition parsing.
- Docs/help setext-heading render-parity win (rev150): docs/help rendering now reuses the same tiny heading scan already trusted for titles / outline rows / fragment jumps / heading breadcrumbs, so setext heading title lines finally render like headings in the live TUI too while their underline line gets a dim heading-ish treatment.
- Docs/help list-marker scanability win (rev149): the minimal TUI now gives ordinary markdown list markers (`-` / `+` / `*`, `1.` / `1)`) a little scanability polish via one shared helper, so list-heavy docs and worklists read a bit more like real markdown while task-list checkbox styling continues to layer on top.
- Prompt-display truncation/readability win (rev148): shared visible picker rows now preserve trailing path/location detail when widths get tight instead of naively chopping the whole row at the right edge; tiny headers/more markers also ellipsize a bit more cleanly, keeping the shared `prompt_display_model` slightly closer to a real picker surface.
- Prompt-window/shared-scroll-model win (rev146): the minimal TUI's picker windowing now lives in one shared editor helper (`prompt_window_model`) instead of only inside `tui.py`, and future UIs/scripts/LLMs can inspect the same sticky-header / more-marker / hidden-count structure headlessly through `ed.prompt-window`.
- Docs-focused picker browse-budget parity (rev144): `helplinkpick` and `helpnavpick` now flatten their grouped help sections through the same shared browse-window policy as the other section-aware pickers, so empty-query docs browsing keeps `Docs` / `Files` / `External` (and `Headings` for `helpnavpick`) visible instead of hiding later sections behind a large first bucket.
- Command-palette/live-grouping win (rev142): `commandpick` now flattens the same grouped palette sections already exposed through `ed.command-palette-section-rows`, so the live prompt, TUI section headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces all agree on visible labels like `Recent Files`, `Recent`, `Commands`, and `Actions`. Empty-query browse windows also now budget rows across visible sections so commands do not consume the whole first page before actions appear.
- Topic-picker/live-grouping win (rev141): `topicpick` now flattens the same grouped topic families already exposed through `ed.topic-section-rows` / `ed.apropos-section-rows`, so the live prompt, TUI section headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces all agree on `Commands` / `Actions` / `Words`. Empty-query `topicpick` also now budgets the first row window across visible sections so Actions/Words remain browseable instead of disappearing behind the command list cap.
- Recent picker/readability win (rev140): picker-style prompts now expose one shared current-item position model (`prompt_current_position`, status-model `prompt_*` ordinal fields, and `ed.prompt-current-position`), and the minimal TUI prompt line now shows that same compact `index/count • section i/n` summary next to the existing preview so long grouped pickers answer “where am I?” consistently across headless status/debug surfaces and the live UI.
- Previous recent picker/readability win (rev139): `recentpick` now flattens the same shared project-root grouping already exposed through `ed.recent-section-rows`, so the live prompt, TUI headers/sticky headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces all agree on one recent-files section model. Recent rows also rewrite their visible detail to project-name + project-relative path for faster scanning.

- Previous picker/readability win (rev138): `helppick` now groups docs rows by numbered doc families (`00–09 Project`, `10–19 Research`, `20–29 Language + VM`, etc.) and exposes that same shape through `ed.doc-section-rows`, while `prompt_current_section` / preview / status now reuse those same visible labels and docs previews now lead with the human doc title instead of the slug topic.

- Previous picker/readability win (rev137): `bindingpick` now groups rows by winning mode and exposes that same shape through `ed.binding-section-rows`, while `prompt_current_section` / preview / status now reuse those same visible labels (`Prompt`, active mode names like `nav`, `Global`) instead of the generic `Binding` bucket.

- Recent docs-browser win (rev134): docs/help navigation now keeps empty and whitespace-only markdown labels literal prose across inline/reference/shortcut links, so malformed cases like `[](doc.md)` and `[ ](doc.md)` no longer leak into `helpfollow`, `helplinkpick`, or TUI underlining.

- Previous docs-browser win (rev133): docs/help navigation now refuses outer markdown links whose label text contains a valid inner link, keeping the outer prose literal while still exposing the valid inner link through `helpfollow`, `helplinkpick`, and TUI underlining.

- Previous docs-browser win (rev132): docs/help navigation now also covers tiny wrapped angle-bracket destinations (`<path with spaces.md>`) in inline links and reference definitions, while the same shared destination helper now rejects malformed title starts that appear immediately after a closing `>` with no separating whitespace.
- Previous docs-browser win (rev131): docs/help inline links now also support tiny wrapped forms where the destination can sit on the next line and the title/closing `)` can wrap once as well, with one shared continuation helper keeping `helpfollow`, `helplinkpick`, and TUI docs-link underlining aligned around fenced/raw-HTML/comment-hidden lines.

- Previous docs-browser win (rev130): docs/help block starters now keep a shared spaces-only 0–3 indent guard, so four-space and tab-indented reference definitions / footnote definitions / ATX heading lookalikes stay code-ish prose instead of leaking into navigation, pickers, or outline rows.
- TUI search-highlight win (rev172): the minimal curses TUI now honors the existing `hlsearch` option, reverse-highlighting visible matches for the current search pattern and bolding the visible current match under the primary cursor, while keeping the feature renderer-local instead of promoting search-highlight spans into headless editor state.
- Portability corpus follow-up (rev172): `portability/kernel_cases.json` now also covers typed string ordering via `s<` plus the bare-kernel `host.features` default shape, giving future Rust/WASM hosts one more tiny typed-string contract point and one more host-boundary inventory check.

- Previous docs-browser win (rev127): common raw HTML blocks now stay inert through one shared block helper, so helpfollow/helplinkpick/outline scans/reference+footnote defs/TUI underlining agree on `<div>`/`<pre>`-style precedence.

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

7. **`PageUp` / `PageDown`.** ✅ DONE (rev61): actions `PageUp`/`PageDown` use option `page.height` (default 30). *(rev185)* the shared editor core now also honors `pageoverlap`, so paging keeps a configurable amount of prior view context visible in both ordinary and softwrapped views. Code: `src/micromax_editor/editor.py`. Tests: `tests/test_editor_tier0_basics.py::test_doc_top_bottom_and_page_moves`, `tests/test_editor_tier0_basics.py::test_page_moves_respect_pageoverlap_and_shift_viewport`, `tests/test_editor_softwrap.py::test_softwrap_page_moves_respect_pageoverlap_by_visual_row`.

8. **`Ctrl-Home` / `Ctrl-End`.** ✅ DONE (rev61): actions `DocTop`/`DocBottom`. Same test as above.

9. **Go-to-line command (`goto` / `Ctrl-L`).** ✅ DONE: command `goto line[:col]` existed; rev61 adds default binding `Ctrl-l` → `command-edit:goto `.

9b. **Prompt typing/editing works.** ✅ DONE (rev63): unbound printable keys insert text; when a prompt is active, they edit the prompt instead of the buffer. Prompt mode bindings override arrows/backspace/delete. Tests: `tests/test_editor_viewport_and_typing.py`.

9d. **Picker prompt UX: selection, paging, copy, and section stability.** ✅ DONE (rev93): in picker-style prompts (buffer/doc/help pickers, palette, etc.), Up/Down moves the highlighted selection without mutating the typed query, PageUp/PageDown jumps selection by a small window (option: `prompt.page`), `Ctrl-y` copies the selected row (for links: copies the target), `Ctrl-Home`/`Ctrl-End` jumps to first/last selection, `Alt-Up`/`Alt-Down` jumps between section headers, and option `prompt.wrap` controls wrap vs clamp at ends. The minimal TUI repeats the active section header as a sticky header when paging through long mixed sections. Tests: `tests/test_editor_prompt_picker_navigation.py`, `tests/test_editor_prompt_picker_navigation_page.py`, `tests/test_editor_prompt_picker_navigation_home_end.py`, `tests/test_editor_prompt_picker_navigation_wrap.py`, `tests/test_editor_prompt_picker_navigation_sections.py`, `tests/test_tui_prompt_display_lines_sticky_header.py`.

9e. **Docs markdown: shortcut reference links.** ✅ DONE (rev94): help/docs pages can use shortcut reference links (`[id]` with a matching `[id]: target`), and the minimal TUI underlines inline/reference/shortcut/autolinks consistently. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_shortcut_reference_link`, `tests/test_tui_md_link_label_spans.py`.

9f. **Docs markdown: heading fragments.** ✅ DONE (rev109): help/docs navigation now follows same-page fragments (`#section`) and cross-doc fragments (`page.md#section`) using best-effort GitHub-style heading slugs, and also recognizes explicit heading ids in common attr-list syntax (`{#id}` / `{: #id }`). Outline rows and heading-breadcrumb labels strip the raw attr-list suffix so picker/search surfaces show rendered titles instead of source syntax. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_same_page_fragment_link`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_cross_doc_fragment_link`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_explicit_heading_id_fragment_link`, `tests/test_editor_helpoutlinepick.py::test_help_outline_rows_lists_headings`.

9g. **Docs markdown: footnotes.** ✅ DONE (rev110): help/docs navigation now recognizes common footnote refs (`[^id]`) and definitions (`[^id]: ...`) and can jump to the matching definition in-place. The same tiny footnote model also flows through `helplinkcopy`, `helplinkpick`, `helpnavpick`, and the minimal TUI's link underline/current-link detection so docs surfaces stay aligned. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_footnote_reference`, `tests/test_editor_helplinkpick.py::test_helplinkpick_includes_footnote_references`, `tests/test_editor_helplinkcopy_and_openurl_confirm.py::test_helplinkcopy_copies_footnote_target_under_cursor`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_cover_footnote_refs_but_not_definitions`.

9h. **Docs markdown: table scanability.** ✅ DONE (rev111): the minimal TUI now recognizes simple GFM-style pipe tables in docs/help buffers and renders header rows bold, delimiter rows dim, and `|` separators dim. This stays deliberately UI-only (`src/micromax_editor/tui.py`) so the headless core still avoids a full markdown parser. Tests: `tests/test_tui_md_tables.py`.

9i. **Docs markdown: task-list scanability.** ✅ DONE (rev112): the minimal TUI now recognizes small GFM-style task-list markers in docs/help buffers (`- [ ]`, `* [x]`, `1. [X]`), bolding checkbox tokens and dimming checked task bodies. This stays deliberately UI-only (`src/micromax_editor/tui.py`) so the headless core still avoids a full markdown block parser. Tests: `tests/test_tui_md_tasklists.py`.

9j. **Docs markdown: thematic-break scanability.** ✅ DONE (rev114): the minimal TUI now recognizes common thematic-break lines in docs/help buffers (`---`, `***`, `___`, and spaced forms like `- - -`), dimming the separator line and bolding the visible marker run. This stays deliberately UI-only (`src/micromax_editor/tui.py`) so the headless core still avoids a full markdown block parser. Tests: `tests/test_tui_md_thematic_breaks.py`.

9k. **Docs markdown: inline emphasis/strong/strike scanability.** ✅ DONE (rev115): the minimal TUI now recognizes small markdown inline emphasis forms in docs/help buffers — `**strong**` bodies render bold, `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline), and `~~strike~~` bodies render dim. This stays deliberately UI-only (`src/micromax_editor/tui.py`) so the headless core still avoids a fuller inline markdown parser. Tests: `tests/test_tui_md_inline_emphasis.py`.

9l. **Docs markdown: inline code equal-length backtick runs + code-span precedence.** ✅ DONE (rev116): the minimal TUI now recognizes inline code spans with equal-length backtick delimiters (so double-backtick forms can contain literal backticks), and masks code spans before docs-link underlining so markdown-looking text inside code does not appear clickable. This stays deliberately UI-only (`src/micromax_editor/tui.py`) so the headless core still avoids a fuller inline markdown parser. Tests: `tests/test_tui_md_inline_code_spans.py`, `tests/test_tui_md_link_label_spans.py`.

9m. **Docs markdown: inline-code precedence reaches editor actions.** ✅ DONE (rev118): `helpfollow` and `helplinkpick` now ignore markdown-looking inline/reference/autolinks that sit inside inline code spans, keeping editor-side docs actions aligned with the tiny TUI's code-first link policy without introducing a fuller markdown parser. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_markdown_looking_links_inside_inline_code`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_markdown_looking_links_inside_inline_code`.

9n. **Docs markdown: escape-aware link discipline.** ✅ DONE (rev119): backslash-escaped markdown openers now stay literal prose across both styling and actions, so `\[link]`, `\![image]`, `\[^footnote]`, and `\<autolink>` no longer leak into `helpfollow`, `helplinkpick`, or TUI docs-link underlining. This remains a small shared-policy fix (`md_backslash_escaped`) rather than a fuller markdown parser. Tests: `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_escaped_markdown_forms`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_escaped_markdown_forms`, `tests/test_editor_help_docs_navigation.py::test_markdown_definition_parsers_ignore_escaped_definitions`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_escaped_markdown_forms`.

9o. **Docs markdown: balanced bracket labels.** ✅ DONE (rev120): the tiny docs/help link model now supports balanced bracket labels like `[Vision [nested]](doc.md)`, `[Vision [nested]][id]`, and `[Vision [nested]]` through a shared scanner used by `helpfollow`, `helplinkpick`, TUI docs-link underlining, and reference-definition parsing. This remains a small shared-parser substrate (`MdLinkMatch`, `md_balanced_span`, `md_link_matches`) rather than a fuller markdown parser. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_nested_bracket_label_links`, `tests/test_editor_help_docs_navigation.py::test_markdown_definition_parser_supports_nested_bracket_ids`, `tests/test_editor_helplinkpick.py::test_helplinkpick_includes_nested_bracket_label_links`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_cover_nested_bracket_labels`.

9p. **Docs markdown: tiny destination escapes + local-doc path decoding.** ✅ DONE (rev121): inline and reference link destinations in docs/help buffers now support balanced parentheses, markdown-safe backslash unescaping, and percent-decoded local doc paths before follow. This keeps local links like `104-paren\(topic\).md`, `103-space\ path.md`, and `103-space%20path.md` navigable through `helpfollow`, `helplinkpick`, TUI docs-link underlining, and the shared tiny docs-link scanner without committing Micromax to a fuller markdown destination/title parser. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_inline_link_with_escaped_space_destination`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_inline_link_with_percent_encoded_destination`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_inline_link_with_escaped_paren_destination`, `tests/test_editor_help_docs_navigation.py::test_markdown_definition_parser_unescapes_tiny_destinations`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_reference_link_with_unescaped_destination`, `tests/test_editor_helplinkpick.py::test_helplinkpick_includes_destination_escape_examples`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_cover_destination_escape_examples`.

9q. **Docs markdown: fenced-code precedence across styling + actions.** ✅ DONE (rev122): fenced code blocks in help/docs buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, TUI docs-link underlining, and markdown reference-definition parsing, so literal markdown examples inside triple-backtick/tilde fences no longer leak into the live docs browser. This remains a tiny shared-helper policy (`md_fenced_code_line_flags`) rather than a fuller markdown block parser. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_markdown_looking_links_inside_fenced_code_blocks`, `tests/test_editor_help_docs_navigation.py::test_markdown_definition_parsers_ignore_fenced_code_blocks`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_markdown_looking_links_inside_fenced_code_blocks`, `tests/test_tui_md_link_label_spans.py::test_md_fenced_code_line_flags_mark_fenced_blocks`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_do_not_resolve_reference_defs_inside_fenced_blocks`.

9r. **Docs markdown: tiny setext headings.** ✅ DONE (rev123): single-line setext headings (`Title` + `===` / `---`) now participate in help/docs fragment jumps, outline rows, heading breadcrumbs, and docs-picker titles, reusing the same heading-title cleanup / explicit attr-list id handling as ATX headings. This remains a small shared heading scanner (`_md_heading_entries`) and stays fenced-code-aware rather than becoming a fuller markdown block parser. Tests: `tests/test_editor_help_docs_buffers.py::test_doc_prompt_rows_and_helppick_command`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_setext_fragment_links`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_explicit_setext_heading_id_fragment_link`, `tests/test_editor_helpoutlinepick.py::test_help_outline_rows_include_setext_headings`, `tests/test_editor_helplink_section_rows_heading_option.py::test_helplink_sections_can_group_by_setext_heading`.

9s. **Docs markdown: raw HTML comment precedence.** ✅ DONE (rev124): raw HTML comments in help/docs buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, outline scanning, TUI docs-link underlining, and markdown reference/footnote-definition parsing, so commented-out markdown examples stay literal instead of leaking into the live docs browser. This remains a small shared-comment policy (`md_html_comment_spans`, `md_html_comment_line_spans`) rather than a fuller raw-HTML or Markdown-in-HTML parser. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_markdown_looking_links_inside_html_comments`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_comment_defined_refs_and_footnotes`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_html_comment_links_and_defs`, `tests/test_editor_helpoutlinepick.py::test_help_outline_rows_ignore_headings_inside_html_comments`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_html_comments_but_keep_visible_links`.

9t. **Docs markdown: raw HTML/autolink precedence inside link labels.** ✅ DONE (rev125): the tiny docs/help link model now treats inline raw HTML tags and autolinks as tighter than markdown link grouping when they begin inside a would-be link label, so CommonMark-shaped cases like `[fake <span title="](doc.md)">`, `[fake <span title="][id]">`, and `[fake <https://example.invalid/?x=](doc.md)>` stay literal prose instead of becoming regex-shaped false positives. This remains a small shared-helper policy (`md_inline_html_tag_spans` + `md_link_matches`) reused by `helpfollow`, `helplinkpick`, and TUI docs-link underlining rather than a fuller HTML parser. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_raw_html_tag_and_autolink_precedence_inside_labels`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_raw_html_tag_and_autolink_precedence_inside_labels`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_raw_html_tag_and_autolink_precedence_inside_labels`.

9u. **Docs markdown: common raw HTML blocks.** ✅ DONE (rev127): help/docs navigation now treats common raw HTML blocks as inert prose across `helpfollow`, `helplinkpick`, outline scanning, markdown reference/footnote-definition parsing, and TUI docs-link underlining, covering both blank-line-terminated block-tag forms like `<div>...</div>` and `<pre>`/`<script>`/`<style>`/`<textarea>`-style blocks that stay inert across internal blank lines. This remains a small shared block helper (`md_html_block_line_flags`) rather than a fuller HTML parser or Markdown-in-HTML model. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_markdown_looking_links_inside_raw_html_blocks`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_raw_html_block_links_and_defs`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_raw_html_blocks_and_hidden_defs`.

9w. **Docs markdown: tiny wrapped reference definitions.** ✅ DONE (rev129): help/docs reference definitions now also recognize small CommonMark-style wrapped forms where the destination sits on the next line and the optional title may wrap once as well, while still reusing the same shared destination parser as inline links/follow actions instead of growing a second multiline regex path. Tests: `tests/test_editor_help_docs_navigation.py::test_markdown_definition_parser_supports_tiny_multiline_reference_definitions`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_multiline_reference_definitions`, `tests/test_editor_helplinkpick.py::test_helplinkpick_includes_tiny_multiline_reference_examples`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_cover_tiny_multiline_reference_definitions`.

9x. **Docs markdown: spaces-only 0–3 indent guards.** ✅ DONE (rev130): docs/help reference definitions, footnote definitions, and ATX heading scanning now consistently follow the small CommonMark-style “up to three leading spaces” rule, so four-space and tab-indented code-ish lookalikes stay prose instead of becoming live docs structure. Tests: `tests/test_editor_help_docs_navigation.py::test_markdown_definition_parser_ignores_code_indented_reference_definitions`, `tests/test_editor_help_docs_navigation.py::test_markdown_footnote_parser_ignores_code_indented_definitions`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_code_indented_reference_and_footnote_definitions`, `tests/test_editor_helpoutlinepick.py::test_help_outline_rows_ignore_code_indented_heading_lookalikes`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_code_indented_defs_and_footnotes`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_code_indented_reference_and_footnote_defs`.

9y. **Docs markdown: tiny wrapped inline links.** ✅ DONE (rev131): help/docs inline links now also recognize small CommonMark-style wrapped forms where the destination sits on the next line and the optional title/closing `)` may wrap once as well, while reusing the same shared destination parser and one shared continuation-line helper across `helpfollow`, `helplinkpick`, and TUI docs-link underlining instead of growing another multiline regex path. Tests: `tests/test_editor_help_docs_navigation.py::test_md_inline_link_target_multiline_supports_tiny_wrapped_inline_forms`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_tiny_wrapped_inline_links`, `tests/test_editor_helplinkpick.py::test_helplinkpick_includes_tiny_wrapped_inline_examples`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_cover_tiny_wrapped_inline_links`.

9z. **Docs markdown: wrapped angle-bracket destinations + separator guard.** ✅ DONE (rev132): help/docs inline links and wrapped reference definitions now also cover tiny CommonMark-style wrapped angle-bracket destinations like `[doc](
  <space path.md>)` / `[id]:
  <space path.md>`, while the shared destination parser now also rejects malformed optional titles that begin immediately after a closing `>` without the whitespace CommonMark requires. This stays shared-policy-first (`_md_link_target_prefix` + `_md_link_rest_has_required_separator`) across `helpfollow`, `helplinkpick`, reference-definition parsing, and TUI docs-link underlining rather than growing a special-case multiline regex. Tests: `tests/test_editor_help_docs_navigation.py::test_md_reference_def_target_supports_tiny_multiline_reference_forms`, `tests/test_editor_help_docs_navigation.py::test_md_inline_link_target_multiline_supports_tiny_wrapped_inline_forms`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_can_follow_tiny_wrapped_inline_links`, `tests/test_editor_helplinkpick.py::test_helplinkpick_includes_tiny_wrapped_inline_examples`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_cover_tiny_wrapped_inline_links`.

9za. **Docs markdown: nested links inside labels should prefer the inner valid link.** ✅ DONE (rev133): help/docs navigation now refuses outer markdown links whose label text contains a valid inner link, so CommonMark-shaped cases like `[outer [inner](doc)](other)` and `[outer [inner][ref]](other)` keep the outer prose literal while still exposing the valid inner link. This stays shared-policy-first by reusing the same docs-link matcher recursively on the label body instead of growing a separate nested-link regex path. Tests: `tests/test_editor_help_docs_navigation.py::test_md_link_matches_reject_outer_links_that_contain_valid_inner_links`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_prefers_valid_inner_link_when_outer_label_contains_link`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_prefers_valid_inner_reference_link_when_outer_label_contains_link`, `tests/test_editor_helplinkpick.py::test_helplinkpick_prefers_valid_inner_links_over_outer_nested_links`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_prefer_valid_inner_links_over_outer_nested_links`.

9zb. **Docs markdown: empty/whitespace-only labels stay prose.** ✅ DONE (rev134): help/docs navigation now rejects markdown labels that do not contain at least one non-whitespace character, so malformed inline/reference/shortcut forms like `[](doc.md)`, `[ ](doc.md)`, `[   ][id]`, and `[]` stay literal prose instead of turning into invisible or blank docs links. This stays shared-policy-first via one small `md_link_label_has_text()` helper reused by the docs-link matcher and reference-definition parsing rather than growing surface-specific regex guards. Tests: `tests/test_editor_help_docs_navigation.py::test_md_link_matches_reject_empty_and_whitespace_only_labels`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_empty_and_whitespace_only_labels`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_empty_and_whitespace_only_labels`.

9v. **Docs markdown: conservative generic type-7-ish HTML blocks.** ✅ DONE (rev128): the same shared raw-HTML block helper now also treats complete generic tag-only lines like `<widget-box ...>` / `</widget-box>` as inert prose through the next blank line when they begin after a blank line (or at doc start), while deliberately refusing to let those blocks interrupt paragraphs. Tests: `tests/test_editor_help_docs_navigation.py::test_helpfollow_ignores_markdown_looking_links_inside_generic_html_blocks`, `tests/test_editor_help_docs_navigation.py::test_helpfollow_generic_html_blocks_do_not_interrupt_paragraphs`, `tests/test_editor_helplinkpick.py::test_helplinkpick_ignores_generic_html_block_links_and_defs`, `tests/test_tui_md_link_label_spans.py::test_md_link_label_spans_ignore_generic_html_blocks_but_not_paragraph_adjacent_tags`.

9c. **Jumplist picker (`jumppick`).** ✅ DONE (rev64): searchable prompt over the current buffer's navigation history. Code: `src/micromax_editor/editor.py`, `src/micromax_editor/command_dispatcher.py`. Docs: `docs/63-editor-jumplist.md`. Tests: `tests/test_editor_jumppick.py`.
    - *(rev135)* `jumppick` rows are now grouped into `Current` / `Back` / `Forward`, the minimal TUI shows those section headers, `Alt-Up` / `Alt-Down` reuses the same labels, and future UIs/scripts can read the grouped shape directly through `ed.jump-section-rows`. `markpick` gained the parallel `ed.mark-section-rows` surface and now groups rows by owning buffer.

9c1. **Open-target cursor parsing (`parsecursor`).** ✅ DONE (rev191, relanded in rev192): the shared editor core now honors a tiny `parsecursor` option so `open` targets like `file:line[:col]` can position the primary cursor immediately without inventing a larger session/open-command subsystem. Explicit open targets override `savecursor`, line numbers stay 1-based while columns stay 0-based, and the same behavior is preserved through interactive open, capability-gated/scripted open, persistence-aware reopen, and path-style command-palette opens.
   - Option: `parsecursor` (`src/micromax_editor/editor.py::_install_default_options`)
   - Helpers: `src/micromax_editor/editor.py::{_parse_open_target,_set_buffer_primary_cursor,open_file}`
   - Capability-gated/scripted paths: `src/micromax_editor/{command_dispatcher.py,micromax_bridge.py}`
   - Docs: `docs/132-parsecursor.md`
   - Tests: `tests/test_editor_fs_open_save.py`, `tests/test_editor_persistence_cap_persist.py`, `tests/test_editor_script_context_fs_caps.py`

10. **Line wrapping awareness in Up/Down.** 💤 DEFER: needs a UI-provided viewport width + “visual line” model (or a future layout engine). This should be designed alongside the first TUI renderer.

10a. **Softwrap `wordwrap`.** ✅ DONE (rev198): the shared editor core now honors a tiny `wordwrap` option so softwrapped rows can prefer breaking at spaces while keeping `view_rows`, cursor mapping, visual-row Home/End, and visual-row motion in one shared wrap model instead of growing a second renderer-only policy.
   - Option: `wordwrap` (`src/micromax_editor/editor.py::_install_default_options`)
   - Shared helpers: `src/micromax_editor/editor.py::{_find_wordwrap_break,_wrap_row_starts_for_line_with_cont,view_rows,cursor_view_pos}`
   - Docs: `docs/139-wordwrap.md` + `docs/94-softwrap.md`
   - Tests: `tests/test_editor_softwrap.py`

## Tier 6 — TUI (the actual rendering layer)

47. **Pick a terminal library.** ✅ DONE (rev148): stay on Python `curses` for the current TUI; document `prompt_toolkit` as a later optional backend only if Micromax genuinely needs a richer layout/widget layer than the shared headless substrate wants. Docs: `docs/111-terminal-library-decision.md`.

48. **Minimal TUI loop.** ✅ DONE (rev63): `micromax-editor --tui` runs a tiny curses loop (input → `ed.dispatch_key` → render). Requirements:
- translate terminal keys → the same key strings used in `plugins/core/init.mx`
- render buffer lines + statusline + command bar
- support a fixed viewport height/width (no softwrap yet)

   - *(rev95)* Picker suggestion rows now highlight query-token substring matches

   - *(rev104)* The curses TUI enables bracketed paste mode (CSI ? 2004) and inserts bracketed pastes as a single chunk (plus a micro-esque `paste` option to aggregate non-bracketed paste bursts). (UI-only polish that makes long pickers feel much closer to fzf/micro).

49. **Color/style model.** 💤 DEFER until syntax highlighting exists; but define the *shape* early: per-line spans with style tags.

50. **Scrolling / viewport management.** ✅ DONE (rev63): headless viewport stored on Editor; exposed via `ed.viewport` / `ed.viewport!` and status model fields. Tests: `tests/test_editor_viewport_and_typing.py`.
   - *(rev175)* the shared viewport contract now also honors a tiny `scrollmargin` option, so ordinary and softwrapped views keep a small band of vertical context rows around the primary cursor without relegating that policy to the curses TUI.

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


19. **Line numbers gutter.** ✅ DONE (rev171): the minimal curses TUI now has an optional micro-esque `ruler` / `relativeruler` gutter. Wrapped continuation rows keep a blank gutter cell, the viewport width/cursor offset account for the gutter honestly, and the feature stays option-driven rather than baking numbers into headless buffer state.
   - Options: `ruler`, `relativeruler` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helpers: `src/micromax_editor/tui.py::{line_number_gutter_width,line_number_gutter_text}`
   - Docs: `docs/112-line-numbers.md`
   - Tests: `tests/test_tui_ruler.py`

19b. **Search-highlight rendering (`hlsearch`).** ✅ DONE (rev172): the minimal curses TUI now honors the existing `hlsearch` option, reverse-highlighting visible matches for the current search pattern and bolding the visible current match under the primary cursor. The first pass intentionally stays renderer-local and fragment-local under softwrap/scrolling instead of promoting persistent search-highlight spans into the headless editor model.
   - Option: `hlsearch` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helper: `src/micromax_editor/tui.py::search_match_spans`
   - Docs: `docs/113-search-highlighting.md`
   - Tests: `tests/test_tui_hlsearch.py`

19c. **Search-position summary (`i/n`).** ✅ DONE (rev173): the editor now exposes a tiny shared whole-buffer search-position model through `status_model()` / `ed.status`, and the minimal curses TUI reuses that same summary in the live find prompt as `[current/total]` instead of leaving search awareness trapped inside `hlsearch` row styling.
   - Editor helper: `src/micromax_editor/editor.py::search_position_model`
   - Search helper: `src/micromax_editor/search.py::search_position`
   - Docs: `docs/114-search-position-summary.md`
   - Tests: `tests/test_editor_statusline.py`, `tests/test_tui_hlsearch.py`

19d. **Current-row cue (`cursorline`).** ✅ DONE (rev176): the minimal curses TUI now honors a tiny `cursorline` option by underlining the current visible buffer row. The first pass intentionally stays renderer-local and row-local: under `softwrap` it highlights the active wrapped screen row instead of inventing a headless whole-line highlight model.
   - Option: `cursorline` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helper: `src/micromax_editor/tui.py::cursorline_row_attr`
   - Docs: `docs/117-cursorline.md`
   - Tests: `tests/test_tui_cursorline.py`

19e. **Trailing-whitespace cue (`hltrailingws`).** ✅ DONE (rev177): the minimal curses TUI now honors a tiny `hltrailingws` option by reverse-dimming visible trailing spaces/tabs. The first pass intentionally stays renderer-local and fragment-local: only the intersection with the current visible fragment is highlighted, so softwrap and horizontal scroll stay honest without inventing headless warning spans or edit-freshness tracking.
   - Option: `hltrailingws` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helper: `src/micromax_editor/tui.py::trailing_whitespace_spans`
   - Docs: `docs/118-hltrailingws.md`
   - Tests: `tests/test_tui_hltrailingws.py`

19f. **Tab-error cue (`hltaberrors`).** ✅ DONE (rev178): the minimal curses TUI now honors a tiny `hltaberrors` option by reverse-dimming visible indentation-mismatch characters using the existing `tabstospaces` policy. The first pass intentionally stays renderer-local and fragment-local: tabs are marked when spaces are expected, leading spaces in the initial indent run are marked when tabs are expected, and only the visible fragment intersection is highlighted so softwrap and horizontal scroll stay honest without inventing headless diagnostics.
   - Option: `hltaberrors` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helper: `src/micromax_editor/tui.py::tab_error_spans`
   - Docs: `docs/119-hltaberrors.md`
   - Tests: `tests/test_tui_hltaberrors.py`

19g. **Guide-column cue (`colorcolumn`).** ✅ DONE (rev179): the minimal curses TUI now honors a tiny `colorcolumn` option by reverse-dimming one visible guide column. The first pass intentionally stays renderer-local: in ordinary horizontally scrolled views it tracks the configured document column honestly, while under `softwrap` it repeats as a screen-column cue on each wrapped visual row instead of inventing a deeper logical-column overlay model.
   - Option: `colorcolumn` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helper: `src/micromax_editor/tui.py::colorcolumn_screen_x`
   - Docs: `docs/120-colorcolumn.md`
   - Tests: `tests/test_tui_colorcolumn.py`

19h. **Scrollbar cue (`scrollbar`).** ✅ DONE (rev180): the minimal curses TUI now honors a tiny `scrollbar` option by reserving one right-edge column for a proportional thumb when the document is taller than the viewport. The first pass intentionally stays renderer-local: ordinary views size the thumb from logical lines, while `softwrap` sizes it from visual rows instead of inventing shared scrollbar state in the headless editor model.
   - Option: `scrollbar` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helpers: `src/micromax_editor/tui.py::{scrollbar_gutter_width,scrollbar_thumb_span}`
   - Docs: `docs/121-scrollbar.md`
   - Tests: `tests/test_tui_scrollbar.py`

19i. **Scrollbar thumb character (`scrollbarchar`).** ✅ DONE (rev181): the minimal curses TUI now honors a tiny `scrollbarchar` option so the existing one-column scrollbar thumb can render a user-chosen glyph. The first pass intentionally keeps the same renderer-local contract: empty values fall back to `|`, longer strings use only their first visible character, and the rest of the thumb sizing/placement logic stays unchanged.
   - Option: `scrollbarchar` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helper: `src/micromax_editor/tui.py::scrollbar_thumb_char`
   - Docs: `docs/122-scrollbarchar.md`
   - Tests: `tests/test_tui_scrollbar.py`

20. **Tab width / tabs-to-spaces.** ✅ DONE (rev65): editor options `tabsize` + `tabstospaces` + visual-column-aware `InsertTab`.
   - Options: `src/micromax_editor/editor.py::_install_default_options`
   - Action: `src/micromax_editor/editor.py::a_insert_tab`
   - Tests: `tests/test_editor_autoindent_tabs.py::test_insert_tab_respects_tabstospaces_and_tabsize`

20b. **Leading-indent cursor stepping (`tabmovement`).** ✅ DONE (rev194): the shared editor core now honors a tiny `tabmovement` option so `CursorLeft` / `CursorRight` and `SelectLeft` / `SelectRight` can treat leading runs of exactly `tabsize` spaces like one tab stop when `tabstospaces` is enabled, mirroring micro's conservative indent-only rule without inventing a richer visual-column subsystem.
   - Option: `tabmovement` (`src/micromax_editor/editor.py::_install_default_options`)
   - Shared helper/actions: `src/micromax_editor/editor.py::{_tabmovement_step,a_left,a_right,a_select_left,a_select_right}`
   - Docs: `docs/135-tabmovement.md`
   - Tests: `tests/test_editor_autoindent_tabs.py`

21. **Auto-indent on newline.** ✅ DONE (rev65, expanded in rev195): `InsertNewline` preserves current-line indentation without doubling when splitting inside the indent prefix, and the shared editor core now exposes that behavior through a tiny ordinary `autoindent` option so Enter can also insert a plain newline when desired.
   - Option/action: `src/micromax_editor/editor.py::{_install_default_options,a_insert_newline}`
   - Docs: `docs/136-autoindent.md`
   - Tests: `tests/test_editor_autoindent_tabs.py`

21c. **Protected-buffer option (`readonly`).** ✅ DONE (rev193): the editor's existing protected-buffer path is now available through a tiny ordinary `readonly` option, so `setlocal readonly true` can block mutating actions and saves in ordinary buffers while help/docs buffers keep reusing that same shared policy. The first pass intentionally stays option-shaped instead of inventing a new “protect buffer” command or mode.
   - Option: `readonly` (`src/micromax_editor/editor.py::_install_default_options`)
   - Shared checks: `src/micromax_editor/editor.py::{save,is_protected_buffer,status_model,run_action}`, `src/micromax_editor/micromax_bridge.py::hc_ed_save`
   - Docs: `docs/134-readonly.md`
   - Tests: `tests/test_editor_readonly_option.py`

21b. **Whitespace-only autoindent cleanup (`keepautoindent`).** ✅ DONE (rev192): the shared editor core now honors a tiny `keepautoindent` option so pressing Enter again on a whitespace-only autoindented line clears the previous line's auto-added indent by default, while `set keepautoindent true` keeps it. The first pass intentionally stays in the same `InsertNewline` action instead of inventing a richer per-line provenance model.
   - Option: `keepautoindent` (`src/micromax_editor/editor.py::_install_default_options`)
   - Action: `src/micromax_editor/editor.py::a_insert_newline`
   - Docs: `docs/133-keepautoindent.md`
   - Tests: `tests/test_editor_autoindent_tabs.py`

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


25b. **Shared buffer-position summary (`bufpos`).** ✅ DONE (rev184): the editor now exposes a tiny current-buffer position model through `status_model()` / `ed.status` as `buffer_index`, `buffer_count`, and `buffer_summary`, and the reference statusline formatter supports `$(bufpos)` / `$(bufferpos)` / `$(buffers)` so ordinary TUI/statusline rendering can surface multi-buffer context without reconstructing buffer ordering by hand.
   - Editor helper: `src/micromax_editor/editor.py::status_model`
   - Formatter: `src/micromax_editor/statusformat.py`
   - Docs: `docs/125-statusline-bufferpos.md`
   - Tests: `tests/test_editor_statusline.py`, `tests/test_statusline_strings.py`

26. **Buffer management UX bindings.** ✅ DONE (rev85): core plugin binds `Ctrl-b` → `bufferpick` and `Ctrl-o` → `open` (prefilled). Tests: `tests/test_editor_default_keybindings_core.py`.
    - *(rev136)* grouped buffer rows are now exposed headlessly through `ed.buffer-section-rows`, so future UIs/LLMs do not need to reconstruct `Help` / `Scratch` / project-root buckets from flat row text.

26b. **Recent files list + picker.** ✅ DONE (rev75): MRU list + picker, optional persistence (`recent.persist`/`recent.file`), grouped section rows (`ed.recent-section-rows` / `ed.recent-dir-section-rows`), and a `Recent Files` bucket inside `commandpick`. Tests: `tests/test_editor_buffer_lifecycle_recent.py`, `tests/test_editor_buffer_mru_and_closeall.py`.
    - *(rev139)* `recentpick` now flattens the same project-root grouping exposed by `ed.recent-section-rows`, so the minimal TUI shows contiguous project sections/sticky headers, `Alt-Up` / `Alt-Down` jumps between those project groups, and prompt preview/status surfaces inherit the same labels instead of repeated section flicker in a flat MRU stream.
    - *(rev140)* picker-style prompts now also expose a shared current-item position model (`prompt_current_position`, `prompt_position_summary`, `ed.prompt-current-position`), and the minimal TUI prompt line now shows that same compact `index/count • section i/n` summary next to the existing preview so users/scripts do not need to reconstruct “where am I?” separately per surface.

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

42. **Portability test suite.** ✅ DONE (rev108): added a tiny JSON-based starter corpus (`portability/kernel_cases.json`) plus shared runner (`src/micromax/portability_suite.py`) and CLI (`tools/mxportable.py`) so future hosts can validate portable kernel/stdlib behavior without importing the whole pytest suite. Tests: `tests/test_portability_suite.py`. Docs: `docs/102-portability-suite.md`.

43. **Minimal Rust VM spike.** 🧱 TODO.

44. **Binary bytecode format.** 💤 DEFER.

45. **Hostcall ABI for WASM.** 💤 DEFER.

46. **TiddlyWiki integration spike.** 💡 IDEA.

## Tier 7 — Nice-to-haves and polish

51. **`ed.config` / RC file loading.** ✅ DONE (rev64): editor loads `~/.config/micromax/init.mx` (override: `$MICROMAX_INIT`) at startup after plugins. Docs: `docs/87-editor-config.md`. Tests: `tests/test_editor_user_init.py`.

52. **Comment toggling.** 💤 DEFER (filetype-aware).

53. **Bracket matching / pair highlighting.** ✅ DONE (rev182, expanded rev204): the minimal curses TUI now honors tiny micro-esque `matchbrace` / `matchbraceleft` options, and now also a tiny `matchbracestyle` choice, so visible brace pairs under or just left of the primary cursor can be rendered either bold+underlined or bold+reversed. The feature still intentionally stays renderer-local and syntax-agnostic: only classic `()[]{}` pairs are considered, matching is purely textual/nest-aware across the whole buffer, and only the visible brace cells are styled in ordinary and docs/help buffers rather than promoting persistent brace spans or theme state into headless editor state.
   - Options: `matchbrace`, `matchbraceleft`, `matchbracestyle` (`src/micromax_editor/editor.py::_install_default_options`)
   - TUI helpers: `src/micromax_editor/tui.py::{matching_brace_positions,brace_match_spans,brace_match_attr}`
   - Docs: `docs/123-matchbrace.md`, `docs/145-matchbracestyle.md`
   - Tests: `tests/test_tui_matchbrace.py`

54. **Trailing whitespace visualization / cleanup.** ✅ DONE (rev177 + rev186): the minimal curses TUI already provides a tiny `hltrailingws` cue, and the shared editor core now also honors a tiny `rmtrailingws` option so manual saves trim trailing spaces/tabs from buffer lines before writing to disk. The first cleanup pass intentionally stays small and shared-core: it updates the in-memory buffer before writing, clamps cursors/anchors honestly, and records an undoable cleanup snapshot instead of inventing a separate strip command or TUI-only save hook.
   - Option: `rmtrailingws` (`src/micromax_editor/editor.py::_install_default_options`)
   - Save path: `src/micromax_editor/editor.py::save`
   - Docs: `docs/127-rmtrailingws.md`
   - Tests: `tests/test_editor_fs_open_save.py`, `tests/test_portability_suite.py`

54b. **Final newline on save (`eofnewline`).** ✅ DONE (rev187): the shared editor core now also honors a tiny `eofnewline` option so manual saves can ensure a non-empty buffer ends with one final `\n`. The first pass deliberately reuses the same honest save-normalization path as `rmtrailingws`: the live buffer is updated before write, the change is undoable, empty buffers stay empty, and `rmtrailingws` + `eofnewline` compose into one normalization step instead of stacking hidden edits.
   - Option: `eofnewline` (`src/micromax_editor/editor.py::_install_default_options`)
   - Save path: `src/micromax_editor/editor.py::save`
   - Docs: `docs/128-eofnewline.md`
   - Tests: `tests/test_editor_fs_open_save.py`, `tests/test_portability_suite.py`

54c. **Create parent directories on save (`mkparents`).** ✅ DONE (rev188): the shared editor core now also honors a tiny `mkparents` option so manual saves can create missing parent directories already implied by the buffer path before writing. The first pass deliberately stays in the same honest shared save path as `rmtrailingws` / `eofnewline`: no path rewriting, no backup subsystem, just best-effort `mkdir -p` behavior when explicitly enabled.
   - Option: `mkparents` (`src/micromax_editor/editor.py::_install_default_options`)
   - Save path: `src/micromax_editor/editor.py::save`
   - Docs: `docs/129-mkparents.md`
   - Tests: `tests/test_editor_fs_open_save.py`, `tests/test_portability_suite.py`

54d. **Remember cursor position per file (`savecursor`).** ✅ DONE (rev189): the shared editor core now honors a tiny `savecursor` option so reopening a file can restore its last remembered primary cursor position through the existing persistence boundary. The first pass intentionally stays small and inspectable: best-effort JSON storage, primary cursor only, honest clamping when files changed, and load/save wiring shared by the headless REPL and curses TUI instead of a larger session subsystem.
   - Options: `savecursor`, `savecursor.file` (`src/micromax_editor/editor.py::_install_default_options`)
   - Persistence helpers: `src/micromax_editor/editor.py::{load_saved_cursors,save_saved_cursors,_remember_cursor_for_buffer,_restore_cursor_for_buffer}`
   - Startup wiring: `src/micromax_editor/__main__.py`, `src/micromax_editor/tui.py`
   - Docs: `docs/130-savecursor.md`, `docs/87-editor-config.md`, `docs/32-capabilities.md`
   - Tests: `tests/test_editor_persistence_cap_persist.py`

55. **`ed.exec` hostcall (run shell command).** 💤 DEFER: capability-gated; useful but security-sensitive.

56. **Scrollbar model for the TUI.** ✅ DONE (rev180 + rev181): the minimal curses TUI now supports a tiny right-edge `scrollbar` thumb plus micro-esque `scrollbarchar` glyph customization while keeping the whole feature renderer-local rather than promoting scrollbar state into the shared headless editor model.

57. **Mouse-drag selection.** 💤 DEFER.

58. **Multi-buffer tab bar or buffer list in statusline.** 💤 DEFER.

59. **Help system loaded from docs.** ✅ DONE (rev76): `help TOPIC` falls back to opening a matching `docs/*.md` page into a protected read-only buffer; includes a docs picker (`helppick`).
    - *(rev138)* `helppick` rows are now grouped into stable numbered doc families (`00–09 Project`, `10–19 Research`, `20–29 Language + VM`, etc.), that grouped shape is exposed headlessly through `ed.doc-section-rows`, and prompt preview/status now reuse those same labels while doc previews lead with the human title instead of the slug topic.

    - *(rev77)* Added docs navigation helpers: `helpfollow` (follow markdown link under cursor) and `helpback` (return to previous docs page).
    - *(rev84)* Added a combined page navigator picker: `helpnavpick` merges headings + links.

60. **Plugin manager.** 💤 DEFER: late-stage; design `plugin.json` schema first.

61. **Open URL under cursor.** ✅ DONE (rev89): added `urlopen` / `urlcopy` commands and default `Alt-o`/`Alt-y` bindings to open/copy URLs under cursor, capability-gated by `cap.open-url` and confirmed by default via `open-url.confirm`.
   - Code: `src/micromax_editor/editor.py` (`url_under_cursor`, `open_url_under_cursor`, `copy_url_under_cursor`)
   - Commands: `src/micromax_editor/command_dispatcher.py` (`urlopen`, `openurl`, `urlcopy`)
   - Keybinds: `plugins/core/init.mx`
   - Tests: `tests/test_editor_url_under_cursor.py`
