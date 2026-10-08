# TODO (rev204)
If you want the **current priorities**, start here.

The detailed, tiered list lives in: `docs/43-worklist.md`.



## Next up (high leverage)

1. **Recent UX polish**: keep iterating on picker/TUI readability (colors, preview affordances, and maybe a few more section types where grouping helps; prompt/status/TUI surfaces now also share a compact current-item position model (`prompt_current_position`, `prompt_position_summary`, `ed.prompt-current-position`), a shared visible-window model (`prompt_window_model`, `ed.prompt-window`), and a shared rendered prompt-row/display model (`prompt_display_model`, `ed.prompt-display`) for sticky headers / more markers / visible row text. Rev171 landed an optional tiny `ruler` / `relativeruler` gutter, rev172 made the existing `hlsearch` option visible in the curses TUI, rev175 adds a shared `scrollmargin` viewport rule, rev176 adds a tiny `cursorline` current-row cue, rev177 adds a tiny `hltrailingws` scanability cue, rev178 adds a tiny `hltaberrors` indentation-mismatch cue, rev179 adds a tiny `colorcolumn` guide-column cue, rev180 adds a tiny `scrollbar` thumb, rev181 adds micro-esque `scrollbarchar` customization for that thumb, rev182 adds a tiny `matchbrace` / `matchbraceleft` visible-pair cue, rev183 adds tiny left/right overflow markers for horizontally clipped rows, rev184 adds a tiny shared current-buffer position/statusline cue (`buffer_summary`, `$(bufpos)`), rev185 adds a shared `pageoverlap` paging/viewport rule, rev190 adds a tiny shared `smartpaste` paste-indentation rule, rev193 turns the editor's existing protected-buffer path into an ordinary `readonly` option, rev194 adds a tiny shared `tabmovement` rule for leading-space indentation, and rev198 adds shared softwrap `wordwrap` row-breaking, rev204 adds `matchbracestyle` for the existing brace cue, so the next wins are likely similarly small shared-context or edit-loop affordances rather than brand-new picker structure).
2. **Docs browser polish**: keep adding small markdown affordances (fragments + footnotes + table-ish scanability + tiny task-list scanability + tiny blockquote scanability + tiny thematic-break scanability + tiny inline emphasis/strong/strike scanability + visible delimiter cues + code-span precedence across both TUI and editor actions now work; fenced code blocks are now inert for docs-link actions/underlining too; escaped markdown openers stay literal prose. Tiny destination parsing is a bit less toy-like now as well: balanced parens, markdown-safe backslash escapes, percent-decoded local doc paths, and now wrapped angle-bracket destinations work in inline/reference links. Raw-HTML comments, raw-HTML/autolink precedence inside would-be link labels, common raw-HTML blocks, conservative generic type-7-ish tag-only blocks, and now the shared nested-link rule for outer-label prose and the non-whitespace label guard for empty/space-only labels all stay aligned too. Tiny multi-line setext handling and tiny multi-line reference definitions now work as well, and blank-separated top-level indented code-ish runs now stay inert for inline link follow/pickers/TUI underlining too while rendering dim in the live docs buffer. Raw HTML comments and raw HTML block lines now also dim in the live docs/help TUI so those already-inert regions finally look a little less like ordinary prose; visible inline/reference image tokens now dim too so already-inert `![alt](dest)` / `![alt][id]` source stops reading like ordinary prose; visible ordinary markdown links now also dim their source scaffolding (`[` / `](` / destination or reference tail / `]`) while the live label stays underlined; visible inline raw HTML tags like `<kbd>` / `<ins>` / `<a name=...>` now dim too while supported autolinks keep their separate bold whole-token cue. Next likely wins are probably a few remaining nested-link-ish/editor-facing edge cases only if they show up in real docs, otherwise picker/TUI polish can steal priority).
3. **Portability discipline**: keep expanding the portable corpus / cross-host validation story as the VM surface grows (recently improved again in rev172 with coverage for `s<` and bare-VM `host.features`, after rev171's typed predicates/`m?`/`get-current`/`dict-version`/`host.api-version` pass, rev170's `0=`/successful-`catch`/map-items/session-local/set-current pass, rev169's lighter-weight inventory mode, and rev168's broader tagging/coverage and machine-readable `--json` output).
4. **Safety boundaries**: keep expanding capability-gated surfaces (jobs, filesystem, UI integration), keeping defaults safe.

## Recently completed


- **Tiny `matchbracestyle` renderer choice + map-overwrite portability follow-up:** the minimal curses TUI now honors a tiny micro-esque `matchbracestyle` option so the existing visible brace cue can use either bold+underline or bold+reverse highlighting without promoting theme/style state into the headless editor model; the portability corpus now also covers overwriting an existing map key updating its value ✅ (rev204).

- **Tiny `showchars` TUI pass + missing-map-predicate portability follow-up:** the minimal curses TUI now honors a tiny micro-esque `showchars` option so ordinary and help/docs buffers can display visible one-cell replacements for spaces/tabs (including `ispace` / `itab` overrides in the leading indent run) without mutating buffer text or promoting invisible-character spans into the headless editor model; the portability corpus now also covers `m?` returning `0` for a missing key ✅ (rev203).

- **Shared `fastdirty` modified-state policy + portability follow-up:** the shared editor core now treats `fastdirty` as a real ordinary option, so buffers can either keep the cheap “edited once means dirty” rule or accurately clear `dirty` again when the text returns to the last clean baseline; command-bar / Micromax option paths resync existing buffers immediately, and the portability corpus now also covers merging into an empty destination map adopting the source pairs ✅ (rev202).

- **Shared `autosave` timed save path + portability follow-up:** the shared editor core now treats `autosave` as a real ordinary option, so dirty path-backed buffers can save through the same headless save path after N seconds, `quit` can reuse that same autosave path for eligible dirty buffers, and the portability corpus now also covers merging an empty source map preserving destination pairs ✅ (rev201).

- **`basename` status/display option + portability follow-up:** the shared editor core now treats the visible filename as real editor state instead of a hardcoded basename, so `status_model()` carries both raw `file_name` and effective `display_name`, `$(filename)` / `showstatus` honor a tiny `basename` option, and the portability corpus now also covers `m-items` returning `[]` for an empty map ✅ (rev200).

- **Real `encoding` open/save behavior + portability follow-up:** the shared editor core now treats text encoding as a real per-buffer option instead of a hardcoded `utf-8` status token, so `open_file(...)` decodes using the configured encoding, `save()` writes using the effective buffer encoding, and the portability corpus now also covers `m-keys` returning an empty list for an empty map ✅ (rev199).

- **Softwrap `wordwrap` + map-delete portability follow-up:** the shared editor core now honors a tiny `wordwrap` option so softwrapped rows can prefer breaking at spaces while keeping `view_rows`, cursor mapping, and visual-row motion in one shared wrap model, and the portability corpus now also covers deleting a missing map key leaving existing entries intact ✅ (rev198).

- **Micro-esque `savehistory` option alias + portability follow-up:** the editor's existing prompt-history persistence can now be enabled through `savehistory`, backed by a tiny alias-aware option registry so reads/writes/toggles and command-bar completion all resolve to the same canonical `history.persist` state; the portability corpus now also covers `m@` returning `0` for a missing key ✅ (rev197).

- **Real `fileformat` open/save behavior + portability follow-up:** the shared editor core now treats line endings as a real per-buffer option instead of a hardcoded statusline placeholder, so `open_file(...)` best-effort detects CRLF files as `fileformat=dos`, normalizes buffer text internally to `\n`, and `save()` writes either LF or CRLF from the effective option value; the portability corpus now also covers *missing* `host.feature?` probes staying lookup-only with respect to `dict-version` ✅ (rev196).

- **Shared `autoindent` option + portability follow-up:** the shared editor core now exposes its existing copy-indent-on-newline rule through a tiny ordinary `autoindent` option, so `InsertNewline` can either preserve leading whitespace (default) or insert a plain newline without inventing a separate mode or frontend policy; the portability corpus now also covers `host.feature?` staying lookup-only with respect to `dict-version` ✅ (rev195).

- **Leading-indent cursor stepping + portability follow-up:** the shared editor core now honors a tiny `tabmovement` option so `CursorLeft` / `CursorRight` and selection-extension motion can treat leading runs of `tabsize` spaces like one tab stop when `tabstospaces` is enabled, mirroring micro's conservative indent-only rule without inventing a richer visual-column engine; the portability corpus now also covers `host.api-version` staying lookup-only with respect to `dict-version` ✅ (rev194).

- **`readonly` protected-buffer option + portability follow-up:** the editor's existing protected-buffer path is now available through a tiny ordinary `readonly` option, so `setlocal readonly true` can block edits and saves in ordinary buffers while still sharing the same behavior as help/docs buffers; the portability corpus now also covers `host.features` staying lookup-only with respect to `dict-version` ✅ (rev193).

- **`keepautoindent` whitespace-only newline cleanup:** the shared editor core now honors a tiny `keepautoindent` option so pressing Enter again on a whitespace-only autoindented line can either clear that previous indent (default, micro-esque) or keep it when explicitly enabled, all in the same headless `InsertNewline` path rather than a frontend/save-time cleanup hack ✅ (rev192).

- **`parsecursor` open-target parsing:** the shared editor core now honors a tiny `parsecursor` option so open targets like `file:line[:col]` can place the primary cursor immediately, with explicit parsed targets overriding `savecursor` and with the same behavior preserved through interactive open, capability-gated/scripted open, and path-style command-palette opens ✅ (rev191, relanded in rev192).

- **Smart multiline paste indentation + host-inventory portability follow-up:** the shared editor core now honors a tiny `smartpaste` option so multi-line `Paste` can reuse the current line's existing whitespace prefix for otherwise-unindented blocks, keeping the behavior headless-first across ordinary, multi-cursor, and external/internal clipboard pastes without inventing a formatter; the portability corpus now also covers seeded `host.features` inventory deduplicating repeated feature names while staying sorted ✅ (rev190).

- **Per-file savecursor persistence:** the shared editor core now honors a tiny `savecursor` option so reopening a file can restore its last remembered primary cursor position through the existing `cap.persist` boundary, with best-effort JSON storage, honest clamping when files change, and load/save wiring shared by the headless REPL and curses TUI ✅ (rev189).

- **Save-time parent creation + search-order portability follow-up:** the shared editor core now honors a tiny `mkparents` option so manual saves can create missing parent directories already implied by the buffer path before writing, reusing the same honest shared save path as `rmtrailingws` / `eofnewline`; the portability corpus now also covers that `set-current` alone does not make a wordlist searchable through `find` until search order changes ✅ (rev188).

- **Save-time final-newline normalization + search-order portability follow-up:** the shared editor core now honors a tiny `eofnewline` option so manual saves can ensure a non-empty buffer ends with one final `\n`, reusing the same honest/undoable save-normalization path as `rmtrailingws`; the portability corpus now also covers that `definitions` keeps the compilation wordlist it selected even after later `set-order` changes ✅ (rev187).

- **Save-time trailing-whitespace cleanup + search-order portability follow-up:** the shared editor core now honors a tiny `rmtrailingws` option so manual saves trim trailing spaces/tabs from buffer lines before writing to disk, keeping the in-memory buffer honest and recording an undoable cleanup snapshot when anything changed; the portability corpus now also covers same-wordlist redefinition lookup, pinning down that name search inside one wordlist prefers the most recent definition ✅ (rev186).

- **Shared page-overlap paging + dictionary-version portability follow-up:** the editor core now honors a tiny `pageoverlap` option so `PageUp` / `PageDown` keep a few rows from the previous view visible in both ordinary and softwrapped views, with the overlap measured in visual rows under `softwrap`; the portability corpus now also covers `dict-version` staying stable across lookup-only `get-current` so future Rust/WASM hosts can validate one more namespace-adjacent cache-invalidation truth from JSON alone ✅ (rev185).

- **Shared buffer-position status cue + dictionary-version portability follow-up:** the editor now exposes a tiny shared current-buffer position model (`buffer_index`, `buffer_count`, `buffer_summary`) through `status_model()` / `ed.status`, the reference statusline formatter now supports `$(bufpos)` / `$(bufferpos)` / `$(buffers)`, and the default statusline surfaces that cue automatically when more than one buffer is open; the portability corpus now also covers `dict-version` staying stable across lookup-only `get-order` so future Rust/WASM hosts can validate one more search-order-adjacent cache-invalidation truth from JSON alone ✅ (rev184).

- **Tiny overflow markers + dictionary-version portability follow-up:** the minimal curses TUI now honors a tiny `overflowmarkers` option by drawing bold+dim `<` / `>` cues at the visible edges of horizontally clipped rows in ordinary buffers and docs/help buffers while intentionally suppressing them under `softwrap`, and the portability corpus now also covers `dict-version` staying stable across lookup-only `find` so future Rust/WASM hosts can validate one more tier-2-adjacent dictionary contract from JSON alone ✅ (rev183).

- **Tiny `matchbrace` cue + search-order portability follow-up:** the minimal curses TUI now honors tiny micro-esque `matchbrace` / `matchbraceleft` options by bold-underlining visible brace pairs under (or just left of) the primary cursor without promoting brace state into the headless editor model, and the portability corpus now also covers a `get-order`/`set-order` roundtrip that preserves search-order precedence so future Rust/WASM hosts can validate one more namespace contract from JSON alone ✅ (rev182).

- **Scrollbar thumb-character follow-up + search-order portability case:** the minimal curses TUI now honors a tiny `scrollbarchar` option so the existing right-edge scrollbar cue can render a user-chosen one-cell glyph (default `|`, empty falls back to `|`, longer strings use their first character) without changing the headless editor model, and the portability corpus now also covers search-order conflict precedence so future Rust/WASM hosts can validate that the first search-order entry wins on duplicate names without scraping Python tests ✅ (rev181).

- **Scrollbar cue + host-feature portability follow-up:** the minimal curses TUI now honors a tiny `scrollbar` option by reserving one right-edge column for a proportional thumb in ordinary and softwrapped views without promoting scrollbar state into the headless editor model, and the portability corpus can now seed per-case `host_features` so future Rust/WASM hosts can validate positive host-boundary probes like `host.feature?` success and sorted `host.features` inventory directly from JSON ✅ (rev180).

- **Color-column cue + search-order portability follow-up:** the minimal curses TUI now honors a tiny `colorcolumn` option by reverse-dimming a single visible guide column in ordinary buffers, docs/help buffers, horizontally scrolled views, and softwrapped rows (where the cue repeats per visual row as a screen-column marker), and the portability corpus now also covers `only` resetting the search-order length back to one entry so future Rust/WASM hosts can validate one more namespace/search-order contract without scraping Python tests ✅ (rev179).

- **Tab-error cue + search-order portability follow-up:** the minimal curses TUI now honors a tiny `hltaberrors` option by reverse-dimming visible tab/indentation-mismatch characters using the existing `tabstospaces` policy (tabs when spaces are expected, leading spaces when tabs are expected) in ordinary buffers, docs/help buffers, and visible fragments under softwrap/horizontal scroll without promoting indentation diagnostics into headless editor state, and the portability corpus now also covers `also` duplicating the top search-order entry so future Rust/WASM hosts can validate one more namespace contract without scraping Python tests ✅ (rev178).

- **Trailing-whitespace cue + search-order portability follow-up:** the minimal curses TUI now honors a tiny `hltrailingws` option by reverse-dimming visible trailing spaces/tabs in ordinary buffers, docs/help buffers, and softwrapped final fragments without promoting whitespace-warning spans into the headless editor model, and the portability corpus now also covers `previous` dropping the top search-order entry so future Rust/WASM hosts can validate one more namespace/search-order contract without scraping Python tests ✅ (rev177).
- **Tiny `cursorline` TUI pass + namespace portability follow-up:** the minimal curses TUI now honors a tiny `cursorline` option by underlining the current visible buffer row (including the active wrapped screen row under `softwrap`) without promoting row-highlighting into the headless editor model, and the portability corpus now also covers `definitions` following the top of the current search order so future Rust/WASM hosts can validate one more namespace/search-order contract without scraping Python tests ✅ (rev176).

- **Shared scrollmargin viewport pass + tiny portability follow-up:** the editor core now honors a tiny `scrollmargin` option inside the shared viewport contract, keeping vertical context rows around the primary cursor in both plain and softwrapped views, and the portability corpus now also covers `compiled?` returning `0` for a primitive XT so future Rust/WASM hosts can validate one more tier-2-adjacent dictionary contract without scraping Python tests ✅ (rev175).


- **Statusline search-count cue + tiny portability follow-up:** the reference statusline formatter now has a dedicated `$(searchpos)` token that renders the shared search-position summary as ` [i/n]`, the default right-side status format now uses it so ordinary TUI/statusline rendering finally exposes active search position outside the transient find prompt too, and the portability corpus now also covers missing-word `find` returning `0` so future Rust/WASM hosts can validate one more tiny dictionary contract point without scraping Python tests ✅ (rev174).

- **Search-position/statusline pass + tiny portability follow-up:** the editor now exposes one shared whole-buffer search-position model (`search_position_model`) through `ed.status` / `status_model()` as `search_query`, `search_literal`, `search_case_sensitive`, `search_match_index`, `search_match_count`, and `search_summary`, the minimal TUI now shows that same compact `[i/n]` summary right in the find prompt, and the portability corpus picked up bare-VM `host.feature?` coverage so future Rust/WASM hosts can validate one more host-boundary probe shape without scraping Python-side tests ✅ (rev173).

- **TUI search-highlight pass + tiny portability follow-up:** the minimal curses TUI now honors the existing `hlsearch` option by reverse-highlighting visible matches for the current search pattern and bolding the visible match under the primary cursor, while the portability corpus picked up `s<` plus bare-VM `host.features` coverage so future Rust/WASM hosts can validate one more typed-string behavior and one more host-boundary inventory shape without scraping Python-side tests ✅ (rev172).
- **Micro-esque ruler + portability contract pass:** the curses TUI now has an optional tiny line-number gutter (`ruler` / `relativeruler`) that keeps wrapped continuation rows blank and shifts the viewport/cursor honestly instead of faking overlay text, while the portability corpus picked up a few more ledger-promised contract points (`m?`, typed predicates, `get-current`, `dict-version`, and `host.api-version`) so future Rust/WASM hosts can replay more of the real kernel surface data-only ✅ (rev171).

- **Portability exact-slice + missing-kernel-contract pass:** the tiny JSON portability suite now covers a few more small-but-important portable behaviors already promised by the ledger — `0=`, successful `catch`, list clone/pop isolation, `m-keys`, `m-items`, session-local query/removal, and `set-current` round-tripping — and `tools/mxportable.py` / `src/micromax/portability_suite.py` now support exact case-name selection via `--name` / `names=` so future Rust/WASM hosts and future LLMs can ask for precise corpus slices without fuzzy substring matching ✅ (rev170).

- **Portability inventory + kernel-coverage pass:** the tiny JSON portability suite now also covers a few more portable kernel behaviors Micromax already leans on (`when`, `to-int`, `to-str`, `m-del`, `m-merge`), and `tools/mxportable.py` / `src/micromax/portability_suite.py` now expose a lighter-weight inventory path for matching categories/tags/case names so future Rust/WASM hosts and future LLMs can inspect the contract without pulling full case bodies ✅ (rev169).

- **Portability corpus discovery + machine-readable CLI pass:** the tiny JSON portability suite now covers a few more missing portable kernel behaviors (`while`, `constant`, `variable`, locals shadowing), carries much broader tags for sliceable bring-up work, and `tools/mxportable.py` can now emit machine-readable JSON summaries/results so future Rust/WASM hosts and future LLMs can inspect corpus slices without scraping human text ✅ (rev168).

- **Portability suite contract + tooling pass:** the tiny JSON portability suite now covers more missing portable kernel/boot-stdlib ground (`>r/r@/rdepth/rdrop`, `execute`, wordlist/search-order lookup, `in`, `2dip`, `recover`, `finally`), and the runner/CLI now validate case shape, reject duplicate names / malformed expectations, and support category/tag/name filtering for targeted cross-host runs ✅ (rev167).

- **Portability corpus expansion for real stdlib/safety behavior:** the tiny JSON portability suite now covers more of the language Micromax actually leans on across docs/editor work: quotation combinators (`dip`, `2keep`, `tri`), recovery/cleanup helpers (`try?`, `try`, `ensure`), and budget exhaustion under `catch`, so future Rust/WASM hosts have a sturdier cross-host semantic floor than arithmetic plus one `bi` example ✅ (rev166).

- **Docs/help multi-line footnote-definition render parity (tiny shared helper follow-up):** visible markdown footnote-definition starter lines already rendered dim with a bold `[^id]:` token in the live docs/help TUI; now tiny indented continuation lines under those starters render dim too, reusing the same shared definition-line roles instead of inventing another parser path ✅ (rev165).

- **Docs/help escaped-markdown source-view cue (tiny shared helper):** visible backslash-escaped markdown punctuation pairs like `\[`, `\!`, `\<`, `\*`, `\_`, `\~`, and ``\``` now also get a small source-view cue in the live docs/help TUI: the visible two-character escape pair renders dim while the escaped form still stays literal prose and non-navigable, reusing one tiny helper layered on the existing shared backslash-escape policy instead of inventing another parser path ✅ (rev164).

- **Docs/help inline-code delimiter source-view cue (tiny shared helper):** visible markdown inline-code backtick delimiters now also get a small source-view cue in the live docs/help TUI: opening/closing backtick runs render bold+dim while the already-dim code body styling stays intact, reusing one tiny shared helper layered on the existing equal-length backtick scan instead of inventing another parser path ✅ (rev163).

- **Docs/help inline-emphasis delimiter source-view cue (tiny shared helper):** visible markdown emphasis delimiters like `**`, `*`, `_`, and `~~` now also get a small source-view cue in the live docs/help TUI: delimiter tokens render dim while the already-styled emphasis/strong/strike bodies keep their existing body styling, reusing one tiny helper layered on the existing inline-emphasis regex helpers instead of inventing another parser path ✅ (rev162).

- **Docs/help live-link source-scaffolding cue (tiny shared helper):** visible supported ordinary markdown links like `[Vision](00-vision.md)`, `[Vision ref][visionref]`, and `[Vision shortcut]` now also get a small source-view cue in the live docs/help TUI: the non-label scaffolding (`[` / `](` + destination or reference tail / `]`) renders dim while the live label stays underlined, reusing one tiny helper layered on the existing shared link matcher instead of inventing another parser path ✅ (rev161).


- **Docs/help inline raw-HTML source-view cue (tiny shared helper):** visible inline raw HTML tags like `<kbd>` / `</kbd>` / `<a name=...>` now also get a small inert-source cue in the live docs/help TUI: the whole tag token renders dim, reusing the existing shared inline raw-HTML span helper while keeping supported autolinks on their existing bold whole-token path ✅ (rev160).

- **Docs/help image-token inert-source cue (tiny shared helper):** visible supported markdown image forms like `![alt](dest)` and `![alt][id]` now also get a small inert-source cue in the live docs/help TUI: the whole token renders dim, reusing one tiny helper layered on the existing shared markdown destination/reference helpers instead of inventing another parser path ✅ (rev159).

- **Docs/help autolink-token source-view cue (tiny shared helper):** visible supported angle-bracket autolinks like `<https://...>` now also get a small source-view cue in the live docs/help TUI: the whole token renders bold while the inner URL still keeps the ordinary docs-link underline, reusing one tiny helper layered on the existing shared autolink matcher instead of inventing another parser path ✅ (rev158).

- **Docs/help footnote-reference source-view cue (tiny shared helper):** visible markdown footnote references like `[^note]` now also get a small source-view cue in the live docs/help TUI: the whole token renders bold while the inner `^note` still keeps the ordinary docs-link underline, reusing one tiny helper layered on the existing shared footnote matcher instead of inventing another parser path ✅ (rev157).

- **Docs/help GitHub-alert source-view scanability (tiny shared helper):** blockquote-based GitHub alert opener tokens like `[!NOTE]` / `[!WARNING]` now also read a little more like alert markers in the live docs/help TUI: the quote rail stays bold, the quoted body stays dim, and the alert token itself now renders bold too via one tiny shared helper instead of another parser path ✅ (rev156).

- **Docs/help nested-list source-view scanability (tiny relaxed-indent follow-up):** the live docs/help TUI now also bolds nested markdown list/task markers when deeper indentation is clearly acting like list nesting rather than top-level indented code, so repo worklists/readmes with sub-bullets finally scan more honestly without making real code blocks look clickable or list-like ✅ (rev155).

- **Docs/help definition render parity (tiny shared helper):** reference-definition starter lines now render dim with a bold `[id]:` token, tiny wrapped reference-destination/title continuation lines render dim too, and footnote-definition starter lines now get the same dim+bold treatment in the live docs/help TUI — all reusing one shared definition-line helper instead of growing another parser path ✅ (rev154).

- **Docs/help raw-HTML render parity (tiny shared precedence reused):** raw HTML comments and raw HTML block lines were already inert for docs navigation/underlining/definition parsing, and now the live docs/help TUI also dims those spans/lines so commented-out notes and embedded HTML examples finally read less like ordinary prose without adding another parser path ✅ (rev153).

- **Docs/help indented-code parity (tiny shared helper):** blank-separated top-level indented code-ish markdown lines now stay inert for `helpfollow`, `helplinkpick`, and TUI docs-link underlining too, while the live docs/help TUI dims those lines so source-view examples finally read like code instead of accidentally clickable prose ✅ (rev152).

- **Docs/help fenced-code render scanability (tiny shared helper):** docs/help rendering now also reuses one tiny shared fenced-code line-role helper, so fenced markdown examples finally look visibly code-ish in the live TUI too: opening/closing fence lines render bold+dim while fenced body lines render dim, staying aligned with the same fence precedence already trusted for docs-link actions and definition parsing ✅ (rev151).

- **Docs/help setext-heading render parity (tiny shared helper):** docs/help rendering now reuses the same tiny heading scan already trusted for titles, outline rows, fragment jumps, and heading breadcrumbs, so setext heading title lines render like headings in the live TUI too while their `===` / `---` underline line gets a dim heading-ish treatment ✅ (rev150).

- **Docs/help list-marker scanability (tiny shared helper):** the minimal TUI now gives ordinary markdown list markers (`-` / `+` / `*`) and ordered markers (`1.` / `1)`) render bold via one small shared helper, and existing task-list checkbox styling now layers on top of that same list substrate ✅ (rev149).
- **Prompt-display clipping keeps tail detail visible:** shared rendered picker rows now fit narrow widths more like a real picker, preserving trailing path/location detail when possible instead of blindly chopping the combined row at the right edge; tiny headers and `more…` rows also ellipsize a bit more cleanly ✅ (rev148).

- **Shared rendered prompt-display model (visible-row parity + headless hostcall):** the minimal TUI's visible picker rows now live in one shared editor helper (`prompt_display_model`) instead of only inside `tui.py`, and future UIs/scripts/LLMs can inspect the same rendered headers / sticky headers / more markers / indented heading rows / selected row text through `ed.prompt-display` / `prompt-display` ✅ (rev147).

- **Shared picker window model (scroll-window parity + headless hostcall):** the minimal TUI's section-aware picker windowing now lives in one shared editor helper (`prompt_window_model`) instead of being trapped inside `tui.py`, and the same sticky-header / more-marker / hidden-count structure is now exposed headlessly through `ed.prompt-window` / `prompt-window` for future UIs/scripts/LLMs ✅ (rev146).

- **Docs picker visible section-label parity (preview/status/help prompts):** `helplinkpick`, `helpnavpick`, and `helpoutlinepick` now reuse the same visible section labels already shown by grouped picker headers (`Docs` / `Files` / `External` / `Headings` or heading-breadcrumb labels), so `prompt_current_section`, `prompt_current_preview`, and headless status surfaces no longer drift into older singular fallbacks like `Doc link`, `File link`, `External link`, and `Heading` ✅ (rev145).

- **Docs picker browse-budget parity (live docs navigator/link windowing):** `helplinkpick` and `helpnavpick` now flatten their grouped section rows through the same shared browse-window policy used by the other section-aware pickers, so empty-query browsing keeps `Docs` / `Files` / `External` (and `Headings` for `helpnavpick`) visible instead of letting one large first bucket hide every later section behind the row cap. This keeps TUI headers, `Alt-Up`/`Alt-Down`, and the live prompt window aligned with the existing grouped help-section APIs ✅ (rev144).

- **Sectioned picker browse-budget parity (live prompt windowing):** `bindingpick`, `bufferpick`, `markpick`, `jumppick`, `pluginpick`, `recentpick`, and `helppick` now flatten their grouped section rows through the same shared browse-window policy already used by `topicpick` / `commandpick`, so one large first section no longer hides every later section behind the initial row cap. Empty-query browse windows now budget rows across visible sections for all of those picker kinds, keeping TUI headers, `Alt-Up`/`Alt-Down`, preview/status surfaces, and headless grouped row APIs aligned ✅ (rev143).

- **Command palette live section parity (grouped browse rows + visible section labels):** `commandpick` now flattens the same grouped sections already exposed via `ed.command-palette-section-rows`, so the live prompt, TUI section headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces all agree on visible labels like `Recent Files`, `Recent`, `Commands`, and `Actions`. Empty-query browse windows now also budget rows across visible sections so commands do not monopolize the first page before actions appear ✅ (rev142).

- **Topic picker live section parity (grouped browse rows + visible section labels):** `topicpick` now flattens the same grouped topic families already exposed headlessly via `ed.topic-section-rows` / `ed.apropos-section-rows`, so the live prompt, TUI section headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces all agree on `Commands` / `Actions` / `Words` instead of drifting between flat rows and singular fallback labels. Empty-query `topicpick` also now budgets the initial row window across visible sections so Commands do not consume the whole browse view before Actions/Words ever appear ✅ (rev141).

- **Prompt position model for searchable pickers (shared ordinals + status/TUI parity):** picker-style prompts now expose one compact current-item position model — overall `index/count`, current section label, section-local `i/n`, and a ready-to-display summary string — through `prompt_current_position()`, status-model fields (`prompt_index`, `prompt_count`, `prompt_section_index`, `prompt_section_count`, `prompt_position_summary`), and new hostcall `ed.prompt-current-position`. The minimal TUI prompt line now shows that same compact position summary next to the existing preview, so long grouped pickers answer “where am I?” consistently across hostcalls, status/debug surfaces, and the live UI ✅ (rev140).

- **Recent picker grouped by project roots (shared labels + grouped rows):** `recentpick` now flattens the same shared project-root grouping already exposed headlessly through `ed.recent-section-rows`, so the live prompt, TUI section headers, sticky headers, `Alt-Up`/`Alt-Down`, and prompt preview/status surfaces all agree on one recent-files structure instead of showing repeated project labels in a flat MRU stream. Recent rows also now rewrite their visible detail to `project-name` + project-relative path for faster scanning ✅ (rev139).

- **Docs picker grouped by numbered families (shared labels + hostcall):** `helppick` now groups rows into stable numbered doc families like `00–09 Project`, `10–19 Research`, and `20–29 Language + VM`, exposes the same grouped shape through `ed.doc-section-rows`, and reuses those same labels for TUI headers, `Alt-Up`/`Alt-Down` section jumps, and prompt preview/status surfaces. Docs previews now also lead with the human doc title instead of the slug topic ✅ (rev138).

- **Binding picker grouped by winning mode (shared labels + hostcall):** `bindingpick` now groups rows by their resolved winning mode (`Prompt`, active mode names like `nav`, `Global`) and exposes the same grouped shape through `ed.binding-section-rows`. The minimal TUI, `Alt-Up`/`Alt-Down` section jumps, and `prompt_current_section` / preview / status surfaces all now reuse those same visible labels instead of falling back to the generic `Binding` bucket ✅ (rev137).

- **Buffer/plugin picker section parity (shared grouping helper + prompt preview parity):** buffer and plugin pickers now expose the same grouped structure headlessly via `ed.buffer-section-rows` / `ed.plugin-section-rows`, while `prompt_current_section`, `prompt_current_preview`, and headless `status-summary` now reuse the visible picker section labels for grouped picker kinds like recent/buffer/plugin instead of drifting into generic `Buffer` / `Word` labels ✅ (rev136).

- **Picker grouping for marks + jumplist (shared row labels + hostcalls):** `markpick` now groups rows by owning buffer and exposes that same structure through `ed.mark-section-rows`, while `jumppick` now groups rows by `Current` / `Back` / `Forward` and exposes `ed.jump-section-rows`. The minimal TUI, `Alt-Up`/`Alt-Down` section jumps, `prompt_current_section`, and preview/status surfaces all reuse the same shared labels instead of inventing picker-only grouping rules ✅ (rev135).

- **Docs non-whitespace label guard (shared matcher + ref-id helper):** help/docs navigation now keeps empty and whitespace-only markdown labels literal prose across inline links, full reference links, and shortcut reference links, so malformed cases like `[](doc.md)`, `[ ](doc.md)`, and `[   ][id]` no longer leak into `helpfollow`, `helplinkpick`, or TUI docs-link underlining ✅ (rev134).

- **Docs nested-link precedence inside labels (shared matcher guard):** help/docs navigation now refuses outer markdown links whose label text contains a valid inner link, so CommonMark-shaped cases like `[outer [inner](doc)](other)` keep the outer prose literal while still exposing the valid inner link through `helpfollow`, `helplinkpick`, and TUI docs-link underlining ✅ (rev133).

- **Docs wrapped angle-bracket destinations + separator guard (shared destination helper):** help/docs navigation now covers tiny CommonMark-style wrapped inline/reference links whose destination uses `<...>` on the next line, while the shared destination parser also now refuses malformed title starts that appear immediately after a closing `>` with no separating whitespace, keeping `helpfollow`, `helplinkpick`, reference-definition parsing, and TUI docs-link underlining aligned around one small destination policy ✅ (rev132).

- **Docs tiny wrapped inline links (shared continuation helper):** help/docs navigation now recognizes small CommonMark-style inline links whose destination can sit on the next line and whose title/closer can wrap once as well, with one shared `md_docs_continuation_line()` policy keeping `helpfollow`, `helplinkpick`, and TUI docs-link underlining aligned around fenced/raw-HTML/comment-hidden lines ✅ (rev131).

- **Docs spaces-only 0–3 indent guards (shared tiny block-start helper):** help/docs reference definitions, footnote definitions, and ATX heading scanning now consistently follow the small CommonMark-style “up to three leading spaces” rule, so four-space and tab-indented code-ish lookalikes stay prose instead of leaking into `helpfollow`, `helplinkpick`, outline rows, or TUI docs-link underlining ✅ (rev130).

- **Docs multi-line reference definitions (shared tiny destination parser):** help/docs navigation now recognizes small CommonMark-style reference definitions whose destination lives on the next line and whose optional title can also wrap to the following line, with the same shared destination policy reused by `helpfollow`, `helplinkpick`, reference-definition parsing, and TUI docs-link underlining ✅ (rev129).

- **Docs generic type-7-ish HTML blocks (shared tiny block helper):** help/docs navigation now also treats complete generic tag-only lines like `<widget-box ...>` / `</widget-box>` as inert prose through the next blank line when they begin after a blank line (or at doc start), while still refusing to let those blocks interrupt paragraphs. The same small `md_html_block_line_flags()` policy now stays aligned across `helpfollow`, `helplinkpick`, outline scanning, markdown reference/footnote-definition parsing, and TUI docs-link underlining ✅ (rev128).

- **Docs raw-HTML blocks (shared tiny block helper):** help/docs navigation now treats common raw HTML blocks as inert prose across `helpfollow`, `helplinkpick`, outline scanning, markdown reference/footnote-definition parsing, and TUI docs-link underlining, covering both blank-line-terminated blocks like `<div>...</div>` and `<pre>...</pre>`-style blocks that stay inert across internal blank lines ✅ (rev127).

- **Docs multi-line setext headings (shared tiny heading scanner):** help/docs heading discovery now recognizes setext headings whose title spans multiple paragraph lines, so doc titles, picker summaries, outline rows, heading-grouped link sections, and fragment jumps stay aligned with current CommonMark/GFM-style setext behavior without committing Micromax to a full markdown block parser ✅ (rev126).

- **Docs destination escapes + local-doc path decoding (shared tiny parser):** help/docs inline and reference link destinations now support balanced parentheses, markdown-safe backslash unescaping, and percent-decoded local doc paths before follow, so local docs links like `104-paren\(topic\).md`, `103-space\ path.md`, and `103-space%20path.md` navigate cleanly through `helpfollow`, `helplinkpick`, and the same shared scanner/TUI surfaces ✅ (rev121).
- **Docs fenced-code precedence (shared tiny block helper):** fenced code blocks in help/docs buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, TUI docs-link underlining, and reference-definition parsing, so literal markdown examples inside triple-backtick/tilde fences no longer leak into the live docs browser ✅ (rev122).
- **Docs setext headings (shared tiny heading scanner):** single-line setext headings (`Title` + `===` / `---`) now participate in help/docs fragment jumps, outline rows, heading breadcrumbs, and docs-picker titles, with the same heading-title cleanup / explicit `{#id}` handling as ATX headings. This stays deliberately small and fenced-code-aware rather than becoming a full markdown block parser ✅ (rev123).

- **Docs raw-HTML comment precedence (shared tiny comment helper):** raw HTML comments in help/docs buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, outline scanning, TUI docs-link underlining, and markdown reference/footnote-definition parsing, so commented-out markdown examples stay literal instead of leaking into the live docs browser ✅ (rev124).

- **Docs raw-HTML/autolink precedence inside link labels (shared tiny inline-HTML helper):** help/docs link detection now treats inline raw HTML tags and autolinks as tighter than markdown link grouping inside would-be labels, so CommonMark-shaped cases like `[fake <span title="](doc.md)">`, `[fake <span title="][id]">`, and `[fake <https://example.invalid/?x=](doc.md)>` stay literal prose for `helpfollow`, `helplinkpick`, and TUI docs-link underlining instead of turning into regex-shaped false positives ✅ (rev125).

- **Docs balanced-bracket link labels (shared docs-browser scanner):** help/docs link detection now supports balanced bracket labels like `[Vision [nested]](doc.md)`, `[Vision [nested]][id]`, and `[Vision [nested]]`, with the same tiny shared policy reused by `helpfollow`, `helplinkpick`, TUI docs-link underlining, and reference-definition parsing. This fixes a real regex-shaped gap without committing the project to a full markdown parser ✅ (rev120).

- **Docs inline-code precedence now applies to editor actions too:** `helpfollow` and `helplinkpick` now ignore markdown-looking inline/reference/autolinks that sit inside inline code spans, keeping docs-browser actions aligned with the tiny TUI's code-first link-underlining policy ✅ (rev118).

- **Docs inline image syntax no longer leaks into the tiny docs-link model:** markdown image forms like `![alt](dest)` and `![alt][id]` are now ignored consistently by `helpfollow`, `helplinkpick`, and TUI docs-link underlining, so image alt text is treated as prose until Micromax grows a clearer image-aware docs policy ✅ (rev117).

- **Docs inline code precedence + equal-length backtick runs (tiny, UI-only):** the minimal curses TUI now recognizes inline code spans with equal-length backtick delimiters (so forms like ``code `with tick` `` work), and masks those code spans before docs-link underlining so markdown-looking text inside code does not appear clickable. The implementation remains local and inspectable (`md_inline_code_spans` + `md_link_label_spans`) rather than a full inline markdown parser ✅ (rev116).

- **Docs inline emphasis/strong/strike scanability (tiny, UI-only):** the minimal curses TUI now recognizes small markdown inline emphasis forms in docs/help buffers — `**strong**` bodies render bold, `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline), and `~~strike~~` bodies render dim. The implementation remains local and inspectable (`md_strong_spans`, `md_emphasis_spans`, `md_strikethrough_spans`) rather than a full inline markdown parser or AST commitment ✅ (rev115).

- **Docs thematic-break scanability (tiny, UI-only):** the minimal curses TUI now recognizes common markdown thematic breaks in docs/help buffers (`---`, `***`, `___`, including spaced forms like `- - -`), dimming the separator line and bolding the visible marker run for faster scanning. The implementation remains local and inspectable (`md_thematic_break_span`, `md_thematic_break_char_spans`) rather than a full block parser or markdown AST commitment ✅ (rev114).
- **Docs markdown escapes stay prose across styling + actions:** backslash-escaped markdown openers like `\[link]`, `\![image]`, `\[^footnote]`, and `\<autolink>` are now ignored consistently by `helpfollow`, `helplinkpick`, and TUI docs-link underlining, so help pages can teach markdown literally without becoming accidentally navigable ✅ (rev119).

- **Docs blockquote scanability (tiny, UI-only):** the minimal curses TUI now recognizes small markdown blockquote prefixes in docs/help buffers, bolding the quote-marker rail and dimming the quoted body for faster scanning. The implementation remains local and inspectable (`md_blockquote_prefix`, `md_blockquote_body_span`) rather than a full block parser or rich markdown renderer ✅ (rev113).

- **Docs task-list scanability (tiny, UI-only):** the minimal curses TUI now recognizes small GFM-style task-list markers in docs/help buffers (`- [ ]`, `* [x]`, `1. [X]`), bolding the checkbox token and dimming the body of checked tasks for faster scanning. The implementation remains local and inspectable (`md_task_checkbox`, `md_task_body_span`) rather than a full markdown block model ✅ (rev112).

- **Docs table scanability (tiny, UI-only):** the minimal curses TUI now recognizes small GFM-style pipe tables in docs/help buffers, rendering header rows bold, delimiter rows dim, and literal `|` separators dim for faster scanning. The implementation is intentionally UI-only and inspectable (`md_table_delimiter_row`, `md_table_row_kinds`, `md_table_pipe_spans`) rather than a full markdown parser ✅ (rev111).

- **Docs footnotes + picker/copy parity:** help/docs buffers now recognize common markdown footnote references (`[^id]`) and definition anchors (`[^id]: ...`), so `helpfollow` jumps to the matching footnote definition in-place and the same tiny footnote model flows through `helplinkcopy`, `helplinkpick`, `helpnavpick`, and TUI link underlining/current-link detection ✅ (rev110).

- **Docs fragment links + explicit heading ids:** help/docs navigation now follows same-page fragments (`#section`) and cross-doc fragments (`page.md#section`), using best-effort GitHub-style auto slugs plus explicit heading ids (`{#id}` / `{: #id }`). Outline rows and heading-based breadcrumbs also strip raw attr-list syntax so docs UIs show rendered titles instead of source noise ✅ (rev109).

- **Command palette path sections + starter portability corpus:** path-like `commandpick` results now split into `Directories` / `Files` / `Open` sections instead of one generic `Open` bucket, making drill-down and scanability clearer in both headless data and the TUI. The repo also now ships `portability/kernel_cases.json`, `src/micromax/portability_suite.py`, and `tools/mxportable.py` so future Rust/WASM ports have a small JSON-based semantic corpus independent of pytest internals ✅ (rev108).

- **Help navigator grouping parity + source-aware external-link confirm:** `helpnavpick` / `ed.helpnav-section-rows` now reuse the same link-section policy as `helplinkpick` (so `set help.linksections heading` affects both), the picker/TUI section reconstruction paths now agree with that grouping, and external-link confirmation prompts now mention whether the request came from help, the cursor, or an explicit command ✅ (rev107).

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
