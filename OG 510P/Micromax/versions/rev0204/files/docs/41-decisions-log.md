## rev204 — brace-match style should stay a tiny renderer choice

**Decision**: add a tiny `matchbracestyle` option to the existing renderer-local brace cue so visible brace matches can use either bold+underline or bold+reverse styling without promoting theme/style state into the headless editor model. Also add one more portability case proving that storing to an existing map key overwrites its value.

**Why**: micro's current options docs still present `matchbracestyle` as a small ordinary option layered directly on top of `matchbrace`, not as part of a larger theme or semantic-highlighting subsystem. Micromax already had the useful hard part in place — one shared visible brace-position calculation used by both ordinary and docs/help rendering — so the right follow-up is just a small renderer choice.

**Consequence**:
- registered `matchbracestyle` (default `underline`, enum `underline|highlight`)
- added `brace_match_attr()` so the existing brace spans can render consistently in both ordinary and docs/help paths
- kept `highlight` deliberately tiny and theme-agnostic for now: bold+reverse rather than a new color contract
- portability follow-up: `map-store-overwrite-updates-value` now pins down that `m!` overwrites an existing key's value rather than creating host-shaped duplicates

## rev203 — `showchars` should stay a tiny renderer-side visibility aid

**Decision**: register a tiny `showchars` option and implement it only in the curses TUI as one-cell display replacements for spaces/tabs, including indent-aware `ispace` / `itab` overrides, while leaving buffer text, cursor math, and host-visible editor state unchanged. Also add one more portability case proving `m?` returns `0` for a missing key.

**Why**: micro's current options docs still present `showchars` as a display-only aid for invisible characters rather than a formatting or editing subsystem. Micromax's current wrap/search/cursor model is still character-cell-based, so a one-cell renderer pass is the honest low-risk move; multi-cell tab decorations can wait for a richer layout contract.

**What changed**:
- registered `showchars` (default `""`)
- added tiny TUI helpers for parsing the option string and rewriting visible row fragments only
- ordinary and help/docs buffers now honor `space` / `tab` plus indent-aware `ispace` / `itab` overrides
- softwrap continuation-indent prefix spaces intentionally stay plain because they are renderer-created, not file content
- the portability corpus now covers `m?` returning `0` for a missing key

**Consequence**: Micromax gets another small but real scanability feature in the current TUI without promoting invisible-character spans into the shared editor core, and future frontends/LLMs have one explicit place to evolve this behavior later.

## rev202 — `fastdirty` should be a shared dirty-state policy

**Decision**: register a tiny `fastdirty` option and keep a clean baseline in the shared buffer model, so the default path can recompute whether a buffer is truly modified while `fastdirty=true` keeps the cheaper sticky modified-flag rule.

**Why**: Micromax had already grown shared save, autosave, quit, and statusline behaviors that all rely on `dirty`, but it was still implicitly acting like `fastdirty=true` all the time. Making the policy explicit keeps those surfaces aligned without inventing a background hash service or renderer-only exceptions.

**What changed**:
- registered `fastdirty` (default `false`)
- the buffer model now keeps a clean baseline signature and refreshes `dirty` against it when `fastdirty=false`
- option changes from commands, Micromax option words, and hostcalls now resync existing buffers immediately
- the portability corpus now also covers `m-merge` with an empty destination adopting the source pairs

**Consequence**: Micromax gets a more honest modified-state contract for future UIs, scripts, and LLMs while still preserving the cheaper micro-esque behavior when explicitly requested.

## rev198 — `wordwrap` should stay in the shared wrap model


## rev201 — autosave should reuse the shared save path, not invent a side-channel

**Decision**: register a tiny `autosave` option and implement it through the existing host-driven timer pump plus the same shared `_save_buffer(...)` path used by manual saves. Let `quit` opportunistically reuse that same autosave path for eligible dirty buffers before falling back to the ordinary dirty-buffer warning.

**Why**: upstream micro still treats `autosave` as a normal editor option rather than a plugin. Micromax already had the right substrate — deterministic timer pumping, headless save logic, and a deliberately simple dirty bit — so adding autosave as shared editor policy closes a real workflow gap without committing the project to crash-recovery, background threads, or undo persistence.

**What changed**:
- registered `autosave` (int seconds, `0` = off)
- added tiny per-buffer autosave scheduling state
- `pump_timers()` now also checks due autosaves without changing timer callback counts
- autosave and manual save now share the same normalization/write path
- `quit` first tries immediate autosave for eligible dirty buffers, then warns only for the remaining dirty set
- the portability corpus now covers `m-merge` with an empty source preserving destination pairs

**Consequence**: Micromax gains one more practical, micro-esque editing behavior in the shared headless core, and future UIs/LLMs do not have to rediscover or reimplement a separate autosave codepath.

**Decision**: register a tiny `wordwrap` option and teach the existing shared softwrap helpers to prefer breaking at spaces when possible, so `view_rows`, cursor mapping, visual-row Home/End, and visual-row Up/Down all keep agreeing on the same wrapped-row boundaries. Also add one more portability case proving that deleting a missing map key leaves existing pairs intact.

**Why**: micro's current options docs still expose `wordwrap` as a softwrap-only option, and the 2.0.9 release notes explicitly mention the new option alongside softwrap-navigation improvements. Micromax already had a real headless wrap model (`view_rows`, `cursor_view_pos`, `top_subline`, visual-row paging/motion), so the smallest honest follow-up was shared wrap-row calculation rather than a renderer-only word-splitting pass.

**What changed**:
- registered `wordwrap` (default `false`)
- shared wrap-row calculation now prefers the last whitespace that fits on a row before falling back to hard wrapping
- the same row starts now drive rendering, cursor→screen mapping, visual-row document-position mapping, and visual-row Home/End
- added a portability case covering `m-del` on a missing key preserving existing map entries

**Consequence**: Micromax closes one more real editing-behavior gap without inventing a richer layout engine, and future frontends/LLMs inherit one inspectable wrap contract instead of recreating word wrapping differently in each surface.


### D197 — Add tiny option aliases and expose prompt-history persistence as `savehistory`
**Decision**: teach the editor option registry about small aliases that resolve to one canonical option key, and use that to expose `savehistory` as an alias for `history.persist`.

**Why**:
- Micromax already had prompt-history persistence; the missing piece was a more micro-esque option spelling.
- A tiny alias layer is safer than duplicating storage or teaching individual command paths about bespoke synonyms.
- Canonical storage keeps future UI/script/LLM inspection honest: one real setting, optional compatibility names.

**Consequence**:
- `set` / `show` / `toggle`, option words, and command-bar completion can all accept `savehistory`.
- Canonical storage stays under `history.persist`, so aliases do not fork local/global state.
- `show` with no arguments still lists canonical options only.

**Tests**:
- `tests/test_editor_option_words_set_toggle_show.py`
- `tests/test_editor_persistence_cap_persist.py`
- `tests/test_editor_core.py`

## rev196 — `fileformat` should become a real shared open/save policy

**Decision**: register a tiny `fileformat` option and teach the shared editor core to best-effort detect CRLF files on open while writing LF/CRLF on save from the effective option value. Also add one more portability case proving even a *missing* `host.feature?` probe does not bump `dict-version`.

**Why**: micro's current options docs still treat `fileformat` as a real buffer setting whose value is auto-detected from existing files and affects save behavior. Micromax was still faking that field in `status_model()` while `open_file()` used text decoding that erased CRLF/LF distinctions before the editor could inspect them. The smallest honest follow-up was therefore shared open/save policy, not a renderer tweak or a richer newline engine.

**What changed**:
- registered `fileformat` (`unix`/`dos`, default `unix`)
- `open_file(...)` now preserves raw newline information long enough to detect CRLF vs LF before normalizing in-memory text to `\n`
- `save()` now emits LF or CRLF based on the effective option value
- `status_model()` / `$(opt:fileformat)` now report the actual buffer option instead of a hardcoded placeholder
- added a portability case covering `dict-version` stability across a missing `host.feature?` probe

**Consequence**: Micromax closes another small but user-visible “status/config says one thing, shared behavior does another” gap in the editor core, while future frontends and future LLMs inherit one explicit line-ending policy instead of guessing.


## rev195 — `autoindent` should become a visible shared option

**Decision**: register a tiny `autoindent` option and keep newline indentation behavior inside the shared `InsertNewline` action, so Micromax can preserve leading whitespace by default while still allowing `set autoindent false` to insert a plain newline. Also add one more portability case proving `host.feature?` does not bump `dict-version`.

**Why**: micro's current options docs still treat `autoindent` as a plain editor setting and document `keepautoindent` separately as the follow-up policy for whitespace that autoindent inserted. Micromax already had copy-indent-on-newline in the shared editor core and had already taught that same path about `keepautoindent`, so the smallest honest follow-up was to make the behavior explicit in the option registry instead of leaving it as an always-on hidden policy.

**What changed**:
- registered `autoindent` (default `true`)
- `InsertNewline` now reuses leading whitespace only when `autoindent` is enabled
- `keepautoindent` now only applies when autoindent actually inserted indentation
- added a portability case covering `dict-version` stability across `host.feature?`

**Consequence**: Micromax closes one more small “the editor already behaves this way, now make it inspectable and configurable” gap in the shared core, which is exactly the kind of low-risk, future-LLM-friendly progress this archive wants.


## rev194 — `tabmovement` should stay a tiny shared cursor-motion rule

**Decision**: register a tiny `tabmovement` option and route ordinary left/right cursor motion plus selection-extension motion through one shared helper that can treat leading runs of exactly `tabsize` spaces like one tab stop when `tabstospaces` is enabled.

**Why**: micro's current options docs still expose `tabmovement`, and current upstream action code keeps the rule deliberately conservative: only leading indentation participates, only all-space chunks of width `tabsize` collapse, and otherwise movement stays character-wise. Micromax already had the right substrate in its headless action layer, so the smallest honest move was one shared cursor-motion helper rather than another TUI-only convenience. The portability sibling closes one more lookup-only truth by pinning down that `host.api-version` should not bump `dict-version` either.

**What changed**:
- registered `tabmovement` (default `false`)
- `CursorLeft` / `CursorRight` now optionally collapse leading runs of spaces by `tabsize` when `tabstospaces` is enabled
- `SelectLeft` / `SelectRight` reuse the same step rule so selection semantics stay aligned with plain movement
- the portability corpus now covers `dict-version` staying stable across `host.api-version`

**Consequence**: Micromax now closes one more small micro-esque movement gap in the shared editor core, while future UIs/scripts keep inheriting the same inspectable cursor semantics automatically.


## rev193 — `readonly` should become a normal option, not stay an internal buffer-only flag

**Decision**: register a tiny `readonly` option and route the editor's existing protected-buffer checks through the ordinary option system, so ordinary buffers can be marked read-only with `setlocal readonly true` while the existing help/docs protection path keeps reusing the same shared rule.

**Why**: micro's current options docs still treat `readonly` as a small ordinary editor setting and explicitly steer users toward the local form. Micromax already had the hard part: mutating actions, status reporting, `save`, and capability-gated `ed.save` all understood the idea of a protected buffer. The smallest honest next move was therefore not a new command or mode, but one registered option and one shared “effective readonly” policy. The portability sibling closes one more lookup-only truth by pinning down that `host.features` inspection should not bump `dict-version`.

**What changed**:
- registered `readonly` (default `false`)
- mutating action dispatch, `save`, protected-buffer queries, status reporting, and capability-gated `ed.save` now all consult the effective option value (`global` with buffer-local override)
- ordinary buffers can now opt into the same protection path already used by help/docs buffers
- the portability corpus now covers `dict-version` staying stable across `host.features`

**Consequence**: Micromax now exposes one more practical editor behavior through the same small option vocabulary future humans/LLMs already inspect, without splitting “internal protected buffers” from “user read-only buffers” into two different semantics.


## rev188 — parent creation should be shared save behavior, not a separate command

**Decision**:
- add a tiny `mkparents` option to the ordinary editor option registry
- have `Editor.save()` create missing parent directories when that option is enabled
- keep the option default `false` so saves stay conservative unless explicitly opted in
- extend the portability corpus with one more search-order case: `set-current` alone does not make a wordlist searchable

**Why**:
- micro's current options docs already describe `mkparents` as save-path behavior rather than a separate file-management feature
- Micromax already centralizes save normalization in `Editor.save()`, so parent creation belongs in the same shared path instead of being reimplemented in commands or UI layers
- this keeps future frontends and LLMs from having to guess whether nested-path saves should succeed
- the namespaces corpus already covered search-order precedence and `definitions`; adding the complementary `set-current`/`find` separation makes the contract easier for future hosts to learn from data alone

**Consequence**:
- `save` / `saveas` can now create missing parent directories when explicitly enabled
- default behavior stays conservative and existing save errors still surface honestly when the option is off
- future hosts/frontends can treat parent creation as a shared editor policy rather than a UI quirk


## rev185 — page overlap should live in shared paging, not in the TUI

**Decision**:
- add a tiny `pageoverlap` option to the ordinary editor option registry
- compute an effective page jump as `page.height - pageoverlap`, clamped to at least one row
- make `PageUp` / `PageDown` shift both the cursor(s) and the shared viewport origin by that same step
- keep the softwrap case honest by measuring the overlap in visual rows via `top_subline`
- extend the portability corpus with one more tiny lookup-only dictionary/version case: `dict-version` stays stable across `get-current`

**Why**:
- micro's current options docs already define `pageoverlap`, so the project had an obvious micro-esque paging affordance still missing from the shared editor core
- paging overlap is fundamentally about *what the view keeps visible*, so burying it in the curses renderer would make future frontends and headless tests guess the rule independently
- Micromax already had the necessary viewport ingredients (`page.height`, `top_line`, `top_subline`, softwrap visual-row motion), so this was a good time to promote the behavior into the shared contract
- `dict-version` is already used for tier-2 cache invalidation, so future hosts benefit from one more explicit lookup-only non-bump case in the JSON corpus

**Consequence**:
- ordinary views and softwrapped views now page with the same overlap idea instead of only sharing cursor movement
- future frontends/LLMs can inspect paging behavior from editor state and tests without reconstructing it from renderer code
- the first pass stays conservative by defaulting `pageoverlap` to `0`, leaving micro's more aggressive default for a later decision if the project wants it


## rev181 — scrollbar glyphs should be configurable without changing the scrollbar model

**Decision**:
- add a tiny `scrollbarchar` option to the ordinary editor option registry
- keep the existing right-edge scrollbar contract exactly one column wide
- let the curses TUI use the configured glyph for the thumb while preserving the existing proportional sizing/placement logic
- extend the portability corpus with one more small search-order case: duplicate-name conflict resolution should prefer the first search-order entry

**Why**:
- micro's current options docs already pair `scrollbar` with `scrollbarchar`, so Micromax's new scrollbar cue was missing an obvious micro-esque customization knob
- character choice is renderer-local polish, not a reason to invent shared scrollbar state or a richer theme system yet
- keeping empty values and multi-character values normalized to one visible glyph preserves the one-column contract in narrow terminals
- the portability ledger already names search-order behavior as portable surface, and conflict precedence is a useful real-world lookup guarantee that future hosts should not infer from Python tests

**Consequence**:
- users/configs get a tiny extra readability affordance without changing viewport semantics
- future richer renderers remain free to style the thumb differently or add track/theme behavior later
- future Rust/WASM hosts can validate one more namespace/search-order behavior from JSON alone


## rev180 — scrollbars should stay renderer-local, and host-feature probes should stay data-only

**Decision**:
- add a tiny `scrollbar` option to the ordinary editor option registry
- let the curses TUI reserve one right-edge column and derive a proportional thumb from the current viewport
- keep the first pass renderer-local: ordinary views size the thumb from logical rows, while `softwrap` sizes it from visual rows
- extend the portability corpus schema with optional per-case `host_features` seeds, then add positive `host.feature?` and seeded/sorted `host.features` cases

**Why**:
- the recent micro-inspired TUI work keeps landing best when cues stay ordinary options instead of turning into shared editor state
- a terminal scrollbar is most useful right now as a passive "where am I?" cue, not as a clickable widget or a deeper viewport subsystem
- Micromax already has enough shared viewport/softwrap behavior to size the thumb honestly without storing extra scrollbar state
- the host-boundary corpus already covered the empty and missing-feature cases, but future hosts still needed Python-side setup to validate positive feature probes

**Consequence**:
- ordinary buffers, docs/help buffers, and softwrapped views get one more tiny scanability cue without changing headless editor semantics
- future richer renderers remain free to replace the visuals or add theme-aware track/thumb variants later
- future Rust/WASM hosts and future LLMs can validate positive host-feature probes directly from JSON instead of inferring them from Python tests


# Decisions log

This file records **why** some choices were made so future humans/LLMs do not have to reconstruct intent from code archaeology.

## rev179 — guide columns should stay renderer-local first

**Decision**:
- add a tiny `colorcolumn` option to the ordinary editor option registry
- let the curses TUI derive a one-cell visible guide-column cue per rendered row
- keep the first pass renderer-local: ordinary horizontally scrolled views track the configured document column honestly, while `softwrap` repeats the cue per visual row as a screen-column marker
- extend the portability corpus with one more small search-order case: `only` resetting the search-order length back to one entry

**Why**:
- micro already frames `colorcolumn` as a plain numeric display option rather than a larger subsystem
- Neovim's docs are a useful reminder that guide columns are fundamentally screen-column cues, which matters once wrapped views enter the picture
- Micromax already has the shared viewport/softwrap behavior needed to place a tiny visible marker honestly without promoting the idea into headless editor state
- the portability ledger already names `only` alongside the other search-order words, so the JSON corpus should keep catching up one data-only expectation at a time

**Consequence**:
- ordinary buffers, docs/help buffers, horizontal scroll, and softwrap all get the same small guide-column affordance
- future richer renderers remain free to replace the visuals or add smarter multi-column policy later without changing editor semantics
- future Rust/WASM hosts can validate one more namespace/search-order behavior from data alone instead of inferring `only` from Python tests


## rev178 — tab/indent mismatch should stay renderer-local and reuse `tabstospaces`

**Decision**:
- add a tiny `hltaberrors` option to the ordinary editor option registry
- let the curses TUI derive visible tab/indentation-mismatch spans from the logical line + current visible fragment
- reuse the existing `tabstospaces` policy directly: tabs are cues when spaces are expected, leading spaces in the initial indent are cues when tabs are expected
- extend the portability corpus with one more small search-order case: `also` duplicating the top search-order entry

**Why**:
- micro already frames `hltaberrors` as a small display toggle rather than a full diagnostics feature
- Micromax already had the real editing policy knob (`tabstospaces`) and enough shared viewport/softwrap state to compute the visible intersection honestly
- keeping the first pass renderer-local avoids pretending the project already has a richer indentation-warning or linting model than it actually does
- the portability ledger already names `only` / `also` / `previous` / `definitions` as portable kernel surface, so the JSON corpus should keep catching up one contract point at a time

**Consequence**:
- ordinary buffers, docs/help buffers, softwrap, and horizontal scroll all get the same tiny indentation-mismatch cue
- future richer renderers can reuse the helper or replace the visuals without changing editor semantics
- future Rust/WASM hosts can validate one more namespace/search-order behavior from data alone instead of inferring `also` from Python tests


## rev177 — trailing whitespace stays renderer-local and fragment-local

**Decision**:
- add a tiny `hltrailingws` option to the ordinary editor option registry
- let the curses TUI derive visible trailing-whitespace spans from the logical line + current visible fragment
- keep the first pass visual-only instead of storing whitespace-warning spans or edit-freshness state in the headless editor core

**Why**:
- this is the same small-option direction micro already uses for `hltrailingws`
- Micromax already has enough shared viewport/softwrap state to compute the visible intersection honestly
- keeping it renderer-local avoids pretending the project already has a richer diagnostics/span model than it actually does

**Consequence**:
- ordinary buffers, docs/help buffers, softwrap, and horizontal scroll all get the same tiny cue
- future richer renderers can reuse the helper or replace the visuals without changing editor semantics
- the current pass intentionally does **not** try to emulate micro's more stateful “forgotten trailing whitespace only” behavior

## rev170 — portability slices should support exact names, not just fuzzy matching

**Decision**: keep the JSON portability corpus data-only and hand-editable, but let callers select cases by exact name as well as by category/tag/substring. Rev170 also fills a few more missing-but-ledger-promised kernel contracts: `0=`, successful `catch`, list clone/pop isolation, `m-keys`, `m-items`, session-local query/removal, and `set-current` round-tripping.

**Why**:
- precise bring-up work often starts from one failing behavior, not a whole tag slice
- fuzzy substring matching is handy for humans but brittle for automation and future LLMs
- the portability ledger already promised several of these kernel behaviors, so the corpus should keep catching up in small data-only steps

**What changed**:
- added exact-name selection in `select_portability_cases(...)`
- added repeatable `mxportable --name` filtering
- added focused tests for exact-name filtering and the new kernel cases
- expanded `portability/kernel_cases.json` with the missing kernel behaviors above

**Consequence**: the portability suite stays tiny, but it is now a little closer to a real bring-up contract: future hosts can request exact cases, and the corpus covers more of the small semantic surface the portability ledger already names.

## rev169 — the portability corpus should support light-weight inventory as well as replay

**Decision**: keep the JSON portability corpus data-only, but add one lighter-weight inspection path on top of it. Rev169 expands the corpus with a few more portable kernel behaviors Micromax already relies on (`when`, `to-int`, `to-str`, `m-del`, `m-merge`) and teaches `mxportable` / `portability_suite.py` to expose a small inventory of matching categories, tags, and case names without requiring callers to pull full case bodies.

**Why**: the worklist still treats portability discipline as active, and current language ecosystems keep teaching the same lesson: a conformance corpus is most useful when it is both replayable and easy to inspect. Micromax already had run-mode JSON and list-mode case dumps, but future Rust/WASM hosts and future LLMs also benefit from a smaller answer to “what does the `memory` slice cover?” that does not force them to parse every source/expectation field.

**What changed**:
- expanded `portability/kernel_cases.json` to cover `when`, `to-int`, `to-str`, `m-del`, and `m-merge`
- added `portability_inventory(...)` in `src/micromax/portability_suite.py`
- added `mxportable --inventory` and `mxportable --inventory --json`
- added focused tests for the new cases and inventory output

**Consequence**: the portability suite stays tiny and hand-editable, but the repo now has a better “quick contract inventory” path for bring-up notes, CI glue, future hosts, and future humans/LLMs.

## rev168 — the portability corpus should be machine-readable on the way out too

**Decision**: keep the JSON portability suite tiny and data-only, but make it easier to inspect directly during bring-up. Rev168 adds a few more portable kernel cases (`while`, `constant`, `variable`, locals shadowing), tags the corpus much more broadly, and teaches `mxportable` to emit machine-readable JSON summaries/results in both list and run modes.

**Why**: the worklist still calls out portability discipline as an active priority, and larger language ecosystems keep teaching the same lesson: a conformance corpus becomes more useful when it is both implementation-agnostic and easy to consume mechanically. Micromax already had a small replayable corpus, but future Rust/WASM hosts and future LLMs benefit from not having to scrape human console output just to answer “which memory cases exist?” or “did the locals slice pass?”

**What changed**:
- expanded `portability/kernel_cases.json` to cover `while`, `constant`, `variable`, and locals shadowing, and added broader tags across the corpus
- `src/micromax/portability_suite.py` now exposes machine-friendly case/result/summary helpers
- `tools/mxportable.py` now supports `--json` for both `--list` and run mode
- added focused tests for machine-readable records/summaries and JSON CLI output

**Consequence**: the portability suite stays tiny, hand-editable, and replayable offline, but it is now friendlier both to future second implementations and to future humans/LLMs trying to inspect what the portable contract already covers.

## rev167 — the portability corpus should validate itself and support targeted slices

**Decision**: treat the JSON portability corpus more like a tiny conformance contract than a loose demo file. Rev167 adds more portable kernel/boot-stdlib cases (`>r`/`r@`/`rdepth`/`rdrop`, `execute`, wordlist/search-order lookup, `in`, `2dip`, `recover`, `finally`) and tightens the shared runner/CLI so malformed corpora fail fast and targeted subsets can be listed or run by category, tag, or name.

**Why**: the worklist still calls out portability discipline as an active priority, and current language ecosystems keep teaching the same lesson: a small data-oriented conformance suite becomes far more useful when it is explicit, implementation-agnostic, and easy to slice during bring-up. Micromax already had the start of that, but future Rust/WASM hosts and future LLMs benefit from a runner that rejects duplicate/malformed cases early and a corpus that covers a few more core namespace/execution/alias behaviors the repo already relies on.

**What changed**:
- expanded `portability/kernel_cases.json` to cover return-stack basics, `execute`, wordlist/search-order lookup, `in`, `2dip`, `recover`, and `finally`
- `src/micromax/portability_suite.py` now validates case shape up front and offers `select_portability_cases(...)`
- `tools/mxportable.py` now supports `--category`, `--tag`, `--name-contains`, and `--list` for targeted runs
- added focused tests for malformed corpora, tag normalization/filtering, and filtered CLI execution

**Consequence**: the portability suite is a little closer to the sort of boring, replayable contract a second implementation can actually live on, while still staying tiny and hand-editable offline.

# Decisions log

- Rev164: visible backslash-escaped markdown punctuation pairs in docs/help buffers (for example `\[`, `\!`, `\<`, `\*`, `\_`, `\~`, and ``\``` ) now also get a tiny source-view cue in the live TUI: the visible two-character escape pair renders dim while the escaped form stays literal and non-navigable, all through one small helper layered on the existing shared backslash-escape policy instead of another parser path.
- Rev161: visible supported ordinary markdown links in docs/help buffers (for example `[Vision](00-vision.md)` / `[Vision ref][visionref]` / `[Vision shortcut]`) now also get a tiny source-view cue in the live TUI: the non-label scaffolding (`[` / `](` + destination or reference tail / `]`) renders dim while the live label stays underlined, all through one small helper layered on the existing shared link matcher instead of another parser path.
- Rev160: visible inline raw HTML tags in docs/help buffers (for example `<kbd>` / `</kbd>` / `<a name=...>`) now also get a tiny inert-source cue in the live TUI: whole tag tokens render dim via one small helper layered on the existing shared inline raw-HTML span helper, while supported autolinks keep their separate bold whole-token cue instead of being lumped in with raw HTML.

This is the running list of decisions we’ve made (and why).

## rev2 (2026-02-25)

### D001 — Forth is the plugin system
**Decision**: micromax plugins/config/macros are all micromax.

**Why**: it’s the core differentiator (Emacs-like power) while micro-like UX stays the baseline.

**Risk**: plugins can crash / hang / poison global state.

**Mitigation (planned)**:
- wordlists + search order for namespace hygiene
- explicit hostcall allowlist (capability style)
- structured errors + trace
- later: time/step limits per evaluation + per-plugin VM instances

### D002 — Namespacing starts with wordlists + search order
**Decision**: implement minimal Search-Order-like mechanism early, not as a later add-on.

**Why**: editor/plugin ecosystems die without namespace hygiene.

**Implemented in rev2**:
- `wordlist`, `set-current`, `set-order`, `only/also/previous/definitions`, `order` helper.

### D003 — Quotations are core (not optional)
**Decision**: quotations `[ ... ]` are first-class values executed by `call`.

**Why**: keybindings/macros/callbacks want “code as a value”. It’s the ergonomic bridge to editor scripting.

### D004 — Variables/constants are in v0
**Decision**: include `constant`, `variable`, `@`, `!` in v0.

**Why**: real editor scripting needs some persistent state; this is the smallest useful surface.

### D005 — Host bridge is allowlisted
**Decision**: no ambient power; host calls must be explicitly registered.

**Implemented in rev2**:
- `hostcall ( "name" -- ... )` calls only registered host functions.

## rev3 (2026-02-25)

### D006 — Build tools live *inside the archive*
**Decision**: ship formatting/lint/test tooling in-repo so a future LLM (or human) can continue work immediately.

**Implemented in rev3**:
- `ruff` lint+format, `mypy` typechecks, `pytest` tests
- `Makefile` + `scripts/` helpers
- optional `pre-commit` config

### D007 — Add a hard execution budget as a safety floor
**Decision**: every evaluation can run with a **step budget** to prevent untrusted code (plugins) from freezing the host.

**Why**: editor scripting must be safe by default.

**Implemented in rev3**:
- `set-budget ( n -- )` and `with-budget ( n q -- )`
- budget exhaustion raises a structured error

### D008 — micromax is *Forth-inspired*, not standards-bound
**Decision**: we will happily diverge from traditional Forth where it improves ergonomics/safety.

**Why**: the target is an editor scripting ecosystem, not Forth conformance.

**Near-term implications**:
- keep wordlists/search-order (solves real editor/plugin problems)
- keep quotations + combinators as a core ergonomic pillar
- be suspicious of invisible global state (e.g., implicit `STATE`) unless we can make it explicit and debuggable

### D009 — Concurrency will be cooperative-first
**Decision**: plan for concurrency, but default to **cooperative tasks** with explicit yield points.

**Why**: cooperative scheduling is easier to reason about for editor state, avoids many data races, and composes with budgets.

**Planned**:
- `yield`/`pause` primitive and a tiny task scheduler (later)
- isolate editor mutations to the UI task; background tasks communicate via message queue


## rev4 (2026-02-25)

### D010 — “micromax” is the language name
**Decision**: micromax names the **language** (and VM). The editor is a later target and can be named later.

**Why**: we want a crisp identity for the language as the plugin system.

### D011 — Execution tokens + deferred words are ground-floor features
**Decision**: include:
- `'` + `execute` (xts)
- `defer` + `is` + `defer@`/`defer!` (hooks)

**Why**: editor scripting needs first-class callbacks/hook points and keymap-friendly “code handles”.

**Guardrail**: all callbacks still run under `catch` + budgets in the host.


## rev5 (2026-02-25)

### D012 — Preserve paren comments as documentation
**Decision**: Forth-style paren comments `( ... )` are preserved during parsing and used as docstrings
for colon definitions when they appear at the start of a definition.

**Why**: we want a low-friction path to:
- readable code
- `help`/`where` tooling
- eventual stack-effect checking (Factor-style inspiration)

**Implemented in rev5**:
- `help name` prints docs
- `where name` shows the defining wordlist

### D013 — Add a minimal container type: lists
**Decision**: introduce host-value lists as the first container type.

**Why**: editor scripting needs small collections (handlers, selections, search results) and this is
the least complex useful structure.


## rev7 (2026-02-25)

### D014 — Start a testable editor *core* now (headless)
**Decision**: begin the `micro`-esque editor as a **headless core** first.

**Why**: we can make rapid progress with unit tests in this container, and delay
terminal UI decisions (curses vs. tcell-like wrapper vs. something else).

**Implemented in rev7**:
- `micromax_editor.Buffer` (line-based for now)
- multi-cursor *model* support (list of cursors)
- undo/redo stack
- a minimal command/action registry

### D015 — Adopt micro-style action chains in keybindings
**Decision**: support action chaining separators inspired by micro:

- `,` always continue
- `|` abort if previous action succeeded
- `&` abort if previous action failed

**Why**: this is a tiny feature with outsized UX payoff for keymaps.

**Implemented in rev7**:
- `micromax_editor.keymap.parse_action_chain`
- `Editor.run_action_chain`

### D016 — Plugins are micromax directories with lifecycle words
**Decision**: ship a minimal plugin manager now:

- each plugin has its own wordlist/namespace
- optional `plugin.json`
- `init.mx` entrypoint
- optional lifecycle words: `preinit`, `init`, `postinit`, `deinit`

**Why**: we need a real embedding story early so the language design stays
grounded in the editor use-case.

**Implemented in rev7**:
- `micromax_editor.plugins.PluginManager`
- sample `plugins/core/` plugin

### D017 — Add a tiny `see` word to the language
**Decision**: add `see name` to print a readable representation of a word.

**Why**: debuggability is pedagogy.

**Implemented in rev7**:
- `see` for primitives/colon words/deferred words/hooks

**Implemented in rev5**: `list push pop len nth set-nth clone`

### D018 — Hooks are first-class multi-handler words
**Decision**: add hook words that run an ordered list of callbacks (xts).

**Why**: matches common editor extensibility patterns (Emacs hooks) and keeps extension points cheap.

**Implemented in rev5**: `hook hook-add hook-rm hook-clear hook@ hooks`

### D019 — Modules are friendly named wordlists
**Decision**: layer a small module API on top of wordlists/search order.

**Why**: plugin ecosystems need namespaces. Wordlists solve the core problem; modules make it easy.

**Implemented in rev5**: `module ... endmodule`, `use`, `in`, `modules`

### D020 — Add `require` as load-once include
**Decision**: add `require` which loads a file at most once per VM instance.

**Why**: plugin/config layering wants idempotent loading.



## rev6 (2026-02-25)

### D021 — Prioritize pedagogy and offline hackability
**Decision**: add tutorial/cookbook/hacking docs and keep the VM readable with minimal dependencies.

**Why**: micromax should be maintainable by hand, without internet or LLM support.

**Implemented in rev6**:
- `docs/70-tutorial.md`
- `docs/71-cookbook.md`
- `docs/72-hacking-by-hand.md`

### D022 — Add runtime locals sugar (`->name` / `name`)
**Decision**: support a simple locals mechanism to reduce stack-shuffle noise:
- `->name` stores into a local (popping a value)
- `name` loads the local value
- locals are **per colon call** (frames), plus a persistent session frame

**Why**: editor scripting benefits from readability; locals are a pragmatic concession.
See Gforth locals for precedent in Forth ecosystems:
https://gforth.org/manual/Local-Variables-Tutorial.html

**Guardrail**: locals shadow words; `' name` still quotes the dictionary word.

### D023 — Add postfix message-send sugar (`.word`) + dynamic `send`
**Decision**: support `.word` as sugar for `"word" send`, and define `send` to execute a word by string name.

**Why**: improves ergonomics for “object-ish” pipelines while staying fundamentally word-based.

### D024 — Add hot-reload building blocks (`reload`, `unrequire`)
**Decision**: add `reload` to force re-evaluation of a file and `unrequire` to forget a required path.

**Why**: hot reload is essential for plugin iteration and editor scripting.

### D025 — Make “host owns the world” an explicit contract
**Decision**: treat the host boundary as a first-class design surface.
Add `host.api-version`, `host.feature?`, and `host.features`.

**Why**: embedded language ecosystems need stable host API versioning and feature discovery.


## rev8 (2026-02-25)

### D026 — Separate “actions” from “command-bar commands”
**Decision**: the editor core has two dispatch surfaces:
- **actions**: keybind targets that return success/failure (for chaining)
- **commands**: command-bar strings parsed with shell-like quoting

**Why**: micro’s UX splits these concepts cleanly (actions in keybindings; commands in Ctrl-e bar), and it keeps the editor core testable.

**Implemented in rev8**:
- `ActionRegistry` (`src/micromax_editor/commands.py`)
- `CommandDispatcher` (`src/micromax_editor/command_dispatcher.py`)

### D027 — Implement command bar + `command:` / `command-edit:` keybindings
**Decision**: support micro-style bindings that run command-bar commands (`command:`) and open the command bar prefilled (`command-edit:`).

**Why**: huge leverage for discoverability + macro-like workflows without inventing a macro DSL.

**Implemented in rev8**:
- `Editor.enter_prompt(kind='command')`
- `micromax_editor.cmdline.parse_cmdline` (shlex)
- `Editor._run_action_spec` handling `command:` and `command-edit:`

### D028 — Add a minimal options system + incremental search substrate
**Decision**: implement an options registry with global and buffer-local values, and a search subsystem that respects options.

**Why**: micro’s `incsearch` and `ignorecase` are low-hanging editor features that immediately improve UX and guide the embedding API.

**Implemented in rev8**:
- `Options` (`src/micromax_editor/options.py`)
- `SearchState` (`src/micromax_editor/search.py`)
- default options: `ignorecase=true`, `incsearch=true`, `hlsearch=false`

### D029 — Keybinding chain parsing must respect quotes and escaping
**Decision**: parse action chains so separators can appear inside quoted args or be escaped with `\\`.

**Why**: micro explicitly supports this, and it is necessary for `command:` bindings with quoted args.

**Implemented in rev8**:
- upgraded `parse_action_chain` in `src/micromax_editor/keymap.py`


## rev9 (2026-02-25)

### D030 — Add selection + internal clipboard as core editor substrate
**Decision**: implement a simple, testable selection model (anchor + primary cursor) and an internal clipboard.

**Why**: micro’s headline value is “desktop-default” text operations in the terminal (Shift+arrows select; Ctrl-c/x/v copy/cut/paste). This unlocks real editing workflows immediately.

**Implemented in rev9**:
- selection helpers in `Editor` (`selection_text`, `delete_selection`, etc.)
- actions: `SelectLeft/Right/Up/Down`, `SelectAll`, `Copy`, `Cut`, `Paste`, `CutLine`, `DuplicateLine`
- core plugin binds micro-esque defaults (`plugins/core/init.mx`)

### D031 — Add indentation actions + micro Tab chain
**Decision**: implement `IndentSelection` / `UnindentSelection`, and keep micro’s default Tab chain (`Autocomplete|IndentSelection|InsertTab`).

**Why**: indentation is a common “selection-level” operation and the Tab chain is an elegant low-tech macro.

**Implemented in rev9**:
- options: `indent` (default four spaces)
- actions: `IndentSelection`, `UnindentSelection`, `Autocomplete`, `InsertTab`

### D032 — Add `replace` / `replaceall` command-bar commands (regex by default)
**Decision**: implement micro-like `replace` / `replaceall` commands with `-a` (all) and `-l` (literal) flags.

**Why**: search without replace is half a tool; replace is also a good test of shell parsing + command dispatcher + undo.

**Implemented in rev9**:
- commands: `replace`, `replaceall` in `src/micromax_editor/command_dispatcher.py`
- undo recording for command-driven text edits

### D033 — Best-effort micromax action hooks (`ed.pre-action`, `ed.on-action`)
**Decision**: create micromax hook words for action notifications and fire them from `Editor.run_action`.

**Why**: gives plugins a clean, language-native “event surface” without hardcoding a Python callback registry.

**Implemented in rev9**:
- `hook ed.pre-action` and `hook ed.on-action` created in editor init
- `Editor._emit_mx_hook` + hook notifications around action calls



## rev10 (2026-02-25)

### D034 — Upgrade selection model to per-cursor anchors
**Decision**: selections are per cursor (each cursor can have its own anchor), matching modern multi-cursor editors.

**Why**: multi-cursor editing without per-cursor selections quickly becomes confusing; this also keeps clipboard and insert/delete semantics consistent.

**Implemented in rev10**:
- `EditorBuffer.sel_anchors: list[Cursor|None]` aligned with `cursors`
- selection helpers updated to take an optional cursor index
- multi-cursor-safe editing: apply multi-cursor edits bottom-to-top

### D035 — Implement micro-esque macros (action-level)
**Decision**: macros record executed actions/commands (not raw keypresses) and store a snapshot of `editor.input` for replay.

**Why**: the headless core doesn't have a full key-event model yet; action-level macros are stable across UI implementations.

**Implemented in rev10**:
- actions: `ToggleMacro`, `PlayMacro`
- core plugin binds micro defaults: Ctrl-u / Ctrl-j

### D036 — Implement micro-esque multi-cursor primitives
**Decision**: implement the core micro multi-cursor actions that are easy to test and unlock real workflows.

**Implemented in rev10**:
- `SpawnMultiCursorSelect`, `SpawnMultiCursorUp/Down`, `RemoveMultiCursor`, `RemoveAllMultiCursors`, `SkipMultiCursor`, `SpawnMultiCursor`
- core plugin binds micro defaults (Alt-n / Alt-Shift-Up/Down / Alt-p / Alt-c / Alt-x / Alt-m)

### D037 — Implement CutLine accumulation until paste
**Decision**: `CutLine` appends cut lines to the clipboard until the next paste.

**Why**: micro documents this behavior and it makes repetitive line-cut workflows much nicer.

**Implemented in rev10**:
- clipboard stores either `items` (selection chunks) or `lines` (cut-line blocks)
- paste resets cut-line accumulation

### D038 — Add prompt history navigation with context-aware bindings
**Decision**: keep per-prompt history and bind Up/Down as `PromptHistoryPrev|CursorUp` and `PromptHistoryNext|CursorDown`.

**Why**: micro-style action chains let one binding behave differently in prompt vs buffer without a complex mode system.

**Implemented in rev10**:
- prompt history state in `Prompt` + `Editor.history`
- actions: `PromptHistoryPrev`, `PromptHistoryNext`



## rev11 (2026-02-25)

### D039 — Add a small set of stack ergonomics words (`nip`, `tuck`, `pick`, ...)
**Decision**: implement a small handful of high-leverage stack words used in practice.

**Why**: micromax wants to be ergonomic *without* requiring a huge standard library.
These words also make scripts and tests shorter and clearer.

**Implemented in rev11**:
- `nip`, `tuck`, `2dup`, `2drop`, `depth`, `clear`, `pick`, `roll`

### D040 — Expose a return stack (`>r`, `r>`, `r@`, `rdrop`, `rdepth`)
**Decision**: expose return-stack manipulation primitives.

**Why**: return-stack words are a minimal, well-known extension point in Forth culture.
They also enable certain stack arrangements without adding a long list of primitives.

**Implemented in rev11**:
- `>r`, `r>`, `r@`, `rdrop`, `rdepth`

### D041 — Add tiny quotation combinators (`dip`, `keep`)
**Decision**: add the "two smallest" useful combinators for quotation ergonomics.

**Why**: `dip` and `keep` appear repeatedly across Joy/Factor/Forth-adjacent code.
They reduce noisy stack juggling, which is especially important in editor scripting.

**Implemented in rev11**:
- `dip`, `keep`

### D042 — Improve error formatting with source excerpts
**Decision**: keep evaluated sources in the VM and include a one-line excerpt + caret
in formatted errors.

**Why**: micromax is meant to be hacked by hand and debugged offline; error messages
should point directly at the problem.

**Implemented in rev11**:
- `VM.sources` cache
- `VM.format_error()` includes a best-effort excerpt

## rev13 (2026-02-25)

### D043 — Tier-2 is late-bound and minimal
**Decision**: the first compiled tier uses only `PUSH` and `EXEC_NAME`, where `EXEC_NAME` applies the *same* runtime name rules as tier-1 (locals shadowing, `.name` send sugar), and resolves names at execution time.

**Why**: this preserves dynamic redefinition/reload semantics and keeps the compiler tiny and portable.

**Risk**: fewer speed wins than early-binding or richer bytecode.

**Mitigation**: add optional caching/ids later without changing semantics.

### D044 — Token-parsing words remain tier-1 for now
**Decision**: compiled code rejects words that require reading the token stream at runtime (e.g. `module`, `constant`, `local@`).

**Why**: it keeps tier-2 small and avoids re-creating an interpreter inside the compiler.

**Risk**: some advanced metaprogramming cannot run compiled.

**Mitigation**: expand the compiler story later (compile-time expansion or non-parsing runtime alternatives).

### D045 — Prefer non-parsing runtime lookup
**Decision**: add `find` (`"name" -- xt|0`) so runtime code can look up words without `'` (token parsing).

**Why**: improves portability and makes tier-2 compilation easier.

### D046 — Add orthogonal editor range primitives
**Decision**: expose `ed.range-text`, `ed.replace-range`, `ed.delete-range` as undoable, orthogonal hostcalls (primary buffer).

**Why**: gives scripts real editing power without exploding the hostcall surface with one-off commands.

## rev14 (2026-02-25)

### D047 — Multi-cursor lists are in document order with an explicit primary index
**Decision**: store cursors in document order and track the primary cursor via an explicit `primary` index.

**Why**: this matches how selection-oriented editors describe the world (primary vs document-order selections) and makes scripting deterministic.

**Consequence**: internal editor code must not assume cursor 0 is the primary.

### D048 — Normalize multi-cursor invariants after every action
**Decision**: after each action, normalize cursor lists: clamp positions, align anchor lists, remove duplicates, sort, and fix up `primary`.

**Why**: multi-cursor bugs are "state leaks". Normalization makes the editor resilient and keeps unit tests honest.

### D049 — Expose a minimal multi-cursor host surface
**Decision**: add hostcalls `ed.cursors`, `ed.set-cursors`, `ed.primary`, `ed.set-primary`, `ed.selections`, and `ed.replace-selections`.

**Why**: these few calls let micromax scripts inspect/edit multi-cursor state without committing to a large object model or adding maps/dicts.

## rev15 (2026-02-25)

### D050 — Transactional undo grouping for scripts
**Decision**: add `ed.with-undo` hostcall that runs a quotation while suppressing internal undo recording, then records a single undo snapshot (or rolls back on error).

**Why**: plugin actions frequently need multiple hostcalls but should appear as one user-visible undo step (similar in spirit to grouped changes in modal editors).

### D051 — Expose clipboard as orthogonal host primitives
**Decision**: add clipboard hostcalls `ed.clipboard`, `ed.set-clipboard`, `ed.clipboard-items`, and `ed.set-clipboard-items`.

**Why**: scripts need to cooperate with editor copy/cut/paste semantics (including multi-item clipboards) without reaching into Python internals.

### D052 — Add a per-buffer selection recovery stack (not undo)
**Decision**: add `ed.push-selections`/`ed.pop-selections` and keep the saved state out of undo history.

**Why**: multi-cursor workflows make it easy to accidentally clear/merge selections; a tiny recovery stack is a cheap, testable escape hatch.

## rev16 (2026-02-25)

### D053 — Expose directionless range helpers for the primary selection
**Decision**: add `ed.selection-range` and `ed.set-selection-range` hostcalls.

**Why**: many editor operations (replace, delete, extract) are naturally described as ranges; a directionless, normalized view is convenient and portable.

**Note**: directed endpoints remain available via `ed.selections`.

### D054 — Allow scripts to set directed selections via lists
**Decision**: add `ed.set-selections` hostcall that accepts `[]` or `[aL aC cL cC]` per cursor.

**Why**: this makes cursor/selection state manipulable without introducing maps/dicts or opaque objects.

### D055 — Add selection direction actions
**Decision**: add editor actions `FlipSelections` and `EnsureSelectionsForward`.

**Why**: selection-oriented editors commonly expose anchor/cursor control; having these as core actions keeps behavior testable and scriptable.

## rev17 (2026-02-25)

### D056 — Add a portable cursor/selection snapshot format
**Decision**: expose `ed.cursorstate` and `ed.set-cursorstate` using a lists+ints wire format: `[primary [[id line col aL aC] ...]]` with `-1 -1` for missing anchors.

**Why**: scripts and plugins often need to stash/restore cursor state (e.g. preview helpers, temporary navigation) without coupling to editor internals. Keeping it "portable on the wire" supports a future Rust/WASM host.

### D057 — Add save-excursion style cursor restoration
**Decision**: add `ed.with-cursorstate` that runs a quotation and then restores cursor/selection state in a `finally` block.

**Why**: many editor ecosystems have a common pattern (e.g. Emacs' `save-excursion`) where helper commands can move around without disturbing the user's cursor.

## rev18 (2026-02-25)

### D058 — Add a per-buffer jumplist (navigation history)
**Decision**: implement a per-buffer jumplist with actions `PushJump` / `JumpBack` / `JumpForward` and hostcalls `ed.push-jump`, `ed.jump-back`, `ed.jump-forward`, `ed.jump-info`, `ed.clear-jumps`.

**Why**: navigation history is a ubiquitous editor primitive (Vim/Helix). Keeping it per-buffer and storing full cursor/selection state makes it deterministic and scriptable, while staying separate from undo.

### D059 — Add data-returning XT introspection helpers
**Decision**: add `xt-kind`, `xt-doc`, and `xt-src` words.

**Why**: tooling (including future LLM-assisted refactors) benefits from structured access to documentation and definitions without scraping printed output.

## rev19 (2026-02-25)

### D060 — Add a global dict-version for tier-2 cache invalidation
**Decision**: maintain `VM.dict_version` and expose it as `dict-version`.

**Why**: tier-2 bytecode needs a cheap invalidation mechanism so per-call-site caches stay correct under word redefinition and search-order changes.

### D061 — Use per-call-site inline caches for `EXEC_NAME`
**Decision**: compiled `EXEC_NAME` instructions carry a `WordRef` that caches name resolution keyed by `dict-version`.

**Why**: this preserves tier-1 late-binding semantics while avoiding repeated dictionary lookups when the dictionary/search order is stable.

### D062 — Centralize search-order mutation through `set_search_order`
**Decision**: replace direct writes to `search_order` in core/module/plugin code with `VM.set_search_order(...)`.

**Why**: search order changes affect name resolution; routing all mutations through a single helper ensures `dict-version` is bumped consistently.

## rev20 (2026-02-25)

### D063 — Add a constant pool to tier-2 bytecode
**Decision**: represent bytecode as a constant pool (`consts`) plus a linear instruction stream whose operands are indices.

**Why**: it keeps the instruction stream compact, makes a future binary encoding straightforward for Rust/WASM, and matches common VM practice.

**Note**: this is a representation change only; semantics remain identical.

### D064 — Expose editor message log to scripts
**Decision**: add hostcalls `ed.messages`, `ed.last-message`, `ed.pop-message`, and `ed.clear-messages`.

**Why**: headless-first workflows (and plugin debugging) benefit from being able to inspect and clear the editor message log from micromax without reaching into Python internals.

### D065 — Keep repo context output up to date for future LLMs
**Decision**: update `tools/mxcontext.py` to include bytecode + caching docs and the cursorstate/jumplist docs.

**Why**: future automated refactors work best when the key docs are enumerated in one stable place.

## rev21 (2026-02-25)

### D066 — Add JSON serialization for tier-2 bytecode
**Decision**: add a simple, tagged JSON encoding for tier-2 bytecode and expose it via `bytecode-json` and `bytecode-load-json`.

**Why**: this enables offline caching and provides a straightforward cross-language validation path for the eventual Rust/WASM VM (generate JSON in Python, load/execute in Rust, compare behavior).

### D067 — Add message-log save/capture helpers for scripts
**Decision**: add hostcalls `ed.with-messages` and `ed.capture-messages`.

**Why**: headless-first workflows and tests often want to run an action/command and assert what it *said* without polluting the persistent message log.

### D068 — Document the bytecode serialization shape explicitly
**Decision**: add `docs/27-bytecode-serialization.md` and update the bytecode-format doc to reference it.

**Why**: keeping the archive self-describing makes future refactors and ports (including LLM-assisted ones) significantly easier.

## rev22 (2026-02-25)

### D069 — Add tiny tier-2 control flow ops and compile `if/when/while`
**Decision**: extend tier-2 bytecode with `CALL_Q`, `JZ`, and `JMP`, and add a semantics-preserving peephole compile for:

- `flag [t] when`
- `flag [t] [f] if`
- `[cond] [body] while`

**Why**: these patterns dominate real runtime scripting hot paths (keybindings/actions). Compiling them avoids pushing quotation values and calling the runtime control words, while preserving late binding inside quotations.

### D070 — Auto-record jumplist entries for `goto` and `jump`
**Decision**: add editor option `jumplist.auto` (default true). When enabled, `goto`/`jump` record both the "from" and "to" cursor states.

**Why**: this matches the common “jump list” ergonomics in editors (e.g. Vim/Helix): after a big jump, users expect a single back-step to return.


## rev23 (2026-02-25)

### D071 — Named macro slots + cancel macro
**Decision**: extend macro recording/playback beyond a single "last macro" to support named macro slots, and add `CancelMacro` to discard a recording without overwriting the previous macro.

**Why**: micro's single last-macro is great for quick repetition, but a small library of named macros (like Vim/Emacs) makes early automation dramatically more usable without needing a full plugin ecosystem.

### D072 — Make macros script-visible with a portable encoding
**Decision**: add macro hostcalls (`ed.macro-*`) and define a portable macro representation using only lists/ints/strings:

- `["a", ACTION, [[key val] ...]]` for action steps (with `editor.input` snapshot)
- `["c", CMDLINE]` for command steps

**Why**: this lets scripts inspect/persist/edit macros without needing a map/dict type in the VM, and keeps a clean Rust/WASM port path.

### D073 — Expose `editor.input` for tooling and fix command history duplication
**Decision**: add hostcalls to read/list/clear `editor.input` and ensure command history is recorded exactly once for command prompt submissions.

**Why**: parameterized actions need a stable, scriptable way to set and inspect inputs, and prompt history should not double-record entries.

## rev24 (2026-02-25)

### D074 — Add portable, string-keyed maps to the VM
**Decision**: promote **Map** (mutable, string-keyed dictionaries) to a core value type and add a tiny primitive surface:

- `map map?`
- `m@ m? m! m-del`
- `m-keys m-items m-merge`

**Why**: editor scripting and plugin configuration quickly want structured state that is more readable than “lists of pairs”, and the Rust/WASM port story for a string-keyed hash map is straightforward.

**Policy**: in portable mode, map keys are **strings**; primitives enforce this by parsing keys as strings.

## rev25 (2026-02-25)

### D075 — Prompt completion modeled as a suggestion session
**Decision**: implement command-bar completion as a small, headless *suggestion session* stored on `Prompt`:

- `suggestions`, `suggest_index`
- `suggest_start/suggest_end`
- `suggest_base`

Bind `Tab` to cycle forward (existing `Autocomplete`) and `Shift-Tab` to cycle backward (`PromptCompletePrev`), matching common editor conventions.

Expose minimal hostcalls for UI/scripting experimentation:
- `ed.prompt-suggestions`
- `ed.prompt-suggest-index`
- `ed.prompt-complete`
- `ed.prompt-clear-suggestions`

**Why**: this makes the command bar feel immediately “real editor” (discoverable + fast), while keeping the editor core headless and testable.

### D076 — Add `xt-span` and store spans on colon words
**Decision**: store a definition span on `ColonWord` (the `:` token span) and add `xt-span`:

- `xt-span` ( xt -- [file line col] | 0 )

**Why**: spans are cheap, portable metadata that dramatically improve debugging, tooling, and reloadability, especially when the editor’s commands and keybindings are *data* (quotations) created dynamically.

## rev26 (2026-02-26)

### D077 — Add contract tests for spans and prompt completion hostcalls
**Decision**: add direct unit tests for:

- `xt-span` on colon words + quotations (and `0` on primitives)
- command-bar completion via hostcalls (`ed.prompt-*`)

**Why**: these features are small but foundational for debugging and headless UX. A dedicated test keeps the contract stable across refactors and prevents subtle regressions.

### D078 — Document source-span debugging as a first-class workflow
**Decision**: add `docs/65-debugging-spans.md` describing the span model and how `format_error` and `xt-span` fit together.

**Why**: micromax is meant to be evolved offline by humans and future LLMs; spans are one of the highest leverage “make debugging pleasant” affordances, so the repo should explain them explicitly.

## rev27 (2026-02-26)

### D079 — Add filesystem path completion for `open` / `save` / `cd`
**Decision**: extend command-bar completion to support micro-style file/workspace commands:

- `open PATH`
- `save PATH`
- `cd PATH`

Rules (portable, predictable):
- hidden files are only suggested when the typed name starts with `.`
- directories get a trailing path separator so you can continue completing into them
- files at end-of-line get a trailing space (dirs do not)
- cap suggestion list size to avoid pathological directories

**Why**: path completion is one of the fastest ways to make the command bar feel “real” in daily use, and the suggestion-session model means we can *cycle* candidates instead of committing to the first match.

**Tests**: add a headless test that creates a temp directory and validates unique-dir, unique-file, and multi-candidate cycling behavior.

## rev28 (2026-02-26)

### D080 — Quote-aware path completion for `open` / `save` / `cd`

**Decision**: extend filesystem path completion to handle paths that require quoting.

- If the user started a quoted token (single or double quotes), completion happens *inside* that quote style.
- If the user did not start a quote token, but a completion contains whitespace or a double quote, completion auto-wraps it in **double quotes** and escapes internal `\\` and `"`.
- For directory completions when quoting is active, we keep the closing quote **open** so users can keep tabbing into the directory.
- If the user already typed a closing quote, we preserve it (even for directories).

**Why**: micro’s command bar follows `/bin/sh`-style quoting rules, and real-world usage frequently involves paths with spaces. Quote-aware completion prevents “completion works, execution fails” footguns.

**Tests**: add headless tests for auto-quoting a space-containing file, auto-quoting a space-containing directory (and continuing completion), preserving an explicit closing quote for directories, and escaping embedded double quotes.

## rev29 (2026-02-26)

### D081 — Micromax-defined command-bar commands (`ed.cmd-add`)

**Decision**: expose a minimal hostcall that lets micromax scripts define command-bar commands.

- Hostcall: `ed.cmd-add` with stack effect `( xt name doc -- ok )`.
- The command xt is executed as `( args -- ... )` where `args` is a list of strings.
- If the xt leaves an int/bool on top of the stack, it is treated as an ok flag; otherwise ok defaults to 1.
- Commands are replaceable/reloadable: registering the same name overwrites the previous definition.
- Best-effort provenance: attach a `Span` (via `vm.last_span`) so `help <cmd>` can show where a command was registered.

**Why**: micro’s plugin API has an explicit “make a command” call (`MakeCommand`) and it’s a key bridge from scripting to real UX. We need the same bridge to make micromax the *native* config/plugin system rather than a sidecar macro language.

**Tests**: add headless tests for add/exec/help/provenance/remove.

### D082 — Prompt completion hook (`ed.complete.*`) with additive/replace modes

**Decision**: allow micromax scripts to supply prompt completion candidates without UI entanglement.

- Lookup order: `ed.complete.<cmd>` then `ed.complete`.
- Contract: `( cmd tok_i prefix toks -- cands mode )`
  - `cands` is a list of insertion strings
  - `mode`: 0 none, 1 add, 2 replace
- The editor merges these candidates into the existing suggestion-session machinery.

**Why**: Kakoune’s shift toward a dedicated completion configuration command (`complete-command`) demonstrates that completion wants to be *customizable* separately from command definition. Providing a tiny, scriptable hook now keeps us compatible with that “completion is its own thing” philosophy.

**Tests**: add a headless test exercising command-specific completion and Tab/Shift-Tab cycling.

### D083 — `here-span` + `vm.last_span` as provenance substrate

**Decision**: track the VM’s most recent executed span (`vm.last_span`) and expose it as a primitive `here-span`.

**Why**: embeddings often need to attach “where did this come from?” to dynamic registrations (commands, hooks, bindings). A tiny, best-effort span signal helps debugging and keeps the archive friendly to future tooling.

**Tests**: add a unit test that `here-span` returns `[file line col]`.

## rev30 (2026-02-26)

### D084 — Keybindings carry best-effort provenance and are removable

**Decision**: treat editor keybindings as small records instead of bare strings.

- `Keymap` now stores `key`, `action_spec`, and optional `span`.
- `ed.bind` attaches `vm.last_span` as best-effort provenance.
- Add `ed.unbind` and `ed.bindings` hostcalls.
- Improve `showkey` so it reports provenance when available.
- Add a user-facing `unbind KEY` command.

**Why**: the editor roadmap explicitly wants transparent keybinding introspection: users and plugins should be able to answer “what does this key do right now?” and “where did that binding come from?” without a UI-specific debugger.

**Tests**: add headless tests covering script-defined bindings, `showkey` provenance, `ed.bindings`, and `unbind`.

## rev31 (2026-02-26)

### D085 — Hook definitions and handler registrations carry best-effort provenance

**Decision**: extend hook words with tiny debugging metadata while keeping execution semantics unchanged.

- `HookWord` now records the definition span.
- `hook-add` stores handler entries as `{xt, span}` internally.
- `hook@` stays backward-compatible and returns a plain xt list.
- Add `hook-rows NAME` returning `[[handler-name [file line col]|0] ...]`.
- Extend `xt-span` so hook words participate in the same provenance story as colon words and quotations.
- Add an editor command-bar command `showhook NAME` for headless inspection of installed handlers.

**Why**: once commands and keybindings gained provenance, hooks became the obvious remaining blind spot. Editor/plugin systems only stay pleasant if users can answer “what is attached here right now, and where did it come from?” without reverse-engineering the whole config.

**Tests**: add unit tests for `hook-rows`, `xt-span` on hook words, backward-compatible `hook@`, and editor `showhook`.

## rev32 (2026-02-26)

### D086 — Statusline/infobar state is a shared headless model, not a UI-specific string

**Decision**: expose editor status as portable data first.

- Add `Editor.status_model()` returning a small map of shared editor state.
- Add hostcalls:
  - `ed.status` → portable map
  - `ed.status-summary` → deterministic debug/headless summary string
- Add a user-facing command-bar command `showstatus`.

The model currently includes:

- file/buffer identity (`buffer_name`, `file_name`, `path`, `cwd`)
- dirty/read-only state
- cursor/selection state
- prompt state
- macro recording/playback flags
- last message

**Why**: we want future UIs to render shared semantics instead of each one inventing its own notion of “current status”. Helix’s explicit left/center/right statusline element model is a good reminder that render layout should be configurable, while micro’s statusline-as-real-editor-surface reminds us that even a tiny terminal editor should treat that line as meaningful state, not an afterthought.

**Tests**: add headless tests for `ed.status`, `ed.status-summary`, and `showstatus`.


## rev33 (2026-02-26)

### D087 — Hook handlers may carry a group tag; plugin reload cleans grouped handlers automatically

**Decision**: extend hook registrations with an optional string **group** while keeping plain `hook-add` source compatible.

- `HookHandler` now carries `{xt, span, group}` internally.
- `hook-add` uses `vm.current_hook_group` as a best-effort default group.
- Add:
  - `hook-group!` / `hook-group@` — set/query the default group
  - `hook-groups NAME` — list unique groups on a hook
  - `hook-rm-group NAME` — remove only matching grouped handlers from one hook
  - `hook-detail NAME` — `[[handler-name group|0 span|0] ...]`
- `showhook NAME` now shows `handler#group@file:line:col` when available.
- `PluginManager` evaluates plugin code/lifecycle words with `current_hook_group = "plugin:<name>"` and removes that group on unload/reload.

**Why**: Kakoune's `remove-hooks` group model is a good proof that dynamic hook ecosystems need cheap grouped cleanup. micro's reload-friendly lifecycle makes the same pressure visible from the plugin side: repeated load/unload cycles should not leave stale callbacks behind.

**Tests**: add unit tests for `hook-detail`, `hook-rm-group`, current group state, and plugin reload/unload cleanup of grouped hook handlers.

## rev34 (2026-02-26)

### D088 — Editor commands and keybindings get registration groups

**Decision**: mirror the successful hook-group pattern for the editor bridge.

- `Command` now stores optional `group` metadata.
- `Binding` now stores optional `group` metadata.
- New editor hostcalls:
  - `ed.group!` / `ed.group@` — set/query the default editor registration group
  - `ed.cmd-rows` — `[[name doc group|0 [file line col]|0] ...]`
  - `ed.binding-detail` — `[[key action-spec group|0 [file line col]|0] ...]`
- `ed.cmd-add` and `ed.bind` attach `vm.current_editor_group` as a best-effort group tag.
- `help <cmd>`, `showcmd`, and `showkey` now include group metadata when present.

**Why**:
- plugin reload/unload needs a cheap way to tear down dynamic registrations
- commands and bindings are part of the live editor environment, so they should be inspectable data
- this keeps future mode/layered-keymap work compatible with today’s metadata shape

### D089 — PluginManager cleans grouped editor registrations on unload/reload

**Decision**: the reference `PluginManager` now sets `vm.current_editor_group = "plugin:<name>"` while evaluating plugin source and lifecycle words, and removes grouped commands/bindings on unload.

- `install_editor_hostcalls()` sets `vm.editor_owner = ed` as a best-effort cleanup backpointer.
- `PluginManager.unload()` now removes:
  - grouped hook handlers (`remove_hook_group`)
  - grouped command-bar commands (`command_dispatcher.remove_group`)
  - grouped keybindings (`keymap.remove_group`)

**Consequence**: reloads can safely replace commands/bindings without stale registrations surviving from old plugin revisions, even though the prototype loader still does not garbage-collect plugin wordlists.

**Tests**: add focused tests for group query/detail rows and plugin reload cleanup across commands + keybindings.



### D090 — keybindings gain a small mode/layer system with global fallback

**Decision**: add named keymap modes to the editor core, but keep the model deliberately
small: bindings now carry a `mode` string, the editor keeps an active key mode stack, and
lookup resolves **topmost active mode first, then global**.

New surface:
- command-bar: `bindmode`, `unbindmode`, `keymode`, `pushkeymode`, `popkeymode`, `showkeymodes`
- hostcalls: `ed.bind-mode`, `ed.unbind-mode`, `ed.binding-modes`, `ed.keymode!`, `ed.keymode@`, `ed.keymode-push`, `ed.keymode-pop`, `ed.keymodes`
- status model: `keymode` field

**Why**:
- real editors layer keymaps by context
- this unlocks transient/plugin-owned maps without committing to a full modal UI
- `showkey` can now answer "what does this key do *right now*?" more honestly
- grouped plugin cleanup continues to work because mode bindings use the same metadata path

**Non-goal**: this is not yet a full Helix/Kakoune/Emacs mode architecture. It is a compact, portable substrate that future minor/transient modes can build on.

## rev36 (2026-02-26)

### D091 — Add one-shot keymodes and centralize key dispatch

**Decision**: keep the existing named keymode stack, but allow entries to be either
persistent or **one-shot**.

New surface:
- editor core:
  - `Editor.dispatch_key(key)` — resolve + execute a key through active keymodes
  - active keymode rows now include a one-shot flag
- command-bar:
  - `pushkeymode-once MODE`
  - `showkeymodes` marks one-shot modes with `!`
- hostcalls:
  - `ed.keymode-push-once`
  - `ed.keymode-rows` — `[[mode once?] ...]`
  - `ed.press-key`
- status model:
  - `keymode_once`

**Semantics**:
- the topmost one-shot mode gets first crack at the next key
- if it has a binding for that key, the binding runs and the mode pops
- if it does not, the mode pops and lookup falls through to remaining modes/global
- persistent modes behave as before

**Why**:
- Helix minor modes and Kakoune next-key contexts both show the value of short-lived
  layered keymaps
- Emacs `set-transient-map` is the classic proof that “one (or more) subsequent keys”
  is a useful editor primitive
- centralizing key dispatch keeps future UIs and tests from open-coding
  `resolve_key_binding()` + `run_action_chain()` and accidentally bypassing keymode
  semantics

**Non-goal**: this is not yet a full multi-key parser or timeout-based prefix-map system.
It is a compact, deterministic substrate for future transient maps.


## rev37 (2026-02-26)

### D092 — Add keymap discovery / whichkey-style inspection surfaces

**Decision**: keep bindings as simple records, but add a tiny discovery surface that can answer both:

- what bindings exist in one mode?
- what bindings are currently reachable after active keymode precedence is applied?

New surface:
- hostcalls:
  - `ed.binding-rows-for` — exact bindings for one mode
  - `ed.available-bindings` — precedence-resolved current keymap
  - `ed.resolve-key` — machine-readable sibling of `showkey`
- command-bar:
  - `showbindings [MODE|active]`
  - `whichkey` (alias for active binding discovery)

**Why**:
- once transient keymodes exist, users/scripts need a cheap answer to “what can I press right now?”
- discovery should live in the headless core as data, not as a popup/UI commitment
- this keeps future Rust/WASM or alternate UIs free to render the same semantics differently

**Non-goal**: this is not yet a timeout-driven prefix parser or popup contract. It is a small, deterministic inspection layer over the existing keymap model.


## rev38 (2026-02-26)

### D093 — Add binding descriptions / docstrings as data, not UI chrome

**Decision**: keep keybindings as simple records, but let them carry an optional
**human description** (`desc`) in addition to the exact action spec.

New surface:
- keymap/editor core:
  - bindings now optionally carry `desc`
  - `Editor.binding_desc(binding)` derives a fallback label from command/action docs
- hostcalls:
  - `ed.bind-doc` / `ed.bind-mode-doc`
  - `ed.binding-info-for`
  - `ed.available-binding-info`
  - `ed.resolve-key-info`
- command-bar:
  - `binddoc KEY DOC...`
  - `bindmodedoc MODE KEY DOC...`
  - `whichkey` now prefers human descriptions over raw action specs
  - `showkey` now includes `[desc ...]` when available

**Why**:
- raw action chains are truthful but noisy; discovery surfaces should be able to show
  short human labels
- Kakoune mapping docstrings and Emacs `which-key` descriptions both point toward
  “binding help text belongs with the binding”, not in a UI-only lookup table
- derived fallback labels from command/action docs keep the feature immediately useful
  even before scripts start attaching custom descriptions

**Non-goal**: this is not a popup contract or a full prefix-menu system. It is a
small metadata layer that keeps discovery surfaces portable and testable.


### D094 — Add tiny first-class prefix-map helpers on top of one-shot keymodes

**Why**
- One-shot keymodes already made prefix-style maps *possible*.
- In practice, scripts had to hand-write `command:pushkeymode-once MODE,command:whichkey`, which was correct but noisy.
- A tiny named helper makes the feature much easier to discover without introducing a new binding class or UI commitment.

**Decision**
- Add command-bar `prefixmode MODE` to push a one-shot mode and immediately show reachable bindings.
- Add command-bar `bindprefix KEY MODE [DOC...]` for the common “global prefix key” case.
- Add hostcalls:
  - `ed.prefix-mode`
  - `ed.bind-prefix`
- Keep prefix bindings represented as ordinary bindings whose action-spec is `command:prefixmode MODE`.

**Why this shape**
- Preserves portability: prefix maps remain keymap data, not a special runtime object.
- Preserves discoverability: `showkey`, `ed.resolve-key-info`, and `whichkey` all keep working unchanged.
- Preserves reload hygiene: prefix bindings still use the normal grouping/provenance machinery.

**Tests**
- Add focused tests for `ed.bind-prefix`, `prefixmode`, `bindprefix`, dispatch through a prefix key, and one-shot pop behavior after the next matching key.


## rev40 (2026-02-26)

### D095 — Add mode-local prefix-map helpers on top of one-shot keymodes

**Why**
- Global prefix helpers (`bindprefix`, `ed.bind-prefix`) made leader-style menus easy,
  but configs still had to hand-write mode-local prefix bindings.
- Helix/Kakoune-style nested minor modes strongly suggest that “prefix inside one
  mode enters another short-lived key layer” is a normal editor pattern, not a
  special UI feature.
- Keeping this as sugar over ordinary bindings preserves all the introspection and
  cleanup work already in the repo.

**Decision**
- Add command-bar `bindmodeprefix OWNERMODE KEY MODE [DOC...]`.
- Add hostcall `ed.bind-mode-prefix`.
- Keep the resulting binding as an ordinary mode-local keymap row whose action-spec
  is `command:prefixmode MODE`.

**Why this shape**
- Preserves portability: still just strings / ints / lists on the wire.
- Preserves discoverability: `showkey`, `ed.resolve-key-info`, and `whichkey` keep
  working unchanged.
- Preserves reload hygiene: grouped/provenance-aware binding cleanup still applies.

**Tests**
- Add focused tests for hostcall creation, command-bar creation, resolution only in
  the owner mode, and dispatch into a one-shot target mode.


## rev41 (2026-02-26)

### D096 — Add deterministic fuzzy fallback to command-bar completion for command-ish tokens

**Why**
- micro’s command prompt establishes the baseline expectation that `Tab` should complete commands/options/paths.
- Helix’s picker model shows that fuzzy matching is an ergonomic default when users are searching named editor surfaces rather than spelling exact prefixes.
- The repo roadmap already called out “fuzzy + argument completion” as low-hanging fruit, but full fuzzy-open/path search would be a bigger UX commitment.

**Decision**
- Keep the existing completion contract and suggestion-session model.
- For built-in **command-ish** completion sources (`command`, `help`, `set/show/toggle`, `plugin`, `macro`):
  - try **exact prefix** matches first
  - if that yields nothing, fall back to a tiny **subsequence fuzzy matcher**
  - rank fuzzy hits deterministically: contiguous substring hits first, then earlier/tighter/boundary-friendlier matches, then shorter names
- Keep filesystem path completion for `open` / `save` / `cd` explicitly **prefix-based** for now.
- When fuzzy fallback is active, headless messages say `fuzzy:` / `fuzzy matches:` so tests and future UIs can tell what happened.

**Why this shape**
- Preserves the current mental model for users who already rely on exact-prefix `Tab`.
- Makes command discovery more forgiving without silently turning path completion into a file picker.
- Keeps the implementation tiny, inspectable, portable, and easy to reproduce in future Rust/WASM ports.

**Tests**
- Add focused tests for:
  - unique fuzzy command completion
  - multiple fuzzy command matches + cycling
  - help-topic fuzzy ranking that prefers camel-boundary-style matches


## rev42 (2026-02-26)

### D097 — Extend prompt completion to a few high-value argument surfaces before inventing previews

**Why**
- The fuzzy fallback added in rev41 made command discovery more forgiving, but the next obvious friction point was after the command name: users still had to remember option values, keymode names, and inspection topics.
- Neovim’s command-line completion docs are explicit that completion is useful across **different categories** (command names, files, option names, etc.), which reinforces that argument completion should be treated as a normal command-line concern rather than a special UI feature.
- Kakoune’s `complete-command` model is a good reminder that completion policy should stay tied to commands / argument slots, not hidden in a popup implementation.

**Decision**
- Keep the existing prompt suggestion-session contract unchanged.
- Add small built-in completion for a few argument slots that are already stable and inspectable:
  - `set` / `setlocal OPTION VALUE` → built-in bool/enum values
  - `keymode` / `pushkeymode` / `pushkeymode-once` / `prefixmode` → known keymode names
  - `showbindings` → `active` plus known keymode names
  - `bindmode` / `bindmodedoc` / `unbindmode` / `bindmodeprefix` mode slots → known keymode names
  - `showcmd` → command names
  - `showhook` → hook names visible in the current VM
- Reuse the same exact-prefix-first + tiny fuzzy fallback policy for these command-ish argument surfaces.
- Do **not** add a preview/metadata channel yet; keep completion output as plain candidate strings until we need richer UI contracts.

**Why this shape**
- Captures a lot of ergonomic value without widening the prompt/session data model.
- Keeps path completion, option/value semantics, and mode discovery all explicit and testable in the headless core.
- Makes future previews easier to add later because the candidate-source boundaries are now clearer.

**Tests**
- Add focused tests for enum/bool option value completion.
- Add focused tests for keymode-name completion and `showbindings active|MODE` completion.
- Add focused tests for `showhook` topic completion.



## rev43 (2026-02-26)

### D098 — Extend prompt completion into `bind` / `bindmode` action specs

**Why**
- After rev42, the next obvious command-bar friction point was keybinding authoring: `bind` and `bindmode` still required users to remember action names and `command:` / `command-edit:` syntax from memory.
- micro’s keybindings docs make those right-hand-side action specs a first-class user surface, not an implementation detail.
- Reusing the existing command completion logic inside `command:` bindings keeps the model smaller and more portable than inventing a separate “binding RHS” completion engine.

**Decision**
- Keep the existing prompt suggestion-session contract unchanged.
- Add built-in action-spec completion for:
  - `bind KEY ACTIONSPEC`
  - `bindmode MODE KEY ACTIONSPEC`
- Complete plain editor action names in those slots.
- Treat `command:` and `command-edit:` as first-class completion prefixes.
- If the current binding action-spec starts with `command:` / `command-edit:`, reuse the ordinary command-ish completion rules for the embedded command line.

**Why this shape**
- Makes keybinding authoring much more discoverable without widening the prompt/session data model.
- Keeps bindings inspectable as ordinary action-spec strings.
- Reuses the existing slot-aware command completion logic instead of forking a second completion policy.

**Tests**
- Add focused tests for:
  - `bind` action-name completion
  - `bind` `command:NAME` completion
  - nested command-argument completion inside a binding (`command:showbindings a`)
  - `bindmode` `command-edit:NAME` completion


## rev44 (2026-02-26)

### D099 — Add prompt suggestion metadata rows without changing the completion/session contract

**Why**
- After rev43, the next obvious improvement was not “more candidates” but “better context”: future UIs and micromax-side tools need to know *what* a suggestion is (command, option, action, file, keymode) and often want a tiny annotation (doc/current value/etc.).
- Neovim’s completion APIs are a useful precedent: completion items carry fields like `word`, `menu`, `kind`, and `info`, and UI rendering is treated as a separate concern.
- Kakoune’s `complete-command` docs reinforce that completion policy is attached to command argument structure, while menu presentation stays downstream.

**Decision**
- Keep `Prompt.suggestions` and the existing suggestion-session/cycling semantics unchanged.
- Add a parallel best-effort metadata surface for active suggestion sessions:
  - `Prompt.suggestion_rows`
  - row shape: `[insert, kind, menu, info]`
- Expose the rows to micromax via a new hostcall:
  - `ed.prompt-suggestion-rows`
- Populate rows for the current built-in completion surfaces where we already have useful context:
  - commands / actions / hooks / keymodes / plugins / macro slots
  - option names with kind/current/default/doc summaries
  - option values with small “current value” hints
  - binding RHS prefixes / embedded `command:` suggestions
  - path suggestions as `file` / `dir`
- Keep plugin-provided completion candidates string-only for now; if they do not supply richer metadata, rows fall back to blank annotations.

**Why this shape**
- Future terminal or GUI layers can show a richer completion list without forcing a UI decision into the headless core.
- Existing tests, keybindings, and prompt behavior remain stable because insertion/cycling still runs on plain strings.
- The row format is tiny, portable, and easy to mirror in future Rust/WASM ports.

**Tests**
- Add focused tests for command suggestion docs, option suggestion metadata, binding-RHS command docs, and file/dir suggestion kinds.



## rev45 (2026-02-26)

### D100 — Add a tiny second layer of quotation combinators in stdlib, not as VM primitives

**Why**
- The current stdlib already proved the pattern with `dip` and `keep`: small quotation combinators can buy a lot of ergonomics without widening the primitive VM surface.
- Factor’s docs are a strong precedent that `2dip` / `2keep` belong in the same “preserving combinators” family, and that `bi` / `tri` can be defined compositionally in terms of simpler words.
- Joy and Retro both reinforce the same broader lesson: a concatenative language becomes much nicer to script once there are a few standard quotation combinators that reduce stack gymnastics.
- This is especially relevant for Micromax because the editor is meant to become the first serious target; config/plugin scripts will benefit from these patterns quickly.

**Decision**
- Extend `src/micromax/stdlib/core.mx` with:
  - `2dip`
  - `2keep`
  - `bi`
  - `tri`
- Keep them as ordinary stdlib definitions rather than VM primitives.
- Record them in the portability ledger as part of the portable stdlib surface.
- Update tutorial/cookbook/examples so future humans/LLMs see these as intended building blocks, not obscure trivia.

**Why this shape**
- Keeps the VM tiny and inspectable.
- Makes the new words easy to port because their behavior is visible in ordinary Micromax source.
- Avoids prematurely committing to a much larger combinator zoo before real editor scripts demonstrate the need.
- Preserves the project rule that convenience words land in stdlib first whenever possible.

**Tests**
- Add focused tests for `2dip` / `2keep` stack behavior.
- Add focused tests for `bi` / `tri` cleave behavior.


## rev46 (2026-02-26)

### D101 — Add doc-first stack-effect introspection instead of a checker

**Why**
- Earlier research already suggested the right ordering: declarations/comments first, interactive inspection second, optional validation last.
- Gforth’s tutorials reinforce that stack-effect comments are baseline readability, not exotic machinery.
- Factor’s reflective tools (`stack-effect`, `infer`, `effect>string`) are a strong precedent for making stack effects available to users and tools even before committing to a heavyweight checking subsystem.
- Micromax now has enough word introspection (`xt-kind`, `xt-src`, `xt-span`, `help`, `see`) that stack effects were the obvious missing piece.

**Decision**
- Add `xt-effect ( xt -- s )` returning a canonical effect string or `""`.
- Tighten `xt-doc` so it returns the descriptive doc text *without* duplicating a leading stack effect.
- Add row-based dictionary inspection:
  - `words-rows ( -- rows )`
  - `wid-word-rows ( wid -- rows )`
  - row shape: `[name kind effect doc wid wl]`
- Teach colon-definition doc capture to split leading stack-effect comments from descriptive comments while keeping ordinary docs simple.
- Update `help` / `see` to show effect + summary separately.

**Why this shape**
- Gives future UIs, scripts, and LLMs a stable inspection surface without forcing checker semantics into the runtime.
- Keeps the VM tiny: effects remain strings, not a new runtime type.
- Makes stdlib words and colon definitions participate in the same tooling story as primitives.
- Preserves the project’s portability story because the row/data surfaces are plain lists/strings.

**Tests**
- Extend introspection tests for `xt-effect` and cleaned-up `xt-doc`.
- Add tests for `words-rows` and `help` output with separated effect/doc text.
- Verify stdlib combinators expose their effect metadata through the same surface.

### D119 — Editor help falls back to visible Micromax words; add `showword`

**Problem**: rev46 added good VM-side metadata (`xt-effect`, `xt-doc`, `words-rows`), but the editor command bar still treated help as if only editor commands/actions were real topics. That made the live environment feel split: language introspection lived in the REPL, editor discovery lived in the prompt.

**Why now**:
- micro’s command-bar docs treat `help` and prompt completion as real discovery surfaces, not just a string parser.
- Gforth’s word index shows the usefulness of presenting words as *rows with metadata* (name, effect, wordset) rather than raw dumps.
- Factor’s help system / `apropos` reinforces that named words should be searchable topics in the live environment.

**Decision**:
- Keep editor `help` behavior stable for editor commands/actions first.
- If no editor command/action matches, fall back to the **currently visible Micromax word** from the active search order.
- Add `showword NAME` as the explicit editor-side inspection command for VM words.
- Extend command-bar completion so:
  - `help` includes visible Micromax word names
  - `showword` completes visible Micromax word names
  - prompt suggestion rows for those topics include best-effort word metadata (`kind`, `wordlist`, `effect`, doc summary)

**Implementation notes**:
- Reuse the VM’s current search order via `find_word_with_wid()` / `all_words_view()` rather than inventing a parallel editor registry.
- Keep the output intentionally small: `word NAME [kind] ( effect ) [wl NAME]: summary (defined at file:line:col)` when data is available.
- Do not attempt a full help browser or word picker yet. This is reflective plumbing and command-bar ergonomics, not UI commitment.

**Tests**:
- `help NAME` falls back to a visible Micromax word and includes effect/doc/provenance.
- `showword NAME` reports the visible word with wordlist/effect/doc/provenance.
- prompt completion for `showword` returns word candidates and suggestion-row metadata.

**Consequence**: the editor now feels more like the actual Micromax environment. Word metadata is available from both the REPL and the command bar, and the next obvious step (if needed) is a small picker/browser on top of the same row data rather than more bespoke plumbing.



### D120 — Add `apropos QUERY` and row-first editor topic discovery

**Context**: rev47 made visible Micromax words first-class help topics (`help NAME` fallback, `showword NAME`), but discovery still assumed you mostly knew the exact topic name already. The roadmap’s next obvious step was “a tiny searchable word/help picker”, but a real picker would have been a UI commitment rather than a headless-core improvement.

**Decision**:

- Add `Editor.help_topic_rows()` returning shared `[[name kind menu info] ...]` rows for command-bar commands, actions, and visible Micromax words.
- Add `Editor.apropos_rows(query)` using the existing tiny deterministic subsequence ranking used by prompt completion.
- Add command-bar command `apropos QUERY` that prints a ranked preview of matching topics.
- Add hostcalls:
  - `ed.topic-rows` — all searchable topics as rows
  - `ed.apropos-rows` — ranked rows for a query
- Let prompt completion treat `apropos` arguments like `help` topics, so exact-prefix and small fuzzy completion still work there too.

**Why**:

- Factor’s `apropos` is the clean precedent: searchable help/word discovery by subsequence before any heavyweight browser.
- Neovim shows that searchable help/index surfaces (`:help`, `:helpgrep`, command indexes) remain useful even without a unified picker abstraction.
- Helix’s fuzzy pickers are a reminder that search-first discovery is ergonomic, but a picker is a *separate* UX layer that should sit on top of stable row data rather than be the first implementation step.

**Consequence**: Micromax-editor now has a search-first discovery surface that stays completely headless and scriptable. Future UIs/LLMs can build a picker/browser on top of `ed.topic-rows` / `ed.apropos-rows` without inventing another metadata path, while ordinary users immediately get `apropos QUERY` in the command bar.


### D121 — Let Micromax completion hooks return suggestion rows

**Context**: rev44 introduced prompt suggestion metadata rows (`[insert kind menu info]`) for built-in completion surfaces, and rev48 added row-first topic discovery. But Micromax-defined completion hooks (`ed.complete.<cmd>` / `ed.complete`) still only returned plain candidate strings, which meant plugin commands looked second-class in any future UI/tooling that wanted docs/kinds/current-value hints.

**Decision**:

- Keep the original completion-hook contract working:
  - `( cmd tok_i prefix toks -- cands mode )`
- Add an optional richer contract:
  - `( cmd tok_i prefix toks -- cands rows mode )`
- `rows` uses the same aligned row shape already used elsewhere in the editor prompt:
  - `[insert kind menu info]`
- When plugin rows are present, overlay them onto the editor's best-effort inferred rows by insertion string.
- When rows are omitted, keep the current fallback behavior: infer what we can from the final candidate list and leave the rest blank.

**Why**:

- Neovim is a clean precedent for structured completion items (`word`, `kind`, `menu`, `info`) that are separate from the popup UI itself.
- Helix's picker/completion docs reinforce that the UI layer should sit on top of stable item metadata rather than be the first implementation step.
- Micromax already had the right row contract internally; the missing piece was simply letting plugin-provided candidates participate in it.

**Implementation notes**:

- `_mx_prompt_completion_candidates()` now accepts both 2-result and 3-result contracts and normalizes rows to at most four strings per candidate.
- `prompt_complete()` still computes its usual built-in/path metadata rows, then overlays plugin rows on top so plugins can either replace blank metadata or deliberately override built-in hints.
- Replace-mode plugin completion clears `path_mode`; path-specific metadata should only come from actual path completion, not be guessed for arbitrary plugin candidates.

**Tests**:

- A plugin completion word can return `cands rows mode` and those rows appear through `ed.prompt-suggestion-rows`.
- Plugin rows can overlay an existing built-in candidate's metadata without duplicating the candidate.
- Existing `cands mode` tests remain green, preserving backward compatibility.

**Consequence**: custom Micromax commands now participate in the same completion metadata surface as built-ins. That makes future picker/tooltip UIs, REPL helpers, and LLM-facing tooling simpler because they can consume one row language instead of special-casing plugin completions.


### D122 — Make `apropos` summary-aware and use it for failed `help` lookups

**Context**: rev48 added `apropos QUERY` and row-first topic discovery, but matching still looked only at the topic name. That meant the command bar had search-first discovery in principle, yet obvious descriptive queries like “visible micromax” or typo recovery from `help shwrd` still underperformed unless the user already knew the right name.

**Decision**:

- Keep `apropos` **name-first** using the existing tiny deterministic subsequence matcher.
- If the topic name does not match, fall back to the row's summary/doc text (`menu` + `info`) before giving up.
- Reuse the same `apropos` ranking path when `help NAME` fails to find an exact command/action/word, and show a short “Try: ...” suggestion list.
- Do not add a picker/browser yet; keep this improvement entirely in the headless command/row layer.

**Why**:

- Neovim's `:help` / `:helpgrep` split is a strong reminder that “look up this exact topic” and “search the help corpus” are distinct needs, and both matter.
- Helix's command palette/picker model reinforces that search-first discovery is useful, but the picker should sit on top of stable search data rather than be the first implementation step.
- Micromax already had the row model (`[name kind menu info]`); broadening the search policy was cheaper and more composable than inventing a new UI surface.

**Implementation notes**:

- `Editor.apropos_rows()` now uses `_apropos_row_sort_key()`:
  - exact/fuzzy name matches rank first
  - summary/doc substring matches rank after that
  - summary/doc fuzzy matches rank after that
- `c_help` now calls `ed.apropos_rows(topic, limit=4)` on an exact-lookup miss and shows a short preview of likely topics.

**Tests**:

- `apropos visible micromax` now finds `showword` by its summary text.
- `ed.apropos-rows` exposes the same behavior through the hostcall surface.
- `help shwrd` now returns a short suggestion list instead of only `No help for: shwrd`.

**Consequence**: command-bar discovery is noticeably more forgiving without adding UI weight. Future pickers/LLM tools still consume the same row-first topic surface, but ordinary users now get better help search and typo recovery immediately.


### D123 — Add a dedicated searchable topic prompt on top of topic rows

**Context**: rev48-50 established the right substrate for discovery (`help_topic_rows`, `apropos_rows`, summary-aware search, and prompt suggestion rows), but there was still no *single headless interaction model* that felt like a command palette/help picker. Future UIs or scripts had to assemble that lifecycle themselves.

**Decision**:
- Add a new prompt kind: `topic`.
- Add `Editor.enter_topic_prompt(query="")` which preloads ranked topic rows into the ordinary prompt suggestion-session model.
- Add command-bar command `topicpick [QUERY]`, action `TopicPrompt`, and hostcall `ed.topic-prompt`.
- Let `Tab` / `Shift-Tab` cycle ranked topic candidates inside the topic prompt using the existing prompt machinery.
- On submit, open help for the selected topic (or the best-ranked topic for the current query).

**Why**:
- Helix treats pickers as a distinct UI with its own keymap, which suggests Micromax should first define the *state machine* cleanly before worrying about terminal rendering.
- VS Code’s Command Palette and Quick Pick guidance reinforce that one searchable surface for commands/topics is valuable, and that each item should carry small contextual metadata (`description`, `detail`) rather than be a bare string.
- Micromax already had the row shape (`[insert kind menu info]`) and ranking path; the smallest useful step was to reuse them in a dedicated prompt kind instead of inventing a separate browser abstraction.

**Implementation notes**:
- `Editor.prompt_complete()` now supports `prompt.kind == "topic"` in addition to ordinary command prompts.
- Topic prompts use `help_topic_rows()` / `apropos_rows()` directly and keep the query text as `suggest_base`, so the first Tab reveals/caches ranked rows and later Tab/Shift-Tab cycles them predictably.
- Topic-prompt submission records topic history under prompt kind `topic`, which means history recalls the submitted selection/query rather than trying to preserve a pre-selection partial query.

**Consequence**: the editor now has a tiny, genuinely usable, search-first discovery prompt without committing to a heavyweight browser UI. Future UIs/LLMs can still consume `ed.topic-rows` / `ed.apropos-rows` directly, but there is now also a canonical headless interaction flow for “open a topic/help picker and choose something.”


## rev52 (2026-02-26)

### D124 — Make the topic prompt live-updating and expose the active suggestion row

**Context**: rev51 added a dedicated `topic` prompt on top of topic rows, but it still behaved too much like ordinary command-line completion: once the query text changed, the suggestion session was cleared and external tooling had no canonical way to ask “what item is currently selected?” That was enough for tests, but not yet a great substrate for a future command palette/help browser.

**Decision**:
- Centralize prompt text mutation through `Editor.set_prompt_text()` so prompt-specific side effects are explicit.
- Preserve existing `find` behavior (`incsearch` still re-runs on text changes).
- Make `topic` prompts re-run ranking automatically whenever the query text changes.
- Add `Editor.prompt_current_row()` and hostcall `ed.prompt-current-row` returning the selected `[insert kind menu info]` row (or `[]`).
- Keep the ordinary `Prompt` data model tiny; do not add a separate preview/browser object yet.

**Why**:
- Helix pickers are interactive filtered lists with their own keymaps, which suggests the core should expose “query changes update the ranked rows” before worrying about terminal rendering.
- VS Code Quick Pick guidance is a strong reminder that items usually want lightweight metadata (`description`/`detail`) and a notion of the *currently active item* even when the picker UI is otherwise simple.
- Vim's completion docs (`completeopt` preview / popup) reinforce that previewing extra information is a downstream UI concern that depends on the current item; that makes “what is the active row?” the right headless primitive, not a hard-coded preview widget.

**Consequence**: the topic prompt now behaves more like a genuine search picker while staying fully headless. Future TUIs/LLMs can render a side preview or statusline detail from `ed.prompt-current-row` without having to duplicate topic ranking or selection logic.


### D125 — Add grouped topic sections and compact current-item previews

**Context**: rev52 made the topic prompt live-updating and exposed the active row, but two obvious follow-ups remained for future UIs/LLMs: (1) many picker UIs want coarse grouping such as commands vs actions vs words, and (2) statuslines/preview panes want a small “current item” summary string without every downstream consumer reassembling one by hand.

**Decision**:
- Add grouped topic-section helpers:
  - `Editor.help_topic_section_rows()`
  - `Editor.apropos_section_rows(query)`
- Expose them as hostcalls:
  - `ed.topic-section-rows`
  - `ed.apropos-section-rows`
- Add compact current-item helpers:
  - `Editor.prompt_current_section()`
  - `Editor.prompt_current_preview()`
- Expose those as hostcalls too:
  - `ed.prompt-current-section`
  - `ed.prompt-current-preview`
- Mirror the same prompt-current fields into the portable status model so future statuslines/infobars do not need bespoke picker plumbing.

**Why**:
- VS Code Quick Pick explicitly supports separators for “multiple obvious groups of selections”, which is a good precedent for exposing coarse sections before building a richer UI.
- VS Code’s command presentation docs also reinforce that command/category grouping is a meaningful discovery aid, not just decoration.
- Helix pickers keep preview behavior as a separate concern (`Ctrl-t` toggles preview), which supports Micromax exposing the *data needed for previews* rather than baking in a preview widget.
- Neovim’s completion model similarly distinguishes short menu text from longer info text and exposes the currently selected completion item structurally.

**Consequence**: the topic/help picker substrate is now noticeably friendlier to inherit. Future TUIs/LLMs can render grouped sections and preview/status text directly from stable host surfaces instead of reverse-engineering ranking output or inventing a parallel grouping model.


## rev54 (2026-02-26)

### D126 — Add a searchable current-binding prompt on top of resolved binding rows

**Context**: rev51-53 established a solid headless substrate for searchable topic discovery (`topicpick`, row metadata, current-item previews, grouped sections). A nearby discovery problem remained on the keybinding side: the editor already had `whichkey`, `showbindings`, and machine-readable binding rows, but there was still no canonical *search-first* flow for inspecting the currently reachable keymap.

**Decision**:
- Add a new prompt kind: `binding`.
- Add command-bar command `bindingpick [QUERY]`, action `BindingPrompt`, and hostcall `ed.binding-prompt`.
- Add `Editor.binding_prompt_rows()` / `Editor.binding_apropos_rows(query)` plus hostcall `ed.binding-prompt-rows`.
- Keep the row shape aligned with the rest of the prompt system: `[insert kind menu info]`, where `insert` is the key, `menu` contains the winning mode + action-spec, and `info` carries the resolved human description.
- Make binding prompts live-refresh on query changes using the same `Editor.set_prompt_text()` path as topic prompts.
- Submitting a binding prompt runs `showkey KEY` for the selected/best-ranked binding.
- Reuse the existing prompt preview/status machinery (`ed.prompt-current-row`, `ed.prompt-current-preview`, status model fields) instead of inventing binding-specific display plumbing.

**Why**:
- which-key-style tools exist because users often need help *discovering current bindings*, not just learning command names once.
- VS Code’s split between Command Palette and Keyboard Shortcuts is a nice reminder that command discovery and binding discovery are distinct searchable surfaces.
- Helix continues to suggest the same implementation order Micromax has been following: item rows + query/selection state first, picker/popup rendering later.

**Consequence**: Micromax-editor now has a genuinely usable search-first binding discovery surface that stays entirely inside the existing headless prompt/session model. Future TUIs/LLMs can render it like a picker or which-key menu later, but the core already exposes the important semantics today.


## rev55 (2026-02-26)

### D127 — Let topic/help and binding discovery handle small multi-term queries across row fields

**Context**: rev48-54 established solid searchable row surfaces for topics and current bindings (`apropos`, `topicpick`, `bindingpick`), but matching still mostly assumed the query was one ordered string. That meant obvious command-palette searches like `word show` or binding searches like `quit Ctrl` underperformed even though the right metadata was already present in the row model.

**Decision**:
- Keep existing single-string matching/ranking as the first path for topic and binding discovery.
- Add a tiny term-splitting fallback for queries with multiple whitespace-separated words.
- For topics, let terms match across the topic name plus summary/doc text.
- For bindings, let terms match across the key, resolved description, and action-spec/menu text.
- Reuse the same ranking path everywhere that already depends on these rows: `apropos`, failed `help`, `topicpick`, `bindingpick`, and the hostcall row APIs.
- Make `help ...` use the full joined query for fallback suggestions rather than only the first token.

**Why**:
- Helix's picker docs point to `fzf`-style filtering, which is a useful reminder that once a surface becomes “picker-like,” users expect multi-term search to work.
- fzf's default extended search mode explicitly supports multiple space-delimited terms.
- The which-key.nvim command-palette request is a nice concrete signal that key discovery becomes much more useful when search can combine description text and keystrokes.
- VS Code Quick Pick continues to reinforce the “label + description/detail” model, which naturally pushes search beyond a single primary string.

**Consequence**: Micromax's search-first help/topic/binding surfaces now feel much closer to a real command palette while staying completely headless and deterministic. Future UIs/LLMs still consume the same row-first APIs; they just get better multi-term ranking out of the box.


## rev56 (2026-02-26)

### D128 — Add a searchable command/action palette on top of the existing prompt row substrate

**Context**: rev48-55 built a solid search-first discovery substrate (`apropos`, `topicpick`, `bindingpick`, row metadata, current-item previews, multi-term matching), but there was still no canonical “find a command/action and do it” flow. Users could discover topics and bindings, yet had to drop back to the ordinary command bar or raw keybindings to actually *invoke* most things.

**Decision**:
- Add a new prompt kind: `palette`.
- Add command-bar command `commandpick [QUERY]`, action `CommandPalette`, and hostcall `ed.command-palette`.
- Add `Editor.command_palette_rows()` / `Editor.command_palette_apropos_rows(query)` plus hostcall `ed.command-palette-rows`.
- Reuse the same `[insert kind menu info]` row shape as topic/binding prompts, but restrict the palette surface to **commands + actions** (no Micromax words).
- Selecting an **action** executes it immediately.
- Selecting a **command** does **not** eagerly execute it; instead it opens the ordinary command prompt prefilled with `name ` so the user can supply arguments deliberately.
- Reuse existing prompt live-refresh, preview, history, and status-model plumbing instead of inventing palette-specific UI state.

**Why**:
- VS Code’s Command Palette is the canonical precedent for “all commands are found here,” and its UX guidance stresses clear command naming/grouping.
- VS Code’s capabilities docs also reinforce that commands are a primary integration surface for editor features and extensions.
- legendary.nvim is a nice Neovim-side reminder that the *semantic registry* of commands/keymaps can be separate from the eventual picker UI.
- micro’s command bar remains the closest ergonomic family member for Micromax, so a good design is one where the palette can still hand off to the ordinary command bar when arguments matter.

**Consequence**: Micromax-editor now has a genuinely useful execution-oriented search surface without abandoning the small headless design. Future TUIs/LLMs can render it like a command palette, but the core semantics are already present: searchable rows, live query updates, current-item previews, action execution, and command staging through the ordinary command prompt.


### D129 — Add MRU-aware command palette sections instead of a heavier picker

**Context**: rev56 added a small searchable command/action palette on top of the prompt row substrate, but it still treated every command/action as equally fresh. Real command palettes become materially more useful once they remember what the user actually picked recently, and future UIs/LLMs also benefit from knowing when an item belongs to a `Recent` bucket rather than a plain command/action group.

**Decision**:
- Keep the existing `command_palette_rows()` data model as the canonical alphabetical command/action registry.
- Add a tiny palette-local MRU of **successful palette selections** (not all editor actions globally).
- Make empty palette queries show MRU items first without duplicating them in the rest of the list.
- Use MRU as a tiebreaker for equivalent palette matches.
- Expose grouped palette sections through `Editor.command_palette_section_rows(query)` and hostcall `ed.command-palette-section-rows`, with labels such as `Recent`, `Commands`, and `Actions`.
- Let `prompt_current_section` / preview / status surfaces report `Recent` when the active palette item comes from that MRU bucket.

**Why**:
- GitHub's Command Palette docs explicitly mention suggestions based on current context and recently used resources.
- Positron's docs say recently used commands appear first, which is exactly the low-friction behavior a tiny headless palette should steal.
- VS Code's command-palette guidance still stresses naming/grouping, which supports surfacing recency as explicit grouped data rather than hiding it in a UI-only sort order.

**Consequence**: the command palette now behaves more like a real daily-driver surface while staying fully headless. Future TUIs/LLMs can render a `Recent` section directly from stable row data, and the core avoids a broader “track every action forever” commitment by scoping recency to actual palette selections.

## rev58 (2026-02-27)

### D130 — Treat `xt-src` as a first-class inspection surface (definition + provenance + compilation)

**Context**: we already have spans (`xt-span`), doc/effect metadata (`xt-doc`, `xt-effect`), and row-based dictionary views. But the “show me what this thing *is*” workflow still often requires jumping between multiple tools (`showword`, `see`, `disasm`) and losing context in headless message streams.

**Decision**:
- Extend `xt-src` so it returns a **multi-line** source-ish rendering:
  - first line is a compact definition-ish form (stable for tooling/tests)
  - following `\\` comment lines optionally include: `effect`, `doc`, `defined at …`, and tier-2 `compiled …` stats
- Teach the editor’s `showword` command to append `xt-src` output so a single inspection message includes both documentation and a decompiled definition.

**Why**:
- micro’s upstream “help topics” lean heavily on deterministic text output; a headless editor needs strong textual inspection primitives before any UI layer exists.
- Debugging and reloadability in a plugin ecosystem improve dramatically when “what is this binding/command/word” is one copy/paste away.

**Consequence**: inspection flows become more ergonomic without adding any heavier UI machinery. Future TUIs/LLMs can treat `xt-src` as the canonical “printable definition” surface and layer richer views on top when needed.

## rev59 (2026-02-27)

### D131 — Prefer row-shaped inspection APIs when we expect UIs (or LLMs) to consume them

**Context**: `xt-src` became a compact, multi-line “source surface”, but any UI wanting syntax-ish treatment (definition vs metadata) would have to parse free-form text. Meanwhile, editor navigation features (like marks) are only truly useful if scripts and headless UIs can enumerate them deterministically.

**Decision**:
- Add `xt-src-rows` to expose `xt-src` as stable `[[text kind span|0] ...]` rows.
- Add editor **named marks** (`mark`/`markjump`/`marks`) and basic multi-buffer navigation (`buffers`/`buffer`) early, and expose them via hostcalls (`ed.marks`, `ed.mark-set`, `ed.mark-jump`, `ed.buffers`, `ed.active-buffer`, `ed.set-active-buffer`).

**Why**:
- Row APIs are the simplest “contract” between a tiny VM and multiple future UIs (TUI/GUI/LLM tooling) without committing to a heavy renderer.
- Marks are a navigation primitive that keeps headless tests meaningful while we delay UI commitments.

**Tradeoffs**:
- Adds a little surface area.
- Some “metadata kinds” are conventions rather than a full schema.

**Mitigation**:
- Keep kinds minimal and obvious (`def/effect/doc/span/compiled/meta`).
- Keep everything best-effort and non-authoritative (tooling surfaces, not compilation semantics).


## rev60 (2026-02-27)

### D132 — Ship searchable pickers for navigation targets early (buffers + marks)

**Context**: We already had a headless command palette (`commandpick`) and row-shaped prompt suggestion surfaces, plus named marks and multi-buffer primitives. But actually using marks/buffers efficiently without a UI meant either memorizing names or typing them perfectly.

**Decision**:
- Add `bufferpick [QUERY]` and `markpick [QUERY]` prompts that reuse the same suggestion-row model as other pickers.
- Teach command-bar completion to suggest buffer names for `buffer` and mark names for `markjump`/`mark`.
- Extend prompt section naming so `buffer` and `mark` rows render with sensible labels (not defaulting to `Word`).

**Why**:
- micro’s ecosystem relies on small plugins (like bookmark/next/prev) for day-to-day navigation, which implies that "searchable navigation targets" are a high-leverage primitive.
- Helix treats the jumplist as a first-class picker surface in addition to back/forward, suggesting that list+picker is a stable UX pattern worth modeling headlessly.

**Consequence**: Navigation workflows (switch buffer, jump to mark) become discoverable and testable via pure data/rows, without any commitment to a terminal UI widget.


## rev61 (2026-02-27)

### D133 — Keep a living worklist and land Tier-0 “real editor” basics

**Context**: The repo had a long roadmap and many good ideas, but it was becoming hard to tell what was *actually missing* for day-to-day editor use versus what was long-term (syntax highlighting, mouse, async tasks, WASM). At the same time, a few “obvious editor keys” (Delete, word jumps, page/document navigation) were missing, and `quit` didn’t warn on unsaved buffers.

**Decision**:
- Add a living priority entry point: `TODO.md` + a detailed tiered list `docs/43-worklist.md`.
- Implement Tier-0 movement/editing basics:
  - forward delete (`Delete`)
  - word jump + word select (Ctrl-Left/Right, Shift-Ctrl)
  - page/document navigation (PageUp/Down using `page.height`, Ctrl-Home/End)
  - `quit` now warns/arms when any buffers are dirty; `quit -f` / `quit!` force
  - add a default `Ctrl-l` binding to prefill `goto` in the command bar
- Add tests that exercise open/save, quit warning semantics, delete, word/page/document navigation.

**Why**:
- A tiny, inspectable project still needs a **minimum viable editing loop** (otherwise all higher-level features are hard to validate).
- A living worklist reduces repeated audits and makes it easier for future humans/LLMs to pick “the next useful thing” confidently.

**Tradeoffs**:
- Adds more default actions/bindings.

**Mitigation**:
- Keep the semantics conservative and UI-agnostic.
- Keep command/binding doc strings stable (tests + discoverability depend on them).


## rev62 (2026-02-27)

### D134 — Unblock real scripting: string hostcalls + lifecycle hooks + filetypes

**Context**: Plugin authors need basic string operations, type checks, and stable event hooks long before we have a full TUI. Also, “hook handlers accidentally depending on prior handlers’ stack effects” is an easy footgun in a concatenative language.

**Decision**:
- Add a reference string hostcall set (`mx.strings`) and install it by default in the editor embedding:
  - hostcalls: `s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower`
  - editor bridge also defines convenience words with those names in the default wordlist.
- Add typed predicates/conversions as portable primitives: `int? str? list? quote? xt? to-int to-str` and typed string compares `s=`/`s<`.
- Add editor lifecycle hooks: `ed.on-open`, `ed.on-save`, `ed.on-change` (buffer mutation detector).
- Add a minimal filetype detector (extension + shebang) exposed via `ed.filetype` and `status_model()['filetype']`.
- Change hook execution semantics so **each handler runs with the same baseline stack** and stack effects are discarded between handlers.

**Why**:
- Strings are the “glue” type for editor scripting: status messages, prompts, parsing, filetype checks.
- Lifecycle hooks are the smallest useful step toward an ecosystem (formatters, autosave, lint hooks) without over-committing to a complex event system.
- Per-handler stack isolation prevents subtle ordering bugs and makes plugin reload/unload behavior easier to reason about.

**Tradeoffs**:
- Adds surface area (hostcalls + a few core words).
- Hook isolation prevents intentionally pipeline-like hooks.

**Mitigation**:
- Treat hooks as notifications; pipeline composition belongs in explicit combinators or dedicated words.
- Keep the string hostcall set small and well-tested; add richer formatting (`s-format`) later.


## rev63 (2026-02-27)

### D135 — Make it tactile: viewport model + unbound typing + minimal TUI + `s-format`

**Context**: Until you can type into the editor and see the cursor move in something like a real loop, it’s too easy to over-design headless surfaces and under-specify scrolling/movement semantics. Also, plugin authors need a tiny formatting helper to produce usable messages/status text.

**Decision**:
- Store a simple headless viewport model on `Editor`: `(top_line, left_col, height, width)`.
  - Expose it via hostcalls `ed.viewport` and `ed.viewport!` and include it in `ed.status`.
  - After each action, auto-adjust the viewport so the primary cursor remains visible.
- Treat **unbound printable keys** as text input:
  - when a prompt is active, they edit the prompt
  - otherwise, they insert into the buffer
- Add prompt editing actions (`PromptInsertText`, `PromptBackspace`, …) and a reserved `prompt` keymap mode to override arrows/backspace/delete while a prompt is open.
- Add `s-format` hostcall (plus `format` alias word) as a minimal printf-ish formatter (`%s`, `%d`, `%%`).
- Add a minimal curses TUI (`python -m micromax_editor --tui`) implementing input → dispatch → render.

**Why**:
- Viewport + cursor-visibility is the smallest shared scrolling semantics that keeps future TUIs honest.
- Unbound typing is the difference between a “test harness” and something you can actually edit with.
- Prompt editing belongs in the core: it must behave consistently across UIs.
- `s-format` drastically reduces friction for status/messages without bloating the portable kernel.

**Tradeoffs**:
- The `prompt` keymap mode name is now effectively reserved.
- The fallback typing behavior means tests/UIs should use non-printable key names for synthetic inputs when they don’t intend to insert text.

**Mitigation**:
- Keymap lookup still prefers explicit bindings; fallback only applies when a key is truly unbound.
- Document the reserved mode name and keep the TUI explicitly “minimal MVP” until the rendering/span model matures.


## rev64 (2026-02-27)

### D136 — Make it configurable and navigable: `jumppick`, rc/init, and load-path conventions

**Context**: We now have a minimal TUI loop and a viewport model, so navigation history and config become immediately useful. Also, plugin distribution needs a predictable way to locate supporting files without hardcoding absolute paths.

**Decision**:
- Add a searchable **jumplist picker**: `jumppick [QUERY]`.
  - prompt kind: `jump`
  - newest-first rows with position + line preview
  - restore an explicit jumplist entry via `Editor.jump_to_index()`
- Add **user init/rc loading** at editor startup:
  - default: `~/.config/micromax/init.mx`
  - override: `$MICROMAX_INIT`
  - loaded after plugins so user config can override
- Define a small **`include`/`require` search convention** in the VM:
  - relative-to-caller source directory (best-effort via `vm.last_span`)
  - current working directory
  - host-provided `vm.load_paths`
  - `$MICROMAX_PATH` (os.pathsep-separated)
- Make plugin loading more robust:
  - plugin init failures do **not** abort `load_tree`
  - errors are recorded (`PluginManager.load_errors`)
  - best-effort cleanup removes leaked hooks/commands/bindings for failed plugins
- Improve minimal TUI usability for pickers by showing the current picker selection preview inline on the prompt line.

**Why**:
- `jumppick` turns an internal navigation structure into a usable tool.
- A user init file is foundational for a “live environment” editor.
- A load-path convention enables plugin/library sharing without baking in absolute paths.
- Non-fatal plugin loading prevents “one bad plugin bricks startup.”
- The TUI preview is the smallest UI affordance that makes pickers workable without building a full dropdown renderer yet.

**Tradeoffs**:
- `require`/`include` semantics are slightly more complex than “open a path.”
- The caller-relative resolution is best-effort (depends on spans).

**Mitigation**:
- Keep the resolution order short and deterministic; document it (`docs/88-require-and-paths.md`).
- Preserve the ability for hosts to override policy via `vm.load_paths`.


## rev65 (2026-02-27)

### D137 — Micro-esque indentation + tab insertion semantics

**Context**: Enter/Tab are the two highest-frequency editing keys. If they feel wrong, the whole editor feels wrong.

**Decision**:
- Implement auto-indent on newline by copying the current line’s leading whitespace onto the new line.
  - Avoid *double indentation* when splitting before/inside an indent prefix by only copying the portion of the indent that lies to the left of the cursor.
- Add micro-style tab options:
  - `tabsize` (int, default 4)
  - `tabstospaces` (bool, default true)
  - `InsertTab` inserts a literal `\t` when `tabstospaces=false`, otherwise inserts spaces to the next tab stop.
  - Space insertion aligns by **visual column**, accounting for existing tabs on the line.

**Why**:
- Copy-indent-on-newline is the smallest, predictable autoindent that works across languages.
- `tabsize`/`tabstospaces` are common editor muscle memory and match micro naming.
- Visual-column-aware tab alignment avoids “mystery off-by-some-spaces” behavior when a file already contains tabs.

**Tradeoffs**:
- This is not language-aware indentation (no “indent after :” yet).
- The headless model is character-based; tab rendering is a UI concern, so visual column is best-effort.

**Mitigation**:
- Keep the policy extremely small and deterministic; grow to language-aware indent only once we have a syntax-span model.
- Unit tests cover split-at-BOL, inside-indent, and tab alignment edge cases.


## rev66 (2026-02-27)

### D138 — Syntax highlighting as a portable span model

**Context**: We want syntax highlighting without locking the core to a terminal/color library.

**Decision**:
- Define syntax highlighting as *per-line spans*: `[[start_col end_col tag] ...]`.
- Expose it through editor hostcalls:
  - `"ed.highlight" hostcall` → spans for a line range
  - `"ed.highlight-tags" hostcall` → the tag vocabulary
- Ship a tiny default highlighter for `filetype=micromax` that handles strings, comments, numbers, and def names.

**Why**:
- The UI can map tags to colors later (curses, tui, wasm, etc.) without changing plugins.
- Spans are easy to test and reason about, and they compose naturally with later features (pair highlights, search matches, trailing ws, etc.).

**Tradeoffs**:
- The first highlighter is intentionally line-local (no multi-line state).

**Mitigation**:
- Keep the tag vocabulary small and stable; allow richer highlighters later.


### D139 — Timers as a deterministic, thread-free queue

**Context**: Plugins need debouncing/autosave without spawning threads or relying on real time in tests.

**Decision**:
- Add a tiny timer queue owned by the editor and driven by the host event loop.
- Expose three hostcalls:
  - `"ed.after"` schedules a quotation to run after N ms
  - `"ed.cancel-timer"` cancels a timer id
  - `"ed.pump-timers"` runs due timers and returns how many executed
- Timer callbacks run like hooks: stack-isolated and best-effort (errors become messages).
- Plugin unload cancels timers belonging to that plugin’s registration group.

**Why**:
- Deterministic in tests (injectable clock), simple in the TUI loop, and keeps the VM substrate tiny.

**Tradeoffs**:
- Timers are cooperative: nothing runs unless the host pumps.

**Mitigation**:
- Pump timers in every UI tick (curses loop already does this).


## rev71 (2026-02-28)

### D151 — Softwrap is a visual-row world

**Decision**: When `softwrap=true`, vertical movement and scrolling should operate on *visual rows*
(wrapped fragments), not logical lines. This matches what many editors do when wrap is enabled
(e.g. micro's cursor movement within a wrapped line).

**Implementation shape**:
- Add `viewport_top_subline` and treat the viewport start as `(top_line, top_subline)`.
- Keep `view_rows` / `cursor_view_pos` as the shared headless rendering contract.
- Preserve a per-cursor "goal x" for vertical motions so movement feels stable across short wrap rows.

### D152 — Plugin manager should be scriptable + errors should surface

**Decision**: Plugin management isn't just a UI concern; scripts should be able to query/reload plugins and inspect
load/dependency errors.

**Implementation shape**:
- Hostcalls: `plugin.list`, `plugin.reload`, `plugin.errors`.
- CLI command `plugin list` prints recent captured load errors.
- `PluginManager.reload()` must respect `plugin.json`'s `entry` field.


## rev72 (2026-02-28)

### D153 — Statusline format strings should be micro-compatible

**Decision**: implement `statusformatl`/`statusformatr` as micro-esque `$()` directive templates.

**Why**:
- imports configuration muscle-memory from micro (and keeps the split left/right model)
- keeps the default TUI deterministic while still allowing customization

**Shape**:
- a tiny renderer (`src/micromax_editor/statusformat.py`) with compatibility directives (`filename`, `modified`, `line`, `col`, `lines`, `percentage`, `opt`, `bind`, `overwrite`) plus a few editor-specific helpers (`readonly`, `sel`, `cur`, `keymode`, `macro`).

### D154 — Cleanup belongs in stdlib (`ensure`/`finally`)

**Decision**: add an always-run cleanup combinator in the stdlib rather than adding VM primitives.

**Why**:
- keeps the VM kernel small and portable
- `catch`/`throw` already provide the needed semantics (stack restoration + error propagation)

**Semantics**:
- `cleanup` runs regardless of success/failure
- on failure, `cleanup` runs with the pre-body stack (because `catch` restores)
- if `cleanup` fails, it overrides the body error

## rev70 (2026-02-28)

### D00X — Keep exception ergonomics in stdlib, not primitives
**Decision**: add `try?`, `try`, and `recover` as stdlib combinators built on `catch` + `last-error`, rather than adding new VM primitives.

**Why**: keeps the core VM small/portable (Rust/WASM), while still making the common “recover” pattern pleasant.

**Notes**: this matches the spirit of Forth’s minimal exception core (`CATCH`/`THROW`) plus library-level sugar.

### D00Y — Provide a reference statusline formatter
**Decision**: add `Editor.statusline_text(width)` as a deterministic baseline formatter, and have the minimal TUI use it.

**Why**: UI layers should use `status_model()` for structure, but a shared formatter reduces drift and gives tests a single, stable target.



### rev74 — Safe buffer lifecycle + recent files MRU

- **Problem:** `open` previously clobbered an already-open buffer with the same name, which could silently drop unsaved edits.
- **Decision:** Treat `open` as *switch-if-open* (dedupe by normalized `Buffer.path`). A separate explicit `reload`/refresh path can exist later.
- **Additions:**
  - `close` / `close!` to close buffers with a dirty-buffer double-tap guard (mirrors `quit`).
  - Recent-files MRU tracked headlessly (`recent` / `recentpick`) plus hostcalls `ed.recent` / `ed.recent-clear`.
  - Resource helper `ed.with-viewport` (save/restore viewport around a quotation).
- **Why:** This matches common editor expectations (buffers are durable; open should not discard changes) and makes plugin/UX flows (switching files, picker-based navigation) easy to validate headlessly.



## rev75

- Added a tiny buffer MRU to make `close` and `prevbuf` feel predictable (MRU wins over dict order).
- `commandpick` now also surfaces `Recent Files` and can open them directly, while keeping commands staged and actions immediate.
- Recent files can be optionally persisted to `~/.config/micromax/recent.json` when `recent.persist=true` (loaded after user init).
- Added `plugins/capdemo` as a living example of `host.feature?` capability checks.


## rev76

- **Docs-backed help buffers:** `help TOPIC` now falls back to opening a matching `docs/*.md` page into a protected read-only buffer (plus a dedicated docs picker: `helppick`).
- **Protected buffers:** added a small "protected" flag (`local_options['readonly']`) used to reject mutating editor actions/commands for internal buffers.
- **TUI picker list:** the curses TUI now renders a small suggestion list under the prompt line, including section headers when they can be inferred.


## rev77

- **Docs navigation helpers:** help buffers gained `helpfollow` (follow a markdown link under the cursor) and `helpback` (return to the previous docs page), backed by a tiny in-editor stack.
- **Picker UX polish:** the curses TUI suggestion list gained scroll windowing with "more" markers, and uses basic terminal attributes (reverse for selection, bold for headers).


## rev78

- **Docs browser polish:** help/docs buffers now get lightweight link highlighting in the TUI (underline link labels; bold-underline when the cursor is on a link).
- **Link list / picker:** added `helplinkpick` to pick from links on the current docs page.
- **Capability registry:** added a tiny capability registry (`host.capabilities`) and editor options `cap.*` to gate unsafe host surfaces.
- **Unsafe surfaces (gated):** external docs links can open via `cap.open-url`; a minimal `ed.shell` hostcall exists behind `cap.shell`.


## rev79

- **Docs outline / headings picker:** added `helpoutlinepick` to navigate a docs page by headings, plus hostcalls `ed.help-outline-rows` and `ed.help-link-rows` for plugins and tooling.
- **Markdown affordances in TUI:** headings in docs buffers are now rendered in bold (links still underline as before).


## rev80

- **Docs-as-browser keybindings:** in help/docs buffers, `Enter` follows the link under the cursor and `Backspace` goes back (browser-style convenience).


## rev81

- **Capability-gated file reads:** added `ed.fs-read` behind `cap.fs-read` (UTF-8, size-limited) to support safe plugin tooling without implicit host access.
- **Docs quick-jump:** added `helpjump` as a direct heading jump command (and outline picker shortcut), making docs navigation faster than always picking.
- **Picker grouping polish:** buffer and plugin picker rows are now grouped into contiguous sections (help/scratch/dirs; errors/loaded/available), and the TUI indents outline items by heading level for readability.


## rev82

- **Docs browser polish:** `helplinkpick` suggestions are now grouped into Docs/Files/External sections, and this grouping is also exposed headlessly via `ed.helplink-section-rows`.
- **TUI debugging affordance:** added `rawkeys` to show raw terminal key events for binding/debugging.


## rev83

- **Markdown link support:** docs navigation recognizes reference-style links (`[text][id]` + `[id]: target`) and autolinks (`<https://...>`), both for `helpfollow` and the link picker.


## rev84

- **Docs page navigator:** added `helpnavpick`, a combined headings+links picker for the current docs page.
- **Headless nav surface:** added `ed.helpnav-section-rows` (grouped headings + grouped link sections) so future UIs/scripts can reuse the same navigator substrate.


## rev97

- **Docs link picker sections by heading (optional):** `helplinkpick` (and `ed.helplink-section-rows`) can now group links by the nearest markdown heading via `help.linksections heading` (default remains Docs/Files/External).
- **Filesystem metadata helper (gated):** added `ed.fs-stat` behind `cap.fs-stat` to support safe file-picking scripts without giving write access.
- **Archive packaging helper:** added `tools/mkrevzip.py` so offline checkouts can generate standard-named `Micromax-rev####-YYYY.MM.DD.HH.MM-<tag>.zip` archives reproducibly.

## rev107

- **Help navigator grouping parity:** `helpnavpick` and `ed.helpnav-section-rows` now reuse the same link-section policy as `helplinkpick`, so `help.linksections heading` affects both surfaces and the picker/TUI section reconstruction logic stays consistent.
- **Source-aware external-link confirmations:** external-link confirmation prompts now mention whether the open request came from docs help, a URL under cursor, or an explicit command, making the safety prompt slightly more informative without adding ambient power.



## rev108

- **Command palette path sections:** path-like palette results now split into `Directories` / `Files` / `Open` sections instead of one generic `Open` bucket, which keeps drill-down rows easy to scan and makes section-aware TUIs/LLMs more informative.
- **Starter portability corpus:** added `portability/kernel_cases.json` plus shared runner `src/micromax/portability_suite.py` and CLI `tools/mxportable.py` so future Rust/WASM ports can validate a small cross-host semantic corpus against the Python reference VM.


## rev109

- **Docs fragment links:** help/docs navigation now follows same-page heading fragments (`#section`) and cross-doc fragments (`page.md#section`) instead of only whole-document links.
- **Tiny, explicit heading-id policy:** fragment resolution uses best-effort GitHub-style auto slugs for ordinary headings, but also honors explicit heading ids in common markdown attr-list forms (`{#id}` / `{: #id }`) so docs authors can pin stable anchors when wording changes.
- **Rendered-title bias for docs tooling:** outline rows and heading-breadcrumb labels now strip raw attr-list suffixes from headings, so picker/search surfaces reflect the human title instead of source-only syntax.


## rev110

- **Docs footnotes (tiny, local, consistent):** help/docs buffers now recognize common markdown footnote refs (`[^id]`) and definitions (`[^id]: ...`) as a *small internal navigation affordance* rather than a full markdown feature. Following a footnote jumps to its definition in the current docs buffer, and the same footnote model is reused by `helplinkcopy`, `helplinkpick`, `helpnavpick`, and the minimal TUI's underline/current-link logic.
- **Scope rule:** only the anchor/definition jump is modeled for now; richer rendered-footnote behavior (backlinks, multi-block rendering, numbering policy, HTML-id compatibility) remains intentionally out of scope until we need more than docs-browser navigation.


## rev111

- **Docs tables (scanability, not semantics):** the minimal TUI now recognizes small GFM-style pipe tables in docs/help buffers and applies tiny rendering hints (bold header row, dim delimiter row, dim `|` separators).
- **Scope rule:** this remains a UI-only helper model (`md_table_delimiter_row`, `md_table_row_kinds`, `md_table_pipe_spans`), not a new headless markdown AST or block parser. If future UIs need richer table behavior, they can either reuse or replace this tiny policy without destabilizing editor core semantics.


## rev112

- **Docs task lists (scanability, not semantics):** the minimal TUI now recognizes small GFM-style task-list markers in docs/help buffers (`- [ ]`, `* [x]`, `1. [X]`), bolding the checkbox token and dimming the body of checked tasks.
- **Scope rule:** this remains a UI-only helper model (`md_task_checkbox`, `md_task_body_span`), not a new list/block parser or a writable checkbox interaction model.

## rev113

- **Docs blockquotes (scanability, not semantics):** the minimal TUI now recognizes small markdown blockquote prefixes in docs/help buffers and applies tiny rendering hints (bold quote-marker prefix, dim quoted body).
- **Scope rule:** this remains a UI-only helper model (`md_blockquote_prefix`, `md_blockquote_body_span`), not a full blockquote parser, lazy-continuation model, or markdown AST commitment.

## rev114

- **Docs thematic breaks (scanability, not semantics):** the minimal TUI now recognizes small markdown thematic-break lines in docs/help buffers and applies tiny rendering hints (dim separator line, bolder visible marker run).
- **Scope rule:** this remains a UI-only helper model (`md_thematic_break_span`, `md_thematic_break_char_spans`), not a richer block parser, section model, or markdown AST commitment.


## rev115

- **Docs inline emphasis helpers (scanability, not semantics):** the minimal TUI now recognizes a tiny markdown inline-emphasis subset in docs/help buffers: `**strong**` bodies render bold, `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline), and `~~strike~~` bodies render dim.
- **Scope rule:** this remains a UI-only helper model (`md_strong_spans`, `md_emphasis_spans`, `md_strikethrough_spans`), not a full delimiter-run parser, nested-markup guarantee, or markdown AST commitment.


## rev116

- **Docs inline code: equal-length backtick runs.** The minimal TUI now recognizes inline code spans using equal-length backtick delimiters, so repo docs can use double-backtick forms when literal backticks need to appear inside code-like text.
- **Docs inline precedence: code first, links later.** The TUI now masks inline code spans before markdown-link underlining, matching the general markdown intuition that code-ish text should not become clickable-looking prose.
- **Scope rule:** this remains a UI-only helper policy (`md_inline_code_spans` + `md_link_label_spans`), not a general inline markdown parser, whitespace-normalization model, or full delimiter-precedence engine.


## rev117 (2026-03-06)

### D0XX — Docs-browser images are prose until we have an image policy
**Decision**: the tiny docs/help link model should ignore markdown image syntax (`![alt](dest)` and `![alt][id]`) instead of treating image alt text like clickable docs links.

**Why**: CommonMark image syntax reuses much of link syntax, but Micromax does not render images yet. Treating image descriptions as clickable docs links leaks parser coincidence into UX and makes docs navigation feel sloppy.

**Implemented in rev117**:
- `helpfollow` ignores markdown image forms
- `helplinkpick` ignores markdown image forms
- TUI docs-link underlining ignores markdown image forms


## rev118 (2026-03-06)

### D0XX — Inline code precedence should apply to docs-browser actions, not just styling
**Decision**: the tiny inline-code precedence rule should be shared across the docs browser's action surfaces too: `helpfollow` and `helplinkpick` must ignore markdown-looking links/autolinks that sit inside inline code spans.

**Why**: rev116 already taught the TUI to mask inline code before docs-link underlining, which made code-ish text *look* non-clickable. Letting editor actions still follow/pick those pseudo-links would leave the UI and action model out of sync.

**Implemented in rev118**:
- moved the tiny equal-length backtick helper into `editor.py` as shared docs-browser substrate (`md_inline_code_spans`)
- added `md_span_contains` so docs scanners can cheaply skip matches covered by inline-code spans
- `helpfollow` now ignores inline/reference/shortcut/autolink matches when they sit inside inline code
- `helplinkpick` inherits the same policy through `help_link_rows`

**Consequence**: docs-browser precedence rules stay tighter and more predictable without introducing a fuller markdown parser or AST. This is the kind of shared-policy cleanup worth preferring over surface-specific heuristics.


## rev119 (2026-03-06)

### D0XX — Escaped markdown examples must stay prose in the docs browser
**Decision**: the tiny docs/help markdown model should treat backslash-escaped openers as literal prose across *both* styling and actions: `\[link]`, `\![image]`, `\[^footnote]`, and `\<autolink>` must not become clickable-looking or navigable.

**Why**: the repo's help pages increasingly double as executable docs *and* markdown teaching material. Once we started supporting more link-like forms, literal examples began to risk leaking into `helpfollow` / `helplinkpick` or TUI underlining unless escapes were part of the shared precedence policy.

**Implemented in rev119**:
- added a small shared helper (`md_backslash_escaped`) in `editor.py`
- `helpfollow` now ignores escaped inline/reference/shortcut/footnote/autolink forms
- `helplinkpick` inherits the same policy through `help_link_rows`
- TUI docs-link underlining ignores escaped inline/reference/shortcut/footnote/autolink forms
- added docs examples plus tests for escaped inline links, refs, footnotes, autolinks, and escaped definition parsing

**Consequence**: docs that *teach* markdown stay readable and literal without forcing Micromax into a fuller markdown parser. This is another good example of preferring one small shared policy helper over regex drift across surfaces.


## rev120 (2026-03-06)

### D0XX — Balanced bracket labels deserve one shared docs-browser scanner
**Decision**: the tiny docs/help markdown model should support balanced bracket labels like `[Vision [nested]](doc.md)`, `[Vision [nested]][id]`, and `[Vision [nested]]` through one small shared scanner used by editor actions, picker rows, TUI underline spans, and reference-definition parsing.

**Why**: plain regexes were good enough for the first few markdown affordances, but nested bracket labels are a real author-facing CommonMark case that makes regex-only parsing drift across surfaces. This was the next point where one tiny shared parser helper bought more reliability than another layer of regex exceptions.

**Implemented in rev120**:
- added `MdLinkMatch`, `md_balanced_span`, and `md_link_matches` in `editor.py`
- `helpfollow` now uses the shared scanner
- `helplinkpick` / `help_link_rows` now use the shared scanner
- TUI docs-link underlining now uses the shared scanner
- `_md_reference_defs` now accepts balanced bracket ids like `[Vision [nested shortcut]]: ...`

**Consequence**: docs-browser behavior stays aligned across visual and action surfaces, and future LLMs get a clearer place to extend markdown-link behavior without reintroducing regex drift.


## rev121 (2026-03-07)

### D0XX — Tiny destination parsing is worth sharing too
**Decision**: the tiny docs/help markdown model should apply one shared destination policy to inline links, reference definitions, and local-doc follow: bare destinations may include balanced parentheses, markdown-safe backslash escapes should be unescaped before use, and percent-encoded local doc paths should be decoded before follow.

**Why**: rev120 proved that once markdown-link behavior spans `helpfollow`, `helplinkpick`, TUI underlining, and definition parsing, destination quirks become the next place where regex shortcuts drift across surfaces. Local docs examples like `104-paren\(topic\).md`, `103-space\ path.md`, and `103-space%20path.md` are exactly the kind of tiny author-facing cases that should work in an editor-centric help browser.

**Implemented in rev121**:
- added `md_backslash_unescape` plus a slightly smarter `md_inline_link_target` in `editor.py`
- reference-definition parsing now reuses the same tiny destination parser instead of its own whitespace split
- local-doc follow percent-decodes the doc portion before resolving a relative path
- added docs examples plus real test docs (`docs/103-space path.md`, `docs/104-paren(topic).md`)

**Consequence**: Micromax keeps getting the leverage of one small shared docs-browser substrate without paying for a full markdown destination/title parser or AST.


### D0XX — Fenced code blocks must stay prose in the docs browser
**Decision**: fenced code blocks in help/docs buffers should be treated as inert prose for `helpfollow`, `helplinkpick`, TUI docs-link underlining, and markdown reference-definition parsing.

**Why**: rev118–rev121 tightened inline-code precedence, escapes, balanced labels, and destinations, but fenced examples were still a larger block-level escape hatch where markdown-looking text could leak back into live docs behavior. Help pages increasingly double as executable docs *and* literal markdown examples, so fenced examples should not accidentally define references or become clickable.

**Consequence**: a single tiny shared helper (`md_fenced_code_line_flags`) now lets editor actions, picker rows, and the TUI agree on fence precedence without committing Micromax to a fuller markdown block parser or AST.

- rev123: treat single-line setext headings as first-class docs/help headings (fragments, outline, breadcrumbs, docs-title scan), but keep the policy intentionally tiny/shared and fenced-code-aware rather than promising full CommonMark block parsing.


## rev124 (2026-03-07)

### D0XX — Raw HTML comments must stay prose in the docs browser
**Decision**: raw HTML comments in help/docs buffers should be treated as inert prose for `helpfollow`, `helplinkpick`, outline scanning, TUI docs-link underlining, and markdown reference/footnote-definition parsing.

**Why**: after rev118–rev123 tightened code-span precedence, escapes, balanced labels, destination parsing, fenced code blocks, and setext headings, commented-out markdown examples were the next place where literal docs content could still leak back into the live help browser. Docs increasingly double as user-facing prose and parser test fixtures, so HTML comments should behave like literal storage, not hidden active links.

**Implemented in rev124**:
- added shared tiny comment helpers (`md_html_comment_spans`, `md_html_comment_line_spans`) in `editor.py`
- `helpfollow`, `helplinkpick`, TUI docs-link underlining, reference definitions, footnote definitions, and heading scanning now all reuse the same raw-comment masking policy
- added commented examples to `docs/98-help-browser.md` plus focused tests

**Consequence**: Micromax keeps buying leverage from one small shared docs-browser substrate without taking on a fuller raw-HTML parser or Markdown-in-HTML model.


## rev125 (2026-03-07)

### D0XX — Raw HTML tags/autolinks should beat link grouping in the docs browser too
**Decision**: inline raw HTML tags and autolinks that begin inside a would-be markdown link label should keep the whole construct literal for `helpfollow`, `helplinkpick`, and TUI docs-link underlining.

**Why**: rev124 fixed raw HTML comments, but CommonMark-style false positives still remained in smaller inline cases like `[foo <bar attr="](baz)">` and `[foo<https://example.invalid/?x=](doc.md)>`, where HTML tags/autolinks bind tighter than link grouping. Those cases are exactly the sort of regex trap that makes docs-browser behavior drift unless there is one shared precedence helper.

**Implemented in rev125**:
- added `md_inline_html_tag_spans` in `editor.py` as a tiny raw-HTML/autolink precedence helper
- `md_link_matches` now refuses would-be link labels that intersect one of those inline HTML/autolink spans
- added docs examples plus focused editor/picker/TUI tests for raw-HTML-tag and autolink precedence inside labels

**Consequence**: Micromax keeps the docs/help browser conservative and aligned across actions and rendering, while still avoiding a fuller HTML parser or Markdown AST commitment.


## rev126 (2026-03-07)

### D0XX — Multi-line setext headings should use the same tiny shared scanner
**Decision**: help/docs heading discovery now recognizes setext headings whose title spans multiple paragraph lines before the underline.

**Why**: current CommonMark defines setext headings as one or more lines of text, and GitHub Docs says GitHub Flavored Markdown stays CommonMark-compliant. Micromax already used setext headings for doc titles, outline rows, fragment jumps, and heading-grouped link sections, so leaving multi-line forms unsupported created exactly the kind of surface drift the repo is trying to avoid: the second heading line could leak into docs-picker summaries even though users would expect one heading.

**Implemented in rev126**:
- refactored heading discovery into a shared `_md_heading_scan()` helper that records heading line spans
- setext scanning now joins contiguous paragraph-like title lines before the underline
- docs-picker summary extraction now skips the full heading span, preventing continuation lines from becoming fake summaries
- added a dedicated docs fixture plus focused tests for doc titles, fragment jumps, outline rows, and heading-grouped link sections

**Consequence**: Micromax stays conservative but more faithful to the markdown people actually write, without pulling in a full block parser or AST dependency.


## rev127 (2026-03-07)

### D0XX — Common raw HTML blocks should stay inert in the docs browser
**Decision**: help/docs navigation now treats common raw HTML blocks as inert prose across `helpfollow`, `helplinkpick`, outline scanning, markdown reference/footnote-definition parsing, and TUI docs-link underlining.

**Why**: rev124 handled raw HTML comments and rev125 handled inline raw-HTML/autolink precedence inside would-be link labels, but larger block-level HTML islands were still a place where literal docs content could leak back into active help-browser behavior. CommonMark/GFM-style docs regularly include `<div>...</div>` or `<pre>...</pre>` examples, so those should behave like raw storage, not half-parsed markdown.

**Implemented in rev127**:
- added `md_html_block_line_flags()` in `editor.py` as a tiny shared raw-HTML block helper
- reference definitions, footnote definitions, `helpfollow`, `helplinkpick`, heading scanning, and the TUI now all reuse that block-exclusion policy
- covered both blank-line-terminated block-tag forms and `<pre>`/`<script>`/`<style>`/`<textarea>`-style blocks that stay inert across internal blank lines
- added help-browser examples plus focused navigation/picker/TUI tests

**Consequence**: Micromax keeps strengthening the docs/help browser with one small shared substrate instead of growing separate regex exceptions per surface or taking on a fuller HTML/Markdown parser.


## rev128 (2026-03-07)

### D0XX — Conservative type-7-ish HTML blocks should share the same docs-browser helper
**Decision**: help/docs navigation now also treats complete generic tag-only lines like `<widget-box ...>` / `</widget-box>` as inert prose through the next blank line when they begin after a blank line (or at doc start), while still refusing to let those blocks interrupt paragraphs.

**Why**: rev127 fixed the big CommonMark/GFM HTML-block families (`<div>`-style blank-line blocks and `<pre>`/`<script>`-style closing-tag blocks), but generic tag-only lines were still a realistic literal-docs escape hatch. CommonMark's type-7 rule is exactly the right size for Micromax here: useful, shared, and conservative.

**Implemented in rev128**:
- added `md_html_type7_tag_line()` in `editor.py` as a tiny complete-tag recognizer for conservative generic tag-only lines
- extended `md_html_block_line_flags()` so the same shared raw-HTML block policy now covers those type-7-ish cases too
- kept the start condition conservative (`doc start` / `after blank line`) so paragraph-adjacent tag lines do not swallow following markdown links
- added docs examples plus focused navigation/picker/TUI tests

**Consequence**: Micromax keeps strengthening the docs/help browser with one shared policy helper instead of piling on regex exceptions or taking on a fuller HTML parser / Markdown-in-HTML model.

## rev129 (2026-03-07)

### D0XX — Tiny wrapped reference definitions should reuse the shared destination parser

**Decision**: help/docs reference definitions should support small CommonMark-style wrapped forms where the destination may sit on the next line and the optional title may also wrap once, while still reusing the same destination parser shared by inline links and follow actions.

**Why**: current CommonMark allows up to one line ending after the colon and after the destination inside link reference definitions, and GitHub Docs says its GFM stays CommonMark-compliant. After rev121 made destination parsing less regex-shaped and rev128 aligned raw HTML block handling, single-line-only reference definitions had become the next place where otherwise ordinary docs examples could fail even though the shared destination policy was already good enough.

**Implemented in rev129**:
- added a small shared destination-prefix helper so inline links and wrapped reference definitions do not drift
- reference-definition parsing now accepts destination-on-next-line and title-on-next-line forms without promising a fuller block parser
- docs/examples/tests now cover wrapped local-doc destinations with escaped spaces and escaped parentheses

**Consequence**: Micromax keeps buying leverage from one tiny docs-browser substrate — shared helper first, no second multiline regex parser — while becoming more faithful to real markdown people actually write in docs.

## rev130 (2026-03-07)

### D0XX — Docs block starters should share a spaces-only 0–3 indent guard
**Decision**: help/docs reference definitions, footnote definitions, and ATX heading scanning should consistently follow the small CommonMark-style “up to three leading spaces” rule, so four-space and tab-indented lookalikes stay prose instead of becoming live docs-browser structure.

**Why**: rev123–rev129 kept making docs-browser behavior more shared and less regex-shaped, but reference definitions still accepted code-block-ish indentation and ATX heading scans still used `\s{0,3}`, which can accidentally treat tabs as valid leading indentation. Current CommonMark keeps these block starters in the “up to three spaces” bucket, and four spaces belong to indented code-like prose. This was the next tiny shared correctness pass, not a new markdown feature.

**Implemented in rev130**:
- added `md_leading_spaces_upto3()` in `editor.py` as the shared tiny leading-indent helper
- `_md_reference_defs()`, `_md_footnote_defs()`, and `_md_heading_parts()` now all reuse that helper
- setext-heading paragraph guards now also use spaces-only list/blockquote detection instead of `\s`-shaped indentation
- added a dedicated docs fixture (`docs/107-indented-codeish-markdown.md`) plus focused navigation/picker/outline/TUI tests

**Consequence**: Micromax keeps the docs/help browser conservative and shared-policy-driven: code-ish indentation stays literal, docs surfaces agree, and the repo still avoids a fuller markdown parser or AST commitment.

## rev131 (2026-03-07)

### D0XX — Tiny wrapped inline links should reuse the shared continuation policy

**Decision**: help/docs inline links should support small CommonMark-style wrapped forms where the destination may sit on the next line and the optional title/closing `)` may wrap once as well, while reusing the same shared destination parser and one shared continuation-line policy across editor actions and the TUI.

**Why**: current CommonMark says inline-link pieces may be separated by spaces, tabs, and up to one line ending, and GitHub Docs says its GFM stays CommonMark-compliant. After rev129 taught reference definitions to wrap and rev130 made block starters more conservative, single-line-only inline links had become the next place where otherwise ordinary docs examples still failed even though the shared destination policy was already good enough.

**Implemented in rev131**:
- added `md_inline_link_target_multiline()` in `editor.py` as a tiny multiline shell around the existing destination parser
- added `md_docs_continuation_line()` so wrapped link/reference scans share the same fenced/raw-HTML/comment-hidden continuation policy
- `helpfollow`, `helplinkpick`, and TUI docs-link underlining now all pass continuation lines through that helper instead of growing separate multiline heuristics
- added a dedicated docs fixture (`docs/108-wrapped-inline-links.md`) plus focused parser/navigation/picker/TUI tests

**Consequence**: Micromax keeps buying leverage from one tiny docs-browser substrate: shared helpers first, more real markdown examples supported, and still no fuller markdown parser or AST commitment.


## rev132 — wrapped angle-bracket destinations stay tiny and shared

- The docs/help browser already had a tiny shared destination parser, and after rev131 it could already wrap ordinary bare destinations onto the next line. The next small win was to keep that same parser in charge for **angle-bracket destinations** too, instead of adding a second multiline regex path just for `<...>` forms.
- Current CommonMark allows inline-link pieces and reference-definition pieces to be separated by spaces/tabs and up to one line ending, while angle-bracket destinations themselves still cannot contain line endings; GitHub Docs also says its GFM stays CommonMark-compliant. So `[doc](\n  <space path.md>)` and `[id]:\n  <space path.md>` are real author-facing shapes worth supporting in the tiny docs browser.
- Tightened one malformed case at the same time: after an angle-bracket destination closes with `>`, an optional title still needs separating whitespace. The old tiny parser would incorrectly accept forms like `<path.md>"title"` as if the title were separated. The new shared `_md_link_rest_has_required_separator()` guard fixes that once for inline links and wrapped reference definitions.
- Kept the policy intentionally small: we still are not attempting full multiline title parsing or a general CommonMark AST. The goal remains “shared tiny helpers, not regex drift per surface.”

## rev133 (2026-03-08)

### D0XX — Nested links inside labels should keep only the inner valid link live

**Decision**: help/docs navigation should refuse outer markdown links whose label text contains a valid inner link, keeping the outer prose literal while still exposing the inner valid link through `helpfollow`, `helplinkpick`, and TUI underline spans.

**Why**: current CommonMark says links may not contain other links at any level of nesting, and the inner-most otherwise valid link wins. GitHub Docs also says GFM stays aligned with CommonMark. After rev132 tightened wrapped destination/title parsing, nested links inside labels were the next realistic place where Micromax's tiny shared matcher still behaved too much like a regex instead of a precedence-aware scanner.

**Implemented in rev133**:
- added `md_label_contains_nested_links()` in `editor.py` as a small shared guard that recursively reuses `md_link_matches()` on label contents
- outer inline/reference links are now rejected when that label-body scan finds a valid inner markdown link
- images still remain allowed inside labels because the shared matcher already keeps image syntax out of link results
- added end-to-end help-browser examples plus focused navigation/picker/TUI tests

**Consequence**: Micromax keeps improving docs/help correctness with one shared matcher policy instead of accumulating one-off nested-link regex exceptions or committing to a full inline markdown parser.

## rev134 (2026-03-08)

Decision: keep empty or whitespace-only markdown labels literal prose in the tiny docs browser.

Why:
- Current CommonMark requires link labels to contain at least one non-whitespace character.
- Micromax's tiny docs-link matcher was still accepting malformed blank-label shapes like `[](doc.md)` and `[ ](doc.md)`, which leaked into `helpfollow`, `helplinkpick`, and TUI underlining as invisible or blank links.
- This is exactly the kind of small shared-policy bug the docs browser should fix without growing a full inline parser.

Implemented in rev134:
- added `md_link_label_has_text()` in `src/micromax_editor/editor.py`
- `md_link_matches()` now rejects inline/reference/shortcut labels that do not contain at least one non-whitespace character
- `_md_reference_defs()` now reuses the same helper before normalizing a would-be reference id
- expanded `docs/98-help-browser.md` with malformed empty/space-only label examples
- added focused tests for matcher behavior, picker suppression, and TUI span suppression

Consequence:
- malformed empty/space-only labels now stay prose across `helpfollow`, `helplinkpick`, and TUI docs-link underlining
- the fix stays tiny/shared-policy-first rather than becoming another surface-specific regex exception


## rev135 (2026-03-08)

### D0XX — Mark and jumplist pickers should share real section labels across UI + host surfaces

Decision: `markpick` should group rows by owning buffer and `jumppick` should group rows by relation to the active jump (`Current` / `Back` / `Forward`), with the same labels reused by the minimal TUI, prompt section-jump navigation, `prompt_current_section`, and new grouped hostcalls.

Why:
- Recent picker work kept proving that explicit sections are more useful than one long fuzzy list when the groups are obvious.
- VS Code Quick Picks explicitly recommends separators for lists with multiple obvious groups, and Helix treats pickers as a navigation surface with their own interaction model.
- Marks and jumplist entries already had enough metadata to form those groups; the missing piece was one shared label policy instead of TUI-only formatting.

Implemented in rev135:
- added `_mark_section_label()` / `_jump_section_label()` plus small ordering helpers in `src/micromax_editor/editor.py`
- `markpick` rows now sort/group by owning buffer; `jumppick` rows now sort/group by `Current` / `Back` / `Forward` when a current jump exists
- added grouped headless helpers `mark_section_rows()` / `jump_section_rows()` and hostcalls `ed.mark-section-rows` / `ed.jump-section-rows`
- `prompt_row_section_label()` and `prompt_current_section()` now reuse those same helpers so TUI headers, `Alt-Up`/`Alt-Down`, and preview/status surfaces stay aligned
- added focused picker/hostcall/TUI tests

Consequence:
- future UIs/LLMs can inspect grouped navigation rows directly instead of reverse-engineering `menu` strings
- Micromax keeps improving picker ergonomics through shared row metadata rather than committing to a heavier popup/browser widget


## rev136 (2026-03-08)

### D0XX — grouped picker sections should be exposed headlessly and reused by preview/status surfaces

Decision: if a picker already has stable visible section labels, Micromax should expose the same grouped structure through hostcalls and reuse those labels for `prompt_current_section`, `prompt_current_preview`, and headless `status-summary` instead of falling back to generic nouns.

Why:
- rev135 established that marks/jumplist entries benefit from real section labels shared across TUI headers, section-jump navigation, and preview/status surfaces.
- Buffer and plugin pickers already had enough metadata to group rows (`Help` / `Scratch` / project-root buckets for buffers, `Errors` / `Loaded` / `Available` for plugins), but future UIs/scripts still had to reverse-engineer that grouping from flat row text.
- Recent-file, buffer, and plugin previews were also drifting from the visible picker sections (`Recent file`, `Buffer`, `Word`) even when the UI was clearly showing project-root / `Help` / `Errors` sections.

Implemented in rev136:
- added a small shared `_group_prompt_rows_by_section()` helper in `src/micromax_editor/editor.py`
- added `buffer_section_rows()` / `plugin_section_rows()` and hostcalls `ed.buffer-section-rows` / `ed.plugin-section-rows`
- `prompt_current_section()` now reuses visible grouping labels for recent/buffer/plugin picker kinds
- `status_summary()` now includes `prompt_item=` for any non-command/find picker when a current preview exists, not just palette/topic/binding
- added focused tests for grouped buffer/plugin hostcalls, recent/buffer/plugin preview parity, and status-summary parity

Consequence:
- future UIs/LLMs can consume grouped picker structure directly across more picker kinds
- prompt preview/status surfaces now describe the same group the user is visibly in, instead of a generic fallback category



## rev137 (2026-03-08)

### D0XX — Binding picker sections should reuse winning-mode labels across UI + host surfaces

**Decision**: `bindingpick` should group rows by the binding's resolved winning mode and expose that same grouped shape through a hostcall, while `prompt_current_section`, `prompt_current_preview`, status surfaces, TUI headers, and section-jump navigation all reuse those same labels instead of collapsing everything into a generic `Binding` bucket.

**Why**: after rev135/rev136, the remaining obvious flat navigation-heavy picker was the searchable current-binding prompt. VS Code Quick Pick guidance says separators are a good fit when there are multiple obvious groups, and Helix continues to treat pickers as a first-class navigable surface with their own keymaps. Current-binding rows already knew their winning mode; the missing piece was one shared label policy instead of TUI-only formatting or status-only special cases.

**Implemented in rev137**:
- added `_binding_row_mode()`, `_binding_section_label()`, and `binding_section_rows()` in `src/micromax_editor/editor.py`
- added host feature / hostcall `ed.binding-section-rows` plus convenience word `binding-sections`
- `prompt_row_section_label()` and `prompt_current_section()` now reuse binding winning-mode labels (`Prompt`, active mode names like `nav`, `Global`)
- `prompt_current_preview()` / `ed.status` / `ed.status-summary` inherit that same label reuse automatically
- added focused tests for hostcalls, status parity, and TUI section headers

**Consequence**: future UIs/LLMs can consume grouped binding rows directly instead of reverse-engineering picker headers from flat `menu` strings, and the headless picker substrate stays more internally consistent.



## rev138 (2026-03-08)

### D0XX — docs picker sections should reuse numbered docs families across UI + host surfaces

**Decision**: `helppick` should group rows by the repo's existing numbered docs families and expose that same grouped shape through a hostcall, while `prompt_current_section`, `prompt_current_preview`, status surfaces, TUI headers, and section-jump navigation all reuse those same labels instead of collapsing every docs row into a generic `Doc` bucket.

**Why**: after rev135-rev137, the obvious remaining flat navigation-heavy picker was the docs picker. VS Code Quick Pick guidance says separators are a good fit when there are multiple obvious groups, and Helix continues to treat pickers as a first-class navigable surface with their own keymaps. Micromax's docs tree already had a stable grouping signal in its numeric prefixes (`00-*`, `10-*`, `20-*`, ...), so the missing piece was one shared label policy rather than more UI-only decoration.

**Implemented in rev138**:
- added `_doc_section_info_for_path()`, `_doc_section_label()`, and `doc_section_rows()` in `src/micromax_editor/editor.py`
- added host feature / hostcall `ed.doc-section-rows` plus convenience word `doc-sections`
- `prompt_row_section_label()` and `prompt_current_section()` now reuse numbered docs-family labels for docs rows
- `prompt_current_preview()` now leads docs previews with the human doc title (`menu`) instead of the slug topic (`insert`)
- added focused tests for docs hostcalls, section-jump navigation, and status parity

**Consequence**: future UIs/LLMs can consume grouped docs rows directly instead of reverse-engineering section headers from filenames, and the docs picker now reads more like a real navigation surface than a bare file list.


## rev139 (2026-03-08)

### D0XX — recent-file picker sections should reuse the existing project-root grouping across UI + host surfaces

**Decision**: `recentpick` should flatten the same shared project-root grouping already exposed through `ed.recent-section-rows`, while `prompt_row_section_label()`, TUI headers/sticky headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces all reuse those same labels instead of showing repeated project roots inside a flat MRU stream.

**Why**: after rev135-rev138, most navigation-heavy pickers had converged on the same shared pattern: real section labels first, then TUI/host/status reuse. Recent files were the remaining odd case because the host already had grouped project rows, but the live prompt still showed a flat MRU list with repeated section labels. VS Code Quick Pick guidance still recommends separators for multiple obvious groups, and Helix keeps treating pickers as a first-class navigable surface, so the right Micromax move was another small shared-label fix rather than more UI-only decoration.

**Implemented in rev139**:
- added `_recent_section_label()`, `_recent_section_row()`, and `_recent_section_rows()` in `src/micromax_editor/editor.py`
- `recent_section_rows_by_project()` / `recent_section_rows_by_dir()` now reuse that shared helper instead of maintaining separate grouping logic
- `_recent_prompt_rows()` now flattens grouped project-root buckets for the live `recentpick` prompt, keeping items contiguous by section while preserving first-seen MRU section order
- `prompt_row_section_label()` now reuses `_recent_section_label()` for recent rows
- added focused tests for grouped recent prompt rows, section-jump navigation, and minimal-TUI section headers

**Consequence**: future UIs/LLMs no longer need to choose between the grouped hostcall view and the live prompt view for recent files; both now tell the same story, and recent rows read more like a navigable project list than a raw path dump.


## rev140 (2026-03-08)

### D0XX — picker prompts should expose one shared current-item position model

**Decision**: searchable picker-style prompts should expose one compact current-item position model — overall `index/count`, current section label, section-local `i/n`, and a ready-to-display summary string — through `prompt_current_position()`, status-model fields, hostcall `ed.prompt-current-position`, and the minimal TUI prompt line.

**Why**: rev135-rev139 gave Micromax real grouped picker sections plus section-jump navigation, but long pickers still made users/scripts reconstruct “where am I?” independently from raw row lists or TUI window state. VS Code keeps treating Quick Pick separators as navigable structure rather than decoration, Helix keeps treating pickers as their own navigable surface, and GitHub’s command palette keeps emphasizing context/recentness. Once Micromax had sections and recency, the next small shared win was a single ordinal model reused everywhere rather than another UI-only label tweak.

**Implemented in rev140**:
- added `prompt_current_position()` in `src/micromax_editor/editor.py`
- status-model now mirrors that data as `prompt_index`, `prompt_count`, `prompt_section_index`, `prompt_section_count`, and `prompt_position_summary`
- `status_summary()` now also includes `prompt_pos=...` for picker-style prompts
- added host feature / hostcall `ed.prompt-current-position` plus convenience word `prompt-current-position`
- minimal TUI prompt line now shows `[index/count • section i/n]` next to the existing current-item preview
- added focused tests for hostcall, status parity, and TUI prompt-line rendering

**Consequence**: future UIs/LLMs do not need to infer picker ordinals from windowing state or raw suggestion arrays, and the live TUI now explains selection position using the same data shape that headless status/debug surfaces already see.



## rev141 (2026-03-08)

### D0XX — topic picker live rows should reuse visible topic families, not a flat command-heavy stream

**Decision**: `topicpick` should flatten the same grouped topic families already exposed through `ed.topic-section-rows` / `ed.apropos-section-rows`, while `prompt_current_section`, preview/status surfaces, TUI section headers, and `Alt-Up` / `Alt-Down` all reuse the same visible labels (`Commands`, `Actions`, `Words`) instead of drifting between plural host-side groups and singular fallback labels like `Command`.

**Why**: the recent picker work (rev135-rev140) kept teaching the same lesson: once Micromax gives a picker real section labels, the live prompt should usually reuse them too instead of hiding the grouping behind headless helpers. VS Code Quick Pick guidance keeps treating separators as real structure for obvious groups, and Helix keeps treating pickers as their own navigable surface. `topicpick` already had grouped section rows headlessly, but the live prompt still showed a flat command-heavy stream and the status model still reported singular fallback labels.

**Implemented in rev141**:
- `topicpick` now flattens grouped topic families for the live prompt instead of using a flat row list
- empty-query `topicpick` now budgets the initial browse window across visible sections so Commands do not consume the whole first page before Actions/Words appear
- `prompt_current_section()` now reuses the visible plural topic section labels for `topic` prompts
- added focused tests for section ordering, `Alt-Up` / `Alt-Down` jumps, status-model parity, and TUI header rendering

**Consequence**: future UIs/LLMs no longer have to choose between the headless grouped topic view and the live prompt view, and `topicpick` now behaves more like a small browsable navigator than a giant commands-only wall.


## rev142 (2026-03-08)

### D0XX — command palette live rows should reuse visible palette sections, not flat command-heavy browse order

**Decision**: `commandpick` should flatten the same grouped palette sections already exposed through `ed.command-palette-section-rows`, while `prompt_current_section`, preview/status surfaces, TUI section headers, and `Alt-Up` / `Alt-Down` all reuse the same visible labels (`Recent Files`, `Recent`, `Commands`, `Actions`, and path-query buckets like `Directories` / `Files` / `Open`) instead of drifting into singular fallbacks like `Command` or hiding whole sections behind the first-row cap.

**Why**: rev135-rev141 kept teaching the same lesson: once Micromax gives a picker real section labels, the live prompt should usually reuse them too instead of leaving grouping as a hostcall-only affordance. VS Code Quick Pick guidance still recommends separators for multiple obvious groups, Helix still treats pickers as their own navigable surface, and GitHub's command palette still emphasizes context plus recently used resources. `commandpick` already had grouped section rows headlessly, but the live prompt was still mostly flat and empty-query browsing could hide `Actions` behind `Commands`.

**Implemented in rev142**:
- added shared grouped-section limiting helpers so grouped picker hostcalls and live prompt flattening reuse the same browse-window policy
- `command_palette_section_rows()` now keeps empty-query palette sections grouped first and applies a tiny round-robin browse budget across visible sections
- `_palette_prompt_rows()` now flattens those grouped sections instead of pulling from a flat row list
- `prompt_current_section()` for palette prompts now returns the visible section label directly (`Commands`, `Recent Files`, etc.)
- added focused tests for hostcalls, section-jump navigation, status/preview parity, and TUI section headers

**Consequence**: future UIs/LLMs no longer have to choose between the grouped palette hostcall view and the live prompt view, and the command palette now behaves more like a real navigable picker than a flat alphabetized command wall.


## rev143 (2026-03-08)

### D0XX — grouped picker sections should also control the initial browse window across section-aware pickers

**Decision**: `bindingpick`, `bufferpick`, `markpick`, `jumppick`, `pluginpick`, `recentpick`, and `helppick` should flatten their grouped section rows through the same shared browse-window policy already used by `topicpick` / `commandpick`, so empty-query browsing keeps later visible sections represented instead of letting one large first section consume the whole initial row cap.

**Why**: rev135-rev142 kept teaching the same lesson: once Micromax gives a picker real section labels, the live prompt should usually reuse them not just for headers and section jumps, but also for the *windowing policy* that decides what is visible on first open. VS Code Quick Pick guidance still recommends separators for multiple obvious groups, which makes little sense if the initial window can hide every section after the first. Micromax already had grouped headless rows for these picker kinds; the missing piece was making the live prompt borrow rows from each visible section before the user starts filtering.

**Implemented in rev143**:
- `_binding_prompt_rows()`, `_buffer_prompt_rows()`, `_mark_prompt_rows()`, `_jump_prompt_rows()`, `_plugin_prompt_rows()`, `_recent_prompt_rows()`, and new `_doc_prompt_rows()` now flatten grouped section rows through `_flatten_grouped_prompt_sections()`
- empty-query browse windows for those picker kinds now pass `browse_budget=True`, so one large first bucket no longer monopolizes the initial row cap
- added focused tests covering browse-budget parity across binding, buffer, plugin, recent, docs, mark, and jump pickers

**Consequence**: grouped picker structure now matters earlier and more consistently: TUI headers, `Alt-Up` / `Alt-Down`, preview/status surfaces, tests, and headless grouped row APIs all tell the same story even before the user narrows the list.


## rev144 (2026-03-08)

### D0XX — docs-focused pickers should use the same grouped browse-window policy as other section-aware pickers

**Decision**: `helplinkpick` and `helpnavpick` should flatten their grouped section rows through the same shared browse-window policy already used by the other section-aware pickers, so empty-query browsing keeps later visible sections represented instead of letting one large first bucket monopolize the row cap.

**Why**: rev135-rev143 kept teaching the same lesson: once Micromax exposes real section labels for a picker, the live prompt should usually reuse them for headers, section jumps, and *initial windowing* too. Docs-focused pickers still had grouped section APIs (`ed.helplink-section-rows`, `ed.helpnav-section-rows`), but the live empty-query windows could still hide later sections behind a large first group. The right Micromax move was another tiny shared-policy fix rather than docs-picker-specific heuristics.

**Implemented in rev144**:
- added `_helplink_prompt_rows()` and `_helpnav_prompt_rows()` in `src/micromax_editor/editor.py`
- `_refresh_helplink_prompt_suggestions()` now flattens `help_link_section_rows()` through `_flatten_grouped_prompt_sections()` for empty queries
- `_refresh_helpnav_prompt_suggestions()` now flattens `help_nav_section_rows()` through the same helper for empty queries
- added fixture doc `docs/110-help-picker-sections.md` plus focused tests for section visibility and `Alt-Up` / `Alt-Down` navigation under a deliberately small row cap

**Consequence**: future UIs/LLMs no longer need to treat docs-focused pickers as special cases; the grouped section APIs, live prompt window, TUI headers, and section-jump behavior now tell the same story even before filtering narrows the list.

## 2026-03-08 — Docs picker visible section-label parity

**Decision**: docs-focused picker/status surfaces should reuse the same *visible* section labels that the grouped picker/TUI layer already shows, instead of older singular fallback nouns.

**Why**: rev135-rev144 kept pushing Micromax toward one shared picker substrate: once a picker has real visible groups, previews, status/debug output, and section-jump logic should all speak the same labels. `helplinkpick`, `helpnavpick`, and `helpoutlinepick` were the remaining obvious drift: headers said `Docs` / `Files` / `External` / `Headings`, while `prompt_current_section()` still emitted `Doc link`, `File link`, `External link`, and `Heading`. That mismatch was tiny, but it leaked into `prompt_current_preview()` and the headless status model too.

**What changed**:
- `prompt_current_section()` for `helplink`, `helpnav`, and `helpoutline` now returns the same visible section labels already used by `prompt_row_section_label()` and the minimal TUI
- `prompt_current_preview()` and `ed.status` now inherit those same labels automatically
- added focused tests for `helplinkpick`, `helpnavpick`, and `helpoutlinepick` status/preview parity

**Consequence**: docs-picker headers, section jumps, preview/status surfaces, and tests now all use one shared vocabulary, which makes future picker polish less error-prone and easier for headless consumers/LLMs to reason about.


## rev146 (2026-03-08)

### D0XX — picker scroll-window state should be shared editor structure, not TUI-local logic

**Decision**: the minimal TUI's section-aware picker windowing (sticky headers, `more…` markers, hidden-row counts, selected visible slice) should live in one shared editor helper (`prompt_window_model`) and be exposed headlessly through `ed.prompt-window` / `prompt-window` instead of remaining trapped inside `tui.py`.

**Why**: rev135-rev145 kept teaching the same lesson: once Micromax gives pickers real sections, headless surfaces should usually be able to inspect the same structure the live UI uses instead of re-deriving it. The picker row substrate, grouped section hostcalls, current preview text, and current position model were already shared; the remaining drift was that scroll-window state still existed only in the TUI renderer.

**Implemented in rev146**:
- added `Editor.prompt_window_model(max_lines=...)` as the shared picker-window helper
- minimal TUI prompt rendering now consumes that helper instead of recalculating windowing/sticky-header state privately
- added host feature / hostcall `ed.prompt-window` plus convenience word `prompt-window`
- added focused tests for helper/model parity and hostcall exposure

**Consequence**: future UIs/scripts/LLMs can now inspect the same visible picker slice the TUI uses — including sticky section headers and hidden counts — without redoing window math from raw suggestion rows.


### D0XX — rendered picker rows should be shared editor structure, not TUI-local formatting

**Decision**: the minimal TUI's visible picker rows (header text, sticky headers, `more…` markers, selected-row prefixes, and heading indentation for docs/navigation pickers) should live in one shared editor helper (`prompt_display_model`) and be exposed headlessly through `ed.prompt-display` / `prompt-display` instead of remaining trapped inside `tui.py`.

**Why**: rev140-rev146 kept moving picker UX toward one shared substrate: grouped section rows, current preview labels, current-item position, and the visible scroll window are already editor-side data, but the final visible row text still lived only in the TUI renderer. VS Code keeps treating Quick Pick separators as real structure for grouped selections, and Helix keeps treating pickers as a dedicated navigable surface. Once Micromax exposed window structure headlessly in rev146, the smallest follow-on was exposing the actual rendered prompt rows too, so future UIs/scripts/LLMs do not have to re-derive visible row text from raw suggestions plus window metadata.

**Implemented**:
- added `Editor.prompt_display_model(max_lines, width)` as a shared rendered-row helper layered on top of `prompt_window_model()`
- minimal TUI prompt rendering now consumes that helper instead of formatting visible picker rows privately
- added host feature / hostcall `ed.prompt-display` plus convenience word `prompt-display`
- added focused tests for hostcalls and TUI/display parity

**Consequence**: future UIs/scripts/LLMs can inspect the same visible prompt lines the TUI shows — including sticky headers, `more…` markers, selected rows, and heading indentation — without redoing formatting logic from raw suggestion arrays.


## rev148 (2026-03-08)

### D0XX — narrow picker rows should preserve trailing detail instead of blindly truncating at the right edge

**Decision**: shared rendered picker rows should fit narrow widths by preserving trailing detail (paths, locations, modes, etc.) when possible instead of simply slicing the full `name — detail` string at the right edge.

**Why**: rev140-rev147 kept moving picker UX toward one shared substrate, but the final clipping behavior was still a little too dumb: long row names could easily hide the distinguishing part of the row, especially for docs/path-heavy pickers where the tail often matters more than the middle. VS Code keeps treating Quick Pick rows as a scan-heavy surface, and Micromax's shared `prompt_display_model` is already the place future UIs/LLMs inspect visible rows. The smallest honest improvement was not a richer widget system, but slightly smarter clipping in the shared model itself.

**Implemented**:
- added tiny shared helpers for right/left ellipsis and left+right row fitting in `src/micromax_editor/editor.py`
- `prompt_display_model()` now preserves trailing detail blocks when rows are narrow, truncating the leading name first when possible
- header / sticky-header / `more…` rows now also ellipsize a bit more cleanly under tiny widths
- added focused tests for narrow-row tail preservation and tiny-width header clipping

**Consequence**: the shared visible picker model is now a little closer to what users actually need to scan, and future UIs/LLMs inherit that improvement automatically instead of each inventing their own clipping heuristics.


### D0XX — keep `curses` as the current TUI backend until the headless-first substrate truly outgrows it

**Decision**: Micromax should keep Python `curses` as the current TUI backend and treat `prompt_toolkit` as a later optional backend only if the project genuinely needs a richer layout/widget system than the shared headless substrate wants.

**Why**: the project is still winning by moving behavior into shared editor-side models, not by growing a more sophisticated renderer. `curses` keeps the offline archive workflow small and dependency-light, while `prompt_toolkit` remains attractive later if Micromax ever needs a much richer full-screen composition layer. Resolving the lingering worklist TODO explicitly is better than letting future humans/LLMs infer a hidden decision from the existence of the current curses loop.

**Implemented**:
- closed the lingering worklist TODO for terminal-library choice
- added `docs/111-terminal-library-decision.md` with the rationale, tradeoffs, and migration triggers

**Consequence**: future contributors have a documented default: keep the renderer thin, keep shared editor-side models growing, and only pay the cost of a richer terminal toolkit when concrete UI needs justify it.

## rev149 — ordinary markdown list markers get the same tiny scanability treatment

- The docs/help TUI already gave task lists, tables, blockquotes, thematic breaks, and inline emphasis a little scanability polish, but plain bullet/ordered lists were still visually flatter than the markdown people actually read in worklists and docs.
- Current CommonMark keeps ordinary list markers intentionally small and regular: bullet markers are `-`, `+`, or `*`; ordered markers are 1–9 digits followed by `.` or `)`; and list markers may be indented by up to three spaces before the marker. GitHub's task-list docs also keep task items rooted in ordinary list items rather than inventing a separate block form.
- That made the next low-risk win obvious: add one tiny shared list-marker helper in the curses TUI, reuse it under task-list detection, and style only the marker token itself.
- Kept scope intentionally tiny and UI-only: no new headless markdown AST, no nested-list layout model, no wrapped-item semantics, and no promise that every list edge case is recognized outside the common forms already worth scanning in repo docs.

**Consequence**: plain worklists, numbered steps, and TODO-heavy docs become a little easier to scan, while task-list checkbox styling now layers on top of a more general list substrate instead of carrying its own regex forever.

## rev150 — setext headings should reuse the shared heading scan for live TUI styling too

- The docs/help browser already trusted one tiny heading scan for titles, outline rows, fragment jumps, and heading breadcrumbs, but the live TUI still mostly styled headings through an ATX-only regex.
- Current CommonMark says setext headings consist of one or more lines of paragraph-like text followed by `=` / `-` underlines, and GitHub Docs says GFM stays CommonMark-compliant. That made the drift visible: setext headings behaved like headings for navigation, yet still looked like ordinary prose plus punctuation in the live docs buffer.
- The Micromax-sized fix was to add one tiny shared compatibility helper, `Editor._md_heading_line_roles()`, layered directly on `_md_heading_scan()` instead of inventing a second render-only parser.
- The curses TUI now uses that helper so ATX headings, single-line setext headings, and multi-line setext headings share one source of truth for title/underline styling.

**Consequence**: docs/help rendering is a little more honest about the markdown structure the browser already understands, and future UIs/scripts/LLMs can reuse one tiny heading-role helper instead of reverse-engineering setext parity from TUI-local regexes.
## rev151 — fenced-code render parity should reuse the shared fence scan too

**Decision**: docs/help rendering should also reuse one tiny shared fenced-code line-role helper so fenced markdown examples look visibly code-ish in the live TUI instead of only behaving like inert prose under the hood.

**Why**: rev122 already made fenced code blocks inert for `helpfollow`, `helplinkpick`, reference/footnote-definition parsing, and TUI docs-link underlining, but the live docs buffer still rendered those examples as visually ordinary prose. CommonMark keeps fenced code blocks intentionally regular (fence opener/closer, up to three leading spaces), and GitHub Docs treats triple-backtick code fences as a standard authoring form, so the drift was visible in exactly the repo docs people actually read.

**What changed**:
- added `Editor._md_fenced_code_line_roles()` as a tiny shared helper returning `fence` / `body` roles per source line
- the curses TUI now dims fenced body lines and styles opening/closing fence lines bold+dim
- added focused helper/render tests and documented the behavior in the help-browser + handoff docs

**Consequence**: docs/help rendering becomes a little more honest about the fenced examples the browser already understands, and future UIs/scripts/LLMs can reuse one tiny fence-role helper instead of reverse-engineering code-block parity from TUI-local rendering rules.



## rev152 — blank-separated indented code-ish lines should stay inert across docs surfaces too

**Decision**: blank-separated top-level indented code-ish markdown lines in docs/help buffers should stay inert for `helpfollow`, `helplinkpick`, and TUI docs-link underlining too, and the live docs/help TUI should dim those lines through one tiny shared helper.

**Why**: rev130 already taught the docs browser that some four-space/tab-indented lookalikes are really code-ish prose for reference definitions, footnote definitions, and ATX heading scanning, but ordinary inline links/autolinks on blank-separated indented lines could still look live and clickable in the source-view help buffer. Current CommonMark keeps indented code blocks rooted in four-space indentation, and GitHub still teaches indented code as a normal Markdown authoring pattern. Micromax still does not need a full list-aware block parser here; it just needs one shared answer for the top-level examples that actually show up in repo docs.

**What changed**:
- added `md_indented_code_line_flags()` as a tiny shared helper for blank-separated top-level indented code-ish runs
- `helpfollow` / `helplinkpick` now ignore inline links and autolinks on those lines
- the curses TUI now also dims those lines and suppresses docs-link underlining there
- expanded the docs fixture + focused navigation/picker/render tests

**Consequence**: source-view code examples in docs/help buffers are a little more honest and less surprise-clickable, while the project still avoids a fuller markdown block parser or renderer-specific special cases.

## rev153 — raw HTML/comment render parity should reuse the same shared precedence helpers

**Decision**: docs/help rendering should also dim raw HTML comment spans and raw HTML block lines using the same tiny shared helpers already trusted for docs navigation, definition parsing, and TUI docs-link underlining.

**Why**: rev124, rev127, and rev128 already made raw HTML comments and raw HTML blocks inert for the actual docs browser semantics, but the live docs/help TUI still let those regions look mostly like ordinary prose. Current CommonMark treats HTML blocks as raw HTML, and GitHub Docs says its GFM stays CommonMark-compliant. That made the remaining drift obvious: Micromax already knew those regions were literal storage, so the live renderer should stop visually over-promising too.

**What changed**:
- reused existing shared helpers `md_html_comment_line_spans()` and `md_html_block_line_flags()` instead of adding another parser path
- the curses TUI now dims raw HTML block lines through the existing base-line styling path
- raw HTML comment spans now join the existing dim-span overlay path, so inline/block comments both read less like active prose
- added focused render tests and updated the help-browser + handoff docs

**Consequence**: docs/help rendering is a little more honest about the literal HTML/comment regions the browser already understands, and future UIs/scripts/LLMs can keep reusing the same tiny precedence helpers instead of rediscovering special cases from scratch.



## rev154 — reference/footnote definitions should reuse shared definition logic for live TUI styling too

**Decision**: docs/help rendering should also reuse one tiny shared definition-line helper so reference-definition starter lines and footnote-definition starter lines read like definitions in the live TUI instead of only participating invisibly in docs navigation.

**Why**: the docs browser already trusted tiny shared parsers for reference definitions and footnote definitions, including wrapped reference-destination/title forms, but the live docs buffer still let those lines read almost exactly like ordinary prose. Current CommonMark keeps link reference definitions intentionally regular, and GitHub Docs explicitly teaches Markdown footnotes as visible source syntax with definition starter lines and even multi-line note bodies. That made the remaining drift obvious in exactly the repo docs Micromax already ships.

**What changed**:
- added `md_reference_def_target_info()` so the tiny shared reference-definition parser can report how many continuation lines it consumed
- added `Editor._md_definition_line_roles()` as a tiny shared render helper covering reference-definition starter lines, wrapped reference-definition continuation lines, and footnote-definition starter lines
- the curses TUI now dims those definition lines and bolds the visible marker token (`[id]:` / `[^id]:`) on starter lines
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: source-view docs read a little more honestly, and future UIs/scripts/LLMs can reuse one tiny definition-role helper instead of re-deriving where definitions begin from renderer-local regexes.


## rev155 — nested source-view lists should stay list-like once indented-code has already been ruled out

**Decision**: the live docs/help TUI should also bold nested markdown list/task markers when deeper indentation is clearly acting like list nesting, but only after the shared indented-code pass has already ruled out real top-level code blocks.

**Why**: rev149 gave ordinary list markers a small scanability hint, but real repo docs still contain deeper-indented worklist bullets and nested task rows that flattened back into prose in source view. GitHub’s current Markdown docs still teach visually nested lists/task lists as a normal authoring pattern, while CommonMark still keeps top-level indented code as a distinct concept. That made the right Micromax-sized move pretty clear: keep the default helper conservative, then let the live TUI opt into a slightly looser nested-list reading only in already-non-code contexts.

**What changed**:
- extended the tiny list/task helpers with an opt-in relaxed-indent mode
- kept the default helper behavior conservative for isolated line parsing/tests
- the curses TUI now uses the relaxed mode only after `md_indented_code_line_flags()` has already ruled out real code-ish lines
- expanded docs/help fixtures plus focused helper/render tests

**Consequence**: nested bullets and nested task rows in source-view docs scan more like real lists, while literal indented code examples keep their existing inert/code-ish treatment.


## rev156 — GitHub-style blockquote alert markers should get the same tiny source-view cue

**Decision**: docs/help rendering should also give blockquote-based GitHub alert opener tokens like `[!NOTE]` / `[!WARNING]` a tiny source-view cue, reusing one small shared helper layered on the existing blockquote scan instead of growing a fuller alert/admonition parser.

**Why**: rev113 already made ordinary blockquote rails read better in the live docs/help TUI, but current GitHub Markdown docs now also teach alerts as a blockquote-based extension with opener lines like `> [!NOTE]` and `> [!WARNING]`. That makes alert opener lines part of the Markdown authors are actually likely to paste into Micromax, not hypothetical syntax trivia. The drift was small but real: Micromax already made the quote rail visible, yet the high-signal alert token still looked almost like ordinary dim body text.

**What changed**:
- added `md_blockquote_alert_marker()` as a tiny shared helper layered on `md_blockquote_prefix()`
- the curses TUI now bolds common GitHub alert opener tokens (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) while keeping the quoted body dim
- expanded the help-browser docs fixture and added focused helper/render tests

**Consequence**: GitHub-style alert opener lines in source-view docs scan a little more honestly, while the project still avoids promising a fuller admonition/callout renderer or another parser path for docs/help styling.


## rev157 — visible footnote references should get the same tiny source-view cue

**Decision**: docs/help rendering should also give visible markdown footnote references like `[^note]` a small source-view cue, reusing one tiny helper layered on the existing shared footnote matcher instead of adding another parser path.

**Why**: Micromax already lets `[^id]` references navigate correctly in docs/help buffers, but the live TUI still let those source tokens read mostly like ordinary bracketed prose. GitHub's current Markdown docs explicitly teach footnotes as an author-facing syntax and show a multi-line footnote example, while Python-Markdown's footnotes docs also treat `[^id]` references and their definitions as ordinary visible source structure. That made the next Micromax-sized move pretty clear: do not build a richer footnote renderer, just make the existing source token a little easier to scan honestly.

**What changed**:
- added `md_footnote_ref_token_spans()` as a tiny UI helper layered on `md_link_matches()`
- the curses TUI now bolds whole visible footnote-reference tokens while still underlining the inner `^id` through the ordinary docs-link path
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: docs/help source view is a little more honest about the footnote references the browser already understands, while the project still avoids promising a fuller rendered-footnote model or another parser path.


## rev158 — visible autolinks should get the same tiny source-view cue

**Decision**: docs/help rendering should also give visible supported angle-bracket autolinks like `<https://...>` a small source-view cue, reusing one tiny helper layered on the existing shared autolink matcher instead of adding another parser path.

**Why**: Micromax already recognizes supported autolinks in docs/help buffers, but the live TUI still only underlined the inner URL, leaving the surrounding `<` / `>` looking like ordinary punctuation. CommonMark's current spec defines autolinks as angle-bracket-delimited source syntax, and GitHub's current Markdown docs still point authors toward automatic URL linking as an ordinary part of writing on GitHub. That made the next Micromax-sized move pretty clear: do not build a richer rendered-link system, just make the visible autolink token read a little more honestly in source view.

**What changed**:
- added `md_autolink_token_spans()` as a tiny UI helper layered on `md_link_matches()`
- the curses TUI now bolds whole visible supported autolink tokens while still underlining the inner URL through the ordinary docs-link path
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: docs/help source view is a little more honest about the supported autolinks the browser already understands, while the project still avoids promising a fuller rendered-link model or another parser path.

## rev159 — visible markdown image tokens should read like deliberately inert source

**Decision**: docs/help rendering should also give visible supported markdown image forms like `![alt](dest)` and `![alt][id]` a small inert-source cue, reusing one tiny helper layered on the existing shared markdown destination/reference helpers instead of adding another parser path.

**Why**: Micromax already ignores markdown image syntax for `helpfollow`, `helplinkpick`, and docs-link underlining, but the live TUI still let those source tokens read almost like ordinary prose. CommonMark's current spec treats image syntax as distinct visible source where the bracketed text is image description/alt text rather than ordinary link text, and GitHub's current Markdown docs still teach authors to write images with `![alt](url)`. That made the next Micromax-sized move pretty clear: do not build a richer rendered-image system yet, just make the existing inert source token a little easier to scan honestly.

**What changed**:
- added `md_image_token_spans()` as a tiny UI helper layered on shared balanced-span / escape / destination / reference helpers
- the curses TUI now dims whole visible supported inline/reference/shortcut image tokens in docs/help buffers
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: docs/help source view is a little more honest about the markdown image tokens the browser already treats as inert, while the project still avoids promising a fuller rendered-image model or another parser path.




## rev161 — visible ordinary markdown links should show a little source scaffolding too

**Decision**: docs/help rendering should also give visible supported ordinary markdown links like `[label](dest)`, `[label][id]`, and `[shortcut]` a tiny source-view cue by dimming only the non-label source scaffolding, reusing one small helper layered on the existing shared link matcher instead of adding another parser path.

**Why**: Micromax already underlines live docs-link labels, but the surrounding markdown scaffolding still read like ordinary punctuation even though inline, reference, and shortcut links are explicit visible source forms in current CommonMark and GitHub Markdown authoring. That left a small honesty gap in source view: autolinks, footnote references, images, and raw HTML tags already had token-level cues, while the most common markdown links still looked almost fully rendered. The right Micromax-sized move was not a richer markdown renderer; it was a tiny parity follow-up that keeps the label visibly live while letting the brackets and destination/reference tail read more like source.

**What changed**:
- added `md_link_source_token_spans()` as a tiny UI helper layered on `md_link_matches()`
- the curses TUI now dims non-label link scaffolding for supported inline/reference/shortcut links while keeping the label underlined
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: docs/help source view is a little more honest about the ordinary markdown link syntax the browser already understands, while the project still avoids promising a fuller rendered-markdown model or another parser path.

## rev162 — visible inline emphasis delimiters should show up as source punctuation too

**Decision**: docs/help rendering should also give visible markdown inline-emphasis delimiters like `**`, `*`, `_`, and `~~` a tiny source-view cue by dimming the delimiter tokens while keeping the existing body styling, reusing one small helper layered on the existing inline-emphasis regex helpers instead of adding another parser path.

**Why**: Micromax already bolded strong bodies, italicized/underlined emphasis bodies, and dimmed strike bodies in docs/help source view, but the visible delimiter tokens still read almost like stray punctuation. Current CommonMark still defines emphasis/strong emphasis in terms of visible delimiter runs, and GitHub's current Markdown docs still teach bold/italic/strikethrough as ordinary author-facing source syntax. That made the next Micromax-sized move pretty clear: do not build a richer rendered-markdown system, just make the visible punctuation around already-styled emphasis read a little more honestly in source view.

**What changed**:
- added `md_inline_markup_delimiter_spans()` as a tiny UI helper layered on the existing inline-emphasis regex helpers
- the curses TUI now dims visible supported emphasis/strong/strike delimiter tokens while keeping the existing body styling intact
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: docs/help source view is a little more honest about the visible punctuation around the tiny inline emphasis forms Micromax already styles, while the project still avoids promising fuller CommonMark delimiter-run semantics or another parser path.



## rev163 — visible inline-code backticks should show up as source punctuation too

**Decision**: docs/help rendering should also give visible markdown inline-code backtick delimiters a tiny source-view cue by making the opening/closing backtick runs bold+dim while keeping the existing code-body dimming, reusing one small shared helper layered on the existing equal-length backtick scan instead of adding another parser path.

**Why**: Micromax already dims inline-code bodies in docs/help source view and already trusts the same equal-length backtick scan for docs-link precedence, but the visible backtick delimiters still read mostly like stray punctuation. Current CommonMark still defines code spans in terms of matching backtick strings of equal length, and GitHub's current Markdown docs still teach inline code as an ordinary backtick-delimited author-facing form. That made the next Micromax-sized move pretty clear: do not build a richer rendered-markdown system, just make the visible punctuation around already-inert code spans read a little more honestly in source view.

**What changed**:
- added `md_inline_code_delimiter_spans()` as a tiny shared helper layered on the existing equal-length backtick scan
- the curses TUI now renders visible inline-code backtick delimiter runs bold+dim while keeping the existing dim code-body styling intact
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: docs/help source view is a little more honest about the visible punctuation around the inline code spans Micromax already understands, while the project still avoids promising fuller CommonMark whitespace-normalization or another parser path.

## rev165 — multi-line footnote-definition continuation lines should share the existing definition cue

**Decision**: tiny indented continuation lines under markdown footnote-definition starters in docs/help buffers should also render dim in the live TUI, reusing the existing shared definition-line roles instead of adding another parser path.

**Why**: Micromax already gives visible `[^id]:` starter lines a dim+bold definition cue, but small multi-line footnotes still let their continuation lines read like ordinary prose. GitHub's current Markdown docs still show that a footnote can have multiple lines, and Python-Markdown's footnotes implementation still treats indented continuation handling as part of the footnote block model. That made the next Micromax-sized move clear: do not build a richer footnote renderer, just make the already-supported source structure look a little more honest in the live docs buffer.

**What changed**:
- extended `_md_definition_line_roles()` with a tiny `footnote-cont` role for indented continuation lines under footnote-definition starters
- kept the starter-marker cue unchanged (`[^id]:` stays dim+bold) while continuation lines now render dim
- added focused helper/render tests and updated the help-browser + handoff docs

**Consequence**: multi-line footnotes now read a little more like real definition bodies in docs/help source view, while Micromax still avoids promising a fuller footnote parser or changing docs-buffer navigation semantics.
## rev166 — expand the portability corpus around real stdlib and safety behavior

**Decision**: keep growing `portability/kernel_cases.json` with small data-only cases for portable boot-stdlib and safety behavior the repo actually relies on, not just bare kernel arithmetic. Rev166 adds corpus coverage for `dip`, `2keep`, `tri`, `try?`, `try`, `ensure`, and budget exhaustion observed through `catch`.

**Why**: the worklist still calls out portability discipline as a current priority, and the existing corpus was useful but still slightly postcard-sized. Micromax's editor/docs/plugin story already leans on quotation combinators and safety boundaries conceptually, so future Rust/WASM hosts should be able to replay those behaviors against the Python oracle without importing pytest helpers or editor machinery.

**Notes**:
- kept the corpus data-only (`source` + expected stack or error substring)
- avoided hostcalls/editor surfaces/non-portable object expectations
- strengthened `tests/test_portability_suite.py` to assert the new cases stay present

**Consequence**: cross-host validation now covers a little more of the language that makes Micromax feel like Micromax, while still staying tiny enough to evolve by hand offline.



## rev171 — add a tiny optional ruler/relative-ruler gutter in the curses TUI

**Decision**: add optional `ruler` / `relativeruler` editor options and let the minimal curses TUI render a small line-number gutter, while keeping the feature explicitly UI-layer-only rather than promoting line numbers into headless editor state.

**Why**: Micro's current options docs still present line numbers as a small, ordinary editor option (`ruler`) with a relative-number companion (`relativeruler`), which makes that pair a good ergonomic reference for Micromax's micro-esque direction. The repo already has enough TUI substrate that the old worklist defer no longer made sense, but the project still wins by keeping structure headless and presentation thin. That made the next move pretty clear: reuse familiar option names, make the gutter optional, keep prompt/status surfaces full-width, and let wrapped continuation rows stay blank so softwrap does not repeat deceptive numbers on every visual row.

**What changed**:
- registered `ruler` and `relativeruler` options in the editor option registry
- added tiny TUI helpers `line_number_gutter_width()` and `line_number_gutter_text()`
- taught `_render()` to reserve gutter width honestly for viewport/cursor math while leaving prompt/status/picker surfaces full-width
- added focused TUI tests plus a small doc page (`docs/112-line-numbers.md`)

**Consequence**: Micromax now clears one more old micro-parity TODO with a feature small enough to evolve by hand, while future UIs remain free to render line numbers differently without inheriting hidden editor-core state.


## rev172 — make the existing `hlsearch` option visible in the curses TUI

**Decision**: honor the existing `hlsearch` option in the minimal curses TUI by reverse-highlighting visible matches for the current search pattern and bolding the visible match under the primary cursor, while keeping the feature renderer-local instead of storing persistent search-highlight spans in the headless editor model.

**Why**: micro's options docs still frame `hlsearch` as a small search UX toggle rather than a deep editor-state feature, and Neovim's `hlsearch` / current-match distinction points the same way: the editor should own the pattern, case/regex semantics, and cursor movement, but the renderer can derive match styling from whatever text it is already drawing. Micromax already had the option, `incsearch`, and stable search state; making the TUI actually show matches was a low-risk UX win and a better use of momentum than inventing a broader span/theme contract too early.

**Consequence**:
- visible matches in the current viewport now render with a small reverse-video cue when `hlsearch=true`
- the visible match under the primary cursor also renders bold, giving the minimal TUI a tiny `CurSearch`-like distinction without a new theme system
- the first pass intentionally operates on rendered row fragments, so softwrap/hscroll stay simple and future renderers remain free to implement richer search styling later
- the portability corpus also picked up small rev172 contract wins (`s<`, bare-VM `host.features`) so the archive's search/UI work and cross-host discipline both moved forward together

## rev173 — expose one shared whole-buffer search-position model and reuse it in the find prompt

**Decision**: add a tiny shared whole-buffer search-position model (`search_position_model`) to the editor core, mirror it through `status_model()` / `ed.status`, and let the minimal curses TUI reuse that same compact `current/total` summary in the live find prompt instead of leaving search awareness trapped inside `hlsearch` row styling.

**Why**: rev172 made the existing `hlsearch` option visible, but it still left one obvious UX gap: users could now *see* matches without any small shared answer to “which match am I on?” Vim/Neovim-style search count summaries (`[1/5]`) are a well-established lightweight search cue, and Micromax already had all the core ingredients — stable search state, `incsearch`, and a structured status model. The right move was not another TUI-only adornment, but one tiny editor-side contract that future statuslines/UIs/LLMs can all reuse.

**What changed**:
- added shared whole-buffer search helpers in `src/micromax_editor/search.py`
- added `Editor.search_position_model()` plus mirrored status fields: `search_query`, `search_literal`, `search_case_sensitive`, `search_match_index`, `search_match_count`, and `search_summary`
- `status-summary` now includes `search_pos=` when a search is active
- the minimal curses TUI now appends the shared `[i/n]` summary to the live find prompt
- the portability corpus also picked up a small sibling contract win: bare-VM `host.feature?` now has JSON-corpus coverage for a missing feature case

**Consequence**: Micromax search now has one more useful shared contract without growing a richer widget/theme/search-job subsystem too early, and future statuslines or alternate UIs can render search counts without re-deriving search semantics by hand.

## rev174 — make active search counts a first-class statusformat token

**Decision**: add a dedicated statusformat token `$(searchpos)` (aliases: `$(search)` / `$(searchcount)`) that renders the shared search-position summary as ` [i/n]`, and include it in the default right-side status format. Also extend the portability corpus with a tiny `find`-missing-returns-`0` case.

**Why**: rev173 put the whole-buffer search count in shared editor state and surfaced it in the find prompt, but ordinary statusline rendering still had to opt in manually via raw `$(search_summary)` strings. Neovim's documented `searchcount()` statusline pattern is a good precedent for one compact search-count token, while micro's options model keeps search UX in the realm of small composable cues instead of a heavyweight widget. The portability follow-up closes one more dictionary contract gap future Rust/WASM hosts should not have to learn from Python internals.

**Consequence**:
- default statuslines/TUI rendering now show active search position as `[i/n]` without custom configuration
- custom statusformat strings can opt into the same cue with `$(searchpos)` / `$(search)` / `$(searchcount)`
- the JSON portability corpus now includes missing-word `find` returning `0` alongside successful `find` returning an XT

## rev175 — move scroll windowing into the shared viewport contract

**Decision**: add a tiny `scrollmargin` editor option and honor it inside `ensure_cursor_visible()`, so the shared viewport model keeps vertical context rows around the primary cursor in both plain and softwrapped views. Also extend the portability corpus with `compiled?` returning `0` for a primitive XT.

**Why**: the current TODO still called out scroll windowing as one of the best remaining UX-polish areas, and Micro's current options docs still frame `scrollmargin` as a small ordinary editor setting rather than a renderer trick. Neovim's current tips docs point the same way with `scrolloff`: keeping a little context around the cursor makes movement feel calmer, and values above half the window height need a sane cap. For Micromax, that argued for one shared viewport rule instead of another curses-only behavior. The portability sibling closes one more tiny truth about tier-2-adjacent dictionary behavior so future hosts do not have to infer `compiled?` semantics from Python tests.

**Consequence**:
- plain vertical scrolling now moves a little earlier when `scrollmargin>0`, keeping context rows above/below the cursor when possible
- softwrapped views apply the same policy in **visual rows**, updating `top_subline` instead of inventing a separate wrapped-scroll rule
- the first pass stays intentionally small: vertical only, default `0`, and clamped to half the viewport height so tiny windows remain deterministic
- the JSON portability corpus now covers both the positive and negative side of `compiled?` (`compile` can produce bytecode, but primitive XTs still report `0`)

## rev176 — make a tiny `cursorline` cue visible in the curses TUI

**Decision**: honor a tiny `cursorline` option in the minimal curses TUI by underlining the current visible buffer row, including the active wrapped screen row under `softwrap`, while keeping the feature renderer-local instead of promoting current-line highlighting into the headless editor model.

**Why**: micro's current options docs still frame `cursorline` as a small display toggle, and Neovim's `cursorline` / `cursorlineopt=screenline` split is a useful reminder that wrapped views already have more than one honest policy. Micromax is still early enough that the important win is not theme sophistication; it is giving users one more cheap scanning cue without inventing a broader span/theme contract too soon.

**Consequence**:
- added editor option `cursorline` (default `true`)
- added `cursorline_row_attr()` in the curses TUI and layered it into plain-buffer, docs/help, gutter, and softwrap rendering
- under `softwrap`, only the active wrapped screen row is highlighted for now
- portability follow-up: `definitions-follows-top-of-search-order` makes one more namespace contract explicit in `portability/kernel_cases.json`



## rev182 — visible brace matching can now stay tiny and renderer-local

**Decision**: honor tiny micro-esque `matchbrace` / `matchbraceleft` options in the minimal curses TUI by bold-underlining visible brace pairs under or just left of the primary cursor, while keeping the feature renderer-local and syntax-agnostic instead of promoting persistent brace spans into the headless editor model.

**Why**: the worklist originally deferred bracket matching as “needs a renderer span model,” but the last several revisions quietly changed that premise. Micromax now already has enough tiny overlay machinery in the TUI (`hlsearch`, `cursorline`, `hltrailingws`, `hltaberrors`, `colorcolumn`, `scrollbar`) that brace highlighting can be implemented as one more local visibility cue instead of a new shared data model. micro's current options docs also still frame `matchbrace` and `matchbraceleft` as ordinary editor toggles, which makes the feature a good fit for Micromax's current “small option, small cue” direction.

**Consequence**:
- added editor options `matchbrace` and `matchbraceleft` (both default `true`)
- added tiny TUI helpers `matching_brace_positions()` and `brace_match_spans()`
- matching is textual/nest-aware across the whole buffer for classic `()[]{}` pairs, but intentionally not syntax-aware
- ordinary and docs/help buffers now bold-underline visible brace cells when a valid pair exists under or just left of the cursor
- portability follow-up: `get-order-roundtrip-preserves-precedence` makes one more search-order contract explicit in the JSON corpus


## rev183 — tiny overflow markers should stay renderer-local and softwrap-aware

**Decision**: honor a tiny `overflowmarkers` option in the minimal curses TUI by drawing bold+dim `<` / `>` cues at the visible edges of horizontally clipped rows in ordinary buffers and docs/help buffers, while intentionally suppressing the cue under `softwrap` and keeping all overflow state renderer-local instead of promoting it into the headless editor model.

**Why**: the current TODO still called out small viewport/scanability affordances as the best remaining low-risk wins. Recent TUI work (`cursorline`, `hltrailingws`, `hltaberrors`, `colorcolumn`, `scrollbar`, `matchbrace`) already established a useful pattern: small option, small renderer overlay, no new shared state unless future UIs genuinely need it. The best prior art points the same way. Vim/Neovim historically use explicit truncation or wrap cues (`@`, `@@@`, `showbreak`) at render time, while Emacs notes that wrap indicators on every visual line quickly become noisy enough that Visual Line mode suppresses them by default. That made one tiny non-softwrap edge cue the right Micromax-sized move.

**Consequence**:
- added editor option `overflowmarkers` (default `false`)
- added TUI helper `overflow_marker_cells()`
- ordinary buffers and docs/help buffers can now show small `<` / `>` edge cues when horizontal clipping would otherwise be invisible
- softwrapped rows intentionally suppress the cue because wrapping already exposes continuation implicitly
- portability follow-up: `dict-version-stable-across-find` makes one more tier-2-adjacent dictionary/cache-invalidation truth explicit in the JSON corpus


## rev184 — current-buffer position should be a shared status-model primitive, not picker-only state

**Decision**: expose a tiny current-buffer position model (`buffer_index`, `buffer_count`, `buffer_summary`) through `status_model()` / `ed.status`, add a dedicated statusformat token `$(bufpos)` (aliases: `$(bufferpos)` / `$(buffers)`), and include it in the default right-side statusline only when more than one buffer is open. Extend the portability corpus with a read-only `dict-version` case around `get-order`.

**Why**: Micromax already had shared prompt-position and search-position models, but ordinary multi-buffer editing still left one basic question trapped inside `bufferpick`: “which open buffer am I on?” The cheapest honest answer is not a tab bar and not another curses-only adornment; it is one tiny shared status primitive that every UI/script/LLM can reuse. Using `buffer_names()` keeps the ordering deterministic for tests and hostcalls instead of coupling the cue to MRU quirks. On the portability side, `dict-version` is explicitly meant to support tier-2 cache invalidation, so one more lookup-only search-order case makes that contract harder to accidentally regress.

**Consequence**:
- `ed.status` / `status_model()` now expose `buffer_index`, `buffer_count`, and `buffer_summary`
- `status-summary` now includes `buf_pos=` when more than one buffer is open
- statusformat templates can render the cue with `$(bufpos)` / `$(bufferpos)` / `$(buffers)`
- the default right-side statusline now shows the bracketed buffer position automatically in multi-buffer sessions
- the portability corpus now explicitly covers `dict-version` staying stable across lookup-only `get-order`


## rev186 — save-time trailing-whitespace cleanup belongs in shared editor behavior

**Decision**: add a tiny shared `rmtrailingws` option to the editor save path, not another TUI-only cue or a standalone strip command first.

**Why**: the current TODO still called out trailing-whitespace cleanup as unfinished even after rev177's renderer-only `hltrailingws` cue. micro's current options docs frame `rmtrailingws` as save-time behavior, which is exactly the right scale for Micromax too: one small shared rule that every frontend/hostcall inherits, instead of more duplicated UI logic. The portability sibling closes one more search-order truth by pinning down same-wordlist redefinition precedence in JSON data.

**What changed**:
- registered `rmtrailingws` (default `false`)
- `Editor.save()` now trims trailing spaces/tabs from buffer lines before writing when the option is enabled
- the cleanup updates the in-memory buffer too, clamps cursors/anchors honestly, and records an undoable snapshot when anything changed
- the portability corpus now covers `find` preferring the most recent definition within one wordlist

**Consequence**: Micromax now closes the old visualization/cleanup TODO without needing a heavier formatting subsystem, while future UIs/scripts still share the same save semantics automatically.


## rev187 — keep final-newline normalization in the shared save path too

**Decision**: add a tiny shared `eofnewline` option to the editor save path, reusing the same honest/undoable normalization flow that rev186 introduced for `rmtrailingws`.

**Why**: micro's current options docs still describe `eofnewline` as save-time behavior, not as a renderer cue. Micromax already had the hard part after rev186: one shared place where save-time text normalization could happen before bytes hit disk, while keeping the live buffer and undo history honest. The remaining useful step was therefore small: if the buffer is non-empty and not newline-terminated, append exactly one final `\n` during manual save instead of forcing future frontends/scripts to guess or duplicate the policy.

**What changed**:
- registered `eofnewline` (default `false`)
- updated `Editor.save()` to normalize save text once, composing `rmtrailingws` and `eofnewline` in one path
- kept empty buffers empty instead of forcing a one-byte file
- recorded one undoable cleanup snapshot when save changed bytes
- extended the portability corpus with a `definitions` case covering compilation-wordlist stability across later `set-order` changes

**Consequence**: Micromax now has one more small shared save semantic that every frontend/hostcall inherits automatically, without needing a formatter subsystem or curses-only hook.


## rev189 — savecursor should stay a tiny persisted editor behavior, not a session subsystem

**Decision**: add a tiny shared `savecursor` option to the editor core so reopening a file can restore its last remembered primary cursor position through the existing `cap.persist` boundary, using a small JSON store and shared startup/exit wiring instead of inventing a larger session manager.

**Why**: micro's current options docs still describe `savecursor` as a small ordinary editor setting, which matches Micromax's current “headless-first, inspectable, evolvable by hand” posture well. The repo already had the hard part after recent/history persistence: one explicit unsafe capability (`cap.persist`), a sandboxable path policy, and best-effort JSON load/save helpers. That made cursor persistence a good low-risk next step so users can leave a file and come back later without losing place, while future UIs/scripts still inherit one shared behavior instead of growing their own ad hoc workspace restore logic.

**What changed**:
- registered `savecursor` and `savecursor.file`
- added shared helpers to load/save saved cursor positions plus remember/restore a buffer's primary cursor
- wired persistence into ordinary shared-core edges: switching buffers, closing buffers, saving, opening files, and normal REPL/TUI exit
- kept the first pass intentionally narrow: primary cursor only, no multi-cursor/session/undo persistence, honest clamping when files changed

**Consequence**: Micromax now remembers “where was I in this file?” through one tiny explicit persistence boundary that future humans/LLMs can inspect directly, without committing the project to a heavier session-management design yet.


## rev190 — smartpaste should stay a tiny shared paste rule, not a formatter

**Decision**: add a tiny shared `smartpaste` option to the editor core so multi-line `Paste` can reuse the current line's existing whitespace prefix for otherwise-unindented blocks, keeping the behavior headless-first across internal/external/multi-cursor paste flows instead of burying it in one frontend.

**Why**: micro's current options docs still describe `smartpaste` as a small ordinary editor setting, which is exactly the right scale for Micromax too. The repo already did the important hard work in earlier revisions: paste is a shared editor action, bracketed paste already arrives as one chunk, and external clipboard import now feeds the same action instead of inventing a second path. That made one conservative shared indentation assist the right next move: practical enough to help with pasted blocks, still tiny enough to inspect by hand, and still nowhere near a formatter or language-aware reindenter. The portability sibling closes one more small host-boundary truth by pinning down that repeated seeded `host.features` names collapse into one sorted inventory entry.

**What changed**:
- registered `smartpaste` (default `false`)
- added a tiny shared smartpaste helper that only reuses the current line's whitespace prefix for multi-line paste payloads when the insertion point is still inside leading whitespace and the pasted block still has a zero-indent non-empty line
- applied that helper uniformly across ordinary paste, per-cursor item paste, and external clipboard import because they all already flow through `Paste`
- extended the portability corpus with a seeded-`host.features` deduplication case

**Consequence**: Micromax now clears one more practical micro-esque editing TODO with a behavior that future UIs/scripts inherit automatically, while the project still avoids promising a smarter formatter or paste-specific language model.


## rev192 — keep whitespace-only autoindent cleanup inside `InsertNewline`

**Decision**: add a tiny `keepautoindent` option and keep its behavior inside the shared `InsertNewline` action: when the original line is whitespace-only and Enter autoindents the next line, clear the previous line back to empty by default; keep it only when `keepautoindent` is enabled.

**Why**: micro's current options docs still treat `keepautoindent` as a small edit-loop rule rather than a formatter or cleanup subsystem feature. Micromax already had shared autoindent-on-newline behavior, so the right follow-up was another small rule in that same path, not a save hook or TUI-specific workaround.

**Consequence**: whitespace-only autoindent lines now behave more like a real terminal editor in the shared headless core, while the archive still avoids tracking richer indentation provenance too early.

## rev191/rev192 — parse open targets before sandbox resolution, not after

**Decision**: add a tiny shared `parsecursor` option and parse `file:line[:col]` targets before capability-gated/sandbox path resolution, then carry the resulting cursor target through interactive open, `ed.open`, scripted `open ...`, persistence-aware reopen, and path-style command-palette opens.

**Why**: micro's current options docs still treat `parsecursor` as a normal editor option, and micro's release notes explicitly mention recent fixes around colon-containing filenames. That points to one shared parsing policy, not several frontend-specific hacks.

**Consequence**: Micromax again has one inspectable open-target policy future UIs/LLMs can reuse, explicit targets beat `savecursor`, and existing literal colon-containing paths stay openable when they already exist.

## rev199 — make `encoding` a real shared open/save option

**Decision**: treat text encoding as a real per-buffer editor option instead of a hardcoded `utf-8` status token, using the configured encoding for ordinary `open_file(...)` decode and `save()` encode while keeping the user-facing option spelling intact in status/config surfaces.

**Why**: micro's current options docs still present `encoding` as an ordinary buffer setting. Micromax had already promoted `fileformat` into the shared open/save path, but `status_model()` still hardcoded `encoding=utf-8` and the file open/save code ignored configuration entirely. That mismatch made the statusline look more finished than the editor behavior really was.

**What changed**:
- registered `encoding` in the ordinary option registry (default `utf-8`)
- `new_buffer(...)` now carries an `encoding` local option alongside `fileformat`
- `open_file(...)` decodes with the configured encoding while still normalizing newlines separately
- `save()` encodes with the effective buffer encoding after any save-time newline/whitespace normalization
- `status_model()` / `$(opt:encoding)` now report the same user-facing buffer option instead of a fake constant
- added focused tests for configured open, encoded save, local-buffer persistence across global default changes, and statusline rendering
- added portability case `map-keys-empty-map-returns-empty-list`

**Consequence**: Micromax now has one more honest shared file-behavior knob that future UIs/scripts/hosts inherit automatically, without committing the project to auto-detection or mixed-encoding complexity.



## rev200 — make visible filename state explicit instead of hardcoding basename

**Decision**: add a tiny `basename` option and carry an explicit `display_name` through the shared status/display model, so `$(filename)` and `showstatus` can honor the same policy without losing the older raw `file_name`/`path` fields.

**Why**: micro's current options docs still describe `basename` as the switch that decides whether infobar/tabbar surfaces show only the basename or the full path. Micromax had already made `encoding` and `fileformat` honest shared fields, but the visible filename in status output was still always a basename, which made the status surface look more polished than the real display contract actually was.

**What changed**:
- registered `basename` (default `false`)
- added `display_name` to `status_model()` while keeping `file_name` as the raw basename-ish compatibility field
- taught `$(filename)` and `showstatus` to use `display_name`
- added focused tests for raw-vs-display status state, statusline rendering, and `showstatus` output
- added portability case `map-items-empty-map-returns-empty-list`

**Consequence**: Micromax now has one more small but honest shared display rule that future UIs/scripts/LLMs can reuse directly instead of reverse-engineering path display policy from formatter accidents.
