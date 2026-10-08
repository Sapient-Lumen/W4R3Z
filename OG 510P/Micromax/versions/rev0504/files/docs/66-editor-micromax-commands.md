Rev503 note: project-grouped `recentpick` rows now also keep the menu-side MRU/state suffix, so `#N`, flags, and `@ line:col` survive the project-label rewrite.

Rev502 note: `recentpick` / `recentdirpick` now keep dedicated recent-file prompt rows as honest as adjacent `showrecent` and palette `Recent Files` rows, reusing the same tiny disk/action truth before Enter.

Rev500 note: `commandpick` / `ed.command-palette-rows QUERY` now also keep `Recent Files` rows honest about capability-gated saved-file disk truth, so ordinary MRU rows stop being the one remaining recent-file class that says neither `existing file` nor `new file`.

# Micromax-defined editor commands

Micromax is intended to become the **native** scripting/config/plugin language for the editor.
To make that real, scripts must be able to define new **command-bar commands**.

This doc describes the minimal “command bridge” that lets micromax code register commands and
provide prompt completion for them.

## Defining a command

Hostcall:

- `ed.cmd-add` — `( xt name doc -- ok )`

Semantics:

- Registers (or replaces) a command-bar command named `name`.
- When the user runs the command, the command xt is executed with:

  `( args -- ... )`

  where `args` is a list of strings.

- If the xt leaves an **int** or **bool** on top of the stack, it is treated as an ok flag.
  If it leaves no such value, ok defaults to 1.

- Best-effort provenance: the host attaches a span (via `vm.last_span`) so `help <cmd>` can
  display where the command was registered.

Related hostcalls:

- `ed.cmd-rm` — `( name -- ok )` remove a command by name
- `ed.cmds` — `( -- names )` list command names

### Example

A simple command that prints a message:

```forth
: hello-cmd ( args -- ok )
  drop
  "Hello from micromax" "ed.msg" hostcall
  1
;

' hello-cmd "hello" "Print a greeting" "ed.cmd-add" hostcall
```

Now the user can run:

```
> hello
```

And `help hello` will show the doc string and a best-effort “defined at …” location.

## Prompt completion hooks for custom commands

The editor’s command bar uses a **suggestion session** model (Tab/Shift-Tab cycles candidates).
Built-in commands have built-in completion rules, but plugins can provide extra candidates. Those built-in rows increasingly reuse the same tiny exact detail registers (`ed.command-detail-row`, `ed.word-detail-row`, `ed.doc-detail-row`, grouped summary rows, etc.), so prompt metadata stays honest for future scripts/UIs too.

Lookup order:

1) `ed.complete.<cmd>`
2) `ed.complete`

Contracts (best-effort):

```
( cmd tok_i prefix toks -- cands mode )
( cmd tok_i prefix toks -- cands rows mode )
```

- `cmd`: command name (string)
- `tok_i`: token index (0 = command name, 1 = first arg, …)
- `prefix`: current token prefix under the cursor (quote-aware)
- `toks`: token list (strings)
- `cands`: a list of insertion strings
- `rows`: optional completion metadata aligned with `cands`; each row is `[insert kind menu info]`
- `mode`:
  - 0 = no candidates
  - 1 = add candidates to built-ins
  - 2 = replace built-in candidates

### Example: complete the first argument

```forth
: ed.complete.mycmd ( cmd tok_i prefix toks -- cands mode )
  drop drop drop drop
  "alpha " list push
  "beta " swap push
  2  \ replace
;
```

### Example: return richer rows as well

```forth
: mycmd-row-alpha ( -- row )
  list "alpha " swap push "topic" swap push "alpha menu" swap push "alpha info" swap push
;

: mycmd-row-beta ( -- row )
  list "beta " swap push "topic" swap push "beta menu" swap push "beta info" swap push
;

: mycmd-rows ( -- rows )
  list mycmd-row-alpha swap push mycmd-row-beta swap push
;

: ed.complete.mycmd ( cmd tok_i prefix toks -- cands rows mode )
  drop drop drop drop
  "alpha " list push "beta " swap push
  mycmd-rows
  2  \ replace
;
```

With the prompt:

```
> mycmd
```

Tab will begin a session and Tab/Shift-Tab will cycle `alpha` / `beta`.

The active suggestion session also exposes best-effort metadata rows for future UIs/scripts:

- `ed.prompt-suggestion-rows` — `( -- rows )` returns `[[insert kind menu info] ...]`
- `ed.prompt-current-row` — `( -- row|[] )` returns the currently selected suggestion row `[insert kind menu info]`
- `ed.prompt-current-section` — `( -- label )` returns the current item's coarse section label
- `ed.prompt-current-preview` — `( -- s )` returns a compact preview string for the current item
- `ed.prompt-window` — `( lines -- m )` returns the shared picker-window model used by the minimal TUI

These rows are aligned with `ed.prompt-suggestions`. Built-in completions populate small annotations
for commands/actions/options/files/keymodes/etc., and plugin-provided completions may now return the same
row shape directly. When plugin rows are omitted, the editor falls back to its usual best-effort inferred metadata.

## Portability notes

- Commands and completion hooks are editor-host features, not part of the portable VM core.
- Candidate strings are plain text insertions. Quoting/spacing policy is up to the completer.

## Built-in word inspection

Custom commands are not the only prompt topics anymore: the editor now also treats **visible Micromax words** as help targets.

- `help NAME` first checks editor commands/actions through tiny shared detail rows, then falls back to the visible Micromax word named `NAME`
- `showcmd NAME` explicitly prints command doc/group/provenance detail, and command-bar completion now reuses that same exact command row so group/provenance stay visible while choosing one known command
- `command_detail_row(NAME)` / `ed.command-detail-row` expose that same command register headlessly as `[name doc group|0 [file line col]|0]`
- `showaction NAME` explicitly prints editor action docs and best-effort source provenance when the registered action callable comes from inspectable Python source
- `showoption NAME` explicitly prints exact option value/default/doc detail while keeping alias spellings visible
- `showbuffer NAME` explicitly prints exact current buffer state without switching focus
- `buffer NAME` command-bar completion now reuses that same exact buffer row, so switching one open buffer keeps active/dirty/readonly state, current position, section, and path visible while choosing the target
- `showrecent PATH` explicitly prints exact recent-file state without opening the file, and after rev501 it now also keeps the same tiny `existing file` / `new file` plus `current buffer` / `switch buffer` / `empty buffer @ 1:0` truth cues already used by adjacent palette recent-file rows when Micromax already knows them
- `showmark NAME` explicitly prints exact mark state without jumping through it
- `mark NAME` / `markjump NAME` command-bar completion now reuse that same exact mark row, so choosing one known mark keeps owning-buffer plus active/here/preview metadata visible instead of falling back to the older `buffer:line:col` prompt row
- `action_detail_row(NAME)` / `ed.action-detail-row` expose that same action register headlessly as `[name doc [file line col]|0]`
- `option_detail_row(NAME)` / `ed.option-detail-row` expose that same exact option register headlessly as `[query canonical value default kind local_override doc]`
- `showword NAME` explicitly prints the visible word's kind/effect/doc/provenance
- `showdoc TOPIC` explicitly prints the resolved docs page title/section/summary/path
- `showtopic NAME` explicitly prints exact generic help-topic detail without reopening docs: it resolves names with the same precedence as `help NAME` (`command` → `action` → visible `word` → `doc`) and then reuses that narrower exact formatter; command-topic completion now also keeps exact command group/provenance visible instead of collapsing back to a generic `help topic` prompt row, and word-topic completion now keeps exact word definition provenance visible too
- `showtopics [QUERY]` explicitly prints a tiny count-aware summary of the broad generic help-topic families (`Commands`, `Actions`, `Words`, `Docs`), and command-bar completion now reuses those same summary rows so choosing one visible family keeps count/sample metadata visible
- `showdocs [QUERY]` explicitly prints a tiny count-aware summary of the numbered docs families, and command-bar completion now reuses those same summary rows so choosing one visible docs bucket keeps count/sample metadata visible
- `showbuffergroups [QUERY]` explicitly prints a tiny count-aware summary of the current visible buffer buckets (`Help`, `Scratch`, project roots, parent directories, or `Buffers`), and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `showrecentgroups [QUERY]` explicitly prints a tiny count-aware summary of the current visible recent-file project buckets (`Recent Files` or detected project roots), and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `showrecentdirgroups [QUERY]` explicitly prints a tiny count-aware summary of the current visible recent-file directory buckets (parent directories), and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `showplugins [QUERY]` explicitly prints a tiny count-aware summary of the current plugin-state buckets (`Errors`, `Loaded`, `Available`), and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `showplugin NAME` prints one tiny exact plugin-state line for a known plugin without reopening the broader multi-line `plugin info NAME` / `plugin errors NAME` paths
- `showoptiongroups [QUERY]` explicitly prints a tiny count-aware summary of the current visible option families (`Capabilities`, `Editor`, `Rendering`, and so on), and command-bar completion now reuses those same summary rows so choosing one visible family keeps count/sample metadata visible
- `showpalettegroups [QUERY]` explicitly prints a tiny count-aware summary of the current command-palette buckets (`Recent Files`, `Recent`, `Commands`, `Actions`, and path-like `Directories` / `Files` / `Open` buckets when relevant), and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `showhook NAME` explicitly prints the installed handler chain for one hook, and `ed.hook-detail-row` now exposes the smaller exact first-stop row behind that same surface
- `showhooks [QUERY]` explicitly prints a tiny count-aware summary of the current live hook surface, and command-bar completion now reuses those same summary rows so choosing one visible hook keeps handler-count/sample/provenance metadata visible
- `showkeymode NAME` explicitly prints exact current state for one visible or currently active keymode
- `showbindingmodes [QUERY]` explicitly prints a tiny count-aware summary of the current reachable binding buckets grouped by winning mode, and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `showhelpheading` explicitly prints the resolved current docs heading under the primary cursor
- `showhelplink` explicitly prints the resolved current docs-link target under the primary cursor
- `showhelpnav [QUERY]` explicitly prints a tiny count-aware summary of the current docs page's heading/link navigation buckets, and command-bar completion now reuses those same summary rows so choosing one visible bucket keeps count/sample metadata visible
- `helpjump QUERY` explicitly jumps to one resolved heading on the current docs page, `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row` expose that exact `[topic title fragment level line col section]` target headlessly before the jump happens, and command-bar completion now reuses that same exact heading row so choosing one known target keeps title/level/fragment/section visible instead of falling back to a bare query string
- `word_detail_row(NAME)` / `ed.word-detail-row` expose that same visible-word register headlessly as `[name kind effect wordlist doc [file line col]|0 source|0]` so scripts and future UIs do not have to reconstruct it from VM internals or parse command text
- `doc_detail_row(TOPIC)` / `ed.doc-detail-row` expose that same exact-doc register headlessly as `[topic title summary section path]` so scripts and future UIs do not have to search `ed.doc-rows` or duplicate doc-target resolution policy
- `topic_detail_row(NAME)` / `ed.topic-detail-row` expose the exact generic help-topic register headlessly as `[name kind detail_row]`, where `detail_row` is the same narrower row already returned by `ed.command-detail-row` / `ed.action-detail-row` / `ed.word-detail-row` / `ed.doc-detail-row`, so scripts and future UIs do not have to search `ed.topic-rows` or branch before asking what one known topic resolves to
- `help_heading_detail_row(QUERY)` / `ed.help-heading-detail-row` expose the same exact current-doc heading target `helpjump QUERY` would use as `[topic title fragment level line col section]`, so scripts and future UIs do not have to reparse outline rows or reconstruct fragment/section context from picker text
- `current_help_heading_detail_row()` / `ed.help-current-heading-detail-row` expose the same exact current-doc heading `showhelpheading` uses as `[topic title fragment level line col section]`, so scripts and future UIs do not have to rescan `help_outline_rows()` or guess heading context from breadcrumbs alone
- `help_link_detail_row()` / `ed.help-link-detail-row` expose the same exact current-doc link target `showhelplink` / `helpfollow` / `helplinkcopy` would use as `[topic label target kind line col section]`, so scripts and future UIs do not have to rescan `ed.help-link-rows` or infer section/position context from picker text
- `help_nav_section_summary_rows(QUERY)` / `ed.helpnav-section-summary-rows` expose the same broad current-doc heading/link buckets `showhelpnav [QUERY]` uses as `[[label count sample_name sample_detail] ...]`, so scripts and future UIs do not have to open `helpnavpick` or walk every grouped section just to ask what navigation families are visible right now

- `macro status` explicitly prints one tiny combined runtime snapshot as `macro status: STATE [NAME (N step[s])], M macro(s), ...`
- `macro_status_rows()` / `ed.macro-status-rows` expose that same combined register headlessly as `[[status state name steps saved_count] [saved name steps] ...]`, so scripts and future UIs do not have to stitch together `ed.macro-recording?` / `ed.macro-playing?` plus `ed.macro-inventory-rows`

This means plugin-defined commands and ordinary Micromax words can now share the same command-bar discovery surface without needing a separate browser yet.

## Searchable topic rows

The editor now also exposes the broader discovery surface used by `apropos QUERY`:

The human-facing `apropos QUERY` command now keeps that discovery inventory count-aware too: empty searches say `apropos QUERY: 0 topic(s)`, non-empty searches start with `apropos QUERY: N topic(s), ...`, and the existing preview rows still end with `... (+N more)` when only the first slice is shown. Generic `help QUERY` / `apropos QUERY` completion now advertises docs topics from that same shared substrate instead of hiding them behind `help docs` / `showdoc`, resolved command topics keep their exact group/provenance metadata in the prompt info slot instead of flattening back to plain `search topic`, resolved action topics now keep best-effort source provenance visible there too, and resolved word topics now keep exact definition provenance visible there too.


- `ed.topic-rows` — `( -- rows )` returns `[[name kind menu info] ...]` for commands, actions, visible Micromax words, and docs topics
- `ed.topic-detail-row` — `( name -- row|0 )` returns one exact generic help-topic row as `[name kind detail_row]`, reusing the same narrower detail row for the resolved kind
- `ed.topic-section-rows` — `( -- sections )` returns grouped topic rows as `[[label [[name kind menu info] ...]] ...]`
- `ed.topic-section-summary-rows` — `( -- rows )` returns tiny count-aware topic-section rows as `[[label count sample_name sample_detail] ...]`
- `ed.apropos-section-summary-rows` — `( query -- rows )` returns the same tiny summary shape for one generic apropos query
- `ed.apropos-rows` — `( query -- rows )` returns the same rows ranked by the editor's tiny deterministic subsequence matcher; name matches win first, then summary/doc text can rescue broader discovery queries, multi-term/out-of-order queries are matched term-by-term across those fields, and ties still keep commands/actions/words ahead of docs
- `ed.apropos-section-rows` — `( query -- sections )` returns the same grouped shape for a ranked query
- `ed.buffer-section-rows` — `( query -- sections )` groups buffer picker rows by visible picker bucket (`Help`, `Scratch`, project roots, `Buffers`)
- `ed.buffer-detail-row` — `( name -- row|0 )` returns one exact buffer row as `[name position active dirty readonly section path line_count]` behind plain `showbuffer NAME`
- `ed.mark-detail-row` — `( name -- row|0 )` returns one exact mark row as `[name buffer position preview active here]` behind plain `showmark NAME`
- `ed.jump-detail-row` — `( n -- row|0 )` returns one exact jumplist row as `[query index lane depth buffer position preview]` behind plain `showjump INDEX`
- `ed.buffer-section-summary-rows` — `( query -- rows )` returns tiny count-aware buffer-bucket rows as `[[label count sample_name sample_detail] ...]` behind plain `showbuffergroups [QUERY]`
- `ed.plugin-section-rows` — `( query -- sections )` groups plugin picker rows by `Errors` / `Loaded` / `Available`
- `ed.plugin-detail-row` — `( name -- row|0 )` returns one exact plugin row as `[query name state version deps error_count detail]` behind plain `showplugin NAME`
- `ed.plugin-section-summary-rows` — `( query -- rows )` returns tiny count-aware plugin-state rows as `[[label count sample_name sample_detail] ...]`
- `ed.command-palette-section-summary-rows` — `( query -- rows )` returns tiny count-aware command-palette bucket rows as `[[label count sample_name sample_detail] ...]` behind plain `showpalettegroups [QUERY]`
- `ed.hook-detail-row` — `( name -- row|0 )` returns one exact hook row as `[query name handler_count sample_handler|0 sample_detail|0 [file line col]|0]` behind plain `showhook NAME`
- `ed.hook-summary-rows` — `( query -- rows )` returns tiny shared hook-summary rows as `[[name handler_count sample_handler|0 [file line col]|0] ...]`
- `hook-state` — `( name -- row|0 )` convenience word for the same exact hook row surface
- `ed.mark-section-rows` — `( query -- sections )` groups marks by owning buffer
- `ed.jump-section-rows` — `( query -- sections )` groups jumplist rows by `Current` / `Back` / `Forward`
- `ed.binding-section-rows` — `( query -- sections )` groups current bindings by winning mode (`Prompt`, active mode names like `nav`, `Global`)
- `ed.doc-section-rows` — `( query -- sections )` groups docs picker rows by numbered docs family (`00–09 Project`, `10–19 Research`, `20–29 Language + VM`, ...)
- `ed.doc-section-summary-rows` — `( query -- rows )` returns tiny count-aware docs-family rows as `[[label count sample_name sample_detail] ...]`
- docs picker/info summaries now prefer the first meaningful line after the document's primary heading, so rev-note-heavy archive pages still preview as the actual document instead of top-of-file bookkeeping
- `ed.recent-detail-row` — `( path -- row|0 )` returns one exact recent-file row as `[query path index position active open dirty readonly section detail disk_truth action_truth]` behind plain `showrecent PATH`
- `ed.recent-dir-detail-row` — `( dir -- row|0 )` returns one exact recent-directory row as `[query directory count active_count open_count dirty_count readonly_count sample_path sample_detail sample_menu sample_info]` behind plain `showrecentdir DIR`
- `ed.recent-section-rows` — `( query -- sections )` groups recent-file rows by project root; `recentpick` now reuses those same buckets live too, and after rev503 the project-label rewrite also preserves the menu-side `#N`, flags, and `@ line:col` suffix when one visible row already has exact MRU metadata
- `ed.recent-section-summary-rows` — `( query -- rows )` returns tiny count-aware recent-file project-bucket rows as `[[label count sample_name sample_detail] ...]` behind plain `showrecentgroups [QUERY]`
- `ed.recent-dir-section-summary-rows` — `( query -- rows )` returns tiny count-aware recent-file directory-bucket rows as `[[label count sample_name sample_detail] ...]` behind plain `showrecentdirgroups [QUERY]`
- `ed.recent-dir-section-rows` — `( query -- sections )` groups recent-file rows by parent directory; `recentdirpick` now reuses those same buckets live too

The same picker family now also keeps failed submits explicit on the human side: `bufferpick`, `pluginpick`, `recentpick`, `recentdirpick`, `helppick`, `helplinkpick`, `helpoutlinepick`, `helpnavpick`, `markpick`, and `jumppick` report tiny `0 ...` summaries on zero-result submit instead of collapsing to `(none)`.

This is the intended substrate for future picker-style UIs and for LLM/tooling integrations that want a single searchable model of the live editor environment. `help NAME` also uses this surface as a fallback when no exact topic exists, so typo recovery and fuzzy discovery share one ranking path.

The editor now also exposes a tiny canonical interaction flow on top of those rows:

- command `topicpick [QUERY]`
- action `TopicPrompt`
- hostcall `ed.topic-prompt` — `( query -- )` opens the searchable topic/help prompt prefilled with `query`

That prompt reuses the normal prompt suggestion-session model: changing the query live-refreshes ranked topics, `Tab` / `Shift-Tab` cycle them, and `Enter` opens help for the selected/best-ranked topic. The same ranking path now also supports small multi-term/out-of-order queries. The live `topicpick` prompt now flattens the same grouped topic families already exposed through `ed.topic-section-rows` / `ed.apropos-section-rows`, and empty-query browse windows budget rows across `Commands` / `Actions` / `Words` / `Docs` so docs stay visible in the same first-class discovery loop instead of requiring a docs-only command first. Failed submit on a zero-result query now says `topicpick QUERY: 0 topic(s)` instead of collapsing to `(none)`. Scripts/UIs can inspect the active row through `ed.prompt-current-row`, grouped sections through `ed.topic-section-rows` / `ed.apropos-section-rows`, lighter section summaries through `ed.topic-section-summary-rows` / `ed.apropos-section-summary-rows`, and preview text through `ed.prompt-current-preview`.


## Searchable command/action palette

The editor now also exposes an execution-oriented search surface over **commands + actions**:

- `commandpick [QUERY]` — open the searchable command/action palette; command-bar completion for exact command/action targets now keeps the same tiny doc/group/provenance metadata those narrower inspection surfaces already trust, live `Recent Files` rows now also keep exact MRU index/state/detail metadata from `recent_detail_row(PATH)` instead of collapsing back to basename + parent, those same rows now append capability-gated `existing file` when the remembered path still exists on disk, append `new file` when it no longer exists, and existing live-buffer MRU rows now also append `current buffer` / `switch buffer`, visible file-side path-completion `openpath` rows now keep best-effort recent/open/parent-path context instead of a blank info slot, already-open file targets append a tiny `current buffer` / `switch buffer` cue, visible directory rows now also reuse exact recent-directory count/state from `recent_dir_detail_row(DIR)` when one folder target is already known, and the explicit typed `Open` row now keeps exact target context plus the same tiny open-buffer cue, a small `drill down` cue for live directory targets, and capability-gated `existing file` / `directory` / `new file` truth — including already-open unsaved buffers that should still say `new file`, while parsecursor-shaped directory queries now still honor that visible `directory | drill down` row on submit, parsecursor-shaped relative file queries such as `draft.md:3:7` now still keep the same typed `Open` row too, parsecursor-shaped extensionless existing targets such as `guide:2` and `intro:2` now still keep that typed row when the parsed target already resolves to one real directory or file, parsecursor-shaped partial file queries such as `guide/i:2` now keep visible completion rows like `guide/intro.md:2` too, parsecursor-shaped partial directory queries such as `guide/s:2` now keep visible completion rows like `guide/sub/:2` too, partial extensionless current-directory queries such as `gu:2` and `intr:2` now keep visible completion rows like `guide/:2` and `intro:2` too, parsecursor-shaped existing-file targets that are not already open now append a tiny `cursor line:col` request cue, parsecursor-shaped new-file targets like `draft.md:3:7` now append `empty buffer @ 1:0` when Micromax already knows the file does not exist yet, and parsecursor-shaped file queries that already map to an open buffer still append the exact `goto line:col` cue
- `CommandPalette` — action form of the same prompt
- `ed.command-palette` — hostcall form
- `ed.command-palette-rows` — ranked rows in `[name kind menu info]` shape
- `ed.command-palette-section-rows` — grouped rows as `[[label [[name kind menu info] ...]] ...]`

Behavior:

- it uses the same tiny ranking + row metadata substrate as `topicpick`
- successful palette submissions are remembered in a small palette-local MRU
- empty queries surface a `Recent Files` section (opens files immediately) and then the palette-local command/action MRU as `Recent`
- path-like queries surface `Directories` / `Files` / `Open`, visible file rows now keep best-effort recent/open context or a small parent-directory cue so filesystem completion stays honest beside MRU rows, already-open file targets append a tiny `current buffer` / `switch buffer` cue, directory rows append a small `drill down` cue, and the exact `Open` row now tells you whether Enter is aiming at an existing file, an already-open buffer target, a directory drill-down, or a new file path when Micromax is allowed to inspect that target — including unsaved open buffers that still need to say `new file`, while parsecursor-shaped directory queries now still drill down instead of failing against the raw suffixed text, parsecursor-shaped relative file queries such as `draft.md:3:7` now still surface the same typed `Open` row too, parsecursor-shaped extensionless existing targets such as `guide:2` and `intro:2` now still surface that typed row too when the parsed target already resolves to one real directory or file, parsecursor-shaped partial file queries such as `guide/i:2` now also keep visible completion rows like `guide/intro.md:2`, parsecursor-shaped partial directory queries such as `guide/s:2` now also keep visible completion rows like `guide/sub/:2`, partial extensionless current-directory queries such as `gu:2` and `intr:2` now also keep visible completion rows like `guide/:2` and `intro:2`, parsecursor-shaped existing-file targets that are not already open now append a tiny `cursor line:col` request cue, parsecursor-shaped new-file targets like `draft.md:3:7` now append `empty buffer @ 1:0` when Micromax already knows the file does not exist yet, and parsecursor-shaped file queries that already map to an open buffer still say the exact `goto line:col` landing
- equivalent matches can use palette recency as a tiebreaker
- actions execute immediately when submitted
- commands do **not** execute immediately; they reopen the ordinary command bar with `name ` prefilled so the user can add arguments
- failed submit on a zero-result query now says `commandpick QUERY: 0 match(s)` instead of collapsing to `(none)`
- the same `ed.prompt-current-row` / `ed.prompt-current-preview` surfaces apply here too

## Searchable current-binding prompt

The editor now also exposes a searchable prompt over the **currently reachable** keymap:

- command `bindingpick [QUERY]`
- action `BindingPrompt`
- hostcall `ed.binding-prompt`

That prompt reuses the normal prompt suggestion-session model: changing the query live-refreshes ranked bindings, `Tab` / `Shift-Tab` cycle them, and `Enter` runs `showkey KEY` for the selected/best-ranked binding. Failed submit on a zero-result query now says `bindingpick QUERY: 0 binding(s)` instead of collapsing to `(none)`. Failed `showkey KEY` lookups now also stay explicit as `showkey: no such binding: KEY` instead of falling back to a raw `(unbound)` placeholder. The row substrate is exposed separately through `ed.binding-prompt-rows`, where each row is `[key kind menu info]` and `menu` includes the winning mode + action-spec while `info` carries the resolved human description. Grouped winning-mode sections are available through `ed.binding-section-rows`, the lighter broad summary register now lives at `ed.binding-section-summary-rows` behind plain `showbindingmodes [QUERY]`, and `ed.prompt-current-section` / `ed.prompt-current-preview` now reuse those same visible labels instead of a generic `Binding` bucket. Direct single-binding inspection now also has a tiny named sibling through `ed.binding-detail-row`, which reuses the same resolved mode/action/description/group/span row behind plain `showkey KEY`. Command-bar completion for `showkey KEY` now also reuses that same exact binding row, so one reachable key can be chosen directly with its winner mode/action/group/description still visible.
Direct single-keymode inspection now also has a tiny named sibling through `ed.keymode-detail-row`, which reuses the same exact active/known/once/binding-count/sample-binding row behind plain `showkeymode NAME`.
Command-bar completion for `showkeymode NAME`, `showbindings MODE`, `keymode`, `pushkeymode`, `pushkeymode-once`, and `prefixmode` now also reuses that same exact keymode row, so picking a mode keeps active/once/known-or-internal state, binding counts, and one sample binding visible instead of falling back to a generic placeholder.
- missing `showcmd NAME` / `showaction NAME` / `showoption NAME` / `showbuffer NAME` / `showmark NAME` / `showword NAME` / `showdoc TOPIC` lookups now fail plainly as `showcmd: no such command: NAME` / `showaction: no such action: NAME` / `showoption: no such option: NAME` / `showbuffer: no such buffer: NAME` / `showmark: no such mark: NAME` / `showjump: no such jump: INDEX` / `showrecent: no such recent file: PATH` / `showrecentdir: no such recent directory: DIR` / `showword: no such word: NAME` / `showdoc: no such doc: TOPIC` instead of placeholder strings; `showhelpheading` keeps the same typed misses for docs-heading context as `showhelpheading: not in a docs buffer` or `showhelpheading: no heading under cursor`, `showhelplink` keeps the same typed misses for docs-link context as `showhelplink: not in a docs buffer` or `showhelplink: no link under cursor`, and `showhelpnav [QUERY]` keeps the same typed current-doc boundary as `showhelpnav: not in a docs buffer`, and `showkeymode NAME` now keeps the same typed miss as `showkeymode: no such keymode: NAME`
- mistyped ordinary command-bar commands now fail plainly as `command: no such command: NAME` instead of the older `Unknown command: NAME`
- known commands that raise unexpectedly now fail as `command NAME: error: DETAILS` instead of a generic `Command error: ...`
- Micromax-defined commands registered via `ed.cmd-add` now keep that same `command NAME: error: DETAILS` prefix on Micromax/runtime faults too, while preserving formatted span/trace detail after the prefix

  - `help NAME` shows command/action/micromax-word help and falls back to opening a docs topic when possible
  - misses are now typed explicitly too: `help docs TOPIC` -> `help docs: no such doc: TOPIC`; ordinary misses -> `help: no such topic: QUERY`

## Built-in inspection follow-ups

Recent trust/flow follow-ups keep the command bar useful as a side-effect-free inspection surface, not just a mutating action surface. In particular, marks now have both exact and broad inspection siblings: `showmark NAME` reports one named mark without jumping, while `showmarkgroups [QUERY]` reports tiny count-aware owning-buffer buckets that reuse the same grouped state behind `markpick`; command-bar completion for `showmarkgroups` now reuses those same tiny summary rows too so choosing one visible bucket keeps count/sample metadata visible.
