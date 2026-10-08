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

We also treat editor navigation targets as completion candidates (e.g. `buffer NAME` and `markjump NAME` complete buffer/mark names) so workflows stay discoverable even before any UI exists.

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
- `set/setlocal/show/toggle/togglelocal`: option names (`Options.specs`)
- `set/setlocal OPTION VALUE`: small value completion for built-in bool/enum options
- `help`: command names + action names + visible Micromax word names
- `apropos`: the same searchable topic names as `help`
- `showcmd`: command names
- `showword`: visible Micromax word names from the current search order
- `showhook`: hook names visible in the current VM
- `plugin`: `list` / `reload` / `info` / `errors`; `plugin reload` completes only loaded plugin names, while `plugin info` / `plugin errors` complete all known plugin names
- `macro`: subcommands and macro slot names for `macro play NAME`
- `keymode` / `pushkeymode` / `pushkeymode-once` / `prefixmode`: known keymode names
- `showbindings`: `active` plus known keymode names
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
- command/action docs
- option kind + current/default values
- binding-RHS prefixes and embedded command docs
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
- action `TopicPrompt`
- hostcall `ed.topic-prompt`

The topic prompt is deliberately small:

- it preloads ranked command/action/word topic rows
- changing the query live-refreshes the ranked rows
- `Tab` / `Shift-Tab` cycle those topics
- `Enter` opens help for the selected/best-ranked topic
- history is stored under prompt kind `topic`
- the active ranked row is visible through `ed.prompt-current-row`
- grouped topic sections are available through `ed.topic-section-rows` / `ed.apropos-section-rows`
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

- `ed.topic-rows` ( -- rows ) — searchable command/action/word topic rows
- `ed.topic-section-rows` ( -- sections ) — grouped topic rows as `[[label [[name kind menu info] ...]] ...]`
- `ed.apropos-rows` ( query -- rows ) — the same rows ranked by deterministic subsequence match, with lower-priority fallback through topic summary/doc text and small multi-term/out-of-order matching across those fields
- `ed.apropos-section-rows` ( query -- sections ) — grouped apropos rows in the same shape
- `ed.topic-prompt` ( query -- ) — open the searchable topic/help prompt with a prefilled query
- `ed.binding-prompt` ( query -- ) — open the searchable current-binding prompt with a prefilled query
- `ed.binding-prompt-rows` ( query -- rows ) — searchable current-binding rows as `[[key kind menu info] ...]`
- `ed.binding-section-rows` ( query -- sections ) — grouped current-binding rows as `[[label [[key kind menu info] ...]] ...]`
- `ed.doc-section-rows` ( query -- sections ) — grouped docs rows as `[[label [[topic kind menu info] ...]] ...]`
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
- grouped palette sections are available through `ed.command-palette-section-rows`, and the live `commandpick` prompt now flattens those same sections too
- empty-query palette browse windows now budget rows across visible sections (`Recent Files`, `Recent`, `Commands`, `Actions`) so `Actions` are not hidden behind a large command bucket
- failed submit on a zero-result query now says `commandpick QUERY: 0 match(s)` instead of collapsing to `(none)`
- `Enter` on an action executes it
- `Enter` on a command opens the ordinary command prompt prefilled with `name `

The prompt uses the same aligned row shape as other searchable prompts: `[insert kind menu info]`. For `pluginpick`, the `menu` field now carries the same compact bracketed plugin-state summary dialect used by `plugin list` / `plugin reload` / `plugin info` / `plugin errors` (for example `[loaded, v1.0.0]` or `[error, deps:missingdep]`) instead of older free-form labels like `loaded` or `not loaded ... ERROR`. The grouped section shape is `[[label [[name kind menu info] ...]] ...]`. Navigation-heavy pickers now expose the same grouped shape too: `ed.command-palette-section-rows` groups palette rows by visible labels like `Recent Files` / `Recent` / `Commands` / `Actions`, `ed.buffer-section-rows` groups buffers by visible picker bucket, `ed.plugin-section-rows` groups plugins by `Errors` / `Loaded` / `Available`, `ed.mark-section-rows` groups marks by owning buffer, `ed.jump-section-rows` groups jumplist rows by `Current` / `Back` / `Forward`, `ed.binding-section-rows` groups current bindings by their winning mode (`Prompt`, `nav`, `Global`, etc.), `ed.doc-section-rows` groups docs rows by the repo's numbered doc families (`00–09 Project`, `10–19 Research`, `20–29 Language + VM`, and so on), and `ed.recent-section-rows` / `ed.recent-dir-section-rows` group recent-file rows by project root or parent directory. The live `commandpick`, `topicpick`, `bindingpick`, `bufferpick`, `markpick`, `jumppick`, `pluginpick`, `recentpick`, `recentdirpick`, and `helppick` prompts now flatten those same grouped structures too; when opened with an empty query, their initial browse window uses a tiny round-robin section budget so later visible sections stay represented instead of disappearing behind a large first bucket. Relative/path-light file rows now keep those same grouped surfaces human too: buffer sections fall back to `Buffers`, while recent-file sections fall back to `Recent Files`, instead of surfacing raw `.` placeholders when Micromax has no richer parent/project label. After rev371, the zero-result submit paths for the navigation/help side of that family stay explicit too: `bufferpick`, `pluginpick`, `recentpick`, `recentdirpick`, `helppick`, `helplinkpick`, `helpoutlinepick`, `helpnavpick`, `markpick`, and `jumppick` now report tiny `0 ...` summaries instead of collapsing back to `(none)`.
