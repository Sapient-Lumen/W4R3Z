## 2026-03-18 rev282 note

- Current Factor docs still keep dependency cross-referencing and an online help system first-class, which reinforces the Micromax idea that tiny dependency tools become more useful when they also carry enough context to interpret the affected slice instead of only naming it.
- Current pytest docs still describe exact node identifiers as the honest way to rerun a precise slice, which keeps Micromax pointed at exact `--name` replay commands rather than fuzzier selection.
- Micro's current docs still center discoverable commands, rebinding, and plugins as simple user-facing surfaces, which keeps nudging Micromax toward tiny inspectable outputs that stay operational without growing into a framework.
- That made rev282's next honest move one tiny follow-up on rev281: keep the exact replay command, but also rejoin the impacted case names back to the portability corpus so future humans/LLMs can immediately see whether a change mainly touches combinators, cleanup contracts, aliases, or some other small contract family.

## 2026-03-18 rev281 note

- Current Factor docs still keep cross-reference/dependency utilities first-class through `compiler.crossref`, which reinforces the Micromax idea that a tiny dependency view becomes much more useful once it directly supports the next action instead of stopping at inspection.
- Current pytest docs still describe exact identifiers and node IDs as the honest way to rerun a precise slice, which matches Micromax's existing exact `--name` portability filtering far better than fuzzier substring selection.
- Micro's current help docs still center a command bar / help system where discoverable commands are expected to be directly executable, which keeps nudging Micromax toward tiny inspectable surfaces that do not stop at metadata when a direct command can stay equally small.
- That made rev281's next honest move one tiny follow-up on rev280: keep the impact map machine-readable, but also let the selected impact slice carry one copy-pasteable exact replay command so future humans/LLMs stop rebuilding `--name` arguments by hand.

Rev279 note: `mxportable --stdlib-manifest` can now also surface tiny reverse boot-stdlib usage metadata through `--show-users`, and shared helpers in `src/micromax/portability_suite.py` now derive `direct_stdlib_users`, `transitive_stdlib_users`, and `user_depth` from `core.mx` so future Python/Rust/WASM hosts and future LLMs can see which higher-level words depend on a tiny boot word before changing or porting it.

Latest tiny landing (rev279): the archive now exposes a tiny machine-readable reverse stdlib-usage inventory alongside the dependency and closure views, so questions like "what higher-level words would I retest after changing `keep`?" or "who depends on `ensure` besides its alias?" stop requiring ad hoc scans over `core.mx`. The handoff note is `docs/221-portability-stdlib-user-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

- Current Factor docs still warn that `recover` should be used sparingly and that `cleanup` is the better fit when work must run and the original error should keep escaping; that reinforces Micromax's split between recovery combinators (`try` / `recover`) and cleanup combinators (`ensure` / `finally`) while still making later helper failures explicit in the portability corpus.
## 2026-03-17 rev273 note

- The current Forth rationale still frames `CATCH` / `THROW` as the portable way to unwind nested execution while restoring the data-stack depth seen at the matching `CATCH`, which keeps Micromax's cleanup combinators anchored in standard-shaped exception behavior rather than VM-specific magic.
- Current Factor docs still separate `recover` from `cleanup`, and the current pitfalls page still recommends cleanup-style handling when an error must be rethrown automatically. That reinforces Micromax's existing split between `try` / `recover` and `ensure` / `finally`.
- That made rev273's next honest move very small: keep the VM and stdlib unchanged, but extend the JSON portability corpus so future hosts can replay the missing precedence branch where cleanup itself fails and therefore replaces the body result or body error.

## 2026-03-17 rev271 note

- Current CommonMark still keeps headings in the lightweight block-syntax bucket, which reinforces Micromax's existing "reuse the same tiny heading scan everywhere" strategy instead of growing a second docs query/parser path.
- Python-Markdown's current Attribute Lists docs still present explicit ids as a normal author-facing way to assign stable attributes in markdown output, which makes fragment/id-based heading queries a practical docs-authoring affordance rather than a weird power-user edge case.
- That made rev271's next honest move one tiny follow-up on rev269: keep heading rows visibly clean, but let `helpjump`, `helpoutlinepick`, and the heading side of `helpnavpick` reuse resolved fragment/id terms like `custom-frag` during ranking so stable anchors are searchable as well as followable.

## 2026-03-17 rev270 note

- VS Code's current navigation docs still describe breadcrumbs as a location path for quick movement among files and symbols, which reinforces the Micromax idea that already-visible section context should be searchable rather than merely decorative.
- Helix's current picker docs still treat pickers as their own navigable surface with dedicated picker keybindings, which keeps Micromax pointed toward shared picker/query behavior instead of renderer-only affordances.
- That made rev270's next honest move one tiny follow-up on the recent help-outline work: keep docs-link rows visibly small, but let `helplinkpick` and the link side of `helpnavpick` reuse nearest-heading and kind context so mixed queries like `External micro editor` or `Reference Vision ref` stop failing.

## 2026-03-17 rev265 note

- CommonMark's current spec still treats headings as lightweight block syntax rather than a richer document tree, which keeps Micromax's existing heading scan the right source of truth for section ownership instead of adding a second navigation parser.
- GitHub's current docs still generate heading-driven outlines / table-of-contents views for markdown files, which makes "what visible section am I in right now?" one of the most practical tiny metadata questions for future humans/LLMs reading an offline help-buffer dump.
- That made rev265's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep visible heading rows explicit, but also surface nearest-heading `section_entry` metadata for every visible docs/help row so future humans/LLMs can inspect section ownership without rerunning breadcrumbs by hand.

## 2026-03-17 rev264 note

- CommonMark's current spec still defines fenced code blocks as lines beginning with a fence of at least three backticks or tildes, optionally followed by an info string, with literal body content until a matching closing fence. That keeps Micromax's existing shared fence scan the right source of truth instead of a second renderer parser.
- The same spec still treats HTML blocks as raw-HTML line groups and indented code blocks as literal 4-space/tab-indented chunks with no info string, which makes visible block rows practical source-view metadata rather than a cue to build a richer Markdown AST.
- GitHub's current docs still teach fenced code blocks as the ordinary author-facing way to share code, and explicitly mention optional language identifiers for syntax highlighting. That makes visible fence info strings and block grouping useful archive metadata for future humans/LLMs reading Micromax's help/docs buffers.
- That made rev264's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep existing `line_role` values, but also surface explicit row-local `block_entries` plus a few top-level counts so future humans/LLMs can inspect visible fenced/html/indented block rows without rerunning the tiny shared scans by hand.

## 2026-03-17 rev263 note

- CommonMark's current spec still describes link reference definitions as labels that can appear before or after the links that use them, which keeps Micromax's tiny shared definition scan squarely in the source-view metadata bucket instead of pushing it toward a richer block tree.
- GitHub's current Markdown docs still present footnotes as ordinary `[^id]` references plus `[^id]:` definition lines, including multi-line notes, which makes visible definition markers and continuation rows practical help-buffer metadata rather than parser trivia.
- That made rev263's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep `definition_role`, but also surface explicit row-local `definition_entries` plus a few top-level counts so future humans/LLMs can inspect visible reference-definition and footnote-definition rows without reparsing the source by hand.

## 2026-03-17 rev262 note

- CommonMark's current spec still defines ATX headings as one to six `#` markers followed by inline content, and still defines setext headings as one or more paragraph-like title lines followed by an underline. That keeps Micromax's existing shared heading scan the right source of truth instead of a second renderer parser.
- GitHub's current Markdown docs still teach heading anchors as an ordinary docs-navigation affordance, which makes the resolved heading fragment one of the most useful tiny metadata fields future UIs/scripts/LLMs can inspect in a source-view help buffer.
- That made rev262's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the renderer small, keep `line_role` / `heading_level`, but also surface explicit row-local `heading_entries` plus a few top-level counts so future humans/LLMs can inspect visible heading titles and fragments without rerunning `_md_heading_scan()` by hand.

## 2026-03-17 rev261 note

- GitHub's current Markdown docs still teach tables as an ordinary authoring form built from pipes (`|`) and hyphen delimiter rows, which keeps visible pipe-table structure squarely in the "small source-view cue" bucket rather than pushing Micromax toward a richer rendered-table widget model.
- The same docs still call out fixed-width editing as especially helpful for tables and code snippets, which makes "what visible table cells and alignments are on screen right now?" a practical docs-browser question for future humans/LLMs.
- That made rev261's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing table styling helpers, but surface parsed `table_entries` plus a few top-level counts so future humans/LLMs can inspect visible docs/help tables without scraping pipe spans or rerunning tiny table splitters.

## 2026-03-17 rev260 note

- GitHub's current GFM spec still describes task-list items as an extension layered on ordinary list items, with a checkbox marker at the start of the first paragraph, which supports Micromax continuing to expose task structure as a tiny source-view marker rather than a richer rendered widget model.
- CommonMark's current spec still defines block quote markers as a small line-prefix rule (up to three leading spaces, then `>` with optional following space), which fits Micromax continuing to expose blockquote structure as compact per-row marker metadata instead of a fuller block tree.
- GitHub's current Markdown docs still describe alerts as a blockquote-based extension (`> [!NOTE]`, `> [!WARNING]`, etc.), so Micromax's existing alert-prefix cue remains best modeled as a tiny visible row marker layered on top of blockquote metadata rather than a distinct admonition subsystem.
- That made rev260's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing renderer helpers for list/task/blockquote/thematic cues, but surface parsed `structure_entries` plus a few top-level counts so future humans/LLMs can inspect visible docs/help structure without scraping generic spans.

## 2026-03-17 rev259 note

- Current Gforth docs still list `rdrop` (`R:w --`) right next to `>r`, `r>`, `r@`, and `2rdrop` in the return-stack vocabulary, which keeps it squarely in the “small well-known helper” bucket rather than a Micromax-only flourish.
- The current Forth-standard discussion around standardizing `rdrop` explicitly describes it as a well-known word with a trivial pure-Forth implementation and a clear `( R: x -- )` effect, which fits Micromax's preference for keeping such helpers source-visible in `core.mx` instead of growing the VM primitive set.
- That made rev259's next honest move slightly broader than one more case: add tiny replayable `rdrop` and `recover`-success contracts, then add a tiny manifest test that proves every boot-stdlib `: word` now has an explicit portability breadcrumb.

## 2026-03-17 rev258 note

- Current small/embedded Forth projects still describe the path from a tiny kernel to a more usable system as building richer words on top of the base system, which fits Micromax's current preference for a tiny inspectable VM and a source-visible stdlib.
- Current Factor testing docs still distinguish between quotations that should produce specific outputs and quotations that must fail, which matches Micromax's current portability style of pinning down both success and failure contracts explicitly.
- That made rev258's next honest move one more tiny portability follow-up: keep `assert` source-visible in `core.mx`, but make both its success and failure-path stack behavior replayable from JSON so future ports do not have to infer it from stdlib source or ad hoc tests.

- Current Factor docs still group `dip` / `2dip` and `keep` / `2keep` as preserving combinators, and the current `bi` glossary still presents `bi` explicitly in terms of `keep` rather than as a VM-only special form.
- That made rev256's next honest move one more tiny portability follow-up: keep `keep` source-visible in `core.mx`, but make its ordering contract replayable from JSON so future ports do not have to infer it from `bi` / `tri` or ad hoc tests.

## 2026-03-17 rev255 note

- The current Forth standard still lists `NIP` and `TUCK` as CORE EXT words, while `2DUP` and `2DROP` remain CORE words, so these are still standard-shaped stack helpers Micromax can keep source-visible in `core.mx` instead of promoting to VM primitives.
- The current Gforth manual's data-stack section still presents the same stack effects (`nip`: `w1 w2 -- w2`, `tuck`: `w1 w2 -- w2 w1 w2`, `2dup`: `w1 w2 -- w1 w2 w1 w2`, `2drop`: `w1 w2 --`), which makes them a good tiny portability slice to pin down explicitly.
- That made rev255's next honest move one more small JSON portability follow-up: keep the VM small, keep the helpers source-visible, and give future Python/Rust/WASM hosts a replayable stack-helper contract instead of asking them to infer behavior from `core.mx` or broad pytest coverage.

## 2026-03-17 rev254 note

- The current Forth standard still lists `<>` as a CORE EXT word, so it is one more small standard-shaped comparison helper Micromax can keep source-visible in `core.mx` instead of promoting to a VM primitive.
- The same standard still defines `TRUE` as all bits set, while Micromax documents the simpler `0` / nonzero truthiness convention.
- That makes `<>` the cleaner next portability landing: future Python/Rust/WASM hosts can replay a tiny not-equals contract from JSON without forcing Micromax to pretend it already models well-formed all-bits-set Forth flags.

- The current Gforth manual's data-stack section still lists `2nip` (`w1 w2 w3 w4 -- w3 w4`) and `2tuck` (`w1 w2 w3 w4 -- w3 w4 w1 w2 w3 w4`) as small stack words, which makes them a good source-visible Micromax boot-stdlib follow-up instead of a VM-primitive change.
## 2026-03-17 rev249 note

- The current Forth standard still defines `2OVER` as copying the leading cell pair to the top of the stack and `2SWAP` as exchanging the top two cell pairs, which fits Micromax's current habit of keeping small standard-shaped stack helpers source-visible in `core.mx` instead of promoting them to VM primitives.
- That made rev249's next honest move one tiny boot-stdlib/portability follow-up: keep the VM small, define `2over` and `2swap` in source, and pin their behavior down in the JSON portability corpus for future Python/Rust/WASM hosts.

## rev248 — tiny shift words are still a good source-form portability slice

- The current Forth standard still defines `2*` as shifting one bit toward the most-significant bit and `2/` as shifting one bit toward the least-significant bit while leaving the most-significant bit unchanged.
- The standard's current usage requirements still say a system may provide standard words in source form only. That still fits Micromax's boot-stdlib style well: keep the VM primitive set small, keep behavior visible, and make the cross-host contract replayable from JSON.
- For Micromax this argues for one more tiny move instead of new VM primitives: define `2*` / `2/` in `core.mx`, then pin down a small positive/negative replay slice in `portability/kernel_cases.json` so future Python/Rust/WASM hosts can compare stacks directly during bring-up.

## rev247 — tiny arithmetic/predicate stdlib words are still a good source-form portability slice

- The current Forth standard still defines `1+` as adding one, `1-` as subtracting one, `0>` as true only for values greater than zero, and `0<>` as true only for values not equal to zero.
- The standard's current usage requirements still say a system may provide standard words in source form only. That is a good fit for Micromax's boot-stdlib style: keep the VM primitive set small, keep behavior visible, and make the cross-host contract replayable from JSON.
- For Micromax this argues for a tiny move instead of another VM primitive: define these in `core.mx`, then pin them down in `portability/kernel_cases.json` so future Python/Rust/WASM hosts can replay them directly during bring-up.

## 2026-03-17 rev238 note

- CommonMark's current spec still treats raw HTML tags and autolinks as tighter inline structure than surrounding link grouping, and still says backslash escapes do not work in raw HTML, autolinks, or code spans.
- GitHub's current Markdown docs still teach backslash escapes and inline HTML as ordinary lightweight authoring syntax, which makes visible literal-source inspection a practical docs-browser question.
- That made rev238's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing dimming helpers, but surface parsed `literal_entries` plus a few top-level counts so future humans/LLMs can inspect visible raw-HTML tags and escaped markdown pairs without reverse-engineering generic dim spans.

## 2026-03-17 rev237 note

- CommonMark's current spec still treats emphasis/strong as inline delimiter-run markup and keeps code spans higher-precedence than surrounding inline markup, which supports Micromax continuing to expose tiny shared visible-token metadata instead of inventing a richer markdown object model.
- GitHub's current Markdown docs still teach bold, italic, and strikethrough as ordinary lightweight authoring syntax in `.md` files, which makes “what visible token is strong vs emphasis vs strike?” a practical docs-browser question.
- That made rev237's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing small inline-markup helpers, but surface parsed `markup_entries` plus a few top-level kind counts so future humans/LLMs can inspect visible docs/help inline markup without inferring semantics from style spans alone.


## 2026-03-17 rev236 note

- CommonMark still defines code spans as matching equal-length backtick strings, and its examples still use code-span precedence to keep would-be links inside code literal rather than live structure.
- GitHub's current Markdown docs still teach inline code as ordinary backtick-delimited source markup and show it inside prose and tables, which makes “what inline code token is visible on this row?” a practical docs-browser question.
- That made rev236's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing small code-span matcher, but surface parsed `code_entries` plus a few top-level counts so future humans/LLMs can inspect visible docs/help inline code without scraping raw backticks.


## 2026-03-17 rev235 note

- CommonMark's current spec still frames image syntax as link-like inline structure whose description becomes alt text when rendered, which supports Micromax continuing to expose tiny shared image metadata instead of inventing a richer rendered-image object model.
- GitHub's current Markdown docs still teach images as ordinary `![alt](dest)` authoring syntax and recommend relative paths for repository-hosted images, which makes visible image-target inspection a practical help/docs question rather than a theoretical parser exercise.
- GitHub's current docs style guide still treats alt text as a short text equivalent of the image, which fits Micromax exposing the visible image description directly rather than pretending source view has become a rendered image surface.
- That made rev235's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing tiny image matcher, but surface parsed `image_entries` plus a few top-level counts so future humans/LLMs can inspect visible docs/help image targets without scraping raw source.


## 2026-03-17 rev234 note

- CommonMark still frames Markdown links as lightweight inline structure with inline links, reference links, and autolinks rather than a richer rendered-link object model, which supports Micromax continuing to expose tiny shared link metadata instead of inventing a larger docs AST.
- GitHub's current Markdown docs still treat links and automatic URL linking as ordinary authoring syntax, and its file outline/help affordances reinforce that “what section or target does this visible thing point at?” is a practical docs-browser question worth answering directly.
- micro still positions help, commands, keybindings, and plugins as small inspectable editor affordances rather than a heavyweight UI/widget system, which fits Micromax's habit of adding one more tiny shared snapshot instead of a bigger renderer abstraction.
- That made rev234's next honest move one tiny follow-up on `docs_cues_model(lines, cols)`: keep the existing shared link matcher, but surface parsed `link_entries` plus a few top-level counts so future humans/LLMs can inspect visible docs/help link targets without scraping raw source.

## 2026-03-16 rev227 note

- CommonMark's current spec still frames headings, blockquotes, code fences, links, and inline emphasis as lightweight prose conventions rather than a widget tree, which supports exposing docs/help emphasis as spans/roles instead of inventing a richer renderer abstraction.
- GitHub's current markdown writing docs still treat alerts, task lists, tables, links, and inline emphasis as ordinary authoring affordances, which fits Micromax's habit of surfacing the visible cues these lines produce without pretending the docs browser has become a full structured rich-text system.
- That made the next honest move one tiny shared `docs_cues_model(lines, cols)` snapshot: expose only the visible docs/help roles plus link/dim/bold/italic spans the reference TUI already paints, then let the TUI reuse those shared cues instead of re-parsing row fragments ad hoc.
- Sources worth re-reading: https://spec.commonmark.org/current/ and https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

## 2026-03-16 rev224 note

- micro's current options docs still describe `showchars` as an ordinary option for displaying invisible characters, with separate keys for ordinary `space` / `tab` and indent-only `ispace` / `itab`, and they explicitly note that the shown characters are not inserted into files.
- GNU nano's current manual still treats whitespace display as a plain toggleable terminal-view aid rather than a deeper formatting mode.
- That kept Micromax's next honest step small: preserve the existing one-cell renderer policy, but lift the *visible replacement contract* into one shared viewport-local `showchars_rows_model(lines, cols)` surface so future UIs/tests/scripts/LLMs can inspect `display_text` + spans without redoing fragment-local indent math in renderer code.
- Sources worth re-reading: https://github.com/micro-editor/micro/blob/master/runtime/help/options.md and https://www.nano-editor.org/dist/latest/nano.html

## 2026-03-16 rev223 note

- GNU nano still frames the terminal UI as a few plain regions with prompts/messages on the status bar and two help lines at the bottom, which keeps reinforcing Micromax's current bias toward tiny inspectable screen/cue models instead of a richer widget tree.
- That made search highlighting's next honest step a **viewport-local cue model**, not a whole-buffer style system: keep the query semantics in the headless editor, expose only the visible row fragments + match spans + current cursor-owned match, and let the reference curses TUI reuse that shared data.

## 2026-03-09 rev222 note

- micro still documents `statusline`, `infobar`, and `keymenu` as ordinary bottom-bar options rather than a deeper widget hierarchy, and GNU nano still frames the UI as a few plain screen regions, which keeps supporting Micromax's current strategy of exposing tiny inspectable screen snapshots before inventing richer UI abstractions.
- That made a flat plain-text `screen_rows_model(lines, cols)` the next honest step after `screen_model(...)`: it answers “what text is on screen right now?” for tests, scripts, and future LLMs without pretending the styled curses renderer has been generalized away.

*Rev221 note:* GNU nano still documents the interface as a few simple screen regions including the edit window, while micro still treats visible chrome like `statusline`, `infobar`, and `keymenu` as ordinary options, so Micromax keeps following the same small-shared-surface lesson: after layout/edit-window/screen/gutter snapshots, the next honest step was a tiny shared viewport-row model for the practical visible edit rows rather than a richer paint API. The portability sibling keeps following the Forth exception lesson too: after nested recovery returns control to the outer protected region, user-visible `r@` should still see outer user-pushed return-stack items.

*Rev220 note:* GNU nano still describes the UI as a few simple screen regions and micro still treats bottom chrome like ordinary options, so Micromax keeps following the same small-shared-surface lesson: after layout/edit-window/screen/prompt-panel snapshots, the next honest step was a tiny shared gutter model for line numbers + scrollbar rows rather than a richer widget abstraction. The portability sibling keeps following the Forth exception lesson too: visible `rdepth` after recovery should count user-pushed items, not hidden nested exception bookkeeping.

- Rev219 note: GNU nano still documents the interface as a few simple regions and puts user questions/input on the status bar while help lines stay their own bottom region; that keeps reinforcing Micromax's current bias toward tiny inspectable screen regions instead of a deeper widget tree.

## rev215 — the visible interaction row deserves the same tiny shared model
- GNU nano still documents its screen as a handful of fixed regions — title bar, edit window, status bar, and two help lines — which is a good reminder that Micromax can keep small terminal-layout policies explicit and inspectable instead of hiding them in curses math.
- micro still documents `statusline`, `infobar`, and `keymenu` as ordinary options, which fits the ongoing Micromax strategy of lifting tiny visible-chrome policies into shared text-first models rather than inventing a heavyweight widget system.
- Forth exception text still treats the exception frame as implementation-defined state that often includes return-stack depth, and `THROW` removes the exception frame plus the return-stack content above it; that keeps the recent Micromax portability focus on `catch`/`throw` + outer `>r` items well grounded.


- micro's current options docs still frame `infobar`, `keymenu`, and `statusline` as ordinary bottom-bar options, which fits Micromax's recent habit of turning visible bottom chrome into tiny inspectable editor-side helpers rather than leaving it renderer-local.
- GNU nano's current manual still describes the status/prompt area and help lines as a few simple bottom screen regions, which points toward one more small row model rather than a richer widget tree.
- Micromax already had shared `interaction_*` status fields plus width-aware `statusline_model(width)`, `keymenu_model(width)`, and `infobar_model(width)` siblings. The remaining drift was that future UIs/scripts/LLMs still had to re-ellipsize `interaction_line` themselves if they wanted the *visible* prompt/capture row.
- For Micromax this argues for one **tiny width-aware interaction-row helper**: keep the existing interaction metadata, add `raw_line`, visible `text`, and a truncation flag, and let `bottom_rows_model(width)` / the tiny TUI reuse it instead of another round of ad-hoc clipping.

## rev214 — bottom help/message rows are still just terminal regions too

- micro's current options docs still treat `keymenu`, `infobar`, and `statusline` as ordinary bottom-bar options, which keeps reinforcing Micromax's recent approach: promote small visible truths into shared editor-side models before inventing another UI subsystem.
- GNU nano's current manual still treats the help lines and status/message bar as simple terminal regions and also documents `constantshow` as a small status-bar reporting toggle. That is good prior art for exposing tiny row snapshots instead of a widget tree.
- For Micromax this argues for two small sibling helpers after rev213's `statusline_model(width)`: add `keymenu_model(width)` with structured shortcut entries, add `infobar_model(width)` with left/right/padding/truncation details, and keep the curses TUI responsible only for row styling.

## rev213 — shared bottom chrome should expose statusline layout too

- micro's current options docs still treat `statusline`, `keymenu`, and `infobar` as ordinary bottom-bar surfaces, which is a good reminder that Micromax can keep statusline layout inspectable without inventing a richer widget system.
- GNU nano's current manual still describes the screen as a few simple terminal regions and frames hidden chrome as reclaimed editing space, which reinforces that the final status row is still just one small terminal line rather than a secret renderer-only object.
- Micromax had already moved capture state, interaction lines, and the full bottom-row stack into shared editor helpers. The remaining hidden policy was the statusline's left/right truncation and padding.
- For Micromax this argues for one tiny shared `statusline_model(width)` contract (plus hostcall `ed.statusline-model`) that future UIs/scripts/LLMs can inspect directly, while `statusline_text(width)` simply returns that model's final `text`.
- On the VM side, the recent `catch` / `throw` fixes already covered simple success and failure cases. The next honest portability follow-up is a nested case: an inner `throw` inside a successful outer `catch` should still preserve outer user-owned `>r` items.


## rev212 — bottom bars are still just terminal regions, which makes a shared row model the honest next step

- micro's current options docs still present `keymenu`, `infobar`, and `statusline` as ordinary bottom-bar toggles, not as a richer widget/layout subsystem. That is a good reminder that Micromax can keep the contract tiny while still making it inspectable.
- GNU nano's current manual still describes the screen layout as title bar, edit window, status bar, and help lines, and `--zero` still frames hidden chrome as reclaimed editing rows rather than blank UI placeholders. That is strong prior art for treating the visible bottom-row stack as a simple ordered terminal surface.
- Micromax had already moved prompt position, prompt windows, rendered prompt rows, capture status, and the current prompt/capture interaction line into shared editor helpers. The missing piece was the exact final visible stack.
- For Micromax this argues for one small editor-side `bottom_rows_model(width)` contract (plus hostcall `ed.bottom-rows`) that future UIs/scripts/LLMs can inspect directly, while the curses TUI remains responsible only for styling those already-computed rows.
- On the VM side, the recent `catch`/`throw` fixes already established that exception frames must stay invisible to `rdepth` and be trimmed on throw. The next honest portability follow-up is proving that recovery preserves outer user-owned `>r` items instead of flattening the whole return stack.


## rev209 — capture confirmation loops should read like real bottom prompts, and `catch` should unwind both stacks

- GNU nano's current manual still treats query-replace and other confirmation flows as a dedicated yes/no/all/cancel style menu, which is a good reminder that bottom-row confirmation UI can stay tiny while still being explicit.
- micro's prompt/help docs and source still show small bottom-line confirmation prompts like `Reload file? (y,n,esc)`, which is strong prior art for letting Micromax's existing capture keymodes read as real transient prompt states instead of invisible modal machinery.
- The Forth standard still frames `CATCH`/`THROW` around restoring stack state to the point just before protected execution, including return-stack restoration machinery (`RP!` in the reference wording). That means a `catch` implementation that only restores the data stack is subtly wrong.
- Micromax already had the right substrate: `qreplace` / `openurl` capture keymodes, shared status metadata, renderer-local infobar/keymenu rows, and a nearly-correct `catch`. The small honest move is therefore: surface capture-mode prompts in the TUI and trim `rstack` during error recovery, rather than inventing a new prompt subsystem.


## rev208 — constant cursor reporting should stay a tiny bottom-bar cue

- micro's current options docs still treat `infobar` and `statusline` as small bottom-bar toggles rather than a richer widget/layout subsystem. That is a useful reminder that Micromax should keep bottom-bar behavior composable and modest.
- GNU nano's current manual still presents `--constantshow` / `set constantshow` as a simple status-bar behavior: keep cursor position visible all the time. That is strong prior art for a tiny always-on position cue, especially in terminals where every reclaimed row matters.
- Micromax already had the meaningful shared data in `status_model()` (`display_line`, `display_col`, `line_count`, `percentage`, `last_message`). The missing piece was only renderer composition.
- The Micromax-sized move is therefore: add one tiny `constantshow` option, keep it renderer-local in the curses TUI, right-align the cursor summary in the idle infobar, and leave prompt rows and the shared status model alone.
- The matching portability cleanup is similarly small but valuable for future humans/LLMs: make the old `return-stack-roundtrip` case actually use `r>`, so corpus names keep telling the truth during Rust/WASM bring-up.


## rev204 — `matchbracestyle` is the right tiny follow-up to visible brace matching

- micro's current options docs still describe `matchbracestyle` as the choice between `underline` and `highlight` for matching braces, which is a strong signal that Micromax can keep this as a **renderer-local style toggle** rather than a new headless span/theme model.
- Micromax already had the meaningful part of the feature in place: visible brace positions are shared within the TUI for ordinary and docs/help buffers. The remaining gap was just how to style those cells.
- For Micromax this argues for one tiny helper that maps the option to curses attributes (`bold+underline` or `bold+reverse`) and reuses that answer everywhere the existing brace cue is drawn.

# Research notes

## rev203 — `showchars` is a good tiny renderer-side scanability win

- micro's current options docs still describe `showchars` as a plain option for displaying invisible characters, with distinct keys for ordinary spaces/tabs and indent-only `ispace` / `itab`, and they explicitly note that the shown characters are not inserted into files. That is strong evidence that Micromax can treat this as a **renderer-side view aid**, not a new buffer model or formatter.
- The same docs also note that only `tab` / `itab` may expand to multiple characters *if possible*. For Micromax's tiny curses TUI, the honest first pass is one-cell replacements only, because the current viewport/cursor/search styling model is still character-cell-based.
- For Micromax this argues for one shared TUI helper that rewrites visible row fragments only, keeps softwrap continuation-indent prefix spaces plain (because they are renderer-created, not file content), and lets `ispace` / `itab` override the ordinary `space` / `tab` glyphs in the leading indent run.

# Research notes

## rev201 — autosave is small but real editor behavior, not just plugin sugar

Current upstream micro docs still expose `autosave` as an ordinary option: save every N seconds, `0` disables it, and quitting with dirty buffers will also autosave and quit rather than asking twice. Micromax already had the right ingredients for a tiny honest version — a deterministic timer pump, one shared save path, and a deliberately simple dirty bit — so the smallest non-toy move was to make autosave a shared core rule rather than another TUI-only convenience or plugin example.

The result stays conservative:
- path-backed buffers only
- the same save normalization path as manual `save` (`rmtrailingws`, `eofnewline`, `mkparents`, `fileformat`, `encoding`)
- no attempt at crash-recovery backups or undo persistence
- no fake background threads; the existing host-driven timer pump remains the clock


## rev200 note — micro still treats `basename` as a normal display option

- micro's current options docs still describe `basename` as the switch that decides whether infobar/tabbar surfaces show only the basename or the full path.
- That makes Micromax's old always-basename status display misleading once `path`, `encoding`, and `fileformat` are already honest shared fields.
- The useful small fix is shared display state (`display_name`) plus one `basename` option, not another formatter-specific special case.

## rev177 — trailing whitespace is worth a tiny cue before a full diagnostics model

- micro's current options docs still expose `hltrailingws` as a plain display toggle and describe it as highlighting trailing whitespace at line ends, which is strong evidence that Micromax does not need a full lint/subdiagnostic system just to make forgotten spaces visible.
- Neovim's current `listchars` docs make the same broader point from another angle: trailing spaces are useful enough to expose directly in the renderer (`trail:c`) without changing buffer contents or inventing richer semantic state first.
- For Micromax this argues for a **small renderer-local helper** keyed off the logical line plus current visible fragment: honor softwrap/horizontal scroll honestly, keep the option name familiar, and leave “freshly typed trailing spaces” heuristics for a later richer edit-state model.

## rev172 — search highlighting should stay renderer-local first

- micro's current options help still describes `hlsearch` very conservatively: highlight all instances of the searched text after a successful search, let users toggle or temporarily clear the display, and keep the setting distinct from the temporary visibility state. That is a strong signal that Micromax can get real value from a tiny first pass without inventing a persistent search-highlight data model.
- Neovim's docs reinforce the same separation of concerns: `hlsearch` highlights matches for the last search pattern, while the current match can be styled more strongly (`hl-CurSearch`) than the rest. For Micromax, that suggests a minimal TUI cue such as “all visible matches reversed, current visible match also bold” long before there is a richer theme/span system.
- The resulting Micromax-sized policy is: keep search ownership in the headless editor (`query`, regex/literal mode, ignorecase, cursor movement), but let the curses renderer derive visible match segments from the text it is already drawing. That keeps softwrap/hscroll behavior honest enough for now and avoids prematurely freezing a cross-renderer highlight contract.

## rev171 note

Micro's current options docs still keep the line-number story very small: `ruler` means “display line numbers” and `relativeruler` switches non-current rows to relative counts. For Micromax, that argues for a similarly tiny first step in the curses TUI: reuse those familiar option names, keep the gutter renderer-only instead of turning it into headless editor state, and leave wrapped continuation rows blank so softwrap does not visually lie about where a logical line begins.

## rev170 note

Conformance corpora stay most useful when they support both **broad inspection** and **precise replay**. The WebAssembly spec repo still frames the spec, reference implementation, and testsuite as one package, and Test262 still frames its suite around observable behavior. For Micromax, that argues for a tiny data-only portability corpus that keeps growing around missing ledger-promised behaviors, plus exact case-name selection so a future Rust/WASM host or future LLM can ask for one or two specific contract points without fuzzy filtering.

## rev169 note

Conformance suites stay useful when they support both **replay** and **light-weight inventory**. WebAssembly's spec repo still pairs the reference interpreter with a testsuite, and Test262's technical rationale still frames conformance material as an implementation-facing contract. For Micromax, that argues for a tiny data-only portability corpus that can now be inspected in two modes: full case/result JSON when you need replay detail, and a smaller category/tag/name inventory when you only need to answer “what does the contract cover?”

## rev168 — portability corpora should be easy to inspect, not just easy to run

- The WebAssembly spec repo still pairs the spec with a reference implementation and official testsuite, and Test262 still frames itself as the official ECMAScript conformance suite. That keeps reinforcing the same lesson: a second implementation needs boring, machine-consumable ground truth, not just a pile of host-language unit tests.
- For Micromax, that argues for two small follow-ups to the existing JSON portability corpus: keep filling obvious kernel gaps that are already in the portability ledger (`while`, `constant`, `variable`, locals shadowing), and make the runner output easy to consume programmatically during bring-up.
- The right low-hanging-fruit move is still not a heavyweight harness. It is a slightly richer tiny corpus plus a `--json` path in `mxportable`, so future Rust/WASM hosts and future LLMs can ask narrower questions like “show me all memory-related portable cases” or “did the locals slice pass?” without scraping human console text.
- Broad but simple tags also buy leverage: they keep the corpus hand-editable while making targeted slices much more useful than the earlier mostly-untagged file.


## rev163 — visible inline-code backticks deserve a tiny source-view cue

- CommonMark's current spec still defines a code span as matching backtick strings of equal length around inline code content, which makes the visible backtick runs part of the author-facing source rather than accidental punctuation.
- GitHub's current Markdown docs still teach inline code with backticks, which means visible `` ` `` / `` `` `` delimiters are part of the markdown people are actually likely to paste into Micromax docs.
- Micromax already dims inline-code bodies in docs/help buffers and already uses the same equal-length backtick scan for precedence, so letting the visible delimiter runs read a little more like source is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny shared helper** layered on the existing equal-length backtick scan: bold+dim only the opening/closing backtick runs while leaving the already-dim code body styling alone, and still stop well short of promising full CommonMark whitespace-normalization or a richer markdown renderer.


## rev162 — visible inline emphasis delimiters deserve a tiny source-view cue

- CommonMark's current spec still frames emphasis and strong emphasis around visible delimiter runs using `*` or `_`, so the punctuation around emphasized text is part of the author-facing source rather than accidental prose.
- GitHub's current Markdown docs still teach bold, italic, and strikethrough as ordinary source syntax, which means visible `**`, `*`, `_`, and `~~` tokens are part of the markdown people are actually likely to paste into Micromax docs.
- Micromax already styles the body text for tiny inline emphasis forms in docs/help buffers, so letting the visible delimiter tokens read a little more like source is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny UI helper** layered on the existing inline-emphasis regex helpers: dim only the delimiter tokens while leaving the body styling alone, and still stop well short of promising full CommonMark delimiter-run correctness or a richer markdown renderer.


## rev161 — visible ordinary markdown links deserve a tiny source-scaffolding cue

- CommonMark's current spec still frames inline links and reference links as the two basic link forms, with visible source around the link text carrying the destination or reference id, which is the practical reason `[label](dest)` / `[label][id]` / `[shortcut]` should not read exactly like plain prose in source view.
- GitHub's current Markdown docs still teach ordinary inline links directly with bracketed text plus a parenthesized URL, so visible link scaffolding is part of the Markdown authors are actually likely to paste into Micromax docs, not a parser curiosity.
- Micromax already underlines the live label text for supported docs/help links, so letting the surrounding markdown scaffolding read a little more like deliberate source is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny UI helper** layered on the existing shared link matcher: dim only the non-label scaffolding (`[` / `](` + destination or reference tail / `]`) while leaving the live label underlined, and still stop well short of promising a fuller rendered-markdown system.


## rev159 — visible markdown images deserve a tiny inert-source cue

- CommonMark's current spec says image syntax is like link syntax except that the bracketed text is an image description rather than ordinary link text, and that description becomes alt text when rendered. That makes `![alt](dest)` / `![alt][id]` clearly visible source structure rather than just accidental punctuation.
- GitHub's current Markdown docs still teach images directly with `![alt](url)` and explicitly describe the bracketed text as alt text, so image source is part of the Markdown people are actually likely to paste into Micromax docs.
- Micromax already keeps markdown image forms inert for `helpfollow`, `helplinkpick`, and docs-link underlining, so letting the whole visible token read a little more like deliberately inert source is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny UI helper** layered on the existing shared balanced-span / escape / destination / reference helpers: dim the whole visible image token in source view and still stop well short of promising a fuller rendered-image system.


## rev158 — visible autolinks deserve the same tiny source-view cue

- CommonMark's current spec says autolinks are absolute URIs and email addresses inside `<` and `>`, parsed as links with the URL or email address as the label, which makes angle-bracket autolinks clearly visible source syntax rather than incidental punctuation.
- GitHub's current Markdown docs still teach ordinary inline links and also point readers to automatic linking for valid URLs, so autolink-like source remains part of the Markdown people are actually likely to paste into Micromax docs.
- Micromax already underlines the inner URL for the supported autolinks it recognizes in docs/help buffers, so letting the surrounding `<...>` token read a little more like a link is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny UI helper** layered on the existing shared autolink matcher: bold the full `<...>` token in source view while keeping the ordinary docs-link underline on the inner URL, and still stop well short of promising a fuller rendered-link system.


## rev157 — footnote references deserve the same tiny source-view cue

- GitHub's current Markdown docs explicitly teach footnotes as an author-facing syntax and even show a multi-line footnote example, so `[^id]` tokens are part of the docs source people are actually likely to paste into Micromax.
- Python-Markdown's footnotes extension docs make the same point from an implementation angle: a footnote definition starts from the matching `[^id]:` reference and additional content lines belong to that note, which reinforces that footnotes are visible source structure rather than hidden parser trivia.
- Micromax already lets `[^id]` references navigate correctly in docs/help buffers, so letting the visible token itself read a little more like a footnote is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny UI helper** layered on the existing shared footnote matcher: bold the full `[^id]` token in source view while keeping the ordinary docs-link underline on the inner `^id`, and still stop well short of promising a fuller rendered-footnote system.


## rev156 — GitHub-style blockquote alerts deserve a tiny source-view cue

- GitHub's current Markdown docs teach alerts as a blockquote-based extension using opener lines like `> [!NOTE]` and `> [!WARNING]`, which makes those markers relevant to the docs authors are actually likely to paste into Micromax, not a hypothetical syntax flourish.
- Micromax already gives ordinary blockquote rails a tiny source-view cue, so letting the alert token itself look special is a good parity follow-up rather than a new parser commitment.
- For Micromax this argues for one **tiny shared alert-marker helper** layered on top of the existing blockquote-prefix helper: keep the blockquote model, recognize only the common GitHub alert tokens, and let the live docs/help TUI bold that token while the body stays dim.
- That buys a small but honest scanability win for source-view docs while staying deliberately far away from a fuller admonition/callout renderer.


## rev153 — raw HTML/comment precedence should show up in the live docs TUI too

- CommonMark's current spec says HTML blocks are treated as raw HTML, with different start/end rules for the block kinds, and GitHub Docs says its GFM stays CommonMark-compliant. That is the broad reason embedded `<div>` / `<pre>`-style examples in Micromax docs should not feel like ordinary markdown prose.
- The same broad precedence applies to HTML comments too: once the docs browser already keeps commented-out markdown examples inert for navigation/definition parsing, the live TUI should not visually imply that those regions are active prose.
- For Micromax this argues for a **render-parity follow-up, not another parser**: reuse the existing shared `md_html_comment_line_spans()` and `md_html_block_line_flags()` helpers the docs browser already trusts, and let the TUI dim those spans/lines.
- That buys a small but honest win: commented-out notes and embedded HTML examples stop looking quite so much like ordinary prose, while the archive still avoids a fuller HTML/Markdown renderer.


## rev150 — setext headings should not feel second-class in the live docs TUI

- CommonMark's current spec says a setext heading consists of **one or more lines of text** followed by an underline of `=` or `-`, and those lines must otherwise behave like an ordinary paragraph rather than a code fence, ATX heading, blockquote, thematic break, list item, or HTML block.
- GitHub Docs says its GFM stays CommonMark-compliant, so setext headings are relevant to the markdown authors are actually likely to paste into Micromax docs, not just parser trivia.
- For Micromax this argues for a **tiny shared heading-line-role helper** layered on top of the existing heading scan rather than another TUI-only regex: the docs browser already trusts that scan for titles, outline rows, fragments, and heading breadcrumbs.
- That buys a small but honest parity win: setext title lines finally look like headings in the live TUI too, underline lines read as heading rails instead of generic punctuation, and future UIs/LLMs have one tiny shared helper to reuse.


## rev131 — tiny wrapped inline links are the next shared destination win

- Picker UX note (rev147 follow-on): once separators/sections become real structure, the *visible rendered rows* usually become shared substrate too, not just the raw suggestion arrays. Exposing a small rendered-row model (`prompt_display_model`, `ed.prompt-display`) keeps future UIs/LLMs from re-deriving sticky headers / more markers / selected-row text from lower-level window metadata, which is in the same spirit as VS Code Quick Pick separators and Helix treating pickers as a dedicated surface.
- CommonMark's current spec says inline-link components may be separated by spaces, tabs, and **up to one line ending**, and if both destination and title are present they may also be separated that way.
- GitHub Docs says its GFM stays CommonMark-compliant, so wrapped inline links are relevant to the markdown authors are actually likely to paste into Micromax help pages, not just a parser curiosity.
- For Micromax this argues for a **small multiline shell around the existing inline destination parser**: reuse the same destination policy, add one shared continuation-line helper that fences/raw-HTML/comments can also respect, and avoid growing another bespoke multiline regex path for each docs surface.


## rev130 — spaces-only 0–3 indent guards are a good tiny correctness pass

- CommonMark's current spec says ATX headings and link reference definitions may be preceded by **up to three spaces** of indentation, and four spaces are too many because that territory belongs to indented code-like prose.
- GitHub Docs says its GFM stays CommonMark-compliant, so this small indentation rule is relevant to the markdown people are actually likely to paste into Micromax help pages, not just a parser trivia note.
- For Micromax this argues for a **single tiny leading-space helper** reused by reference definitions, footnote definitions, and ATX heading scans: keep tabs/four-space lookalikes inert, keep the policy shared, and avoid another round of per-surface regex drift.


## rev129 — wrapped reference definitions are a good tiny follow-up

- CommonMark's current spec says a link reference definition allows optional spaces or tabs including **up to one line ending** after the colon and again after the destination, which is the practical reason wrapped forms like `[id]:\n  target\n  "title"` are valid.
- GitHub Docs says its GFM stays CommonMark-compliant, so these wrapped reference definitions are relevant to the markdown authors are actually likely to paste into Micromax help pages, not just a spec curiosity.
- For Micromax this argues for a **small multiline shell around the existing shared destination parser**: keep destination parsing in one helper, add only one-line-wrap support for destination/title, and avoid growing a second regex path just for reference definitions.


## rev128 — conservative generic HTML blocks are the next tiny shared win

- CommonMark's current spec says HTML blocks of type 7 begin on a line that is a complete open or closing tag, continue until the next blank line, and — unlike types 1-6 — may not interrupt a paragraph.
- GitHub Docs says its GFM stays CommonMark-compliant, which makes that type-7 distinction relevant to the kind of markdown-like docs people are likely to paste into Micromax.
- For Micromax this argues for a **conservative type-7-ish extension of the existing shared HTML-block helper**: recognize tag-only lines like `<widget-box ...>` or `</widget-box>` at doc start / after blank lines, keep the following literal markdown inert until a blank line, and deliberately refuse paragraph-interrupting cases.
- That buys another real docs-browser safety/clarity win without taking on a fuller HTML parser or Markdown-in-HTML model.


## rev127 — raw HTML blocks should stay raw in the docs browser

- CommonMark's current spec defines seven HTML block kinds; types 1-6 can interrupt a paragraph, while type 7 is intentionally more restricted. That is the broad semantic reason docs-like content under `<div>...</div>` or `<pre>...</pre>` should not leak markdown links/headings/ref-defs back into the live help browser.
- The spec also draws a useful operational distinction: block-tag forms like `<div>` / `<table>` run until the next blank line, while `<pre>` / `<script>` / `<style>` style blocks stay raw until their closing tag and can therefore contain internal blank lines without resuming markdown parsing.
- GitHub Docs says its GFM stays CommonMark-compliant, which makes these HTML-block rules relevant to the markdown people are actually likely to paste into Micromax docs, not just an abstract parser corner.
- For Micromax this argues for a **single tiny HTML-block helper** reused by helpfollow, helplinkpick, outline scans, definition parsing, and TUI underlining — enough to keep embedded HTML examples inert without promising full Markdown-in-HTML semantics.


## rev119 — markdown escapes should stay literal

- CommonMark's current spec says any ASCII punctuation character may be backslash-escaped, which is the broad semantic reason literal markdown examples like `\[link]` should not become active syntax.
- CommonMark also treats autolinks as their own tighter form, so `\<https://...>` is a good example of why escape handling must be part of link precedence, not an afterthought.
- Python-Markdown's inline processors make the operational point from another angle: image, reference, and short-reference parsing all share text/link extraction machinery, and the docs explicitly expose unescaping as part of that inline-processing model.
- For Micromax this argues for a **single tiny escape-awareness helper** reused by docs-browser scanners, not ad hoc per-regex special cases.


## rev167 — tiny conformance suites get more useful when they are sliceable and self-validating

- The WebAssembly spec repo still explicitly couples a reference implementation with a testsuite covering conformance, which is a good reminder that “small executable contract + shared corpus” is part of language design, not an afterthought.
- Test262's current rationale/docs still emphasize a declarative, readable, implementation-agnostic style, and the ecosystem around it keeps leaning on metadata/frontmatter to help runners select the right subsets of tests during bring-up.
- For Micromax this argues for a portability corpus that stays data-only and hand-editable, but also validates itself and offers coarse filtering (`category`, optional `tags`, name substring) so future Rust/WASM ports and future LLMs can ask narrower questions than “run everything.”

# Research notes (selected inspirations)

## rev116 — inline code spans: a little more real, still tiny

- CommonMark defines a code span as opening with a backtick string and closing with an equal-length backtick string; that is the practical reason double-backtick forms exist when literal backticks must appear inside code-like text.
- CommonMark also says code spans bind more tightly than link brackets, which is a strong hint that docs UIs should not underline markdown-looking text that sits inside inline code.
- Python-Markdown’s inline-pattern ordering makes the same point operationally: backticks and escapes are handled before links and before emphasis/strong.
- For Micromax this argues for a **slightly less toy inline-code helper**: support equal-length backtick runs, mask code spans before other inline cues, and still stop well short of promising full CommonMark whitespace-normalization or every delimiter edge case.


## rev115 — inline emphasis: steal the signal, not the parser

- GitHub Docs presents bold, italic, and strikethrough as ordinary author-facing markdown forms (`** **` / `__ __`, `* *` / `_ _`, and `~~ ~~`).
- The GFM spec gives emphasis/strong emphasis a large delimiter-run grammar, and defines strikethrough as an extension.
- ncurses exposes `A_ITALIC` only as an extension, not a portable X/Open Curses guarantee, so a tiny TUI should treat italics as opportunistic and keep a fallback.
- For Micromax this argues for a **tiny UI-only inline helper layer**: bold strong bodies, use italic when available (falling back to underline) for emphasis, dim strike bodies, and stop well short of promising full nested-delimiter correctness.


## rev114 — docs thematic breaks

- CommonMark defines a thematic break as up to three leading spaces, followed by three or more matching `-`, `_`, or `*` characters, with optional spaces or tabs between markers.
- GitHub Docs teaches the common author-facing form as a horizontal rule made from three or more dashes.
- For Micromax this argues for a **tiny UI-only recognizer** in help/docs buffers: enough to make separators visually legible, but not enough to force a full markdown block parser into the headless core.



Rev60 note: Helix explicitly exposes a **jumplist picker** UI (`Space-j`) in addition to back/forward navigation, which is a strong argument for making our navigation targets row-shaped and searchable from day one. Kakoune discussions around marks storing full selections also suggest a future extension where marks can capture multi-cursor state, not just a single cursor.

This is a curated set of ideas we’re borrowing from / reacting to.

## micro editor (target UX baseline)

micro’s philosophy is “modern terminal editor with sane defaults” and includes
common keybindings, a menu, multi-cursor, and a plugin system (Lua + plugin manager).

**Takeaway for micromax**: keep a “nano-like” discoverability layer, but make the
extension language our core differentiator.

References:
- micro repo / feature list: https://github.com/micro-editor/micro
- micro website (plugin system): https://micro-editor.github.io/

## “Forth as the plugin language” has precedent

Forth has been used as an interactive *embedded control language* in real systems:

- **Open Firmware (IEEE 1275)** exposes a Forth CLI, and even supports a compact
  bytecode form (FCode) used for device drivers.
  - https://en.wikipedia.org/wiki/Open_Firmware
  - https://www.devicetree.org/open-firmware/home.html

- **FreeBSD boot loader** historically embeds a Forth interpreter (via FICL) as one
  of its built-in configuration/script interpreters.
  - https://man.freebsd.org/loader
  - FICL overview: https://ficl.sourceforge.net/ficl.html

**Takeaway**: “Forth as a plugin/config language” is *not* an eccentric idea; it
has proven value where interactive debugging + extensibility matter.

## Forth standard (scope boundary)

Forth-2012 defines a small required “Core” word set and organizes everything else into
optional word sets. This “word-set modularity” matches our goal: small kernel, add-ons.

References:
- Core wordset glossary: https://forth-standard.org/standard/core
- Search-Order word set (wordlists + search order): https://forth-standard.org/standard/search

## “Hacker-level Forth”: metaprogrammable control flow

Classical Forth’s deeper magic is that control flow is “just words” cooperating during
compilation. Implementations that keep a linked dictionary and a threaded code model make
it easier to reach this “hacker level”.

Reference:
- Eli Bendersky, *Implementing Forth in Go and C* (user vs hacker-level distinction):
  https://eli.thegreenplace.net/2025/implementing-forth-in-go-and-c/

## Namespacing: wordlists + search order

Modern Forth systems use wordlists and a search order (a stack/list of wordlists) to
control name resolution and keep domains from colliding.

References:
- Forth-2012 Search-Order word set: https://forth-standard.org/standard/search
- Gforth manual: wordlists overview: https://gforth.org/manual/Word-Lists.html

## colorForth: reducing hidden state

Chuck Moore experimented with removing the traditional `STATE` mechanism by attaching
attributes to words so parsing/compilation is less context-sensitive.

Reference:
- Discussion of colorForth removing `STATE` and word-tied attributes:
  https://langdev.stackexchange.com/questions/1170/is-colorforths-unique-syntactic-approach-helpful-to-the-programmer

## Factor: quotations + combinators for ergonomics

Factor formalizes quotations (`[ ... ]`) as anonymous functions and relies heavily on
combinators to reduce stack shuffling. We want *some* of this ergonomics while staying
smaller and closer to Forth.

References:
- Slava Pestov, *Factor: a dynamic stack-based programming language* (DLS paper):
  https://factorcode.org/littledan/dls.pdf
- Factor docs on stack shuffling pain point: https://docs.factorcode.org/content/article-tour-stack-shuffling.html

## “Why Lua in Neovim?” (contrast case)

Neovim makes Lua a first-class scripting/config language.

References:
- Neovim docs: Lua overview: https://neovim.io/doc/user/lua.html
- Neovim Lua guide: https://neovim.io/doc/user/lua-guide.html

**Takeaway**: embedded languages win when they’re:
- always available (no external runtime installation)
- fast enough for interactive use
- tightly integrated with the host API

We should aim for the same, but with micromax.

## RetroForth: “modern, pragmatic Forth”

Retro positions itself as tiny, elegant, and adaptable—a useful datapoint for “modern Forth”
taste and packaging.

Reference:
- https://retroforth.org/

## Additional landscape / adjacencies (rev3)

### Namespaces via Search-Order / wordlists
- Forth 2012 Search-Order word set: https://forth-standard.org/standard/search
- `SET-ORDER`: https://forth-standard.org/standard/search/SET-ORDER

### Quotations + combinators (Factor/Joy/Retro)
- Factor paper (quotations, combinators, tooling): https://factorcode.org/littledan/dls.pdf
- Factor: words vs quotations metadata: https://concatenative.org/wiki/view/Factor/FAQ/What%27s%20Factor%20like%3F
- Joy overview: https://hypercubed.github.io/joy/html/forth-joy.html
- Joy FAQ: https://hypercubed.github.io/joy/html/faq.html
- RetroForth overview (prefix-guided compiler, quotations/combinators, vocabularies): https://retroforth.org/

### Forth interpreter/compile state (why we may diverge)
- Revisiting Forth (describes interpreter states): https://blog.jacobvosmaer.nl/0049-revisiting-forth/
- Starting Forth: compiling words / dual behavior: https://www.forth.com/starting-forth/11-forth-compiler-defining-words/

### Concurrency in Forth systems
- Gforth multitasker (cooperative + pthread): https://gforth.org/manual/Multitasker.html
- Gforth pthread notes (real concurrency implies conflict avoidance): https://gforth.org/manual/Pthreads.html



## New sources (rev4)

- Factor stack checker constraints around combinators (useful model for “stack effects later”):
  https://docs.factorcode.org/content/article-inference-combinators.html
- RetroForth overview + handbook:
  https://retroforth.org/
  https://www.retroforth.com/Handbook-Latest.epub
- FreeBSD loader(8) notes it embeds multiple interpreters including a Forth based on FICL:
  https://man.freebsd.org/loader
- FICL paper (embedding / portability perspective):
  https://dl.acm.org/doi/10.1145/606666.606672
- colorForth discussion (syntactic experiments to reduce hidden interpreter state):
  https://langdev.stackexchange.com/questions/1170/is-colorforths-unique-syntactic-approach-helpful-to-the-programmer


## New sources (rev5)

- Forth-2012 `DEFER` (standardized deferred words):
  https://forth-standard.org/standard/core/DEFER
- Wren embedding docs (embedding API is first-class):
  https://wren.io/embedding/
- Janet embedding docs (stable embedding story):
  https://janet-lang.org/capi/embedding.html
- Emacs hooks/advice docs (cheap extensibility patterns):
  https://www.gnu.org/s/emacs/manual/html_node/elisp/Hooks.html
  https://www.gnu.org/s/emacs/manual/html_node/elisp/Advising-Functions.html

## New sources (rev24)

### Micro editor plugin lifecycle + keybinding philosophy

Micro’s runtime help documents a simple plugin lifecycle (`preinit`, `init`, `postinit`, `deinit`) and a JSON-based keybinding/config surface, with plugins typically written in Lua.

References:
- micro help: plugins: https://github.com/zyedidia/micro/blob/master/runtime/help/plugins.md
- micro help: keybindings: https://github.com/zyedidia/micro/blob/master/runtime/help/keybindings.md
- micro tutorial (mentions `init.lua` + config system): https://github.com/zyedidia/micro/blob/master/runtime/help/tutorial.md

**Takeaway**: a tiny set of predictable lifecycle entrypoints + explicit keybinding/config files scales surprisingly far.
Micromax’s wordlists/modules map cleanly onto “one namespace per plugin”, and editor hostcalls can mirror micro-style lifecycle calls.

### Maps / hashtables in concatenative languages

Factor treats hashtables as a first-class collection and provides a dedicated vocabulary with predictable predicates and constructors.

Reference:
- Factor docs: hashtables vocabulary: https://docs.factorcode.org/content/word-hashtable%2Chashtables.html

In traditional Forth systems, “map” structures tend to be library-level (no standard core wordset), reinforcing the idea that a *small* primitive surface can still be enough if the embedding story is clear.

References:
- Discussion thread on Forth hash tables: https://comp.lang.forth.narkive.com/bcnGy5Uo/hash-tables-in-forth
- Gforth manual: wordlists/search order (namespace model that we already lean on): https://gforth.org/manual/Word-Lists.html

## New sources (rev25)

### Prompt / command bar completion conventions

Many editors converge on the same ergonomic pattern:

- **micro**: command bar (`Ctrl-e`) with `Tab` completing when possible.
  - quick reference cheat sheet: https://cheatography.com/mynocksonmyfalcon/cheat-sheets/micro-text-editor/
- **Kakoune**: prompt completion uses `Tab` / `Shift-Tab` to cycle.
  - discussion + doc pointer: https://discuss.kakoune.com/t/select-from-autocomplete-options/1835
- **Helix**: completion menus use `Tab`/`Shift-Tab` (and `Ctrl-n`/`Ctrl-p`) for next/prev.
  - keymap docs: https://docs.helix-editor.com/keymap.html

**Takeaway**: “Tab = next, Shift-Tab = prev” is a strong default for any completion list, whether it’s LSP, prompt completion, or command palette. If we model completion state as data (candidate list + index + replacement range), the same behavior can be reused across UI layers.

## New sources (rev27)

### File/path completion in command prompts

Micro’s command bar is heavily used for file/workspace operations (e.g., opening files and changing directories). In practice, users rely on `Tab` completion to avoid retyping long paths.

A recurring pain point in some implementations is “Tab completes to the first match” without a clear, predictable way to *cycle* other matches — which shows up as UX friction in real-world `open` workflows.

References:
- Micro command bar overview + `Tab` completion behavior (walkthrough): https://forum.garudalinux.org/t/mastering-the-micro-text-editor/32889
- Micro issue reporting `open`+Tab completing to the first match instead of cycling cleanly: https://github.com/micro-editor/micro/issues/2977

**Takeaway**: if we model prompt completion as a *session* (candidate list + index + replacement range), we can make cycling explicit (`Tab`/`Shift-Tab`) and avoid the “first match trap,” while still keeping a tiny, UI-agnostic core.

## New sources (rev28)

### Quoting and spaces in paths

Micro’s own help text is explicit: arguments containing spaces should be quoted, and the command bar parser follows `/bin/sh`-style quoting and escaping rules.

Separately, there are real-world bug reports where path handling breaks specifically when a completed path contains spaces, even though completion itself can find/cycle the candidate.

References:
- micro help: command bar parsing and quoting rules: https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md
- micro issue: opening via file switcher fails when the path contains spaces: https://github.com/micro-editor/micro/issues/3970

**Takeaway**: path completion needs a quoting/escaping story, not just a directory listing story. Our headless completion model can stay tiny while still auto-quoting paths with spaces (and escaping embedded `"`) so the command parser sees correct arguments.

## 2026-02-26 — Command/arg completion as a first-class extension surface

- micro’s plugin API exposes `MakeCommand(name, fn, completion)` and explicitly passes a completion strategy (e.g. `config.NoComplete`). This reinforces that “command definition” and “how its args complete” should be configurable as separate concerns.
- Kakoune’s shift toward `complete-command` (separate from `define-command`) is a strong design signal: completion wants to be **reconfigurable in hooks** and composable without exploding flag sets.

Links (for later deep reading):
- https://terokarvinen.com/2022/micro-editor-plugin-hello-world/ (shows `config.MakeCommand(..., config.NoComplete)`)
- https://discuss.kakoune.com/t/designing-the-new-complete-command-command/2008 (motivation and tradeoffs for `complete-command`)

## New sources (rev30)

### Keybinding discoverability and removal

Micro already treats “what is this key bound to?” as an explicit command-bar workflow via `showkey`, and its keybinding docs describe disabling bindings by assigning the `None` action. Helix’s remapping docs similarly frame keybindings as a table of commands/macros and explicitly allow disabling keys with `no_op`. Kakoune’s mode docs emphasize attaching docstrings to mappings so discoverability information can be surfaced in the automatic info box.

References:
- micro commands help (`showkey`): https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md
- micro keybindings help (`None` action disables bindings): https://github.com/micro-editor/micro/blob/master/runtime/help/keybindings.md
- Helix remapping docs (`no_op`, command/macros in keymaps): https://docs.helix-editor.com/remapping.html
- Kakoune modes docs (mapping docstrings shown in info box): https://github.com/mawww/kakoune/blob/master/doc/pages/modes.asciidoc

**Takeaway**: bindings should be treated as inspectable data, not only executable shortcuts. Even before we have layered keymaps or a rich UI, a small provenance-bearing binding record gives us better debugging, help, and reloadability.

## rev31 — hooks should be inspectable, not just runnable

- micro’s plugin help explicitly treats lifecycle/event callbacks as first-class plugin surface: `preinit`, `init`, `postinit`, `deinit`, `onAction`, `preAction`, `onBufferOpen`, etc. That reinforces the idea that editor hooks are not incidental internals — they are part of the public scripting model and deserve tooling.
- Kakoune’s hooks model emphasizes *named hook groups* and explicit removal via `remove-hooks`, which is a strong design signal that hook installations are configuration data that users need to manage after the fact.
- Emacs documents hooks as variables holding a list of functions to run on an occasion, which maps very closely to Micromax’s ordered multi-handler hook words. The useful lesson is not copying Lisp variables; it is preserving the “hook = inspectable list of callbacks” mental model.
- There is also explicit user demand for seeing currently active hooks in Kakoune discussions, which validates spending a small amount of surface area on hook introspection instead of treating it as a luxury.

Design takeaway for Micromax: keep hook *execution* tiny and portable, but add best-effort provenance and a stable row-oriented inspection word (`hook-rows`) so the live system remains debuggable.

## rev32 — statusline semantics should be shared, rendering should stay flexible

- Helix explicitly models the statusline as configurable **left / center / right** element lists, with defaults including file name, modification indicator, selections, and cursor position. This is a strong design signal that the *semantic pieces* of status belong in a stable model even if rendering/layout changes later.
- Micro treats the statusline as real editor surface rather than pure decoration. Its options/help mention the statusline directly (including how it behaves as a split divider), and user feedback around reclaiming the last line reinforces that this strip of UI matters in a terminal editor where space is precious.

References:
- Helix editor docs, `editor.statusline`: https://docs.helix-editor.com/master/editor.html
- micro options/help (statusline option/divider behavior): https://github.com/micro-editor/micro/blob/master/runtime/help/options.md
- micro issue about reclaiming the last line when statusline is disabled: https://github.com/zyedidia/micro/issues/3630

**Takeaway**: Micromax-editor should keep a tiny, shared **status model** in the headless core, then let future UIs decide how to lay it out (single line, split infobar, transient message strip, etc.).


## rev33 — hook groups are cheap cleanup power

- Kakoune’s hook docs make hook *groups* explicit: a hook registered with `-group` can later be removed with `remove-hooks <scope> <group>`. That is a strong signal that real editor/plugin ecosystems need *grouped cleanup*, not only per-handler removal.
- Emacs’s hook docs emphasize `add-hook` / `remove-hook` as the modular way to manipulate hook lists without trampling unrelated handlers. Even without copying Lisp variables, the lesson is the same: hook installation should preserve other participants and make selective removal easy.
- micro’s plugin lifecycle (`preinit` / `init` / `postinit` / `deinit`) reinforces the value of having a cheap “tear down everything this plugin added” mechanism when reloads happen repeatedly during development.

References:
- Kakoune hooks docs / `remove-hooks`: https://github.com/mawww/kakoune/blob/master/doc/pages/hooks.asciidoc
- Kakoune community hook docs summary: https://discuss.kakoune.com/t/hooks/544
- Emacs Lisp manual, setting hooks (`add-hook` / `remove-hook`): https://www.gnu.org/s/emacs/manual/html_node/elisp/Setting-Hooks.html
- micro plugin lifecycle help: https://github.com/zyedidia/micro/blob/master/runtime/help/plugins.md

**Takeaway**: keep Micromax hook execution tiny, but add a *group tag* to registrations plus a group-removal path so plugin reload/unload can clean up callbacks without full VM resets or fragile per-handler bookkeeping.

## rev34 — dynamic editor registrations should be treated as cleanup-friendly data

- micro’s command and keybinding docs reinforce that commands and bindings are *live editor configuration*, not hardwired code paths: the command bar exposes `bind`, `showkey`, and `reload`, while plugin docs describe `deinit()` followed by `preinit()` / `init()` / `postinit()` on reload. That strongly suggests repeated development reloads need a cheap way to tear down dynamic registrations cleanly.
- micro’s plugin API also exposes `MakeCommand(...)` and `TryBindKey(...)`, which is a nice confirmation that “commands” and “bindings” belong in the plugin/config layer, not buried inside the editor core.
- Kakoune’s mapping docs are explicit that mappings are created and removed with `map` / `unmap`, scoped by mode/context, and can carry docstrings for discoverability. That is another signal that key registrations should be treated as inspectable data structures rather than anonymous callbacks.
- Helix’s remapping docs distinguish static commands, typable commands, and macros, and support disabling keys with `no_op`. Even though Helix is less dynamic at runtime, it still treats the keymap as declarative data with stable command names behind it.
- Emacs’s minor-mode docs are the classic reminder that separate keymaps compose by activation context. We are not copying the whole model yet, but it supports the direction of keeping Micromax-editor registrations explicit, inspectable, and mode-ready.

References:
- micro command bar / reload / showkey: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/commands.md
- micro plugin API + lifecycle (`MakeCommand`, `TryBindKey`, `deinit`): https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/plugins.md
- micro keybindings / `command:` bindings / `None` unbinds: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/keybindings.md
- Kakoune mapping / unmap / docstrings: https://raw.githubusercontent.com/mawww/kakoune/master/doc/pages/mapping.asciidoc
- Helix remapping / minor modes / `no_op`: https://docs.helix-editor.com/remapping.html
- Emacs keymaps and minor modes: https://www.gnu.org/software/emacs/manual/html_node/elisp/Keymaps-and-Minor-Modes.html

**Takeaway**: a tiny editor bridge should still treat dynamic commands and bindings as *registrations with metadata*. Group tags are a cheap addition that make plugin reload/unload safer now, while leaving room for future mode/layered keymaps.



## rev35 — keymaps want context, but the first useful step is tiny

- Helix's remapping docs distinguish normal/insert/select maps and explicitly support **minor modes** by nesting definitions under keys like `g` or `z`. That is a strong signal that context-sensitive keymaps are worth modeling as data, not hardcoded UI behavior.
- Helix's keymap docs also enumerate these minor modes as explicit subcontexts reachable from normal mode, reinforcing the idea that a small editor can have layered keymaps without going "full Vim."
- Kakoune's mapping docs make *mode* part of the mapping contract itself: `map`/`unmap` are parameterized by contexts like `normal`, `insert`, `prompt`, `user`, `goto`, and `view`, and mappings can carry docstrings for discoverability.
- Emacs's minor-mode docs are the classic proof that independent keymaps compose by activation state: each enabled minor mode can contribute its own keymap.
- micro is less mode-heavy, but its command/keybinding docs still reinforce that dynamic bindings are live configuration and should be inspectable (`bind`, `showkey`, `reload`).

References:
- Helix remapping / minor modes: https://docs.helix-editor.com/remapping.html
- Helix keymap docs / minor modes: https://docs.helix-editor.com/keymap.html
- Kakoune mapping modes and `map`/`unmap`: https://raw.githubusercontent.com/mawww/kakoune/master/doc/pages/mapping.asciidoc
- Emacs keymaps and minor modes: https://www.gnu.org/software/emacs/manual/html_node/elisp/Keymaps-and-Minor-Modes.html
- micro command bar / `showkey` / reload: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/commands.md
- micro keybindings / chaining / `command:` bindings: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/keybindings.md

**Takeaway**: Micromax-editor does not need a huge modal architecture yet. A small contract gets most of the value: bindings carry a `mode`, the editor keeps an active mode stack, lookup falls back to global, and the result stays introspectable + reload-safe.

## rev36 — transient keymodes are a small feature with big editor leverage

- Emacs’s `set-transient-map` is the most explicit statement of the pattern: a transient keymap takes precedence over other active keymaps for one or more subsequent keys, and the default behavior is “use it once”.
- Helix’s keymap and remapping docs show the same family of idea from a more editor-facing angle: `g`, `z`, and other minor modes are short-lived dedicated binding layers that you enter from a normal map.
- Kakoune’s docs mention `next-key[...]` style mode pushes, which is further confirmation that temporary binding layers are a natural primitive in modal-ish editors.

References:
- Emacs Lisp manual, `set-transient-map`: https://www.gnu.org/software/emacs/manual/html_node/elisp/Controlling-Active-Maps.html
- Helix keymap docs / minor modes: https://docs.helix-editor.com/keymap.html
- Helix remapping / nested minor modes: https://docs.helix-editor.com/remapping.html
- Kakoune hooks docs mentioning `next-key[...]` modes: https://github.com/mawww/kakoune/blob/master/doc/pages/hooks.asciidoc

**Takeaway**: Micromax-editor should keep key dispatch centralized and make short-lived keymap layers explicit data. A tiny “one-shot keymode” mechanism gets most of the value of prefix/transient maps without dragging in a full modal architecture or a complex event parser.


## rev37 — transient maps get much more useful once users can inspect them

- Emacs `which-key` exists for a reason: once prefixes / transient maps are part of the workflow, users need a quick “what keys follow this?” reminder. The important lesson for Micromax-editor is not copying the popup UI; it is keeping **available bindings** as data that a UI can render.
- Helix’s keymap docs make minor modes very explicit (`g`, `z`, `Space`, etc.) and many of those modes are effectively “discovery menus” for grouped commands. That reinforces the value of a headless `available-bindings` surface once Micromax-editor has named keymodes.
- micro is less modal, but its command-bar docs and keybinding help still reinforce that bindings should be inspectable and user-facing.
- Kakoune’s mode/mapping story points in the same direction: mappings are data attached to contexts, so surfacing the reachable ones is natural.

References:
- which-key README / prefix discovery popup: https://github.com/justbur/emacs-which-key
- Helix keymap docs / minor modes and `Space` mode: https://docs.helix-editor.com/keymap.html
- Kakoune mapping docs: https://github.com/mawww/kakoune/blob/master/doc/pages/mapping.asciidoc
- micro command docs / command-bar binding workflows: https://github.com/zyedidia/micro/blob/master/runtime/help/commands.md

**Takeaway**: now that Micromax-editor has named + transient keymodes, the next small win is a **headless keymap discovery layer**. `showbindings` / `whichkey` are just thin renderers over portable data (`ed.available-bindings`, `ed.resolve-key`), which keeps the core honest and future UIs flexible.


## rev38 — once a keymap is discoverable, labels become part of the data model

- Kakoune’s mode docs explicitly say mapping docstrings are shown in the automatic info box. That is the cleanest statement of the idea that “human label for a binding” belongs with the mapping, not in an after-the-fact UI lookup table.
- Emacs `which-key` is not just about listing raw commands; it includes description replacement/customization features, and real user configs attach `:which-key` labels like “files”, “open file”, and “save file”. That is a strong signal that raw command names are often too noisy for discovery surfaces.
- Helix’s remapping docs keep bindings declarative and nested by mode, which reinforces that labels/descriptions can ride alongside the same binding data rather than living in a separate subsystem.
- micro is less elaborate here, but its `showkey`/command-bar story still supports the broader lesson that bindings are live, inspectable configuration — so adding a short human description is a natural extension, not a UI gimmick.

References:
- Kakoune modes docs / mapping docstrings surfaced in the info box: https://github.com/mawww/kakoune/blob/master/doc/pages/modes.asciidoc
- Emacs which-key README / description replacement support: https://github.com/justbur/emacs-which-key
- Emacs which-key issue showing `:which-key` labels in real configs: https://github.com/justbur/emacs-which-key/issues/267
- Helix remapping / minor modes as data: https://docs.helix-editor.com/remapping.html
- micro command-bar binding workflows: https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md

**Takeaway**: once Micromax-editor has keymap discovery, the next small win is letting bindings carry a **human label**. `showbindings` can keep showing exact action specs, while `whichkey` and future UIs prefer descriptions. The label should live on the binding record (with derived fallbacks) so it survives reloads, tests, and future ports.


## rev39: prefix maps as a tiny first-class helper

Fresh outside references all pointed toward the same lesson: **temporary key layers are more usable when the editor treats them as a named primitive instead of expecting every config to hand-roll them**.

- The Emacs Transient manual describes a transient prefix command as activating a transient keymap that temporarily binds suffix/infix commands. That is almost exactly the conceptual model Micromax-editor already has with one-shot keymodes.
- The `which-key` README frames its job as showing the bindings that follow an incomplete/prefix key sequence. That validates pairing prefix-mode entry with immediate discovery output instead of making the user ask separately.
- Helix’s docs present `g`, `z`, and `Space` as minor-mode style key layers, which reinforces that prefix maps should be modeled as stateful keymap data, not hidden UI behavior.

References:
- Emacs Transient manual: https://www.gnu.org/software/emacs/manual/html_mono/transient.html
- which-key README / prefix discovery popup: https://github.com/justbur/emacs-which-key
- Helix keymap docs / minor modes (`g`, `z`, `Space`): https://docs.helix-editor.com/keymap.html

**Takeaway**: Micromax-editor did not need a new “special” prefix-map subsystem. The right low-hanging-fruit move was a tiny helper (`prefixmode`, `ed.bind-prefix`) built directly on top of the existing one-shot keymode + `whichkey` discovery substrate.



## rev40: mode-local prefix helpers are the smallest useful “local leader”

Fresh references all pointed toward the same lesson: once an editor has named
keymodes and one-shot maps, the next useful thing is **nesting them locally**
without inventing a new kind of object.

- Helix’s remapping docs explicitly describe minor modes accessed by pressing a
  key, and show nested definitions like `[keys.normal.g]` and `[keys.normal.z]`.
  That is a clean model for “a binding in one mode opens another small key layer”.
- general.el’s docs describe named prefix keymaps via `:prefix-command` /
  `:prefix-map`, which reinforces the broader idea that prefix maps should be
  named data, not ad-hoc action chains.
- Kakoune’s mode docs keep emphasizing that modes are how keys are grouped and
  discovered, which supports treating a mode-local prefix as “just another binding
  in the current mode that enters a short-lived submode”.

References:
- Helix remapping / minor modes and nested bindings: https://docs.helix-editor.com/remapping.html
- general.el / named prefix keymaps: https://github.com/noctuid/general.el
- Kakoune modes / mappings as grouped discoverable behavior: https://github.com/mawww/kakoune/blob/master/doc/pages/modes.asciidoc

**Takeaway**: Micromax-editor did not need a separate “local leader” subsystem.
The right low-hanging-fruit move was a tiny mode-local helper (`bindmodeprefix`,
`ed.bind-mode-prefix`) built directly on top of the existing one-shot `prefixmode`
and keymode stack.


## rev41: fuzzy command completion should help discovery without making paths spooky

Fresh references kept pointing at the same split:

- **micro** sets the baseline expectation that `Tab` in the command prompt should complete commands and filenames.
- **Helix** leans on fuzzy matching in pickers, which is a strong reminder that named editor surfaces are often easier to *search* than to spell exactly.
- **Kakoune** keeps completion as a distinct configurable subsystem, which reinforces that completion policy should stay explicit and inspectable rather than hidden inside a UI widget.

That suggests a very small, low-risk move for Micromax-editor:

- keep exact-prefix completion as the first rule
- add fuzzy fallback only for **command-ish names** (commands, actions, options, macro/plugin subcommands)
- keep filesystem paths prefix-based until we intentionally design a fuzzy-open/file-picker surface

References:
- micro help / `Tab` autocompletes in the command prompt: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md
- micro default keys / command prompt autocomplete: https://github.com/zyedidia/micro/blob/master/runtime/help/defaultkeys.md
- Helix pickers / fuzzy matching: https://docs.helix-editor.com/pickers.html
- Helix completion menu / `Tab` and `Shift-Tab`: https://docs.helix-editor.com/keymap.html
- Kakoune prompt/completion direction: https://github.com/mawww/kakoune/blob/master/README.asciidoc

**Takeaway**: Micromax-editor did not need a heavyweight fuzzy engine or a new popup contract. The right low-hanging-fruit move was a tiny deterministic fuzzy fallback layered under the existing suggestion-session model, while keeping path completion conservative and explicit.

## rev41 (language follow-up): if Micromax grows stack-effect checking, keep it optional and tool-first

Factor’s docs remain a very good warning against over-designing this too early:

- stack-effect declarations are useful as lightweight executable documentation
- stack-effect tools can infer/report effects interactively
- stack checking catches real errors, but it is also a substantial subsystem with escape hatches and combinator-specific rules

References:
- Factor stack effect checking overview: https://docs.factorcode.org/content/article-inference.html
- Factor stack effect tools (`infer`, `stack-effect`, `effect>string`): https://docs.factorcode.org/content/article-tools.inference.html
- Factor stack effect declarations: https://docs.factorcode.org/content/article-effects.html

**Takeaway**: Micromax should likely grow any stack-effect support in this order: doc syntax first, interactive inspection next, optional dev-mode validation last. That keeps the language pleasant to script in before we commit to a full checker.

## rev42: argument completion should grow by command/slot, not by generic popup cleverness

Fresh references all pointed toward the same lesson: once a command bar exists,
**argument completion is part of the command model**, not just a UI flourish.

- Neovim’s command-line docs are explicit that completion applies to several
  categories such as command names, file names, and option names. That is a
  useful reminder that command bars become much more learnable once users can
  complete *what comes after the verb*, not only the verb itself.
- Kakoune’s `complete-command` docs go further and make completion a property of
  a command’s arguments / slots (`file`, `command`, shell-script-backed
  candidates, etc.). That reinforces Micromax-editor’s direction: keep
  completion policy attached to specific commands and argument positions.
- micro’s options help/docs keep exposing concrete option values (for example,
  enum-like settings such as clipboard backends), which is a practical reminder
  that users often need help recalling the *value vocabulary* as much as the
  command name.

References:
- Neovim command-line completion overview: https://neovim.io/doc/user/cmdline.html
- Kakoune `complete-command` / command completion configuration: https://igor-ramazanov.github.io/doc/pages/commands.html
- micro options help: https://github.com/micro-editor/micro/blob/master/runtime/help/options.md
- micro command-bar docs: https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md

**Takeaway**: Micromax-editor did not need a generic preview popup or a separate
completion engine yet. The right low-hanging-fruit move was to grow completion
*by command and argument slot*: option values, keymode names, and inspection
subjects first; richer previews/metadata later.


## rev43: keybinding prompts should complete the thing you are about to bind, not just the command that edits bindings

Fresh references pointed at the same ergonomic lesson: once an editor exposes
**keybindings as commandable data**, users should not have to memorize the whole
right-hand side grammar by hand.

- micro’s keybindings docs are explicit that bindings can target ordinary editor
  actions, *chained* actions, and micro-style `command:` / `command-edit:`
  command-bar strings. That means the thing after `bind KEY ...` is a real user
  surface, not an opaque blob.
- Neovim’s command-line completion docs are a useful reminder that completion is
  often categorized by syntactic position: command names at the start, options
  after `:set`, mappings after `:map`, etc. That supports treating Micromax
  binding specs as another slot-aware completion surface.
- Kakoune’s mapping docs reinforce that mappings are first-class, documented
  objects with modes and docstrings; mapping ergonomics are part of the editor’s
  language, not an afterthought.

That suggests a compact move for Micromax-editor:

- let `bind` / `bindmode` complete editor action names
- treat `command:` / `command-edit:` as first-class action-spec prefixes
- when those prefixes are present, reuse the ordinary **command-ish**
  command-bar completion logic for the embedded command line instead of inventing
  a second mini-parser

References:
- micro keybindings / chaining / `command:` / `command-edit:`: https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/keybindings.md
- Neovim command-line completion categories (`:set`, `:map`, etc.): https://raw.githubusercontent.com/neovim/neovim/master/runtime/doc/cmdline.txt
- Kakoune mapping docs / docstrings / modes: https://raw.githubusercontent.com/mawww/kakoune/master/doc/pages/mapping.asciidoc

**Takeaway**: Micromax-editor did not need a new “binding wizard” UI. The right
low-hanging-fruit move was to extend the existing suggestion-session model into
`bind` / `bindmode`, and to treat `command:` / `command-edit:` bindings as
embedded command lines that can reuse the completion work already done.


## New sources (rev44)

### Completion metadata and UI separation

Neovim’s completion docs are a strong precedent for separating *candidate data* from *presentation*: `complete_info()` exposes per-item fields such as `word`, `menu`, `kind`, and `info`, while command-line completion state is available separately via `cmdcomplete_info()`.

Kakoune’s command completion docs reinforce that completion should be configured around command argument structure, with menu behavior treated as an option layered on top.

References:
- Neovim builtin docs: `complete_info()` / `cmdcomplete_info()`: https://neovim.io/doc/user/builtin.html
- Neovim UI docs: popupmenu / wildmenu are UI concerns: https://neovim.io/doc/user/api-ui-events.html
- Kakoune `complete-command`: https://igor-ramazanov.github.io/doc/pages/commands.html

**Takeaway**: Micromax should keep prompt completion headless and string-driven at its core, but attach a tiny, optional metadata channel (`kind/menu/info`) so future UIs do not have to reverse-engineer what each candidate means.


## rev45: tiny combinators buy a lot of ergonomics if they stay ordinary library code

A fresh pass over primary concatenative references pointed at the same lesson:
**quotation ergonomics matter early**, but the first wins do not require a large
optimizer-aware combinator tower.

- Factor’s docs explicitly group `dip` / `2dip` and `keep` / `2keep` as
  “preserving combinators,” which is a helpful mental bucket for Micromax: hide
  some values, run a quotation, restore them.
- Factor’s `bi` and `tri` docs are also useful because they show the words as
  *definitions in terms of simpler combinators* (`keep`/`dip`), not as magical
  VM-only behavior.
- Joy’s rationale keeps reinforcing why `dip` matters in the first place: it is
  the small abstraction that lets a stack language affect values *under* the top
  of stack without dropping into endless shuffle code.
- Retro’s docs are a good reminder that a tiny practical concatenative system can
  still lean heavily on quotes and combinators without becoming huge.

References:
- Factor preserving combinators: https://docs.factorcode.org/content/article-dip-keep-combinators.html
- Factor `bi`: https://docs.factorcode.org/content/word-bi%2Ckernel.html
- Factor `tri`: https://docs.factorcode.org/content/word-tri%2Ckernel.html
- Joy rationale (`dip` discussion): https://hypercubed.github.io/joy/html/j00rat.html
- RetroForth quotes and combinators: https://retroforth.org/nga/docs/QuotesAndCombinators.md

**Takeaway**: Micromax should keep stealing the *smallest useful* combinators first,
preferably as ordinary stdlib code. `2dip`, `2keep`, `bi`, and `tri` are the right size:
they noticeably reduce stack gymnastics in editor/config/plugin scripts while keeping the
VM tiny, inspectable, and easy to port.


## rev46: stack effects should be exposed as cheap metadata before they are validated

Fresh references pointed in the same direction:

- Gforth treats stack-effect comments as baseline readability hygiene and explicitly says you should write one for every definition when possible.
- Factor goes further and exposes stack effects as a reflective/tooling surface (`stack-effect`, `effect>string`, `infer`) instead of making the syntax useful only to the compiler.
- That combination is a good fit for Micromax: store/extract effect strings, expose them to tools and future UIs, and postpone any real checker until editor/plugin code proves it is worth the weight.

References:
- Gforth stack-effect comments tutorial: https://gforth.org/manual/Stack_002dEffect-Comments-Tutorial.html
- Gforth colon definitions tutorial: https://gforth.org/manual/Colon-Definitions-Tutorial.html
- Factor stack effect declarations: https://docs.factorcode.org/content/article-effects.html
- Factor stack effect tools: https://docs.factorcode.org/content/article-tools.inference.html
- Factor `stack-effect`: https://docs.factorcode.org/content/word-stack-effect%2Ceffects.html

**Takeaway**: the right rev46 move is small reflective plumbing (`xt-effect`, row-based word metadata, cleaner `help`) rather than a checker. That improves learnability immediately and keeps the VM/tier-2 story simple.

## rev47: in-editor word inspection should feel like part of the live environment

The new VM-level metadata (`xt-effect`, `xt-doc`, `words-rows`) made one next step feel obvious: the editor command bar should be able to inspect *visible Micromax words* directly instead of forcing users to drop into the REPL or write one-off scripts.

A few outside references lined up neatly here:

- **micro** keeps a built-in command-bar help workflow centered on `Ctrl-e`, `help`, and discoverability via command prompt completion. That is a strong reminder that the editor prompt itself should be a first-class discovery surface, not merely a thin parser.
- **Gforth**’s manual includes a **Word Index** where each entry is listed with stack effect and wordset, which is a nice precedent for surfacing word metadata as rows rather than just raw text dumps.
- **Factor** goes even further with a searchable help system and `apropos`, where named words/help topics are discoverable by fuzzy-ish subsequence search and then rendered with structured metadata.

**Takeaway**: the right rev47 move is *not* a full browser or picker yet. It is smaller: let editor `help` fall back to the currently visible Micromax word, add an explicit `showword NAME`, and wire prompt completion/metadata rows to the same live dictionary. That keeps the system inspectable and headless while making the editor feel much more like Micromax’s native environment.

References:
- micro command bar / help topics / Tab discovery: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/help.md
- micro command list / command-bar parsing: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/commands.md
- Gforth Word Index (stack effect + wordset): https://gforth.org/manual/Word-Index.html
- Gforth stack-effect comments tutorial: https://gforth.org/manual/Stack_002dEffect-Comments-Tutorial.html
- Factor help vocabulary: https://docs.factorcode.org/content/vocab-help.html
- Factor `apropos`: https://docs.factorcode.org/content/word-apropos%2Chelp.apropos.html



## rev48: searchable topic rows beat a premature picker

Fresh references pointed in the same direction:

- **Factor** already has `apropos`, which searches words/vocabularies/help articles by subsequence and ranks the results with a simple distance algorithm.
- **Neovim** still leans heavily on searchable help/index surfaces such as `:helpgrep` and the command index rather than requiring one monolithic help browser first.
- **micro** keeps the command bar and built-in help system as the main discovery path, which is a reminder that Micromax should strengthen the prompt before inventing a larger UI.
- **Helix** shows that fuzzy search belongs naturally on named editor surfaces, but also that a full picker is a separate UX commitment with its own keymap and lifecycle.

Useful references:

- Factor `apropos`: https://docs.factorcode.org/content/word-apropos%2Chelp.apropos.html
- Neovim `:helpgrep` / help search: https://neovim.io/doc/user/usr_02.html
- Neovim help index: https://neovim.io/doc/user/vimindex.html
- micro command-bar help: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md
- micro prompt autocomplete note: https://github.com/zyedidia/micro/blob/master/runtime/help/defaultkeys.md
- Helix pickers: https://docs.helix-editor.com/pickers.html

**Takeaway**: the right rev48 move is still *not* a heavyweight picker. It is smaller and more composable: expose a shared topic-row model for commands/actions/words, add a tiny `apropos QUERY` command using the existing deterministic fuzzy ranking, and surface the same rows to scripts via hostcalls so future UIs/LLMs can reuse exactly the same discovery substrate.


## rev49: plugin completion should speak the same row language as built-ins

- **Neovim**'s completion/UI surface is a strong precedent for exposing completion items as structured rows rather than plain strings: `complete_info()` returns items with fields such as `word`, `menu`, `kind`, and `info`, and the UI popupmenu event uses an array form `[word, kind, menu, info]`.
- **Helix** treats pickers and completion menus as their own UI layer with separate navigation semantics, which is a good reminder that the headless core should expose *item metadata*, not commit to a specific popup implementation.
- Micromax already had exactly the right row shape on the editor side (`[insert kind menu info]`) for built-in prompt completion. The awkward gap was that plugin-provided completions could only return strings, so custom commands looked second-class in future UIs/tooling.

Sources:
- Neovim `complete_info()` / complete items: https://neovim.io/doc/user/builtin.html
- Neovim UI popupmenu items: https://neovim.io/doc/user/api-ui-events.html
- Helix pickers / completion navigation: https://docs.helix-editor.com/pickers.html and https://docs.helix-editor.com/keymap.html

**Takeaway**: the right rev49 move is not a picker yet. It is smaller and more composable: let `ed.complete.<cmd>` / `ed.complete` optionally return aligned completion rows in the same `[insert kind menu info]` shape already used by built-ins, and make the host merge/overlay those rows instead of inventing a plugin-only metadata path.


## rev50: let `apropos` search summaries/docs before building a picker

Fresh references still point to the same general lesson: **search-first help is valuable even before you commit to a picker UI**, and those searches should not be limited to exact names.

- **Neovim** keeps a strong split between direct help lookup (`:help`) and broader help search (`:helpgrep` / help indexes), which is a reminder that discovery often needs to search *descriptions*, not just tags.
- **Helix** has a command palette and fuzzy pickers, reinforcing that search-first discovery is ergonomic, but the picker itself is still a separate UX layer from the searchable data.
- **micro** keeps built-in help in the command bar, which supports the idea that Micromax should keep strengthening prompt-driven discovery rather than jumping straight to a browser UI.

Useful references:

- Neovim `:help` / `:helpgrep`: https://neovim.io/doc/user/helphelp.html and https://neovim.io/doc/user/usr_02.html
- Neovim help index: https://neovim.io/doc/user/vimindex.html
- Helix command palette / pickers: https://docs.helix-editor.com/keymap.html and https://docs.helix-editor.com/pickers.html
- micro help overview: https://github.com/zyedidia/micro

**Takeaway**: the right rev50 move is still *not* a full picker. It is smaller and more composable: keep `apropos QUERY` name-first, but let it fall back to topic summary/doc text, and make `help NAME` surface a few likely matches when exact lookup fails. That improves discovery and typo recovery immediately while preserving the same headless topic-row substrate for any future picker UI.


## rev51: a tiny topic/help prompt beats a premature browser

Fresh references still point in the same direction: **searchable pickers are useful, but the stable substrate should be item rows + prompt semantics before a heavyweight UI/browser lands.**

- **Helix** describes pickers as interactive windows with their own keymap and fuzzy filtering, which is a good reminder that a picker is a distinct UI layer rather than just “more completion.”
- **VS Code** separates the broader **Command Palette** idea (all commands are discoverable from one search surface) from **Quick Pick** item design guidance (`description` for current-item context, `detail` for extra context). That maps surprisingly well onto Micromax’s existing `[insert kind menu info]` rows.
- Micromax already had the hard part: `help_topic_rows()`, `apropos_rows()`, and prompt suggestion rows. The missing piece was a tiny *searchable prompt mode* that could reuse those rows directly instead of forcing future UIs/scripts to assemble a picker lifecycle themselves.

Sources:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- VS Code Quick Picks: https://code.visualstudio.com/api/ux-guidelines/quick-picks
- VS Code Command Palette: https://code.visualstudio.com/api/ux-guidelines/command-palette

**Takeaway**: the right rev51 move is not a full browser, command palette UI, or popup menu system. It is smaller and more composable: add a `topic` prompt kind plus `topicpick [QUERY]`, `TopicPrompt`, and `ed.topic-prompt`, preload it with ranked topic rows, let `Tab` / `Shift-Tab` cycle within that prompt, and make `Enter` open help for the selected/best-ranked topic. That gives the editor a real search-first discovery surface while preserving the same headless prompt/session contract.


## Searchable prompts / command palette lessons

A few editor/UI systems converge on the same useful separation:

- keep a **filterable item model** with lightweight metadata (`label`/`kind`/`description`/`detail`)
- let the query update the ranked item list continuously
- treat any richer preview panel as a *downstream UI concern*, not the core completion/search contract

References:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- VS Code Quick Pick UX guidelines: https://code.visualstudio.com/api/ux-guidelines/quick-picks
- Vim `completeopt` preview docs: https://vim-jp.org/vimdoc-en/options.html

**Takeaway for Micromax**: the headless core should expose stable rows + active selection state first. That gives future TUIs/LLMs enough substrate to render a command palette / topic browser / preview pane later without changing ranking or command-discovery semantics.


## rev53: grouped sections and current-item previews belong in the headless substrate

Fresh references point to a small but important next step: once Micromax already has ranked topic rows and an active selection, the next useful thing is **not** a full picker widget. It is exposing the two bits of structure downstream UIs repeatedly want:

- **coarse grouping** (commands vs actions vs words)
- a tiny **current-item preview summary**

- **VS Code Quick Pick** explicitly supports separators for “multiple obvious groups of selections”, which is a strong precedent for adding section/group surfaces before any richer UI work.
- **VS Code command/category presentation** is another reminder that grouping command-like items is part of discoverability, not just decoration.
- **Helix** keeps preview as a picker-level concern (`Ctrl-t` toggles preview), which reinforces the idea that Micromax should expose preview *data* first instead of baking in a preview widget.
- **Neovim** continues to support the same split in completion: short `menu` text, longer `info` text, and structural access to the currently selected item via `complete_info()`.

Sources:
- VS Code Quick Picks (`Using separators`): https://code.visualstudio.com/api/ux-guidelines/quick-picks
- VS Code command categories / grouping: https://code.visualstudio.com/api/references/contribution-points
- Helix pickers and preview toggle: https://docs.helix-editor.com/pickers.html and https://docs.helix-editor.com/keymap.html
- Neovim completion item fields / current selection: https://neovim.io/doc/user/insert/ and https://neovim.io/doc/user/builtin.html

**Takeaway**: the right rev53 move is to add grouped topic-section rows plus compact current-item preview helpers (`section`, `preview`, status-model fields). That makes the archive much friendlier for future TUIs/LLMs while keeping the actual UI commitment deferred.


## rev54: searchable binding discovery should reuse the same prompt/row substrate, not invent a popup contract

Fresh references point to a small but useful next step after `topicpick`: editors often need a way to **discover current keybindings** without forcing users to memorize prefix trees or commit the core to a popup UI too early.

- **which-key.nvim** states its core value very plainly: it helps users remember keymaps by showing available keybindings *as you type*. That is a strong reminder that Micromax should treat binding discovery as a first-class editor surface.
- **VS Code** keeps command discovery and keyboard-shortcut discovery as separate but related searchable surfaces: the Command Palette is the universal command finder, while the Keyboard Shortcuts editor is where bindings are inspected and searched.
- **Helix** continues to reinforce the architectural split: pickers are a real UI layer with their own keymap, so the headless core should first expose stable searchable rows + active selection semantics, not a hard-coded popup/browser.

Sources:
- which-key.nvim README: https://github.com/folke/which-key.nvim
- VS Code Keyboard Shortcuts: https://code.visualstudio.com/docs/configure/keybindings
- VS Code Command Palette: https://code.visualstudio.com/api/ux-guidelines/command-palette
- Helix pickers/keymap: https://docs.helix-editor.com/pickers.html and https://docs.helix-editor.com/keymap.html

**Takeaway**: the right rev54 move is not “build which-key as a popup.” It is smaller and more composable: add a searchable `binding` prompt (`bindingpick`, `BindingPrompt`, `ed.binding-prompt`) plus searchable current-binding rows (`ed.binding-prompt-rows`) that reuse the existing prompt/session/status substrate. That gives Micromax a `whichkey`-adjacent discovery path while keeping the renderer decision deferred.


## rev55: search prompts should handle multiple terms across names + metadata, not just one ordered string

Fresh references point to a small but meaningful refinement after `apropos`, `topicpick`, and `bindingpick`: once you have searchable rows, users very quickly expect **multiple terms** to work across both the primary label and the supporting metadata.

- **Helix** says most pickers use **fzf syntax** for filtering, which is a useful reminder that picker search is usually richer than “match one string in order.”
- **fzf** itself documents “extended-search mode” where users can type **multiple search terms delimited by spaces**. That is exactly the expectation Micromax was starting to brush up against.
- A **which-key.nvim** feature request makes the keybinding side explicit: a command-palette-style search should be able to search by both the **description** and the **keystrokes**, not just a single field.
- **VS Code Quick Picks** keep reinforcing the same architectural idea: items have a main label plus supporting description/detail text, so search/discovery surfaces naturally want to benefit from more than just the first label.

Sources:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- fzf search syntax: https://github.com/junegunn/fzf
- which-key.nvim command-palette request: https://github.com/folke/which-key.nvim/issues/978
- VS Code Quick Picks: https://code.visualstudio.com/api/ux-guidelines/quick-picks

**Takeaway**: the right rev55 move is still *not* a heavier picker UI. It is smaller and more composable: keep the existing deterministic ranking, but let `apropos`, failed `help`, `topicpick`, and `bindingpick` treat whitespace-separated terms as a tiny bag-of-words query across the row fields they already expose. That brings Micromax much closer to real command-palette / key-discovery expectations while preserving the same headless row-first design.


## rev56: a real command palette should execute actions but stage commands for arguments

Fresh references point to a very natural next step after `topicpick` and `bindingpick`: once a small editor already has searchable rows for commands/actions and a live prompt substrate, the next useful thing is a **real command palette**.

- **VS Code** is explicit that the Command Palette is where all commands are found, and that clear naming/grouping matter for discoverability.
- **VS Code** also treats commands as central editor integration points, which is a good reminder that Micromax should make command/action discovery a first-class native surface rather than only a help search trick.
- **legendary.nvim** is a nice Neovim-side precedent because it builds a legend/command-palette surface over commands, keymaps, and autocommands while still delegating the finder UI to picker plugins.
- **micro** keeps the command bar as a central interaction surface (`Ctrl-e`), which suggests that Micromax should keep the palette tightly connected to the existing command prompt instead of inventing a separate execution model.

Sources:
- VS Code Command Palette UX guidelines: https://code.visualstudio.com/api/ux-guidelines/command-palette
- VS Code command capabilities: https://code.visualstudio.com/api/extension-capabilities/common-capabilities
- legendary.nvim README: https://github.com/mrjones2014/legendary.nvim
- micro command/help docs: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md and https://github.com/zyedidia/micro/blob/master/runtime/help/commands.md

**Takeaway**: the right rev56 move is still *not* a heavyweight popup or browser. It is smaller and more composable: add a searchable command/action palette on top of the existing prompt/row/ranking substrate, let selecting an **action** execute it immediately, and let selecting a **command** open the ordinary command bar prefilled so the user can still supply arguments deliberately.


## rev57: command palettes get materially better when they remember what you actually picked

A small search-first palette already existed in Micromax by rev56, but outside precedents point to an obvious next ergonomic step: **recently used items belong near the top**.

- **GitHub** describes its command palette as showing suggestions based on current context and resources used recently, which is a good reminder that search-first surfaces become more helpful when they remember what mattered to *this* user recently.
- **Positron**'s command-palette docs are explicit: recent commands appear first, making repeated actions faster.
- **VS Code**'s Command Palette UX guidance still reinforces the complementary structural lesson: clear names and grouping matter, which argues for exposing a grouped `Recent` / `Commands` / `Actions` view in the headless substrate rather than burying recency in a UI-only layer.

References:
- GitHub Command Palette: https://docs.github.com/en/get-started/accessibility/github-command-palette
- Positron Command Palette: https://positron.posit.co/command-palette.html
- VS Code Command Palette UX guidelines: https://code.visualstudio.com/api/ux-guidelines/command-palette

**Takeaway**: the right rev57 move is still not a heavier popup. It is smaller and more composable: keep the existing row-first command palette, but add a tiny MRU of successful palette selections, rank those recents first for empty queries (and as tie-breakers for equivalent matches), and expose grouped palette sections so future TUIs/LLMs can render `Recent` explicitly instead of reverse-engineering it.

## rev59: tooling-friendly “source surfaces” + introspection-first UX

While continuing to steal editor UX ideas from micro and Emacs, it’s worth noticing a very practical
pattern across “serious” programmable editors:

- **Discovery** surfaces (help/which-key/describe) are only as good as their underlying *data models*.
- A scripting language embedded in an editor needs not just an evaluator, but a set of stable
  introspection hooks: *what is this thing*, *where did it come from*, *what does it do*, and
  *show me its source-ish definition*.

New concrete “steals”:

- micro’s upstream help topics make heavy use of *simple textual inspection* as the primary UX.
  That argues for a small, deterministic `xt-src` surface that hosts can render without a full UI.
  - https://github.com/zyedidia/micro/blob/master/runtime/help/keybindings.md
  - https://github.com/zyedidia/micro/blob/master/runtime/help/plugins.md

- Emacs’ manual emphasizes the layered nature of keymaps (global maps, major-mode local maps, and
  even more local overrides). That is a great conceptual justification for keeping micromax’s
  mode-aware keymap resolution *inspectable* rather than “just a lookup”.
  - https://www.gnu.org/software/emacs/manual/html_node/emacs/Customization.html

- zForth is a reminder that “tiny, embeddable, engineer-friendly Forth” is a real and recurrent
  niche: prioritize integration ergonomics and a small surface area over language purity.
  - https://github.com/zevv/zForth

**Takeaway**: invest in *inspection-first* primitives (spans, rows, and source-ish renderers) early;
they pay back immediately for headless tests, future TUIs, and LLM-driven workflows.


## rev98: picker UX steals from fzf + capability discipline wants an explicit sandbox knob

Two small but useful "steals" from existing tools:

- fzf explicitly supports *sticky headers* / non-selectable header lines (`--header` and `--header-lines`).
  That aligns with Micromax's picker UX direction (sticky section headers + section jumps) and suggests
  that *structured list rendering* should remain a first-class headless concept, not UI glue.

- micro users have long asked for (and built plugins around) lightweight fuzzy file/buffer search via fzf.
  That reinforces that "command palette" and "open file" flows become dramatically more useful when
  they can safely consult the filesystem.

But a safety note: capability-based design literature keeps returning to "no ambient authority" and
least-privilege. For Micromax that translates into two pragmatic rules:

1) default capabilities off,
2) when a capability is enabled, provide a way to *reduce its blast radius*.

An optional `cap.fs-root` knob (a sandbox root for fs helpers) is a small, inspectable step in that direction.

References:
- fzf advanced options (`--header`, `--header-lines`): https://github.com/junegunn/fzf/blob/master/ADVANCED.md
- micro fuzzy finder request + fzf plugin note: https://github.com/zyedidia/micro/issues/477
- capability-based security overview: https://en.wikipedia.org/wiki/Capability-based_security


## rev103: clipboard backends — micro’s OSC 52 notes + “side effects as capabilities”

Micro’s docs have a very practical perspective on clipboard behavior:

- `clipboard=terminal` is a strong default for SSH workflows, because it can *export* clipboard
  content to your local system clipboard via OSC 52.
- terminal support is uneven: some emulators support writing but not reading; some require explicit
  opt-in settings.

For Micromax, this maps cleanly onto our capability story:

- an internal clipboard is harmless and always available
- exporting to the system clipboard is a **side effect**, and scripts should not get that power
  “for free” when a privileged backend is selected

So we implement:
- best-effort OSC 52 export in the curses TUI when `clipboard=terminal`
- a dedicated `cap.clipboard-write` gate for script-originated exports

References:
- micro `copypaste` help (OSC 52 support caveats): https://github.com/zyedidia/micro/blob/master/runtime/help/copypaste.md
- micro `options` help (`clipboard` backends): https://github.com/zyedidia/micro/blob/master/runtime/help/options.md



## rev104 — bracketed paste + external clipboard

- Bracketed paste wraps pasted text in `ESC[200~ ... ESC[201~` and is enabled via `CSI ? 2004 h` (and disabled with `CSI ? 2004 l`).
- micro recommends bracketed paste when available, and otherwise temporarily enabling its `paste` option to aggregate paste key bursts.
- For external clipboard integration, micro expects tools like `xclip`/`xsel` on Linux and `pbcopy` on macOS; Windows has `clip`.

Pointers:
- https://github.com/zyedidia/micro/blob/master/runtime/help/copypaste.md
- https://cirw.in/blog/bracketed-paste
- https://stackoverflow.com/questions/749544/pipe-to-from-the-clipboard-in-a-bash-script
- https://superuser.com/questions/97762/how-to-pipe-text-from-command-line-to-the-clipboard


## rev105 — external clipboard import: micro’s Ctrl-v behavior + wl-paste no-newline

Micro’s `copypaste` help notes that its default paste binding (`Ctrl-v`) reads the
*system* clipboard via platform tools like `pbpaste` on macOS and `xclip`/`xsel`
on Linux (and syscalls on Windows).

That’s a useful “micro-esque” target for Micromax when `clipboard=external`:
- copy/cut exports to system clipboard (already done)
- paste can best-effort **import** from system clipboard (new)

On Wayland, `wl-paste` has a `-n/--no-newline` flag to avoid appending a newline
after the pasted content, which is a nice default for editor pastes.

Pointers:
- micro `copypaste` help (Ctrl-v reads system clipboard): https://github.com/zyedidia/micro/blob/master/runtime/help/copypaste.md
- wl-paste man page (`-n/--no-newline`): https://man.archlinux.org/man/wl-paste.1.en


## rev106 — scanability polish: fzf-style kind cues + markdown inline code

Two small patterns from other tools are worth stealing:

1) **fzf uses separate “text elements” for coloring** (prompt, pointer, marker, header, info, hl, etc.), which is a good mental model for our pickers: style *kinds* and *roles* rather than repainting everything. We applied this lightly in the minimal TUI by giving hint styles to action rows, file-ish rows, and link-ish rows.

2) **Inline markdown code spans** (`` `code` ``) are a common docs affordance; dimming them (without going full syntax highlighting) makes docs pages easier to scan in a terminal UI.

Pointers:
- fzf advanced doc (color elements + themes): https://github.com/junegunn/fzf/blob/master/ADVANCED.md
- fzf man page (shows `--color` element names): https://man.archlinux.org/man/fzf.1.en
- markdown inline code spans (backticks; multiple delimiters for literal backticks): https://stackoverflow.com/questions/33224686/how-to-render-triple-backticks-as-inline-code-block-in-markdown


## rev107 — picker consistency + source-aware prompts

A few adjacent tools reinforce two tiny UX rules that matter for Micromax:

1) **The same item class should keep the same picker rules across surfaces.** Helix documents pickers as a distinct interaction mode with their own navigation model, while its picker docs explicitly call out fuzzy filtering as shared picker behavior. That is a good argument for keeping our docs-link picker and combined docs navigator aligned instead of letting them drift into slightly different grouping semantics.

2) **Sticky / fixed headers are worth preserving when lists are long.** fzf’s `--header` + `--header-lines` pattern is a strong precedent for treating headers as real UI structure rather than decoration. That supports our continuing “section headers are first-class” direction in the tiny TUI.

3) **Built-in help should stay command-bar reachable and explicit.** micro’s help docs keep the path simple: open the command bar, ask for help, then drill into topics. That argues for keeping Micromax’s docs browser searchable and discoverable from commands first, not hiding it behind a heavier UI commitment.

Pointers:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- Helix picker keymap: https://docs.helix-editor.com/keymap.html
- fzf advanced usage (`--header`, `--header-lines`, reload): https://github.com/junegunn/fzf/blob/master/ADVANCED.md
- micro help overview: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md



## rev108 — palette section clarity + portability corpus

Two small lessons from adjacent tools point in a useful direction:

1) **Pickers benefit from stable structural sections, not just a flat fuzzy list.** Helix explicitly treats pickers as a dedicated interaction surface with their own navigation model, and its picker docs emphasize that filtering sits *on top of* that stable picker structure. fzf similarly treats fixed headers / header-lines as first-class list structure rather than decoration. That argues for letting Micromax path-like palette results say `Directories` / `Files` / `Open` explicitly instead of burying those roles in one generic `Open` section.

2) **Portability wants a small corpus separate from the host implementation’s full test harness.** The WebAssembly spec repo pairing a reference implementation with an official test suite is a good pattern to steal in miniature. Micromax does not need a giant conformance suite yet, but it does benefit from a tiny JSON corpus that future Rust/WASM hosts can run without depending on Python-specific pytest helpers.

Pointers:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- Helix picker keymap: https://docs.helix-editor.com/keymap.html
- fzf README/examples (`--header-lines` and structured lists): https://github.com/junegunn/fzf
- WebAssembly spec + official test suite: https://github.com/WebAssembly/spec


## rev109 — markdown fragments: small, useful, and worth making explicit

Three adjacent markdown ecosystems point to a good tiny policy for the help browser:

- Backslash escapes are still part of that practical source-view story too: CommonMark keeps them as punctuation-level source syntax, and GitHub Docs still teaches `\` as the ordinary way to ignore markdown formatting in prose. That makes tiny escaped-markdown cues a grounded Micromax follow-up: dim the visible two-character escape pair, but keep the escaped form literal and non-navigable.

1) **GitHub-style section links are the practical default.** GitHub documents a simple heading-anchor rule of thumb: lowercase, spaces become hyphens, most punctuation disappears, and duplicate headings get `-1`, `-2`, etc. That is a good best-effort default for Micromax docs because the repo already lives in a GitHub-shaped markdown world.

2) **Explicit heading ids are worth honoring even in a tiny implementation.** Python-Markdown's attr-list syntax allows headings like `### Title {#stable-id}` (or `{: #stable-id }`), which is a nice low-complexity escape hatch when docs authors want links that survive heading renames.

3) **Do not overfit to a full markdown engine yet.** Pandoc's heading-identifier story is richer than what Micromax needs today. The right move for now is to steal the common cases (auto ids + explicit ids) without importing a full parser or freezing ourselves to one renderer's complete rules.

Pointers:
- GitHub Docs, section links / heading anchor rules: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links
- Python-Markdown attr_list heading ids: https://python-markdown.github.io/extensions/attr_list/
- Pandoc auto identifiers: https://pandoc.org/demo/example33/7.2-headings-and-sections.html



## rev110 — markdown footnotes: tiny navigation beats a full parser

A few adjacent markdown ecosystems line up on the same useful common case:

1) **GitHub treats `[^1]`-style footnotes as native markdown footnotes** and styles them as linked references + linked definitions.
2) **Python-Markdown ships footnotes as a standard extension**, which is a good reminder that footnotes are common enough to be worth recognizing even when the rest of the markdown surface stays deliberately small.
3) **Pandoc's footnote syntax grows into multi-block notes**, which is useful context but more than Micromax needs today.

So the right tiny policy for Micromax is:
- recognize `[^id]` references
- recognize `[^id]: ...` definition anchors
- treat them as local navigation targets in docs/help buffers
- keep the rest out of scope until we actually need richer rendering semantics

Pointers:
- GitHub Docs footnotes/style guidance: https://docs.github.com/en/contributing/style-guide-and-content-model/style-guide#footnotes
- Python-Markdown footnotes extension: https://python-markdown.github.io/extensions/footnotes/
- Pandoc footnotes syntax: https://pandoc.org/MANUAL.html#footnotes



## rev111 — markdown tables: steal just enough structure for scanability

A few markdown sources point to the same small, practical compromise for Micromax docs buffers:

1) **GitHub documents pipe tables as a standard authoring form** using pipes and hyphens, so recognizing them in repo docs is a good fit for the markdown people will actually write here.
2) **The GFM spec makes the table shape explicit**: one header row, one delimiter row, then zero or more data rows. That is enough structure to drive tiny TUI hints without implementing a full block parser.
3) **Python-Markdown treats tables as a standard extension**, which is a useful signal that tables are common enough to be worth a small affordance even if Micromax still refuses to become a general markdown renderer.

So the rev111 move is intentionally narrow:
- detect simple pipe-table header/delimiter/body rows in the TUI
- bold the header row
- dim the delimiter row
- dim literal `|` separators for easier scanning
- keep everything local to the UI layer

Pointers:
- GitHub Docs, organizing information with tables: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables
- GFM spec, tables extension: https://github.github.com/gfm/#tables-extension
- Python-Markdown tables extension: https://python-markdown.github.io/extensions/tables/


## rev112 — markdown task lists: cheap signal, no parser debt

A few markdown sources point to the same tiny policy for Micromax docs/help buffers:

1) **GitHub treats task lists as a common authoring form** using list items that begin with `[ ]` or `[x]`, so recognizing that shape is a good fit for repo-local docs and TODO-heavy pages.
2) **GFM defines task-list items as an extension over ordinary list items**, which argues for keeping Micromax's support as a light recognition layer rather than inventing a whole new block model.
3) **Python-Markdown ships a tasklist extension**, which is a useful reminder that the form is common enough to deserve a tiny scanability affordance even in a deliberately small markdown-aware TUI.

**Takeaway**: the right rev112 move is a *UI-only task-list hint*, not interactive checkboxes or markdown AST growth. Bold the checkbox token, dim checked bodies, and keep the policy local and replaceable.

Sources:
- GitHub Docs task lists: https://docs.github.com/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
- GFM task-list items extension: https://github.github.com/gfm/
- Python-Markdown tasklist extension: https://python-markdown.github.io/extensions/tasklist/

## rev113 — markdown blockquotes: cheap scanability, tiny policy

A couple of adjacent markdown sources point to a good tiny compromise for Micromax docs/help buffers:

1) **Blockquotes are a common, high-signal form.** GitHub documents quoting text with `>` and renders quoted text with a visible left rail and subdued gray body text, which is exactly the kind of scanability hint Micromax can steal without needing a full renderer.
2) **CommonMark blockquote rules are richer than we need today.** The spec allows up to three leading spaces and even permits `>` without a following space, but that also introduces edge cases and smiley-ish false positives that are not worth chasing in a tiny TUI helper.
3) **So the right Micromax move is a readable subset.** Recognize the common `> ` / `> > ` forms, bold the quote rail, dim the body, and keep the whole thing local to the UI layer.

Sources:
- GitHub Docs, quoting text: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#quoting-text
- CommonMark spec, block quotes: https://spec.commonmark.org/current/#block-quotes



## rev117 — markdown images should not leak into tiny docs-link UX

CommonMark treats image syntax as link-like but distinct: `![desc](dest)` produces an image whose description becomes alt text, not an ordinary link label. Python-Markdown also keeps careful inline-pattern ordering because links/images/code/emphasis interact in precedence-sensitive ways. That points Micromax toward a small but important policy: until the docs browser has an image-aware rendering/navigation story, image descriptions should stay prose and should not appear as clickable help links.


## rev120 — balanced bracket labels in markdown links

- CommonMark explicitly allows matched square brackets inside link text, while code spans still bind tighter than link brackets.
- Python-Markdown exposes custom inline processors partly because nested brackets / recursive link pieces are awkward to model with regex alone.
- Micromax should keep stealing the *smallest useful parser substrate* here: a shared balanced-span scanner for docs/help navigation is worth it; a full markdown AST still is not.


## rev121 — tiny destination parsing for local docs links

- CommonMark says inline and reference link destinations apply backslash escapes in the URI/title, while bare destinations may include balanced parentheses rather than only raw regex-friendly tokens.
- The spec also makes it clear that spaces are not really part of the strict bare-destination grammar, which nudges Micromax toward a pragmatic editor-centric stance: keep strict-enough parsing, but allow a tiny local-doc convenience for backslash-escaped spaces and decode percent-encoded local paths before follow.
- Python-Markdown exposes explicit backslash-unescape helpers in its inline processing model, which reinforces the idea that unescaping belongs in the shared destination policy, not in three different UI/action surfaces.
- So the right Micromax move is still the smallest useful shared helper layer: one tiny destination parser used by `helpfollow`, `helplinkpick`, TUI underline spans, and reference-definition parsing.

Sources:
- CommonMark spec (current): https://spec.commonmark.org/current/
- Python-Markdown inlinepatterns reference: https://python-markdown.github.io/reference/markdown/inlinepatterns/


## rev123 note: setext headings as a high-leverage tiny feature

CommonMark treats setext headings as ordinary headings with up to three spaces of indentation on the underline, and Python-Markdown's Attribute Lists docs explicitly show custom ids on setext-style headings. That made single-line setext support a good Micromax-sized win: fragment jumps, outline rows, breadcrumbs, and docs-picker titles all improve together without pulling in a full block parser.


## rev124 note: raw HTML comments should stay inert by default

CommonMark treats HTML comments as raw HTML, and Python-Markdown's `md_in_html` docs make the default policy explicit: content inside raw HTML block-level elements is ignored unless you opt into markdown parsing with a `markdown` attribute / extension behavior. That made raw HTML comment precedence a good Micromax-sized follow-up to fenced code and setext headings: keep commented-out markdown examples, ref defs, and heading text literal across `helpfollow`, picker rows, outline scanning, and TUI underline spans without promising a fuller HTML parser.


## rev125 note: raw HTML tags/autolinks should beat link grouping too

Current CommonMark examples explicitly show that raw HTML tags, inline code, and autolinks bind tighter than markdown link grouping, including cases like `[foo <bar attr="](baz)">` and `[foo<http://example.com/?search=](uri)>`. GitHub Docs also states that GitHub Flavored Markdown tracks CommonMark. That made raw-HTML/autolink precedence inside would-be link labels the next Micromax-sized follow-up after comment precedence: keep fake links from appearing in help navigation/TUI underlining, but do it with one tiny shared helper rather than a fuller HTML parser.


## rev126 note: current CommonMark setext headings can span multiple lines

Current CommonMark says a setext heading consists of **one or more lines of text** followed by the underline, while GitHub Docs says their GFM stays compliant with CommonMark. That made tiny multi-line setext handling the right follow-up to rev123: the docs browser should join those paragraph lines once in the shared heading scanner so doc titles, picker summaries, outline rows, heading breadcrumbs, and fragment jumps all agree, instead of teaching each surface a slightly different regex.


## rev132 notes — wrapped angle destinations

- CommonMark's current link rules still allow inline-link pieces and reference-definition pieces to be separated by spaces/tabs and up to one line ending, while angle-bracket destinations themselves cannot contain line endings. That means a tiny docs browser can reasonably support wrapped forms like `[doc](\n  <space path.md>)` without committing to a full multiline inline parser.
- The same spec also requires whitespace between a destination and an optional title. For angle-bracket destinations, that means `<path.md>"title"` is malformed even though `<path.md> "title"` is valid. This was a good tiny shared-guard improvement because it removes one regex-shaped false positive without increasing parser ambition.

## rev133 note: nested links should prefer the inner-most valid link

Current CommonMark says links may not contain other links at any level of nesting, and when multiple otherwise valid link definitions appear nested, the inner-most definition wins. That made nested links inside labels the next good Micromax-sized follow-up after wrapped destinations/title guards: keep the docs browser's shared matcher honest about real inline precedence without growing a full inline parser.

## rev134 note: empty or whitespace-only labels should stay prose

Fresh CommonMark text adds a tiny but worthwhile shared guard for Micromax's docs browser: **link labels must contain at least one non-whitespace character**. That means malformed shapes like `[](doc.md)`, `[ ](doc.md)`, `[   ][id]`, and `[]` should stay literal prose instead of becoming invisible or blank live links.

- **CommonMark** explicitly requires a link label to contain at least one non-whitespace character. That is a good fit for Micromax's tiny docs-browser philosophy because it removes a real class of regex-shaped false positives without committing the project to a full inline parser.
- **GitHub Docs** says its GFM stays CommonMark-compliant, which makes this worth following even in a deliberately small markdown model: weird malformed labels do show up in documentation examples and tutorials.
- Micromax already had the right architecture for this: one shared docs-link matcher feeding `helpfollow`, `helplinkpick`, and TUI underlining. The missing piece was just a tiny shared `md_link_label_has_text()` guard instead of another per-surface exception.

**Takeaway**: the right rev134 move is not fuller inline parsing. It is smaller and more composable: require at least one non-whitespace character in the label body, share that rule between live-link matching and reference-definition parsing, and prove it with low-level matcher tests plus end-to-end picker/TUI coverage so malformed blank-label examples stay prose everywhere.


## rev135 — grouped navigation pickers should expose the same structure headlessly

A couple of picker references point to a small but useful follow-up after command palette/topic grouping: **navigation pickers also benefit from explicit section structure** when the groups are obvious.

1) **VS Code Quick Picks** explicitly recommends separators when a picker contains multiple obvious groups of selections. That is a good fit for marks and jumplist rows: marks naturally cluster by owning buffer, and a jumplist naturally clusters around the current entry vs back/forward history.
2) **Helix** keeps pickers as their own interaction surface with dedicated navigation behavior, which reinforces that grouping should be part of the shared picker substrate, not something invented only in one TUI renderer.
3) So the right Micromax move is still the small shared one: add grouped section helpers (`ed.mark-section-rows`, `ed.jump-section-rows`) and reuse the same labels for TUI headers, section-jump navigation, and prompt preview/status surfaces.

Sources:
- VS Code Quick Picks (`Using separators`): https://code.visualstudio.com/api/ux-guidelines/quick-picks
- Helix pickers: https://docs.helix-editor.com/pickers.html

## rev136 — grouped pickers need headless parity, not just TUI separators

A small but useful follow-up from the rev135 picker work: **if a picker visibly has sections, future UIs/scripts should not have to reverse-engineer those sections from row text**.

1) **VS Code Quick Picks** explicitly recommends separators when a quick pick contains multiple obvious groups. That is a good fit not just for the minimal TUI, but for the *row model itself*: if the groups are obvious enough to render, they are obvious enough to expose headlessly.
2) **Helix** treats pickers as their own navigable surface, which reinforces that grouping/preview context belongs in the shared picker substrate, not only in a renderer.
3) The practical Micromax follow-up is small: add grouped section-row hostcalls for the remaining grouped pickers (`ed.buffer-section-rows`, `ed.plugin-section-rows`) and make `prompt_current_section` / `prompt_current_preview` reuse those same labels for grouped picker kinds like recent/buffer/plugin, rather than drifting into generic fallback nouns like `Buffer` or `Word`.

Sources:
- VS Code Quick Picks (`Using separators`): https://code.visualstudio.com/api/ux-guidelines/quick-picks
- Helix pickers: https://docs.helix-editor.com/pickers.html



## rev137 — binding pickers should inherit the same grouping contract as other pickers

Fresh references still point in the same direction as the recent picker work:

- VS Code's Quick Pick guidance says separators are appropriate when there are multiple obvious groups of selections.
- Helix's picker docs keep reinforcing that pickers are their own navigable surface with their own keymap, not just a filtered list dumped into one flat bucket.

**Takeaway**: once Micromax already had grouped sections for buffers, plugins, marks, and jumps, leaving `bindingpick` flat was becoming accidental inconsistency rather than principled minimalism. The small shared move is to group current-binding rows by their *winning mode* (`Prompt`, active mode names like `nav`, `Global`), expose that grouping headlessly (`ed.binding-section-rows`), and make `prompt_current_section` / preview / status reuse the same labels instead of inventing a generic `Binding` bucket.


## rev138 — numbered docs families are an obvious picker grouping

- VS Code Quick Pick guidance explicitly recommends separators when a picker contains multiple obvious groups.
- Helix continues to treat pickers as their own navigable surface with dedicated picker keymaps.
- Micromax's docs tree is already intentionally numbered into coarse families (`00-*`, `10-*`, `20-*`, ...), so leaving `helppick` flat was accidental inconsistency rather than principled minimalism.

**Takeaway**: the small shared move is to expose docs-family grouping headlessly (`ed.doc-section-rows`) and make TUI headers, `Alt-Up` / `Alt-Down`, `prompt_current_section`, and `prompt_current_preview` all reuse the same numbered family labels instead of a generic `Docs` bucket. Because docs rows already carry both a slug topic and a human title, the preview can also become more readable by leading with the title rather than the slug.


## 2026-03-08 — recent-file pickers should reuse the same grouping policy everywhere

VS Code's Quick Pick guidance keeps reinforcing the same small lesson: separators are worth using when a picker has multiple obvious groups, and Helix keeps treating pickers as a first-class navigable surface rather than a throwaway dropdown. The Micromax-shaped takeaway is that once recent files already had grouped headless rows (`ed.recent-section-rows` / `ed.recent-dir-section-rows`), leaving the live `recentpick` prompt flat was needless drift.

So the small shared move is: reuse one recent-files section helper for prompt rows, TUI headers/sticky headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces; keep the grouping project-root-first by default; and make the row detail more scan-friendly by showing `project-name` + project-relative path when a root is known.


## 2026-03-08 — grouped pickers also need a shared answer to “where am I?”

VS Code keeps treating Quick Pick separators as navigable structure rather than passive decoration — the guidance recommends separators for obvious groups, and the product itself now has separator navigation keybindings. Helix keeps reinforcing the same broader lesson by treating pickers as their own navigable surface with a dedicated picker keymap, while GitHub frames its command palette as a context-sensitive search surface for resources you have used recently.

The Micromax-shaped takeaway is that once pickers have real sections and recency/context bias, they also need one shared notion of current position. So the next small shared move is not another bespoke row format: it is one compact current-item position model (`index/count`, current section label, section-local `i/n`, summary string) reused by headless status surfaces, hostcalls, tests, and the live TUI prompt line.


## rev141 — topic picker should browse by visible section, not just expose section labels headlessly

A small but repeatable lesson from the recent picker work: once a picker has real section labels, the live prompt should usually reuse them too instead of keeping a flat row stream that only *headless* surfaces can group. VS Code Quick Pick keeps treating separators as real structure for obvious groups, Helix keeps treating pickers as their own navigable surface, and GitHub keeps emphasizing command-palette context/recentness. For Micromax, that argues for another shared-substrate move: `topicpick` should browse as `Commands` / `Actions` / `Words` in the live prompt, not only in `ed.topic-section-rows`.

One extra wrinkle showed up in practice: empty `topicpick` had enough commands to fill the entire 40-row window before actions/words appeared, which meant the picker technically had sections but users could not reach them without changing the row budget first. The small fix was to keep sections contiguous while budgeting the initial empty-query browse window across visible sections, so the first page acts like a scan-friendly overview instead of a command-only wall.

- rev142 note: the same external lesson from VS Code Quick Pick separators and Helix picker navigation kept applying: once a picker has obvious sections, the live prompt should usually expose them too instead of leaving grouping as a hostcall-only artifact. That pushed `commandpick` to flatten `Recent Files` / `Recent` / `Commands` / `Actions` live, with a tiny browse budget so empty-query browsing surfaces more than just commands.


## rev143 notes — grouped picker windowing parity

- VS Code Quick Pick guidance still explicitly recommends separators for lists with multiple obvious groups, which continues to justify Micromax treating section labels as real navigational structure rather than decoration.
- The concrete repo lesson from rev135–rev142 was that grouped headless rows are not enough on their own: if the live browse window still takes the first N flat rows, a large first section can hide every later section until the user starts filtering.
- So rev143 generalizes the tiny round-robin browse budget that already worked well for `topicpick` and `commandpick` to the rest of the section-aware pickers (`bindingpick`, `bufferpick`, `markpick`, `jumppick`, `pluginpick`, `recentpick`, `helppick`). The main idea is still shared-substrate-first: one windowing helper, reused by live prompts, TUI headers, section jumps, preview/status, and the existing headless section-row APIs.


## rev144 notes — docs-focused pickers also need grouped browse-window parity

- VS Code Quick Pick guidance still points the same way: separators are for multiple obvious groups, which is only useful if the initial browse window does not let one large first group hide every later one.
- Helix still treats pickers as a first-class navigable surface, which argues for reusing the same tiny browse-window policy across the docs-focused pickers instead of leaving `helplinkpick` / `helpnavpick` as flat exceptions.
- So rev144 extends the shared grouped-window helper to the remaining docs-focused live prompts: `helplinkpick` now keeps `Docs` / `Files` / `External` visible on empty browse, and `helpnavpick` keeps `Headings` plus later link groups visible too. The small rule is still the same one from rev143: borrow at least one row from each visible group before handing the rest of the budget back to the earlier groups.


## rev146 — picker windowing should be shared structure, not TUI-only math

- VS Code's Quick Pick guidance still treats separators as real structure for obvious groups, which continues to justify Micromax treating grouped picker sections as more than decorative labels.
- Helix still documents pickers as their own navigable surface with dedicated picker keybindings, which pushes Micromax toward shared picker state instead of renderer-private behavior.
- GitHub still frames its command palette as a context/recentness-driven suggestion surface, which fits the same general lesson: the visible picker window is real user-facing state, not an internal implementation detail.
- So the next Micromax-sized move is small but useful: expose the minimal TUI's existing scroll-window/sticky-header/more-marker math through one shared helper (`prompt_window_model`) and a headless hostcall (`ed.prompt-window`) so future UIs/scripts/LLMs can inspect the same visible slice without re-deriving it from raw suggestion rows.
## rev151 — fenced markdown examples should also look code-ish in the live docs TUI

A couple of adjacent markdown sources point to the same small, practical follow-up for Micromax docs/help buffers:

1) **CommonMark keeps fenced code blocks intentionally regular.** A fenced block begins with a run of backticks or tildes, indented no more than three spaces, and the closing fence follows the same marker family. That regularity makes fenced examples a good candidate for one tiny shared line-role helper instead of a TUI-local parser.
2) **GitHub treats fenced code blocks as ordinary authoring practice.** Repo docs, READMEs, and tutorials are full of triple-backtick examples, so once Micromax already keeps fenced blocks inert for docs navigation, the next tiny win is letting them *look* visibly code-ish too.

**Takeaway**: the right rev151 move is still *not* syntax highlighting or a markdown AST. It is a tiny shared fence-role helper that the live TUI can reuse so opening/closing fence lines read like delimiters and fenced body lines read like code, while staying aligned with the existing docs-browser fence precedence.



## rev152 — blank-separated indented code examples should stay code-ish across docs surfaces

A couple of current markdown references point to the same tiny follow-up for Micromax docs/help buffers:

1) **CommonMark keeps indented code blocks simple at the top level.** An indented chunk is one or more non-blank lines indented four or more spaces, with blank lines allowed inside the block. Micromax does not need the whole list-aware block parser to learn from that shape; the useful part for repo docs is the ordinary blank-separated top-level example.
2) **GitHub still teaches indented code as a normal Markdown authoring form.** GitHub's docs still show four-space-indented code in Markdown source, so once Micromax already keeps some four-space lookalikes inert for definitions/headings, the next visible drift is ordinary inline links/autolinks on those code-ish lines still looking/live like prose.

**Takeaway**: the right rev152 move is still shared-substrate-first and intentionally small: add one tiny shared `md_indented_code_line_flags()` helper for blank-separated top-level indented code-ish runs, reuse it for `helpfollow`, `helplinkpick`, and TUI link-underlining precedence, and dim those lines in the live docs buffer so source-view examples read more like code without pretending Micromax has a full markdown block AST.


## rev154 — source-view definitions should look like definitions too

- CommonMark's current spec says a link reference definition can span the starter line plus up to one following line ending after the colon and after the destination, which matches the tiny wrapped destination/title support Micromax already had in navigation.
- GitHub Docs also explicitly shows Markdown footnotes with definition starter lines and multi-line note bodies, which reinforces the source-view lesson: definitions are real author-facing structure, not just hidden parser fuel.
- For Micromax this points to a small render-parity move, not a full block parser: reuse the existing tiny definition logic, expose per-line definition roles, dim those lines in the live docs/help TUI, and bold just the visible `[id]:` / `[^id]:` marker token so source-view docs read a little more honestly.


## 2026-03-08 — Nested list scanability in source view

1) **GitHub’s current Markdown docs still teach visually nested lists and task lists as normal authoring patterns.**
   - Their examples use deeper indentation under ordinary list markers, not a separate block form.
   - That makes Micromax’s source-view docs browser more honest if nested list/task markers keep reading like list markers instead of flattening back into plain prose.

2) **CommonMark’s list-item discussion still distinguishes nested list structure from true code blocks.**
   - Top-level indented code remains a separate four-space/tab concept.
   - Content under a list item can itself be indented, and code under a list item needs *more* indentation again.
   - So a tiny renderer can safely relax marker styling for deeper indentation *after* a separate indented-code pass has already ruled out top-level code blocks.

3) **Micromax-sized implication:** keep the default line helper conservative, but let the live docs/help TUI opt into deeper-indent list/task marker styling only in already-non-code contexts.
   - This improves real repo docs (`docs/43-worklist.md`, prompt-completion docs, README-ish worklists) without promising a full markdown list layout engine.


## rev160 — inline raw HTML tags deserve a tiny inert-source cue too

- CommonMark's current spec treats raw HTML tags inside a paragraph as inline raw HTML rather than ordinary text, which is the practical reason literal `<kbd>` / `<ins>` / `<a ...>` examples in Micromax docs should not read exactly like prose in source view.
- GitHub's current Markdown docs still teach inline HTML forms such as `<sub>`, `<sup>`, and `<ins>`, and they also rely on custom HTML anchors and supported HTML elements in ordinary markdown authoring, so literal raw-HTML tags are part of the docs authors are actually likely to paste into Micromax.
- Micromax already uses the shared inline raw-HTML/autolink span helper for docs-link precedence, so the next honest follow-up is render parity: dim visible raw-HTML tag tokens in source view while keeping supported autolinks on their separate bold whole-token path.
- For Micromax this argues for one **tiny UI helper** layered on the existing shared inline raw-HTML span helper: make visible tag tokens read a little more like deliberately inert source, and still stop well short of promising a fuller HTML renderer.

## rev165 — multi-line footnote bodies should look like footnote bodies too

- GitHub's current Markdown docs still present footnotes as ordinary author-facing source syntax and explicitly show that a footnote can have multiple lines, which means multi-line footnotes are not a niche edge case for docs authors.
- Python-Markdown's footnotes implementation still treats indented continuation handling as part of the footnote block model (`detectTabbed` / `detab`), which is a useful reminder that continuation lines are part of the visible source structure, not just hidden parser state.
- Micromax already gave `[^id]:` starter lines a dim+bold definition cue in rev154, so the next honest follow-up is small render parity: let tiny indented continuation lines under those starters render dim too through the same shared definition-line helper, without changing navigation or promising a fuller block parser.
## rev166 — the portability corpus should cover the language people actually script, not just the kernel postcard

- The WebAssembly spec repository explicitly ships the specification, a reference implementation, and an official test suite. That is a good reminder that a language meant to survive new hosts needs a small replayable conformance story, not just one implementation's unit tests.
- Factor's combinator docs still treat `bi` / `tri`-style quotation combinators as ordinary, central vocabulary rather than exotic extras. That is a useful signal for Micromax too: if the language wants concatenative ergonomics to feel real, future hosts should validate more than arithmetic and one happy-path quotation call.
- So rev166 keeps the Micromax portability corpus tiny but less toy-like by adding data-only cases for `dip`, `2keep`, `tri`, `try?`, `try`, `ensure`, and budget exhaustion under `catch`. The important design choice is still scope control: portable language behavior yes, host/editor integration no.


## rev173 — shared search-position summaries are a good tiny follow-up to `hlsearch`

Vim/Neovim's search UX does two small but useful things at once: `hlsearch` keeps
matches visible, and the editor can also surface a compact current/total search
count like `[1/5]` without forcing every UI to invent its own counting rules.
That is a good Micromax-sized follow-up after rev172's renderer-local
highlighting pass.

The practical lesson for Micromax is **model first, cue second**:

- keep counting semantics in one shared editor/search helper
- expose the result through the existing status model so future UIs/LLMs/scripts
  can inspect it without scraping the live TUI
- let the minimal curses TUI merely reuse the shared `summary` string in the
  active find prompt instead of growing a separate search widget

That preserves the project's headless-first discipline while still making the
live search loop feel more informative.


## rev174 — search counts belong in the statusline as a shared token, not a TUI special case

- micro's current options help still treats `hlsearch` / `incsearch` as small editor options rather than a separate search UI, which is a good reminder that Micromax should keep search cues composable and lightweight.
- Neovim's help for `searchcount()` explicitly shows adding a compact `[current/total]` search count to the statusline, and even shows gating it on active `hlsearch`. That is a strong precedent for a statusline-friendly search-count token instead of another renderer-only special case.
- The Micromax-sized move is therefore: keep the counting logic in the existing shared search-position model, add one tiny statusformat token that renders ` [i/n]` when available, and let the default statusline adopt it so ordinary editing surfaces benefit too.
- A second tiny follow-up on the portability side is to pin down the missing-word `find` contract (`xt|0`) in the JSON corpus, because that is exactly the sort of dictionary behavior a future host should validate mechanically rather than infer from Python code.

## rev175 — scroll windowing belongs in the shared viewport contract, not just the TUI

- Micro's current options docs still expose `scrollmargin` as a small ordinary editor option and describe it as the margin at which the view starts scrolling. That is a good reminder that cursor context is part of the editor's movement feel, not just renderer garnish.
- Neovim's current tips docs still recommend a larger `scrolloff` when you want to always keep some context around the cursor, and explicitly note that values above half the window height push the cursor toward the middle. That is a useful implementation hint for Micromax too: keep the idea, but clamp it sanely in tiny windows instead of inventing contradictory rules.
- The Micromax-sized move is therefore: add one tiny `scrollmargin` option to the shared viewport logic, make it vertical-only for now, measure it in visual rows under softwrap, and cap it at half the viewport height so headless tests, the current curses TUI, and future frontends all inherit the same calm scrolling rule.

## rev175 — one more portability case for tier-2-adjacent dictionary truth

- The portability ledger still treats `compile` / `compiled?` as optional but portable tooling, which means future hosts should validate at least a couple of tiny truths about those words instead of inferring them from Python code.
- Micromax already had the positive corpus case (`compile` produces compiled code), so the smallest next completion is the obvious negative twin: primitive XTs should still report `compiled? = 0`.
- That keeps the JSON corpus data-only and tiny, while helping future Rust/WASM bring-up avoid a surprisingly common category of confusion: “is this word callable” versus “does this XT carry tier-2 bytecode?”

## rev176 — current-row highlighting should stay tiny and renderer-local

- micro's current options help still treats `cursorline` as a small display toggle: highlight the line that the cursor is on, with the actual color coming from the colorscheme. That is a good reminder that Micromax does not need a deeper editor-state model just to make the active row easier to spot.
- Neovim's docs draw a useful distinction between `cursorline` and `cursorlineopt=screenline`: once softwrap enters the picture, editors may reasonably choose between whole logical lines and the active screen row.
- For Micromax, the smallest honest move is renderer-local: add one `cursorline` option, underline the current visible row in the curses TUI, and make the wrapped-row policy explicit instead of pretending the headless core already owns a richer highlight span model.


## Overflow-marker / wrapped-line notes (rev183)

- Neovim/Vim docs still distinguish ordinary wrapping from explicit continuation cues: `showbreak` adds a visible string at the start of wrapped screen lines, and the intro docs still use `@` / `@@@` to signal truncated last-line display. That is a useful reminder that small overflow signals belong in the renderer before they belong in the editor core.
- GNU Emacs docs also note that Visual Line mode suppresses wrap fringe indicators by default because a cue on every wrapped line becomes visually distracting. That is good prior art for Micromax keeping overflow markers for **horizontally clipped** rows only and intentionally suppressing them under `softwrap`.


## rev184 — buffer position belongs with search position and prompt position as a tiny shared summary

- micro's current options help still treats the statusline as a small composable template surface rather than a heavyweight widget system. That is a good reminder that Micromax should prefer another small reusable status primitive over jumping straight to a tab bar.
- Neovim's statusline ecosystem and docs keep reinforcing the same broad lesson: current/total summaries are useful because they are compact and composable, whether the thing being counted is quickfix items, search hits, or buffers.
- For Micromax the small honest move is therefore: expose `buffer_index` / `buffer_count` / `buffer_summary` in the shared status model, add one tiny `$(bufpos)` token that renders ` [i/n]` only when it adds information, and keep buffer ordering deterministic by reusing `buffer_names()` instead of MRU state.


## rev186 — trailing-whitespace cleanup should live in the shared save path, not in the TUI

- micro's current options docs still describe `rmtrailingws` as a save-time behavior: trailing whitespace at ends of lines is automatically trimmed on save. That is a strong hint that Micromax should treat this as editor behavior rather than as another renderer-only cue.
- Micromax already had the complementary visual cue via `hltrailingws`, but that only helps you *notice* junk. The smallest honest next step is to let the shared save path clean it up for every frontend and hostcall, instead of burying cleanup inside curses-only code.
- The first-pass scope should stay intentionally small: trim only spaces/tabs at end of lines, only during manual save, keep the in-memory buffer synchronized with what hit disk, and record an undoable snapshot instead of inventing a separate strip command first.
- On the portability side, Forth's search-order text explicitly says each word list is searched from its last definition to its first. That makes same-wordlist redefinition precedence a good JSON corpus case instead of a fact hidden in Python-only tests.


## rev187 — final-newline normalization belongs in the same honest save path as `rmtrailingws`

- micro's current options docs still describe `eofnewline` as a save-time behavior: add a newline to the end of the file if one does not exist. That is a strong hint that Micromax should treat this as shared editor behavior rather than another renderer-only cue.
- Micromax already had the key substrate after rev186: save-time normalization in the shared editor core, undoable hidden cleanup, and a buffer model that already preserves terminal newlines when present by keeping a trailing empty line.
- The smallest honest next step is therefore to reuse that same save normalization path: if save is manual, the buffer is non-empty, and the text is not newline-terminated, append exactly one final `\n` before writing.
- Keeping the default conservative (`false`) avoids silently changing every save in existing repos, while still giving future frontends and config files one small shared policy knob.
- On the portability side, the matching low-risk namespace follow-up is to pin down one more `definitions` truth from the Forth standard: once `definitions` chooses the compilation wordlist from the top of the search order, later `set-order` calls should not silently retarget it.


## rev199 — `encoding` should be a shared open/save contract, not a fake status token

- micro's current options docs still expose `encoding` as an ordinary buffer option alongside `fileformat`, which is a good reminder that text decoding/encoding policy belongs in the editor core rather than in ad hoc file-open helpers or statusline placeholders.
- Python's codec registry also reinforces a useful implementation split for Micromax: keep the *configured spelling* user-facing (`latin-1`, `cp1252`, etc.), but normalize only at the actual encode/decode boundary so aliases still work without forcing the status/config surface to rewrite what the user typed.
- The Micromax-sized move is therefore: add one tiny `encoding` option, thread it through `open_file(...)`, `new_buffer(...)`, `save()`, and `status_model()`, and keep docs/help buffers on their existing explicit UTF-8 path rather than pretending every project doc or host file should share one policy.



## rev202 — `fastdirty` should be an explicit shared dirty-state policy

- micro's current options docs still expose `fastdirty` as the switch between a cheap modified flag and a more accurate content-based check, which is a good reminder that “is this buffer modified?” is editor-core behavior, not just statusline decoration.
- Micromax had quietly been acting like `fastdirty=true` all the time: one edit set `dirty`, and only save/open cleared it again, even if undo or later edits returned the text to the clean state.
- The Micromax-sized move is therefore: add one tiny `fastdirty` option, keep a clean baseline in the shared buffer model, let the default path recompute `dirty` against that baseline, and let `fastdirty=true` opt back into the cheaper sticky-bit rule.
- That keeps `quit`, `autosave`, statusline `$(modified)`, and future UIs/scripts aligned without inventing a separate “modified hash service” or background worker.


## rev210 — capture state belongs in the shared status model

- micro's current options docs still treat bottom-bar surfaces like `infobar`, `statusline`, and `keymenu` as small ordinary editor affordances rather than a heavyweight widget system, which reinforces Micromax's recent pattern of making bottom chrome honest through small shared contracts first.
- GNU nano's current manual still treats the prompt bar and the two-line key menu as first-class interaction surfaces, which is a good reminder that confirm/replace/open loops should describe themselves explicitly instead of pretending the editor is idle.
- The Forth standard's exception material keeps emphasizing that `CATCH` / `THROW` restore saved stack depths, and the rationale notes that the post-`THROW` stack depth returns to the depth from just before `CATCH` began execution. For Micromax, that made one more tiny JSON portability case around successful `catch` + visible `rdepth` a sensible follow-up to rev209's return-stack leak fix.

Sources:
- micro options: https://github.com/zyedidia/micro/blob/master/runtime/help/options.md
- GNU nano manual / nanorc options: https://www.nano-editor.org/dist/latest/nano.html and https://www.nano-editor.org/dist/latest/nanorc.5.html
- Forth exception set / rationale: https://forth-standard.org/standard/exception and https://forth-standard.org/standard/rationale


- GNU nano's current manual still treats the prompt bar and help lines as first-class but simple terminal regions, not a heavyweight widget system. That keeps reinforcing Micromax's current strategy: move small prompt/keymenu/status truths into shared editor-side models first, and keep the curses renderer thin.


## rev217 — visible edit-window state should be inspectable too

- GNU nano's current manual still describes the screen as a few simple regions — title bar, edit window, status bar, and help lines — which is a good reminder that Micromax can keep moving real UI truth into small inspectable models without inventing a widget tree.
- micro's current options docs still frame `statusline`, `infobar`, and related chrome as ordinary editor options, not as special renderer-owned objects. That keeps pointing Micromax toward small shared snapshots first, renderer cleverness second.
- After rev212–rev216 moved bottom rows and layout into shared editor-side models, the remaining renderer-private truth was the edit window itself: which buffer fragments are visible, where wrapped continuations begin, and where the primary cursor lands on screen. The Micromax-sized move is therefore one more tiny shared `edit_window_model(lines, cols)` surface that future UIs/tests/LLMs can inspect directly.
- On the portability side, the next low-risk exception follow-up is still the same family of truth the Forth standard emphasizes: successful and failing `CATCH` / `THROW` should restore saved stack state cleanly, even when nesting is involved.


## rev218 note

- GNU nano still describes the screen as a few simple regions (title/edit/status/help), which keeps reinforcing Micromax's current direction: keep the renderer thin and move inspectable screen truth into small editor-side models rather than richer widgets.
- micro's current options docs still treat bottom chrome like `statusline`, `infobar`, and `keymenu` as ordinary options, which supports the recent run of tiny shared row/layout models rather than a new UI subsystem.
- The Forth exception wording still treats `THROW` in terms of restoring saved stack state, so continuing to pin down nested return-stack preservation with data-only portability cases remains worthwhile.

## rev225 — final visible row text should be inspectable too

- micro's current options docs still present `showchars`, `colorcolumn`, `cursorline`, and related display toggles as ordinary editor options rather than a separate widget or theme system. That keeps reinforcing Micromax's recent strategy: move tiny visible truth into inspectable editor-side contracts before inventing richer renderer abstractions.
- GNU nano's current manual still describes the interface as a few plain terminal regions and exposes modest view aids like a scrollbar/indicator and visible whitespace options, which is a good reminder that the first shared contract can stay text-first instead of turning into a cell-grid paint API.
- The Micromax-sized move is therefore: keep `screen_rows_model(...)` as the plain pre-overlay screen truth, add one tiny painted-text sibling `display_rows_model(...)` for the final row text after small text-changing cues (`showchars`, overflow markers), and leave styling-only cues such as search highlighting or markdown emphasis in renderer attributes for now.
- While touching that surface, the shared gutter/scrollbar model also surfaced one small honest bug worth fixing: plain scrolling was reading the wrong viewport-start key for thumb placement, so the shared scrollbar thumb could drift upward by one row even before rev225's new display-row model existed.


## rev226 — visible terminal-editor cues still want to stay small, but inspectable

- micro's current options docs still present `cursorline`, `matchbrace`, `colorcolumn`, `showchars`, and `hltaberrors` as ordinary editor display toggles rather than as a larger widget or theme subsystem. That keeps reinforcing Micromax's recent direction: move tiny visible truth into inspectable shared models before inventing richer renderer abstractions.
- GNU nano's current manual still presents related cues in the same small, option-shaped spirit: a guiding stripe (`stripecolor`), a search spotlight (`spotlightcolor`), a scrollbar indicator (`scrollercolor`), and visible whitespace characters (`set whitespace`). That is a good reminder that terminal editors often treat these as lightweight viewport aids, not a reason to grow a full paint engine.
- After rev223–rev225 exposed visible search spans, showchars replacements, and final painted row text, the remaining awkward gap was the non-text overlay math still buried in `_render`: current-row cue, trailing whitespace, tab errors, colorcolumn, and brace-pair spans. The Micromax-sized follow-up is therefore one tiny shared `viewport_cues_model(lines, cols)` snapshot, still span-first and attribute-agnostic, so future UIs/tests/LLMs can inspect the same overlays the reference curses TUI paints without scraping curses output or replaying row-local cue logic.


## rev251 — standard pair-return-stack helpers are useful, but standard Forth warns about a real source-definition trap

- The current Gforth manual still lists `2rdrop` right next to `rdrop`, `2>r`, `2r>`, and `2r@` in its return-stack vocabulary.
- That is a useful small extension to learn from even though it is not a core standard word: it matches Micromax's recent pair-return-stack helpers and is easy to keep source-visible instead of primitive.
- A tiny replayable `2rdrop` contract is valuable for future hand ports because return-stack cleanup mistakes tend to surface late unless they are pinned down directly.

- The current Forth standard still defines `2>R`, `2R>`, and `2R@` as ordinary standard return-stack pair helpers.
- The current `2>R` page also now carries a useful caution: a naive source definition like `SWAP >R >R` can be tricky on systems where return-stack words interact with compile-time nest-sys handling, so reference implementations often need immediacy or environment assumptions.
- That is a good lesson for Micromax rather than a reason to avoid the feature: Micromax's simpler execution model does not share that exact compile-time trap, so source-visible `2>r` / `2r>` / `2r@` helpers are still the honest small move here.
- The portability follow-up is equally worthwhile: future Rust/WASM hosts should not have to infer pair-return-stack ordering/peek behavior from `core.mx` alone.


## rev257 — cleanup/rethrow contracts belong in the portable corpus too

- Current Factor docs still separate `recover` and `cleanup`, and the current pitfalls guide explicitly says cleanup-style code is the right tool when work must run and the original error should still escape.
- That maps well to Micromax's `ensure` / `finally` helpers: the cleanup quotation can intentionally mutate the visible stack and the original failure should still be the one that propagates.
- The portability implication is small but useful: a JSON corpus limited to “success stack *or* error substring” cannot express that contract honestly. Allowing expected-error cases to also pin down the post-error stack is therefore a worthwhile runner evolution, not just test churn.

Sources:
- Factor exception handling: https://docs.factorcode.org/content/article-errors.html
- Factor error-handling pitfalls: https://docs.factorcode.org/content/article-errors-anti-examples.html
