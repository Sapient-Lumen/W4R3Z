Rev503 note: project-grouped `recentpick` rows now preserve MRU recency/state cues too, so the project-label rewrite keeps `#N`, `[active/open/dirty/readonly]`, and `@ line:col` instead of discarding them.

Rev502 note: dedicated `recentpick` / `recentdirpick` rows now reuse exact recent-file state/truth too, so first-class recent-file prompts keep the same tiny `existing file` / `new file` plus `current buffer` / `switch buffer` cues already trusted by adjacent `showrecent` and palette `Recent Files` rows.

Rev500 note: command-palette `Recent Files` rows now also keep explicit capability-gated `existing file` truth for saved targets, so ordinary MRU rows stop being the one remaining class that says neither `existing file` nor `new file`.

# Prompt completion (command bar / prompt UX)

Micromax-editor is **headless-first**, so prompt completion is modeled as data and pure editor behaviors — not a UI widget.

This doc defines the **contract** between:
- the editor core (`Editor.prompt_complete`, `Prompt.suggestions`, `Prompt.suggestion_rows`),
- optional micromax scripts (hostcalls), and
- any future UI layer (terminal UI, GUI, etc.).

## Desired ergonomics

We’re stealing the best “muscle memory” ideas from other editors:

- **micro**: `Ctrl-e` opens a command bar, and `Tab` autocompletes commands in that prompt.
- **Kakoune**: prompt completion uses `Tab` / `Shift-Tab` to cycle candidates.
- **Helix**: completion menus commonly use `Tab`/`Shift-Tab` as next/prev navigation.

We also treat editor navigation targets as completion candidates (e.g. `buffer NAME`, `markjump NAME`, and now `showmark NAME` / `showjump INDEX` complete mark names and jump-history indices) so workflows stay discoverable even before any UI exists.

The result is a tiny, predictable completion model that feels familiar.

## Data model

`Prompt` keeps a *suggestion session* (currently used by command prompts plus searchable pickers like `palette`, `topic`, `binding`, docs/help pickers, and the other section-aware navigator prompts):

- `suggestions: list[str]` — the candidate insert strings.
- `suggestion_rows: list[[insert kind menu info]]` — best-effort annotations aligned with `suggestions`.
- `suggest_index: int` — last applied candidate index.
- `suggest_start/suggest_end: int` — the replacement range.
- `suggest_base: str` — the prompt text at the start of the session.

A UI may:
- display `suggestions` as a dropdown/list
- display `suggestion_rows[*][1:]` as tiny labels/docs/current-value hints
- highlight `suggest_index`
- for section-aware pickers, treat the visible section labels as real browse structure (headers, section jumps, and initial empty-query windowing all now reuse the same grouped-row policy); pluginpick section labels now carry tiny visible counts too when grouping plugin rows

Or it may ignore the list entirely and rely on the message log.

## Editor behavior

### Starting completion

When `Editor.prompt_complete()` is called and no suggestion session exists:

- for **command** prompts:
  1) identify which token the cursor is in (forgiving, quote-aware split)
  2) determine candidates based on command context
  3) if there is one match, insert it immediately
  4) if there are multiple matches:
     - extend to the **longest common prefix** (if it grows)
     - start a suggestion session
     - emit a `matches: ...` message for headless visibility

- for the **topic** prompt:
  1) rank command/action/word topic rows using `apropos_rows()` (or all topic rows for an empty query); multi-term queries are matched term-by-term across names plus summary/doc text
  2) start a suggestion session without destroying the typed query
  3) emit a `topics: ...` preview for headless visibility

- for the **binding** prompt:
  1) rank the *currently reachable* binding rows using `binding_apropos_rows()` (or all current binding rows for an empty query); multi-term queries are matched term-by-term across key, description, and action-spec text
  2) start a suggestion session without destroying the typed query
  3) emit a `bindings: ...` preview for headless visibility

### Cycling completion

When a suggestion session exists:

- `prompt_complete(direction=+1)` selects *next* (Tab)
- `prompt_complete(direction=-1)` selects *previous* (Shift-Tab)

The first cycle applies the first/last candidate without skipping.
Note: this suggestion-session model exists partly to avoid the common “Tab always completes to the *first* match” frustration reported in other editors; cycling is explicit and testable.


## Candidate sources

Current (rev54) completion sources:

- First token: command names (`CommandDispatcher.names()`)
- exact inspection commands like `showoption NAME`, `showbuffer NAME`, `showrecent PATH`, `showmark NAME`, `showjump INDEX`, and `showplugin NAME` can reuse their shared exact row surfaces to populate richer `[insert kind menu info]` suggestion metadata instead of falling back to raw token strings; after rev501, exact `showrecent PATH` completion rows now also keep the same tiny `existing file` / `new file` plus `current buffer` / `switch buffer` / `empty buffer @ 1:0` truth cues already trusted by the adjacent palette recent-file rows when Micromax already knows them
- `mark` / `markjump` / `showmark`: known mark names, and command-bar completion for those mark-target slots now reuses exact mark metadata from `mark_detail_row(NAME)` / `ed.mark-detail-row` so the owning buffer plus active/here/preview state stay visible while choosing one known mark
- `set/setlocal/show/toggle/togglelocal`: option names (`Options.specs`)
- `set/setlocal OPTION VALUE`: small value completion for built-in bool/enum options
- `help`: command names + action names + visible Micromax word names; when a visible topic resolves to a command, the prompt row now reuses exact command metadata from `command_detail_row(NAME)` / `ed.command-detail-row` so group/provenance stay visible during broad help exploration, visible Micromax words now keep their definition provenance from `word_detail_row(NAME)` visible in the info slot too, and docs topics now keep the backing docs path from `doc_detail_row(NAME)` visible as well
- `apropos`: the same searchable topic names as `help`; when a visible result resolves to a command, the prompt keeps exact command group/provenance metadata in the info slot instead of flattening back to plain `search topic`, action results now keep `search topic` while appending best-effort action source provenance, word results now keep `search topic` while appending exact word definition provenance after the summary, and doc-topic rows now keep the same `search topic` cue while appending exact docs section/path metadata too
- `helpjump`: current-doc heading titles plus explicit fragment ids, and completion rows now reuse exact heading metadata from `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row` so the resolved heading title/level/fragment/section stay visible while choosing one navigation target
- `showcmd`: command names, and prompt rows now reuse exact command metadata from `command_detail_row(NAME)` / `ed.command-detail-row` so doc/group/provenance stay visible while choosing one command
- `commandpick`: command/action names in command-bar completion still reuse exact command/action metadata when the visible target resolves to one exact row, the live palette's `Recent Files` rows now also reuse exact MRU metadata from `recent_detail_row(PATH)` so recency index plus active/open/dirty/readonly/cursor state stay visible while browsing file targets, those same MRU rows now append capability-gated `existing file` when the remembered path still exists on disk, append `new file` when it no longer exists, and existing live-buffer MRU rows now also append `current buffer` / `switch buffer`, adjacent file-side `openpath` rows now keep best-effort recent/open/parent-path context instead of an empty info slot, already-open file targets append a tiny `current buffer` / `switch buffer` cue, visible directory rows now also reuse exact recent-directory count/state from `recent_dir_detail_row(DIR)` when one folder target is already known and append a small `drill down` cue, and the explicit typed `Open` row now keeps the same exact context plus that same open-buffer cue, directory `drill down` cue, and capability-gated `existing file` / `directory` / `new file` truth, including already-open unsaved paths that should still say `new file` beside `current buffer` / `switch buffer`, while parsecursor-shaped directory queries like `guide/:2` now still follow the same drill-down path on submit, parsecursor-shaped relative file queries like `draft.md:3:7` now still keep the same typed `Open` row too, parsecursor-shaped extensionless existing targets like `guide:2` and `intro:2` now still keep that typed row when the parsed target already resolves to one real directory or file, parsecursor-shaped partial file queries like `guide/i:2` now keep visible completion rows such as `guide/intro.md:2` too, parsecursor-shaped partial directory queries like `guide/s:2` now keep visible completion rows such as `guide/sub/:2` too, partial extensionless current-directory queries like `gu:2` and `intr:2` now keep visible completion rows such as `guide/:2` and `intro:2` too, parsecursor-shaped existing-file targets that are not already open now append a tiny `cursor line:col` request cue too, parsecursor-shaped new-file targets like `draft.md:3:7` now append `empty buffer @ 1:0` when Micromax already knows the file does not exist yet, and parsecursor-shaped file queries that already map to an open buffer still append the exact `goto line:col` cue, while visible known-path file candidates that no longer exist on disk now append `new file` and, when they are not already backed by one live open buffer, the more honest `empty buffer @ 1:0` landing cue
- `showaction`: action names, now through the same small exact-action prompt helper used by generic topic completion so that one future refinement to action detail only has one prompt substrate to touch; exact action rows now keep best-effort `defined at file:line:col` provenance visible when the registered callable comes from inspectable Python source
- `showword`: visible Micromax word names from the current search order, and prompt rows now keep exact word summary plus definition provenance from `word_detail_row(NAME)` visible during selection
- `showhook`: hook names visible in the current VM, and prompt rows now reuse exact hook metadata from `hook_detail_row(NAME)` / `ed.hook-detail-row` so one completed hook shows handler counts/sample detail instead of a generic placeholder
- `showkey`: currently reachable key names, with prompt rows now reusing exact binding metadata from `binding_detail_row(KEY)` / `ed.binding-detail-row` so the winning mode/action/group/description stay visible while choosing one key
- `showhooks`: the same hook names, and prompt rows now reuse the tiny `ed.hook-summary-rows` metadata so choosing one live hook keeps handler-count/sample/provenance state visible instead of falling back to a generic placeholder
- `plugin`: `list` / `reload` / `info` / `errors`; `plugin reload` completes only loaded plugin names, while `plugin info` / `plugin errors` complete all known plugin names; plain `showplugin NAME` also completes known plugin names with exact state/error metadata
- `macro`: subcommands and macro slot names for `macro play NAME`
- `keymode` / `pushkeymode` / `pushkeymode-once` / `prefixmode`: known keymode names, and the prompt rows now reuse exact keymode metadata from `keymode_detail_row(NAME)` / `ed.keymode-detail-row` so active/once/internal state and one sample binding stay visible while choosing a mode
- `showbindings`: `active` plus known keymode names; concrete mode rows reuse that same exact keymode metadata instead of a generic placeholder
- `showkeymode`: known keymode names plus currently active internal modes, with the same exact keymode metadata reused in completion rows
- `showtopics` / `showoptiongroups` / `showbuffergroups` / `showrecentgroups` / `showrecentdirgroups` / `showmarkgroups` / `showpalettegroups` / `showhelpnav` / `showdocs` / `showplugins` / `showbindingmodes`: visible broad section labels for those grouped summary surfaces, and prompt rows now reuse the matching tiny `[[label count sample_name sample_detail] ...]` summary rows so choosing one known bucket keeps count/sample metadata visible instead of falling back to an opaque label
- `bindmode` / `bindmodedoc` / `unbindmode` / `bindmodeprefix`: known keymode names in their mode slots
- `bind KEY ACTIONSPEC`: editor action names plus `command:` / `command-edit:` prefixes
- `bindmode MODE KEY ACTIONSPEC`: same action-spec completion surface after the key slot
- if a binding action-spec begins with `command:` or `command-edit:`, completion reuses the normal embedded **command-ish** surface (command names first, then the small built-in argument slots such as `showbindings active|MODE`)
- For the **command-ish** sources above, completion is:
  - **exact-prefix first**
  - then a tiny **fuzzy subsequence fallback** if exact-prefix matching found nothing
  - ranked deterministically (substring / earlier / tighter / boundary-friendlier matches first)
- `open` / `save` / `cd` intentionally stay **prefix-based path completion** for now
- `open` / `save` / `cd`: filesystem path completion for the first path argument
  - dirs get a trailing `/` (or platform separator)
  - files at end-of-line get a trailing space
  - hidden files are only suggested when you start with `.`
  - **quoting**: if the completion contains whitespace or `"`, we auto-wrap it in double quotes and escape internal `\\` and `"`
    - for dirs, when quoting is active we keep the closing quote **open** so you can keep tabbing into the path
    - if the user already typed a closing quote, we preserve it (even for dirs)

- micromax completion hooks: `ed.complete.<cmd>` or `ed.complete` (see `docs/66-editor-micromax-commands.md`)
  - hooks may now also return aligned suggestion rows (`[insert kind menu info]`) instead of only plain candidate strings

Examples:

- `open a<Tab>` → `open "alpha beta.txt" `
- `open a<Tab>` → `open "alpha dir/` (dir with spaces keeps quote open)
- `open "a"<Tab>` → `open "alpha dir/"` (user provided closing quote; we keep it)

Current metadata rows are best-effort and currently cover the built-in command-ish/path surfaces with small labels such as:
- command/action docs, plus exact `showcmd` group/provenance detail
- option kind + current/default values
- binding-RHS prefixes and embedded command docs
- action docs plus best-effort source provenance for `showaction`
- Micromax word kind/effect/doc hints for `help` / `showword` / `apropos`
- file vs directory path hints
- plugin-provided rows returned from `ed.complete.*` / `ed.complete`

This is intentionally small; we can later add:
- richer docs/current-value annotations for more argument surfaces
- deeper action-spec completion for chained actions with separators inside one token
- optional file-picker style fuzzy open (separate from path completion)


## Searchable prompts

The editor now has two dedicated searchable prompt kinds built on the same row/session model used elsewhere by the command bar.

### Topic prompt

Open it via:

- command-bar command `topicpick [QUERY]`
- plain `help QUERY` / `apropos QUERY` completion now reuses that same broader topic set too, so docs topics show up before a docs-specific verb is chosen
- action `TopicPrompt`
- hostcall `ed.topic-prompt`

The topic prompt is deliberately small:

- it preloads ranked command/action/word topic rows
- changing the query live-refreshes the ranked rows
- `Tab` / `Shift-Tab` cycle those topics
- `Enter` opens help for the selected/best-ranked topic
- history is stored under prompt kind `topic`
- the active ranked row is visible through `ed.prompt-current-row`
- grouped topic sections are available through `ed.topic-section-rows` / `ed.apropos-section-rows`, lighter count-aware summaries are available through `ed.topic-section-summary-rows` / `ed.apropos-section-summary-rows`, and `showtopics [QUERY]` completion now reuses those same tiny generic topic-family rows too
- compact current-item preview text is available through `ed.prompt-current-section` / `ed.prompt-current-preview` and mirrored into the status model
- the live `topicpick` prompt now flattens those same grouped topic families too, and empty-query browse windows budget rows across `Commands` / `Actions` / `Words` so all three families stay visible in the first page
- failed submit on a zero-result query now says `topicpick QUERY: 0 topic(s)` instead of collapsing to `(none)`
- compact current-item ordinal/section position is available through `ed.prompt-current-position` and mirrored into the status model as `prompt_index`, `prompt_count`, `prompt_section_index`, `prompt_section_count`, and `prompt_position_summary`
- shared picker scroll-window metadata is available through `ed.prompt-window`, so future UIs/scripts can inspect the same sticky-header / more-marker / hidden-count structure the minimal TUI uses instead of re-deriving it from raw rows
- shared rendered picker rows are available through `ed.prompt-display`, so future UIs/scripts/LLMs can inspect the same visible row text / selected prefixes / heading indentation / sticky headers / more markers the minimal TUI shows without redoing formatting from raw rows + window metadata

### Binding prompt

Open it via:

- command-bar command `bindingpick [QUERY]`
- action `BindingPrompt`
- hostcall `ed.binding-prompt`

The binding prompt is the same idea applied to the **currently reachable** keymap:

- it preloads/ranks resolved binding rows after active keymode precedence
- row shape is still `[insert kind menu info]`, where `insert` is the key, `menu` includes mode + action-spec, and `info` is the resolved human description
- changing the query live-refreshes the ranked rows
- visible picker sections now reuse the binding's winning mode (`Prompt`, active mode names like `nav`, `Global`) instead of a generic `Binding` bucket
- failed submit on a zero-result query now says `bindingpick QUERY: 0 binding(s)` instead of collapsing to `(none)`
- grouped binding sections are available headlessly through `ed.binding-section-rows`
- `Tab` / `Shift-Tab` cycle those keys
- `Enter` runs `showkey KEY` for the selected/best-ranked binding
- history is stored under prompt kind `binding`

Together, these are the current “headless palette / searchable discovery prompt” substrate. A future UI can render them as lists/palettes/browsers without changing the core state model.

The docs-focused pickers follow the same rule now as well: `helplinkpick`, `helpnavpick`, and `helpoutlinepick` reuse their **visible** section labels (`Docs` / `Files` / `External`, heading-breadcrumb labels, or parent-heading breadcrumbs like `Top` / document title / `Guide` / `Guide › Links`) for prompt previews and the headless status model instead of older singular fallback names. After rev268, `helpnavpick` heading rows no longer fall back to one generic `Headings` bucket either: they share the same outline-breadcrumb labels as `helpoutlinepick`. After rev269, their heading-query ranking also reuses that breadcrumb context, so queries like `Guide Links` can target the right heading instead of only matching the bare leaf title. After rev271, heading queries also reuse the resolved fragment/id for the heading line, so stable-anchor searches like `custom-frag` work without exposing raw ids in visible picker rows. After rev270, docs-link queries do the same for nearest-heading/kind context, so `helplinkpick` / `helpnavpick` can answer section-aware link queries like `External micro editor` or `Reference Vision ref` too. After rev272, the same link queries also reuse destination doc titles and destination heading titles, so more human queries like `image metadata` or `hidden image metadata anchor` can find generic-label links without exposing that metadata in visible rows.

## Scripting hooks (hostcalls)

For scripting and UI experimentation, the editor exposes:

- `ed.prompt-suggestions` ( -- suggs )
- `ed.prompt-suggestion-rows` ( -- rows )  — `[[insert kind menu info] ...]`
- `ed.prompt-current-row` ( -- row|[] ) — the currently selected suggestion row as `[insert kind menu info]`
- `ed.prompt-current-section` ( -- label ) — coarse section label for the current item (`Commands` / `Actions` / `Words` for topic prompts, or a picker-specific visible section label such as `Prompt`, `nav`, `Global`, `Help`, `Docs`, `Files`, `External`, `Top`, a heading breadcrumb, a project root, `Errors`, or `Current` / `Back` / `Forward`)
- `ed.prompt-current-preview` ( -- s ) — compact preview text for the current item
- `ed.prompt-current-position` ( -- m ) — compact current picker position map `{index count section section_index section_count summary}`
- `ed.prompt-window` ( lines -- m ) — shared picker-window map `{kind max_lines flat_count selected_index selected_flat_index start end show_top show_bottom sticky_section hidden_above hidden_below entries}`
- `ed.prompt-display` ( lines cols -- rows ) — shared rendered picker-row maps `[{type text row_kind section_label selected ...}]`
- `ed.prompt-suggest-index` ( -- i )
- `ed.prompt-complete` ( dir -- ok )
- `ed.prompt-clear-suggestions` ( -- ok )

These return only portable stack values.

For broader discovery tooling, the editor also now exposes:

- `ed.topic-rows` ( -- rows ) — searchable command/action/word/doc topic rows
- `ed.topic-detail-row` ( name -- row|0 ) — exact topic row as `[name kind detail_row]` for the same generic help namespace
- `ed.topic-section-rows` ( -- sections ) — grouped topic rows as `[[label [[name kind menu info] ...]] ...]`
- `ed.topic-section-summary-rows` ( -- rows ) — tiny count-aware topic-section rows as `[[label count sample_name sample_detail] ...]`
- `ed.apropos-rows` ( query -- rows ) — the same rows ranked by deterministic subsequence match, with lower-priority fallback through topic summary/doc text and small multi-term/out-of-order matching across those fields
- `ed.apropos-section-rows` ( query -- sections ) — grouped apropos rows in the same shape
- `ed.topic-prompt` ( query -- ) — open the searchable topic/help prompt with a prefilled query
- `ed.binding-prompt` ( query -- ) — open the searchable current-binding prompt with a prefilled query
- `ed.binding-prompt-rows` ( query -- rows ) — searchable current-binding rows as `[[key kind menu info] ...]`
- `ed.binding-section-rows` ( query -- sections ) — grouped current-binding rows as `[[label [[key kind menu info] ...]] ...]`
- command completion for `showtopic NAME` now reuses that same generic help-topic metadata instead of treating exact topic names as opaque strings
- `ed.doc-section-rows` ( query -- sections ) — grouped docs rows as `[[label [[topic kind menu info] ...]] ...]`
- `ed.doc-section-summary-rows` ( query -- rows ) — tiny count-aware docs-family rows as `[[label count sample_name sample_detail] ...]`
- `ed.recent-section-rows` ( query -- sections ) — grouped recent-file rows by project root as `[[label [[path kind menu info] ...]] ...]`
- `ed.recent-dir-section-rows` ( query -- sections ) — grouped recent-file rows by parent directory as `[[label [[path kind menu info] ...]] ...]`


## Command palette prompt

The searchable `palette` prompt is the execution-oriented sibling of `topicpick`:

- `commandpick [QUERY]` opens it from the command bar
- `CommandPalette` opens it as an action
- `ed.command-palette` opens it from Micromax
- it searches only **commands + actions** (not Micromax words)
- successful palette selections are remembered in a small palette-local MRU
- empty queries show those recent items first
- path-like queries can expose grouped `Directories` / `Files` / `Open` sections in `ed.command-palette-section-rows`
- grouped palette sections are available through `ed.command-palette-section-rows`, tiny count-aware palette bucket summaries are available through `ed.command-palette-section-summary-rows`, and the live `commandpick` prompt now flattens those same sections too
- empty-query palette browse windows now budget rows across visible sections (`Recent Files`, `Recent`, `Commands`, `Actions`) so `Actions` are not hidden behind a large command bucket
- failed submit on a zero-result query now says `commandpick QUERY: 0 match(s)` instead of collapsing to `(none)`
- `Enter` on an action executes it
- `Enter` on a command opens the ordinary command prompt prefilled with `name `

The prompt uses the same aligned row shape as other searchable prompts: `[insert kind menu info]`. Exact-selection loops now try to reuse the same tiny honest row the narrower inspection command already trusts: `showcmd NAME`, `showaction NAME`, `showword NAME`, `showdoc NAME`, `showtopic NAME`, and `commandpick NAME` all keep exact command/action/word/doc metadata visible during selection instead of dropping back to thinner placeholders once a visible row has already resolved, and palette `openpath` rows now do the matching filesystem-side version by reusing exact recent/open state for known file targets, appending a tiny `current buffer` / `switch buffer` cue when the file is already open, reusing exact recent-directory count/state for known directory targets, and keeping a more honest typed `Open` row when the query itself is the target. Project-grouped `recentpick` rows now do the matching grouped-recent version too: once a visible recent row already has exact MRU metadata, rewriting it to one project label still preserves the row's `#N`, flags, and `@ line:col` suffix instead of flattening it back to a bare project name. After rev490, parsecursor-shaped partial file queries like `guide/i:2` now keep visible completion rows such as `guide/intro.md:2` by reusing the parsed open target before filesystem listing and by preserving the typed cursor suffix on file candidates. After rev493, the same continuity now extends to partial directory queries like `guide/s:2`, so visible directory candidates can surface as `guide/sub/:2` instead of disappearing from the ranked rows just because the typed suffix was dropped. After rev494, the same path-heuristic continuity now reaches partial extensionless current-directory queries like `gu:2` and `intr:2`, so `guide/:2` and `intro:2` can appear as visible completion rows instead of vanishing before the palette even decides to show path rows. After rev489, the same path heuristic also keeps that exact typed row alive for extensionless existing parsecursor targets like `guide:2` and `intro:2` when the parsed target already resolves to one real directory or file; after rev488, it already did the matching relative-file case for names like `draft.md:3:7` by reusing the parsed open target itself. After rev491, parsecursor-shaped existing-file targets that are not already open now also append a tiny `cursor line:col` request cue instead of going quiet in the info column. After rev492, parsecursor-shaped new-file targets like `draft.md:3:7` now append `empty buffer @ 1:0` too when Micromax already knows the file does not exist yet. After rev487, already-open buffer targets still keep the exact `goto line:col` cue when Enter will move the cursor inside that live buffer. The earlier rev486 directory follow-up still holds too: if the row says `directory | drill down`, submit drills down instead of failing against the raw unparsed text. For `pluginpick`, the `menu` field now carries the same compact bracketed plugin-state summary dialect used by `plugin list` / `plugin reload` / `plugin info` / `plugin errors` (for example `[loaded, v1.0.0]` or `[error, deps:missingdep]`) instead of older free-form labels like `loaded` or `not loaded ... ERROR`. The grouped section shape is `[[label [[name kind menu info] ...]] ...]`, and the lighter summary companion shape used by broad summary hostcalls is `[[label count sample_name sample_detail] ...]`. Navigation-heavy pickers now expose the same grouped shape too: `ed.command-palette-section-rows` groups palette rows by visible labels like `Recent Files` / `Recent` / `Commands` / `Actions`, `ed.command-palette-section-summary-rows` exposes those same broad palette buckets as tiny count-aware rows behind plain `showpalettegroups [QUERY]`, and `showpalettegroups` completion now reuses those same summary rows too; `ed.option-section-summary-rows` exposes visible option families as tiny count-aware rows behind plain `showoptiongroups [QUERY]`, and `showoptiongroups` completion now reuses those same summary rows too; `ed.buffer-section-rows` groups buffers by visible picker bucket, `ed.buffer-section-summary-rows` exposes the same broad buckets as tiny count-aware rows behind plain `showbuffergroups [QUERY]`, and `showbuffergroups` completion now reuses those same count/sample summary rows too; exact `showbuffer NAME` completion now reuses `ed.buffer-detail-row` metadata for one named buffer, ordinary `buffer NAME` completion now reuses that same exact buffer row too, exact `showrecentdir DIR` completion now reuses `ed.recent-dir-detail-row` metadata for one visible recent-directory bucket, including the same sample-row `menu | info` truth visible in adjacent `recentdirpick` rows, exact `showmark NAME` completion now reuses `ed.mark-detail-row` metadata for one named mark, exact `showjump INDEX` completion now reuses `ed.jump-detail-row` metadata for one known jumplist entry, exact `helpjump QUERY` completion now reuses `ed.help-heading-detail-row` metadata for one resolved current-doc heading target, and exact `showplugin NAME` completion now reuses `ed.plugin-detail-row` metadata for one known plugin; `ed.plugin-section-rows` groups plugins by `Errors` / `Loaded` / `Available`, `ed.plugin-section-summary-rows` exposes those same broad buckets as tiny count-aware rows, and `showplugins` completion now reuses those same summary rows too; `ed.mark-section-rows` groups marks by owning buffer and `showmarkgroups` completion now reuses the same tiny summary rows, `ed.jump-section-rows` groups jumplist rows by `Current` / `Back` / `Forward`, `ed.binding-section-rows` groups current bindings by their winning mode (`Prompt`, `nav`, `Global`, etc.), `ed.doc-section-rows` groups docs rows by the repo's numbered doc families (`00–09 Project`, `10–19 Research`, `20–29 Language + VM`, and so on), `ed.helpnav-section-summary-rows` exposes the same current-doc heading/link buckets as tiny `[[label count sample_name sample_detail] ...]` rows behind plain `showhelpnav [QUERY]`, and `showhelpnav` completion now reuses those same summary rows too; `ed.recent-section-rows` / `ed.recent-dir-section-rows` group recent-file rows by project root or parent directory, `ed.recent-section-summary-rows` exposes the same project-root recent buckets as tiny `[[label count sample_name sample_detail] ...]` rows behind plain `showrecentgroups [QUERY]` and `showrecentgroups` completion now reuses those same summary rows, and `ed.recent-dir-section-summary-rows` does the same for the directory-grouped sibling behind plain `showrecentdirgroups [QUERY]` with `showrecentdirgroups` completion reusing them too. The live `commandpick`, `topicpick`, `bindingpick`, `bufferpick`, `markpick`, `jumppick`, `pluginpick`, `recentpick`, `recentdirpick`, and `helppick` prompts now flatten those same grouped structures too; when opened with an empty query, their initial browse window uses a tiny round-robin section budget so later visible sections stay represented instead of disappearing behind a large first bucket. Relative/path-light file rows now keep those same grouped surfaces human too: buffer sections fall back to `Buffers`, while recent-file sections fall back to `Recent Files`, instead of surfacing raw `.` placeholders when Micromax has no richer parent/project label. After rev371, the zero-result submit paths for the navigation/help side of that family stay explicit too: `bufferpick`, `pluginpick`, `recentpick`, `recentdirpick`, `helppick`, `helplinkpick`, `helpoutlinepick`, `helpnavpick`, `markpick`, and `jumppick` now report tiny `0 ...` summaries instead of collapsing back to `(none)`.
