# micromax (v125)
Micromax is a **small, embeddable, concatenative language + VM** designed to become the native
plugin/config/macro system for a lightweight terminal editor in the spirit of **micro**.

Rev171 note: the minimal curses TUI now has an optional micro-esque `ruler` / `relativeruler` gutter that keeps wrapped continuation rows blank and shifts viewport/cursor math honestly, while the JSON portability corpus now also covers typed predicates, `m?`, `get-current`, `dict-version`, and `host.api-version` so future hosts can replay a little more of the real kernel contract.

Rev170 note: the tiny JSON portability suite now covers a few more missing but very contract-like kernel behaviors (`0=`, successful `catch`, list clone/pop isolation, `m-keys`, `m-items`, session-local query/removal, and `set-current` round-tripping), and `mxportable` now supports exact case-name filtering via `--name` so future hosts and future LLMs can ask for precise slices without fuzzy substring matching.

Rev169 note: the tiny JSON portability suite now covers a few more portable kernel behaviors Micromax already relies on (`when`, `to-int`, `to-str`, `m-del`, `m-merge`), and `mxportable` can now emit a lighter-weight inventory of matching categories/tags/case names so future hosts and future LLMs can inspect the contract without pulling full case bodies.

Rev168 note: the tiny JSON portability suite is now easier for future hosts and future LLMs to inspect directly: `mxportable` can emit machine-readable JSON summaries/results, the corpus is tagged much more broadly, and the portable contract now also covers `while`, `constant`, `variable`, and locals shadowing on top of the earlier return-stack / namespace / recovery coverage.

Rev167 note: the tiny JSON portability suite is now a stricter and more sliceable cross-host contract: it adds portable cases for return-stack basics, `execute`, wordlist/search-order lookup, `in`, `2dip`, `recover`, and `finally`, and `tools/mxportable.py` / `src/micromax/portability_suite.py` now validate corpus shape and support category/tag/name filtering for targeted bring-up runs.

Rev166 note: the tiny JSON portability corpus now covers more of the language the repo actually leans on day to day: quotation combinators (`dip`, `2keep`, `tri`), recovery/cleanup helpers (`try?`, `try`, `ensure`), and step-budget exhaustion under `catch`, giving future Rust/WASM hosts a better cross-host semantic floor than just arithmetic plus one `bi` example.

Rev165 note: tiny indented continuation lines under markdown footnote definitions in docs/help buffers now also render dim in the live TUI, while the visible `[^id]:` starter marker keeps its existing dim+bold treatment — reusing the shared definition-line roles instead of inventing another parser path.
Rev164 note: backslash-escaped markdown punctuation pairs in docs/help buffers (for example visible `\[`, `\!`, `\<`, `\*`, `\_`, `\~`, and ``\``` source) now get a tiny source-view cue too — the live TUI dims the visible two-character escape pair while leaving the escaped form literal and non-navigable — reusing one small helper layered on the existing shared backslash-escape policy instead of another parser path.
Rev163 note: inline markdown code-span backtick delimiters in docs/help buffers (for example the visible backticks around `simple code` and the double-backtick runs around ``code with `literal backticks` inside``) now get a tiny source-view cue too — the live TUI renders those delimiter runs bold+dim while leaving the existing code-body dimming alone — reusing one small helper layered on the existing equal-length backtick scan instead of another parser path.
Rev162 note: inline markdown emphasis delimiters in docs/help buffers (for example the visible `**`, `*`, `_`, and `~~` around already-styled emphasis bodies) now get a tiny source-view cue too — the live TUI dims those delimiter tokens while leaving the body styling alone — reusing one small helper layered on the existing inline-emphasis regex helpers instead of another parser path.
Rev161 note: visible supported ordinary markdown links in docs/help buffers (for example `[Vision](00-vision.md)`, `[Vision ref][visionref]`, and `[Vision shortcut]`) now get a tiny source-view cue too — the live TUI dims the non-label scaffolding around the still-underlined live label — reusing one small helper layered on the existing shared link matcher instead of another parser path.
Rev160 note: visible inline raw HTML tags in docs/help buffers (for example `<kbd>` / `</kbd>` / `<a name=...>`) now get a tiny inert-source cue too — the live TUI dims the whole tag token — reusing one small helper layered on the existing shared inline raw-HTML span helper while keeping supported autolinks on their separate bold whole-token path.
Rev159 note: visible supported markdown image forms in docs/help buffers (for example `![alt](dest)` and `![alt][id]`) now get a tiny inert-source cue too — the live TUI dims the whole token — reusing one small helper layered on the existing shared markdown destination/reference helpers rather than another parser path.
Rev157 note: docs/help buffers now give visible markdown footnote references like `[^note]` a tiny source-view cue too — the whole token renders bold while the inner `^note` keeps the ordinary docs-link underline — continuing the shared-substrate-first docs-browser polish thread.
Rev156 note: GitHub-style alert opener tokens inside docs/help blockquotes (for example `> [!NOTE]` and `> [!WARNING]`) now get a tiny source-view cue too: the live TUI bolds the alert marker while keeping the quoted body dim, reusing one shared helper instead of growing an alert-specific parser path.
Rev155 note: nested markdown list/task markers in docs/help buffers now render like real nested list markers in the live TUI too, but only after the shared indented-code guard has already ruled out top-level code blocks, so sub-bullets in worklists/readmes scan better without making code examples look like lists.
Rev154 note: reference-style definition starter lines and footnote-definition starter lines in docs/help buffers now render dim with bold marker tokens in the live TUI, and tiny wrapped reference-definition continuation lines render dim too, reusing one shared definition-line helper instead of another render-only parser path.
Rev153 note: raw HTML comments and raw HTML block lines in docs/help buffers were already inert for `helpfollow`, `helplinkpick`, outline/definition parsing, and TUI docs-link underlining; the live TUI now dims those same comment spans / block lines too so commented-out notes and embedded HTML examples stop reading quite so much like ordinary prose.
Rev152 note: blank-separated indented code-ish markdown lines in docs/help buffers now stay inert for `helpfollow`, `helplinkpick`, and TUI docs-link underlining too, and the live TUI dims those lines so ordinary source-view code examples read like code instead of accidentally clickable prose.
Rev151 note: docs/help rendering now also makes fenced markdown examples look visibly code-ish in the live TUI: opening/closing fence lines render bold+dim, fenced body lines render dim, and the whole thing reuses the same shared fence scan already trusted for docs-link/definition precedence.
Rev150 note: docs/help rendering now reuses the same tiny heading scan already trusted for titles, outline rows, fragment jumps, and heading breadcrumbs, so setext heading title lines finally render like headings in the live TUI too while their `===` / `---` underline line gets a dim heading-ish treatment.
Rev149 note: the minimal TUI now gives ordinary markdown list markers a little scanability polish in docs/help buffers: bullet markers (`-` / `+` / `*`) and ordered markers (`1.` / `1)`) render bold via one tiny shared helper, while existing task-list styling layers cleanly on top.
Rev122 note: fenced code blocks in docs/help buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, TUI docs-link underlining, and markdown reference-definition parsing, so literal markdown examples inside triple-backtick/tilde fences no longer leak into the live help browser.
Rev124 note: raw HTML comments in docs/help buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, outline scanning, TUI docs-link underlining, and markdown reference/footnote-definition parsing, so commented-out markdown examples stay literal instead of leaking back into the live help browser.
Rev123 note: single-line setext headings (`Title` + `===` / `---`) now participate in docs/help fragment jumps, outline rows, heading breadcrumbs, and docs-picker titles, reusing the same tiny heading-title cleanup and explicit `{#id}` handling as ATX headings without committing Micromax to a full markdown block parser.
Rev120 note: docs/help link parsing now handles balanced bracket labels like `[Vision [nested]](00-vision.md)`, `[Vision [nested]][id]`, and `[Vision [nested]]` via a small shared scanner used by `helpfollow`, `helplinkpick`, the docs TUI underline model, and reference-definition parsing. This keeps nested markdown examples navigable without committing Micromax to a full markdown parser.

The project deliberately grows in two directions at once:

Rev121 note: docs/help link destinations now use a slightly smarter tiny parser: balanced parentheses in bare destinations work, markdown-safe backslash escapes are unescaped in inline/reference destinations, and percent-encoded local doc paths are decoded before follow. This keeps local docs links like `104-paren\(topic\).md`, `103-space\ path.md`, and `103-space%20path.md` navigable without committing Micromax to a full destination/title parser.

- **language/VM**: tiny, inspectable, heavily tested, pleasant to evolve by hand offline
- **editor core**: headless-first, deterministic, and unit-testable before any terminal UI hardens

Rev119 note: docs/help markdown escapes now stay literal across both styling and actions: backslash-escaped links, refs, footnotes, images, and autolinks no longer leak into `helpfollow`, `helplinkpick`, or TUI link underlining, so docs that teach markdown stay prose instead of becoming accidentally navigable.

Rev118 note: docs-browser actions now respect inline-code precedence too: `helpfollow` and `helplinkpick` ignore markdown-looking links/autolinks that sit inside inline code spans, keeping editor behavior aligned with the tiny TUI link-highlighting policy.

Rev117 note: markdown image forms like `![alt](dest)` and `![alt][id]` are now ignored consistently by `helpfollow`, `helplinkpick`, and TUI docs-link underlining, so image alt text stays prose until Micromax grows a clearer image-aware docs policy.

Rev116 note: docs/help inline code spans now support equal-length backtick delimiters (so double-backtick forms can include literal backticks), and the TUI now masks code spans before link-underlining so code-ish text doesn’t accidentally look clickable.

Rev115 note: the minimal TUI now gives tiny markdown inline emphasis forms a little scanability polish in docs/help buffers: `**strong**` bodies render bold, `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline), and `~~strike~~` bodies render dim, all staying intentionally UI-only and inspectable.

Rev114 note: the minimal TUI now gives markdown thematic breaks a little scanability polish in docs/help buffers: common separators like `---`, `***`, `___`, and spaced forms such as `- - -` render dim with a bolder marker run, staying intentionally UI-only and inspectable.

Rev113 note: the minimal TUI now gives markdown blockquotes a little scanability polish in docs/help buffers: quote-marker prefixes render bold and quoted bodies dim, staying intentionally UI-only and inspectable.

Rev112 note: the minimal TUI now gives GFM-style task-list markers a little scanability polish in docs/help buffers: checkbox tokens render bold and checked task bodies are dimmed, staying intentionally UI-only and inspectable.

Rev111 note: the minimal TUI now gives GFM-style pipe tables a little scanability polish in docs/help buffers: table header rows render bold, delimiter rows dim, and `|` separators are dimmed without pulling in a full markdown parser or changing the headless core.

Rev110 note: docs/help buffers now recognize common markdown footnote references (`[^id]`) and jump to matching definitions (`[^id]: ...`) in-place. The same tiny footnote model now flows through `helpfollow`, `helplinkcopy`, `helplinkpick`, `helpnavpick`, and TUI underline/current-link detection so docs surfaces stay aligned without committing to a full markdown engine.

Rev109 note: the docs help browser now follows markdown heading fragments — both same-page `#section` links and cross-doc `page.md#section` links — using best-effort GitHub-style heading slugs plus explicit heading ids (`{#id}` / `{: #id }`). Outline rows and heading-based breadcrumbs also strip raw attr-list suffixes so picker/search surfaces show human titles instead of source syntax.

Rev108 note: the command palette now splits path-like results into clearer `Directories` / `Files` / `Open` sections instead of lumping everything under one `Open` bucket, and the repo now ships a tiny JSON portability corpus plus `tools/mxportable.py` so future Rust/WASM ports can validate core semantics against the Python oracle.

Rev107 note: the docs help navigator (`helpnavpick`) now reuses the same link grouping policy as `helplinkpick`, so `set help.linksections heading` affects both surfaces consistently. External-link confirmation prompts also name their source (`help`, `cursor`, or explicit `command`) for slightly better safety/clarity.

Rev69 note: improved VM decompiler surfaces: `see` now includes a compact tier-2 disassembly and const pool when available, and tooling can fetch structured disassembly via `disasm-rows`. The editor embedding also exposes a small regex hostcall set (`re.search`/`re.sub` etc.) aligned with `replace`/`replaceall`.

Rev67 note: the VM now has a **dev-mode stack effect checker starter kit** (`stackcheck!` warn/error modes, `infer-effect`, `check-effect`), and quotations preserve leading paren-comments so you can annotate quote effects like `[ ( x -- y ) ... ]`.

Rev66 added the portable syntax highlight span model (`ed.highlight`) and a deterministic timer queue (`ed.after`/`ed.pump-timers`). Rev65 added autoindent + `tabsize`/`tabstospaces`; rev64 added `jumppick`, user rc/init loading, and the `include`/`require` search convention.

Rev72 note: the editor statusline is now configurable via micro-esque `statusformatl`/`statusformatr` templates (a tiny `$()` renderer), and the stdlib adds `ensure`/`finally` for always-run cleanup built on `catch`/`throw`.

Rev82 note: the docs help browser got a little more micro-esque — `helplinkpick` now groups links into Docs/Files/External sections in the TUI, and external-link follow gives an explicit `cap.open-url` enable hint.

Rev83 note: docs navigation now recognizes **reference-style links** (`[text][id]` + `[id]: target`) and **autolinks** (`<https://...>`), so docs pages can use more idiomatic Markdown forms.

Rev90 note: picker-style prompts (buffer/doc/help pickers, palette, etc.) now support **Up/Down selection** without mutating the typed query, and `Ctrl-y` copies the selected row (for links: copies the target).

Rev91 note: picker-style prompts now also support **PageUp/PageDown selection jumps** (option: `prompt.page`, default 8), which makes long pickers (palette, docs link lists) feel much closer to a real command palette.

Rev92 note: picker-style prompts gain a `prompt.wrap` option (wrap vs clamp), support `Ctrl-Home`/`Ctrl-End` to jump to first/last selection, and the TUI repeats the current section header as a sticky header while paging through long mixed sections.

Rev93 note: picker-style prompts now support `Alt-Up`/`Alt-Down` section jumps (jump between section headers; `Alt-Up` also jumps to the start of the current section when used inside it), implemented in the headless core and used by the minimal TUI.

Rev94 note: the docs browser now understands **shortcut reference links** (`[id]` when a matching `[id]: target` definition exists), and the minimal TUI underlines inline/reference/shortcut/autolinks consistently so help pages feel more like a real in-editor browser.

Rev97 note: docs link pickers (`helplinkpick`) can optionally group links by nearest markdown heading (option: `help.linksections heading`), the host adds a capability-gated `ed.fs-stat` helper for portable path metadata, and the repo includes `tools/mkrevzip.py` to build standard-named offline archives.

Rev95 note: small repo + picker UX polish — the `Makefile` now runs scripts via `bash` (so `make test` works even when executable bits are lost in an archive), and the minimal TUI now highlights query-token substring matches in picker suggestion rows for faster scanning.

Rev84 note: docs navigation gained a combined picker (`helpnavpick`) that merges **Headings** + **Links** into one navigator, and the host now exposes grouped navigator sections via `ed.helpnav-section-rows`.

Rev85 note: the minimal curses TUI now interprets **Alt/Meta chords** (ESC-prefixed sequences) so default `Alt-*` bindings work, and maps **Ctrl-Space** (NUL) to `Ctrl-Space` for command palette muscle memory. Core defaults now include `Ctrl-b` buffer picker, `Ctrl-o` open (prefilled), `Ctrl-r` replace (prefilled), and `Alt-g` binding discovery.

Rev86 note: added an interactive **query-replace** loop (`qreplace` / `queryreplace`) that confirms each replacement with a tiny y/n/a/q keymode (capture mode so global bindings can't accidentally fire). Also unified Cursor<->offset conversion helpers (`micromax_editor.textpos`) used by search + replace.
Rev87 note: `replace` / `replaceall` and `qreplace` now respect the editor's `ignorecase` option (like `find`), and `qreplace` shows a small `match i/N` progress hint when it can pre-count matches.
Rev88 note: docs buffers gained `helplinkcopy` (and `y`) to copy the markdown link target under cursor, and external links now confirm by default when `cap.open-url` is enabled (capture keymode: y/open, n/cancel, c/copy).

Rev89 note: added `urlopen` / `urlcopy` (and default `Alt-o`/`Alt-y` bindings) to open/copy URLs under cursor in any buffer, reusing the same capability gate (`cap.open-url`) and confirmation keymode (`openurl`).

## What is already real

### Language / VM
- Python reference VM with wordlists, quotations, deferred words, hooks, maps, locals, and hostcalls
- two-tier execution path: token interpreter + optional bytecode/compiler scaffolding
- provenance/debug surfaces such as spans, `see`, `help`, `where`, and hook/keybinding inspection
- pure micromax stdlib loaded from `src/micromax/stdlib/core.mx`

### Editor substrate
- headless `Editor` core with buffers, cursors, selections, undo, and action chaining
- command bar + shell-ish parsing + prompt history
- searchable command/action palette, topic/help prompt, and current-binding prompt built on shared headless row metadata
- command palette now has a small MRU/recent section, grouped palette-section rows for future UIs/scripts, and clearer `Directories` / `Files` / `Open` buckets for path-like queries
- incremental search (`ignorecase`, `incsearch`), replace, and jump list
- multi-cursor primitives, macros, clipboard model, and statusline/infobar data model
- keybinding modes, one-shot/transient keymodes, `whichkey`-style discovery, binding docs, and prefix helpers
- micromax-defined commands, completion hooks, plugin lifecycle hooks, and grouped reload cleanup

### Archive ergonomics
- docs aimed at humans **and future LLMs** (`docs/01-llm-start-here.md`, `docs/02-repo-map.md`)
- `make context` for a curated snapshot
- `make doctor` for archive hygiene
- `make pack` for a clean zip archive

## Repository layout

- `docs/` — research notes, design docs, roadmap, decisions log, portability ledger
- `src/micromax/` — reference VM, core words, REPL, stdlib
- `src/micromax_editor/` — headless editor substrate + VM bridge
- `plugins/` — micromax plugins
- `examples/` — small language examples
- `tests/` — headless unit tests
- `tools/` + `scripts/` + `Makefile` — bootstrap/lint/test/context/pack helpers

## Quick start

Run the micromax REPL:

```bash
python -m micromax.repl
```

Run the headless editor prototype (REPL UI):

```bash
python -m micromax_editor
python -m micromax_editor path/to/file.txt
```

Run the minimal curses TUI:

```bash
python -m micromax_editor --tui
python -m micromax_editor --tui path/to/file.txt
```

## Development workflow

```bash
make bootstrap
make test
make doctor
make context
```

Optional local git bootstrap (no remote required):

```bash
make init-git
```

Build a clean archive zip:

```bash
make pack
```

## Good entry points

Read these first:

1. `TODO.md` + `docs/43-worklist.md`
2. `docs/00-vision.md`
3. `docs/01-llm-start-here.md`
4. `docs/42-portability-ledger.md`
5. `docs/102-portability-suite.md`
6. `docs/22-two-tier-execution.md`
7. `docs/50-editor-behaviors.md`
8. `docs/64-editor-prompt-completion.md`
9. `docs/71-cookbook.md`

## Portability contract

The Python implementation is the **reference implementation** and **test oracle** for future ports
(such as Rust/WASM). If you add VM surface area, update `docs/42-portability-ledger.md`, and prefer adding at least one portable corpus case in `portability/kernel_cases.json` when the behavior is part of the portable kernel.

- Docs/help TUI scanability is deliberately tiny and local: headings are bold; markdown links are underlined (bold+underlined when the cursor is on them), with small whole-token cues for supported autolinks like `<https://...>` and footnote references like `[^id]`; visible ordinary markdown links now also dim their non-label source scaffolding while keeping the live label underlined; visible inline raw HTML tags like `<kbd>` / `<a name=...>` now dim as inert source too; inline code spans are masked first so code-ish text does not look clickable; inline code spans are dimmed (including equal-length multi-backtick forms for literal backticks inside code), and visible backtick delimiter runs now render bold+dim too; ordinary markdown list markers (`-` / `+` / `*`, `1.` / `1)`) render bold; `**strong**` bodies render bold; `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline); `~~strike~~` bodies render dim; small pipe tables get bold headers, dim delimiter rows, and dim `|` separators; GFM-style task-list checkboxes are bolded and checked task bodies are dimmed; and editor-side docs actions (`helpfollow` / `helplinkpick`) now also ignore markdown-looking links that appear inside inline code spans; fenced code blocks are likewise treated as inert prose for docs-link actions and underlining, keeping docs-browser behavior aligned with the TUI's code-first scanability policy.
