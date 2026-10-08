Rev503 note: project-grouped `recentpick` rows now preserve menu-side MRU/state cues too, so the project-label rewrite keeps `#N`, flags, and `@ line:col` instead of discarding them.

Rev502 note: dedicated `recentpick` / `recentdirpick` rows now reuse exact recent-file state/truth too, so first-class recent-file prompts keep the same tiny `existing file` / `new file` plus `current buffer` / `switch buffer` cues already trusted by adjacent `showrecent` and palette `Recent Files` rows.

Rev500 note: command-palette `Recent Files` rows now also keep explicit capability-gated `existing file` truth for saved targets, so ordinary MRU rows stop being the one remaining class that says neither `existing file` nor `new file`.

# Editor command bar (micro-inspired)

Micromax-editor borrows micro’s “command bar” idea:

- opened by `Ctrl-e`
- single-line prompt
- arguments parsed with shell-like quoting (`'...'`, `"..."`, backslash escaping)

Micro’s docs state the command bar parser uses the same rules `/bin/sh` would use
for parsing arguments, and lists built-in commands like `help`, `bind`, `save`,
`quit`, `set`, `toggle`, `show`, `reload`, etc. We also add a small `macro` command for recording/playing named macros, tiny `undo` / `redo` mirrors so edit recovery is reachable from the same prompt with the same honest feedback as key-driven actions, `showcmd` / `showaction` / `showoption` / `showoptiongroups` / `showbuffer` / `showbuffergroups` / `showrecent` / `showrecentgroups` / `showrecentdirgroups` / `showmark` / `showmarkgroups` / `showjump` / `showpalettegroups` / `showword` / `showdoc` / `showtopic` / `showtopics` / `showdocs` / `showhelpheading` / `showhelplink` / `showhelpnav` / `showhook` / `showhooks` inspection commands so command/action/word/help/docs/hook/palette/jumplist metadata is visible from the same prompt, `apropos QUERY` so commands/actions/words can be searched without already knowing the exact topic name, `topicpick [QUERY]` as a dedicated searchable topic/help prompt, and `bindingpick [QUERY]` as a dedicated searchable prompt over the *currently reachable* keymap. We also add `bufferpick [QUERY]` and `markpick [QUERY]` so navigation targets (buffers and marks) can be searched and selected without a UI.

In micromax-editor (rev60):

- prompt model: `micromax_editor.commandbar.Prompt`
- parsing: `micromax_editor.cmdline.parse_cmdline` (Python `shlex.split`)
- dispatch: `micromax_editor.command_dispatcher.CommandDispatcher`

We also implemented micro-like `replace` / `replaceall` commands (regex by
default; `-l` for literal), which exercise parsing + undo + buffer rewriting.
Rev457 keeps that tiny bulk-edit loop typed all the way through: `replaceall`
now preserves its own command identity on read-only / invalid-regex failures
and in undo/redo feedback instead of collapsing back to generic `replace`.

Both `replace` and `qreplace` follow the editor's `ignorecase` option (like `find`): when enabled, they match case-insensitively in both literal and regex modes.

Rev86 adds `qreplace` / `queryreplace`: a tiny interactive "confirm each" loop
(`y`/`Enter` replace, `n` skip, `a` all, `l` last, `q`/`Esc` quit) implemented as
a capture keymode so global bindings can't accidentally fire during the loop.

### Keybinding integration

Micro also allows binding keys directly to commands:

- `command:pwd` executes the command immediately
- `command-edit:help ` opens command mode with the line prefilled

We support these prefixes inside action chains (see `Editor._run_action_spec`).

*(rev63: prompt editing is now first-class: printable keys type into the prompt when open, prompt-mode bindings override arrows/backspace/delete, and `quit` warns/arms when any buffers are dirty; `quit -f` or `quit!` force. Default bindings include `Ctrl-s` → `command:save`, `Ctrl-q` → `command:quit`, and `Ctrl-l` → `command-edit:goto `.)*

*(rev74: added `close` / `close!` to close buffers safely (dirty buffers require a second `close`), plus a recent-files MRU with `recent` / `recentpick`; rev267 adds the directory-grouped sibling `recentdirpick`; rev332 makes the ordinary success path more orienting by having `buffer`, `prevbuf`, `bufferpick`, `close`, `only`, and `closeall` report the landed active buffer/cursor target instead of only reporting that a switch/close happened; rev344 makes the plain `buffers` inventory stop collapsing open state to raw names by showing the active marker, `dirty` / `readonly` flags, and current cursor target for each entry; rev345 makes plain `recent` stop collapsing MRU state to raw numbered paths by showing open/active state, visible flags, and current cursor targets for still-open entries; rev365 makes plain `buffers` / `marks` keep one count-aware inventory prefix too, and rev366 does the same for plain `recent`, so all three inventories now start with `N` before the existing entry detail instead of falling back to `(none)` or silent manual counting; rev372 makes the empty `prevbuf` path fail plainly as `prevbuf: no previous buffer` so buffer recovery no longer falls back to a raw placeholder; rev377 makes named `buffer NAME` / `close NAME` misses fail plainly as `buffer: no such buffer: NAME` / `close: no such buffer: NAME` so explicit buffer-target commands keep the command family visible on a miss; rev387 makes successful `close` / `closeall` calls self-identify too as `close: ...` / `closeall -> ...` instead of older `closed...` lines, and rev391 keeps unexpected bulk-close faults in the same typed family by making raised `only` / `closeall` failures report `only: error: ...` / `closeall: error: ...`, so buffer cleanup reads like the rest of the typed command dialect on both success and failure; rev419 adds the tiny shared `buffer_inventory_rows()` / `ed.buffer-inventory-rows` seam underneath plain `buffers`, so the same active/dirty/readonly/position register is available to scripts and future UIs instead of only to the human-facing summary line; rev421 does the same for plain `recent` through `recent_inventory_rows()` / `ed.recent-inventory-rows`, so MRU slot numbers plus active/open/dirty/readonly/position cues stop living only inside the command-layer formatter and stay aligned with the host boundary too.)*

*(rev85: the core plugin now binds `Ctrl-o` → `open` (prefilled), `Ctrl-r` → `replace` (prefilled), `Ctrl-b` → `bufferpick`, `Ctrl-Space` → command palette, and `Alt-g` → binding discovery. The minimal curses TUI also interprets ESC-prefixed Alt/Meta chords so `Alt-*` bindings are reachable.)*

*(rev86: core defaults now also bind `Alt-%` → `qreplace` (prefilled), matching Emacs-ish "query replace" muscle memory.)*

### Design note

We keep “actions” and “command-bar commands” as separate concepts, but `help` is now deliberately broader: it first resolves editor commands/actions, then falls back to the currently visible Micromax word if no editor topic matches.

*(rev76: `help TOPIC` also falls back to opening a matching `docs/*.md` page into a protected read-only help buffer; `helppick [QUERY]` opens a docs picker; in a docs buffer, `helplinkpick` lists links, `helpoutlinepick` lists headings, and `helpjump [QUERY]` can now use parent breadcrumb terms like `Guide Links` and stable fragment/id terms like `custom-frag` instead of only the leaf heading title, and `helplinkpick` / the link side of `helpnavpick` can now use owning-section terms like `External micro editor` or `Reference Vision ref`, plus destination-title queries like `image metadata` or `hidden image metadata anchor`, instead of only the bare link label. The core plugin binds `Ctrl-g` to `command:helppick`, matching micro’s “open help menu” muscle memory.)*

*(rev77: help buffers gained tiny navigation helpers: `helpfollow` follows a markdown link under the cursor, and `helpback` returns to the previous docs page. This is deliberately inspired by “doc buffers with followable links” patterns seen in editors like Kakoune. Rev334 adds a small flow/trust follow-up: picker-driven docs navigation (`helpoutlinepick`, `helpnavpick`, `helplinkpick`) now reuses the same “tell me where I landed” rule as direct jump commands. Rev342 applies the same honesty rule to recovery commands too: command-bar `undo` / `redo` now mirror key-driven `Undo` / `Redo` and report the actual edit description plus touched target instead of mutating text silently. Rev405 adds a companion plain-register surface too: `helphistory` and `ed.helphistory-rows` let the same local docs-history trail be inspected directly instead of inferred from a transient status line. Rev406 adds the matching dormant-resume command: `helpresume` explicitly reopens the last dormant session-local docs target when you have switched away instead of forcing users or scripts to infer that path from buffer lists or `help -> ...` summaries. Rev407 carries one more tiny cue into the plain headless status surface: when docs navigation is actionable, `showstatus` / `ed.status-summary` now name the exact replay commands as `help_actions='helpresume, helpforward'` (or the smaller active/back/forward subsets) instead of leaving that last translation implicit. Rev408 tightens the stale-history side of that same cue: remembered docs targets can still survive as local witnesses after a docs file disappears, but `help_actions=` now only advertises replayable commands while `help_warn=` / `[missing]` trail cues keep blocked replay paths visible instead of pretending they still work. Rev409 adds the matching explicit disposition command: when those stale blockers should stop holding the local trail hostage, `helpprune` / `ed.help-prune` clear only the missing session/back/forward entries and `help_actions='helpprune'` names that exact cleanup step in the plain status surface. Rev410 keeps ordinary `help docs TOPIC` opens inside that same tiny trail too: branching from outside the help buffer now pushes the dormant current docs target onto `helpback` instead of silently overwriting it, and stale dormant forward history clears when the new docs page diverges. Rev411 closes the matching replay seam: direct off-screen `helpback` / `helpforward` now also treat the dormant current docs target as the local branch head, push it onto the opposite stack with its exact saved cursor position, and keep the replay trail continuous without forcing a separate `helpresume` first. Rev412 closes the matching same-topic reopen seam too: reopening the current dormant docs page by name now restores its exact remembered cursor landing even after the old help buffer was closed, so `help docs TOPIC` no longer quietly resets the session's current page back to `1:0` just because the earlier buffer disappeared.)*

- Actions are keybind targets and return success/failure for chaining.
- `show` now reuses a tiny shared canonical option register too: `option_inventory_rows()` / `ed.option-inventory-rows` expose `[name value default kind local_override?]` rows for the active buffer context, and plain `show` marks local overrides as `(local)` instead of leaving that scope split implicit.
- `showoptiongroups [QUERY]` now reuses a tiny shared option-family summary too: `option_section_summary_rows(QUERY)` / `ed.option-section-summary-rows` expose `[label count sample_name sample_detail]` rows so scripts/future UIs can inspect what broad option families are visible before walking the full inventory.
- `showoption NAME` now reuses a tiny shared exact option row too: `option_detail_row(NAME)` / `ed.option-detail-row` expose `[query canonical value default kind local_override doc]` so scripts/future UIs can inspect one option directly without scraping command text or losing alias spelling.
- `showbuffer NAME` now reuses a tiny shared exact buffer row too: `buffer_detail_row(NAME)` / `ed.buffer-detail-row` expose `[name position active dirty readonly section path line_count]` so scripts/future UIs can inspect one named buffer without switching focus via `buffer NAME` or scraping the bulk `buffers` summary.
- `showmark NAME` now gives marks that same tiny first-stop sibling: `mark_detail_row(NAME)` / `ed.mark-detail-row` expose `[name buffer position preview active here]` so scripts/future UIs can inspect one named mark without mutating state through `markjump NAME` or scraping the bulk `marks` summary.
- `showmarkgroups [QUERY]` now gives the same mark surface a tiny broad-summary sibling too: `mark_section_summary_rows(QUERY)` / `ed.mark-section-summary-rows` expose `[label count sample_name sample_detail]` rows so scripts/future UIs can inspect what owning-buffer mark buckets are visible before reopening `markpick` or walking every grouped row.
- `showjump INDEX` now gives jumplist history the same exact sibling too: `jump_detail_row(INDEX)` / `ed.jump-detail-row` expose `[query index lane depth buffer position preview]` so scripts/future UIs can inspect one known history entry without moving through it or scraping the broader `jumps` register.
- `showhook NAME` now has one smaller first-stop sibling too: `hook_detail_row(NAME)` / `ed.hook-detail-row` expose `[query name handler_count sample_handler|0 sample_detail|0 [file line col]|0]` so scripts/future UIs can inspect one known hook without reopening the full ordered handler inventory.
- `showhook NAME` still reuses the tiny shared hook inventory register too: `hook_inventory_rows(NAME)` / `ed.hook-inventory-rows` expose `[handler group|0 [file line col]|0]` rows for one hook, so the human-facing handler chain and the host boundary stay aligned.
- `showhooks [QUERY]` now gives that same live hook namespace a side-effect-free broad summary: `hook_summary_rows(QUERY)` / `ed.hook-summary-rows` expose `[name handler_count sample_handler|0 [file line col]|0]` rows so humans/scripts can inspect the current hook surface without probing one hook at a time.
- Commands are human-oriented strings (parsed) and can call actions internally.
- `showcmd NAME` now reuses a tiny shared command-detail row too: `command_detail_row(NAME)` / `ed.command-detail-row` expose `[name doc group|0 [file line col]|0]` so scripts/future UIs can inspect the same command provenance/detail without rescanning the whole command inventory or scraping command text, and command-bar completion now reuses that exact row so group / definition provenance stay visible while choosing one known command.
- `showaction NAME` gives editor actions that same first-stop direct path, and `action_detail_row(NAME)` / `ed.action-detail-row` expose the same tiny `[name doc [file line col]|0]` register behind both `showaction NAME` and `help ACTION` so exact action inspection can keep best-effort source provenance visible too.
- `showword NAME` is the explicit bridge from the editor prompt to Micromax dictionary metadata, and it now reuses a tiny shared detail row too: `word_detail_row(NAME)` / `ed.word-detail-row` expose `[name kind effect wordlist doc [file line col]|0 source|0]` so scripts/future UIs can inspect the same visible-word detail without scraping command text.
- `showdoc TOPIC` gives docs the same tiny first-stop inspection path, and `doc_detail_row(TOPIC)` / `ed.doc-detail-row` expose `[topic title summary section path]` so scripts/future UIs can inspect one resolved docs page without scraping `ed.doc-rows` or reopening the page.
- `showhelpheading` gives the current docs heading that same tiny first-stop inspection path, and `current_help_heading_detail_row()` / `ed.help-current-heading-detail-row` expose `[topic title fragment level line col section]` for the nearest heading owning the primary cursor instead of making scripts/future UIs reparse `help_outline_rows()` or guess from breadcrumbs alone.
- `helpjump QUERY` now has the same exact-inspection sibling too: `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row` expose `[topic title fragment level line col section]` for the resolved current-doc heading instead of making scripts/future UIs reparse `help_outline_rows()` or scrape picker text.
- `showhelplink` gives current docs-link actions the same first-stop inspection path, and `help_link_detail_row()` / `ed.help-link-detail-row` expose `[topic label target kind line col section]` so scripts/future UIs can inspect the exact link under the cursor without rescanning `ed.help-link-rows`.
- `apropos QUERY` is the search-first sibling: it ranks command/action/word topics by subsequence match, can fall back to topic summary/doc text, supports small multi-term / out-of-order queries (for example `apropos word show`), and now keeps the visible discovery slice count-aware as `apropos QUERY: N topic(s), ...` instead of falling back to `(none)` or forcing manual counting.
- failed `help NAME` now shows a few likely `apropos`-style matches instead of only returning a dead end; if the user typed multiple words, the suggestion path now searches that whole query rather than only the first token.


### Searchable command/action palette

The editor now also has a dedicated **palette** prompt kind. It is the execution-oriented sibling of `topicpick`: instead of opening help for commands/actions/words, it searches only **commands + actions** and then either runs the action or stages the command in the normal command bar.

Ways to open it:

- `commandpick [QUERY]` from the command bar; exact command/action targets now keep the same tiny metadata rows the narrower `showcmd` / `showaction` surfaces already trust while you are choosing them, visible file-side `openpath` rows now keep best-effort recent/open/parent-path context instead of a blank info slot, already-open file targets append a tiny `current buffer` / `switch buffer` cue, visible directory rows now also reuse exact recent-directory counts/state when Micromax already knows that bucket and append a small `drill down` cue, and the explicit typed `Open` row now tells you whether Enter targets an existing file, a known live directory drill-down, or a new file path — including already-open unsaved buffers that still keep `new file` truth beside `current buffer` / `switch buffer`, while parsecursor-shaped directory queries such as `guide/:2` now still honor that same `directory | drill down` promise on submit, parsecursor-shaped relative file queries such as `draft.md:3:7` now still keep the exact typed `Open` row too, parsecursor-shaped extensionless existing targets such as `guide:2` and `intro:2` now still keep that typed row when the parsed target already resolves to one real directory or file, parsecursor-shaped partial file queries such as `guide/i:2` now keep visible completion rows like `guide/intro.md:2` too, parsecursor-shaped partial directory queries such as `guide/s:2` now keep visible completion rows like `guide/sub/:2` too, partial extensionless current-directory queries such as `gu:2` and `intr:2` now keep visible completion rows like `guide/:2` and `intro:2` too, parsecursor-shaped existing-file targets that are not already open now append a tiny `cursor line:col` request cue, parsecursor-shaped new-file targets like `draft.md:3:7` now append `empty buffer @ 1:0` when Micromax already knows the file does not exist yet, and parsecursor-shaped file queries that already map to an open buffer still append the exact `goto line:col` cue
- the `CommandPalette` action
- the `ed.command-palette` hostcall from Micromax

Behavior:

- opening the prompt preloads ranked command/action rows
- the live `commandpick` prompt now flattens the same grouped palette sections exposed headlessly through `ed.command-palette-section-rows`, so visible section labels stay aligned across hostcalls, TUI headers, and prompt preview/status surfaces
- successful palette selections are remembered in a tiny palette-local MRU
- empty queries show a `Recent Files` bucket first (opens files immediately), then the palette-local `Recent` commands/actions bucket, and now budget the initial browse window across visible sections so `Actions` stay visible when `Commands` are numerous
- visible `Recent Files` rows now also reuse exact MRU metadata from `recent_detail_row(PATH)` so recency index plus active/open/dirty/readonly/cursor state stay visible during palette browsing instead of collapsing back to basename + parent, append capability-gated `existing file` when the remembered path still exists on disk, append `new file` when it no longer exists, and append `current buffer` / `switch buffer` when one recent-file target already maps to a live buffer
- visible path-completion `openpath` rows now also keep best-effort recent/open metadata when one filesystem file target is already known, already-open file targets append a tiny `current buffer` / `switch buffer` cue, visible directory rows reuse exact recent-directory count/state when one folder already maps to a known recent bucket, the explicit typed `Open` row now keeps the same exact file/directory context plus the same tiny open-buffer cue and best-effort `existing file` / `directory` / `new file` truth when capability-gated filesystem inspection is allowed, including open unsaved paths that should still say `new file` rather than quietly reading like real on-disk files; parsecursor-shaped directory queries now still reuse the same drill-down path on submit; parsecursor-shaped relative file queries such as `draft.md:3:7` now still produce the same typed `Open` row as other file targets; parsecursor-shaped extensionless existing targets such as `guide:2` and `intro:2` now still produce that typed row too when the parsed target already resolves to one real directory or file; parsecursor-shaped partial file queries such as `guide/i:2` now also keep visible completion rows like `guide/intro.md:2`; partial extensionless current-directory queries such as `gu:2` and `intr:2` now also keep visible completion rows like `guide/:2` and `intro:2`; parsecursor-shaped existing-file targets that are not already open now append a tiny `cursor line:col` request cue; parsecursor-shaped new-file targets like `draft.md:3:7` now append `empty buffer @ 1:0` when Micromax already knows the file does not exist yet; parsecursor-shaped file queries that already map to an open buffer still append the exact `goto line:col` cue; and ordinary fallback rows keep a small parent-directory cue so palette path rows do not degrade to empty context beside the richer MRU surfaces
- `recentpick` now also reuses grouped project-root sections live, so the same recent-file buckets can drive TUI headers/sticky headers, `Alt-Up` / `Alt-Down`, and prompt preview/status surfaces
- those project-grouped `recentpick` rows now also preserve the menu-side MRU/state suffix (`#N`, flags, `@ line:col`) instead of collapsing back to a bare project label, so the direct grouped prompt stays as honest as adjacent literal recent rows
- those same project-root buckets now also have a tiny shared summary sibling through `ed.recent-section-summary-rows` / `showrecentgroups [QUERY]`, so scripts/future UIs can inspect broad recent-file groups without opening `recentpick` or walking every grouped row
- one exact recent file now has the same small first-stop sibling too through `ed.recent-detail-row` / `showrecent PATH`, and that exact surface now keeps the same tiny `existing file` / `new file` plus `current buffer` / `switch buffer` / `empty buffer @ 1:0` truth cues as the adjacent palette rows when Micromax already knows them, so scripts/future UIs can inspect one MRU entry without scraping the flat `recent` inventory or opening it
- `recentdirpick` now does the same for the existing directory-grouped recent rows exposed through `ed.recent-dir-section-rows`, giving the live editor a second honest MRU scan mode when project buckets are too coarse
- one exact recent-directory bucket now has the same small first-stop sibling too through `ed.recent-dir-detail-row` / `showrecentdir DIR`, and after rev504 that exact inspector also keeps the same sample row menu/info truth visible as adjacent `recentdirpick` rows, so scripts/future UIs can inspect one visible directory bucket without reopening `recentdirpick` or inferring counts from `showrecentdirgroups` text
- path-like queries can split into `Directories`, `Files`, and `Open` buckets so drill-down rows do not get buried among ordinary file targets
- changing the query live-refreshes ranked rows
- equivalent matches can use palette recency as a tiebreaker
- `Tab` / `Shift-Tab` cycle ranked items
- `Enter` on an **action** executes it immediately
- `Enter` on a **command** opens the ordinary `command` prompt prefilled with `name `
- palette-prompt history is stored under prompt kind `palette`
- grouped section rows are available via `ed.command-palette-section-rows`, and the matching tiny bucket summaries now sit beside them via `ed.command-palette-section-summary-rows` / `showpalettegroups [QUERY]`
- grouped buffer rows are available via `ed.buffer-section-rows`, the matching tiny bucket summaries now sit beside them via `ed.buffer-section-summary-rows` / `showbuffergroups [QUERY]`, and one exact buffer now has the same small first-stop sibling through `ed.buffer-detail-row` / `showbuffer NAME`
- grouped mark rows are available via `ed.mark-section-rows`, the matching tiny bucket summaries now sit beside them via `ed.mark-section-summary-rows` / `showmarkgroups [QUERY]`, and one exact mark now has the same small first-stop sibling through `ed.mark-detail-row` / `showmark NAME`
- jumplist history is available as a flat register through `jumps` / `ed.jump-history-rows`, grouped browse state through `jumppick` / `ed.jump-section-rows`, and now one exact history entry also has the same small first-stop sibling through `ed.jump-detail-row` / `showjump INDEX`
- grouped recent-directory rows are available via `ed.recent-dir-section-rows`, the matching tiny bucket summaries now sit beside them via `ed.recent-dir-section-summary-rows` / `showrecentdirgroups [QUERY]`, and one exact recent-directory bucket now has the same small first-stop sibling through `ed.recent-dir-detail-row` / `showrecentdir DIR`
- the same current-row / preview / status-model surfaces used by other searchable prompts apply here too, including the compact shared picker-position summary (`index/count • section i/n`) now mirrored into the minimal TUI prompt line

## Topic prompt

The editor now also has a dedicated `topic` prompt kind. It is intentionally tiny and headless: it reuses the ordinary prompt suggestion-session model, but its candidates come from ranked topic rows (`help_topic_rows()` / `apropos_rows()`) instead of shell-ish command tokens. Those shared topic rows now include docs topics too, while still preferring command/action/word hits ahead of docs on ranking ties.

Ways to open it:

- `topicpick [QUERY]` from the command bar
- the `TopicPrompt` action
- the `ed.topic-prompt` hostcall from Micromax

Behavior:

- opening the prompt preloads ranked command/action/word topics
- changing the query live-refreshes those ranked topics
- `Tab` / `Shift-Tab` cycle those ranked topics
- `Enter` opens help for the selected/best-ranked topic
- topic-prompt history is stored under prompt kind `topic`
- the active ranked row is visible headlessly via `ed.prompt-current-row`
- grouped sections for future pickers are exposed via `ed.topic-section-rows` / `ed.apropos-section-rows`, and tiny count-aware summary rows now sit beside them via `ed.topic-section-summary-rows` / `ed.apropos-section-summary-rows`
- `showtopic NAME` is the side-effect-free exact inspector for that same generic help namespace: it resolves names with the same precedence as `help NAME` (command, action, visible word, then docs topic) but prints detail instead of opening docs pages
- `showtopics` now gives that same broader namespace a tiny count-aware first-stop summary without forcing humans/scripts to walk every grouped picker row
- the live `topicpick` prompt now flattens those same grouped families too, and empty-query browse windows budget rows across `Commands` / `Actions` / `Words` so Actions/Words stay visible instead of disappearing behind the command list cap
- compact current-item preview text is exposed via `ed.prompt-current-section` / `ed.prompt-current-preview`
- grouped docs families are also exposed headlessly via `ed.doc-section-rows`, and tiny count-aware family summaries now sit beside them via `ed.doc-section-summary-rows`, so future UIs/scripts can inherit either the full grouped picker shape or one lighter summary register
- `showdocs` gives humans the same side-effect-free count-aware docs-family summary directly from the command bar
- grouped plugin families are also exposed headlessly via `ed.plugin-section-rows`, and tiny count-aware plugin-state summaries now sit beside them via `ed.plugin-section-summary-rows`, so future UIs/scripts can inspect broad plugin health without walking every picker row
- one exact plugin now has the same small first-stop sibling too through `ed.plugin-detail-row` / `showplugin NAME`, so scripts/future UIs can inspect one known plugin without reopening the broader `plugin info` / `plugin errors` detail paths
- `showplugins [QUERY]` gives humans the same side-effect-free count-aware plugin-state summary directly from the command bar


## Searchable binding prompt

The same headless prompt/session model now also powers a small **binding** prompt.

Open it via:

- `bindingpick [QUERY]` from the command bar
- action `BindingPrompt`
- hostcall `ed.binding-prompt`
- inspectable current-binding register: `ed.available-binding-inventory-rows`

Behavior:

- it searches the **currently reachable** bindings after active keymode precedence is applied
- rows carry `[key kind menu info]` where `menu` includes mode + action-spec and `info` carries the resolved human description
- changing the query live-refreshes ranked bindings; small multi-term / out-of-order queries can match across the key itself, the action-spec, and the human description
- `Tab` / `Shift-Tab` cycle the ranked keys
- `Enter` runs `showkey KEY` for the selected/best-ranked binding

This deliberately stays on the discovery side of the line: it is a searchable `whichkey`-style surface, not yet a popup/menu rendering contract.

Rev429 follow-up: plain `showkey KEY` now also reuses a tiny shared machine-facing sibling — `ed.binding-detail-row` exposes the same resolved `[mode key action desc|0 group|0 span|0]` row that the command already renders for humans, so scripts and future UIs can inspect one binding directly without guessing whether the lower-level `ed.resolve-key` or `ed.resolve-key-info` helper is the intended show-surface sibling.

Rev426 follow-up: plain `showkeymodes` now also reuses a tiny shared machine-facing sibling — `ed.keymode-inventory-rows` exposes the same ordered `[section mode once?]` rows that the command already renders for humans, so scripts and future UIs can inspect current active-vs-known keymode state without joining the split raw stacks from `ed.keymode-rows` or reapplying the command's internal-mode filtering policy.

Rev442 follow-up: plain `showkeymode NAME` now also reuses a tiny shared machine-facing sibling — `ed.keymode-detail-row` exposes the same exact `[mode active? known? once? binding_count sample_key|0 sample_action|0 sample_desc|0]` row that the command already renders for humans, so scripts and future UIs can inspect one visible or currently active keymode directly without rejoining `showkeymodes` inventory state with lower-level mode-local binding rows.

Rev459 follow-up: command-bar completion now reuses that same exact keymode row too — prompt rows for `showkeymode NAME`, `showbindings MODE`, `keymode`, `pushkeymode`, `pushkeymode-once`, and `prefixmode` now read from `ed.keymode-detail-row`, so choosing a mode keeps active/once/known-or-internal state, binding counts, and one sample binding visible instead of downgrading back to a generic `keymode` placeholder.

Rev460 follow-up: `showkey KEY` completion now reuses the matching exact binding row too — the command now completes against the currently reachable binding register and prompt rows reuse `ed.binding-detail-row`, so choosing one key keeps the winner mode, action, optional group, and resolved description visible instead of offering no exact prompt help.

Rev461 follow-up: `buffer NAME` completion now reuses the matching exact buffer row too — prompt rows now read from `ed.buffer-detail-row`, so choosing one open buffer keeps active/dirty/readonly state, current position, section, and path visible instead of dropping back to the older generic buffer prompt row.

Rev464 follow-up: the broad navigation summary commands now reuse their own tiny section-summary rows in completion too — `showbuffergroups`, `showrecentgroups`, `showrecentdirgroups`, and `showmarkgroups` now complete visible section labels and keep count/sample metadata visible instead of falling back to opaque raw labels.


Rev336 follow-up: selecting `recentfile` / `openpath` rows from `commandpick` now reports `opened: path @ line:col`, keeping searchable file-open flows aligned with the explicit `open ...` command rather than behaving like a quieter success path.
- missing `showcmd NAME` / `showaction NAME` / `showoption NAME` / `showbuffer NAME` / `showjump INDEX` / `showword NAME` / `showdoc TOPIC` lookups now fail plainly as `showcmd: no such command: NAME` / `showaction: no such action: NAME` / `showoption: no such option: NAME` / `showbuffer: no such buffer: NAME` / `showjump: no such jump: INDEX` / `showword: no such word: NAME` / `showdoc: no such doc: TOPIC` so command-bar inspection stays explicit even on a miss. `showhelpheading` keeps the same typed docs-heading miss dialect too: `showhelpheading: not in a docs buffer` or `showhelpheading: no heading under cursor`, and `showhelplink` keeps the same typed docs-link misses as `showhelplink: not in a docs buffer` or `showhelplink: no link under cursor`.
- mistyped ordinary command-bar commands now fail plainly as `command: no such command: NAME` instead of the older `Unknown command: NAME`, so the first command-entry miss matches the newer inspection/navigation dialect too.
- known commands that raise unexpectedly now fail as `command NAME: error: DETAILS` instead of a generic `Command error: ...`, so the dispatcher keeps the failing command visible during plugin/dev-command debugging.
- Micromax-defined commands registered through `ed.cmd-add` now reuse that same `command NAME: error: DETAILS` dialect on Micromax/runtime faults too, so scripted commands do not regress into a weaker bridge-specific error surface.
- missing `showkey KEY`, `binddoc KEY DOC...`, `bindmodedoc MODE KEY DOC...`, `unbind KEY`, and `unbindmode MODE KEY` targets now fail plainly as `...: no such binding: ...` instead of collapsing to `(unbound)`.
- successful `unbind KEY` / `unbindmode MODE KEY` edits now report `unbind: KEY` / `unbindmode: KEY@MODE`, so small keymap surgery stays self-identifying in message logs.
- successful `bind KEY ACTIONSPEC`, `bindmode MODE KEY ACTIONSPEC`, `bindprefix KEY MODE [DOC...]`, and `bindmodeprefix OWNERMODE KEY MODE [DOC...]` edits now also report typed feedback (`bind: ...`, `bindmode: ...`, `bindprefix: ...`, `bindmodeprefix: ...`) so the creation side of the same loop reads in the same dialect.
- successful `binddoc KEY DOC...` / `bindmodedoc MODE KEY DOC...` edits now also report typed feedback (`binddoc: KEY -> DOC...`, `bindmodedoc: KEY@MODE -> DOC...`) so key descriptions do not fall back to an older ad-hoc success line.
- successful `set OPTION VALUE`, `setlocal OPTION VALUE`, `toggle OPTION`, and `togglelocal OPTION` edits now also report typed feedback (`set: name=value`, `setlocal: name(local)=value`, `toggle: name=value`, `togglelocal: name(local)=value`) so small configuration changes stay attributable in logs instead of collapsing to bare value lines.

  - searchable `apropos QUERY`, `topicpick`, `commandpick`, and `helppick` discovery surfaces for command/word/docs exploration
  - rev413 also keeps the smallest help replay cue honest: `helpresume` stays discoverable as the dormant-session reopen command, but an already-active help page no longer makes `help_resume_available` read as though `helpresume` were actionable there
  - rev414 closes the matching active-command seam too: once the model says there is nothing off-screen to resume, plain `helpresume` / `ed.help-resume` now fail explicitly as `helpresume: already active: topic @ line:col` instead of replaying the current page
  - rev415 keeps stale replay misses in that same typed dialect too: if a remembered `helpresume` / `helpback` / `helpforward` target no longer resolves, the command now fails as `helpresume: missing doc: TOPIC`, `helpback: missing doc: TOPIC`, or `helpforward: missing doc: TOPIC` instead of collapsing back to generic `help docs:` wording
  - rev416 keeps explicit docs opens aligned with that same local replay loop too: when `help docs TOPIC` or `help TOPIC` already names exactly one adjacent back/forward target, Micromax reuses that existing history edge instead of branching a duplicate path or clearing deeper forward history
  - rev417 gives the jumplist the same tiny plain-register treatment too: `jumps` and `ed.jump-history-rows` expose the current/back/forward trail directly instead of forcing humans or scripts through `jumppick` or the thinner `jump-info` summary
  - rev418 keeps the neighboring marks loop aligned too: `marks` now reuses shared `mark_inventory_rows()` data and `ed.mark-inventory-rows` exposes the same active/here/preview-aware inventory to scripts instead of leaving that richer surface trapped behind the human-only command output
  - rev452 closes the exact sibling of that same seam: `showmark NAME` / `mark_detail_row(NAME)` / `ed.mark-detail-row` now expose one named mark without jumping through it, so broad mark inventory and grouped mark browsing no longer leave exact mark inspection trapped inside formatter-only text or mutating navigation
  - plain typed miss feedback for `help` too: `help docs TOPIC` -> `help docs: no such doc: TOPIC`, ordinary lookup misses -> `help: no such topic: QUERY` (with the same `Try: ...` suggestion preview when ranked matches exist)
