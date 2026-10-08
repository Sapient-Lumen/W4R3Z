# Host API (stable surface for editor scripting)

Micromax scripts should interact with the outside world only through **hostcalls**.
Hosts choose what to expose; scripts can probe capabilities via `host.feature?`.

## Versioning

- `host.api-version` returns a string like `"0.1"`.
- Hosts SHOULD expose features as strings in `host.features`.

A script may:
- check `host.api-version` for coarse compatibility
- check `host.feature?` for optional capabilities
- (optionally) call `host.capabilities` for a small registry with descriptions

## Design principles

- **Small, orthogonal primitives**: prefer a few powerful hostcalls over many narrow ones.
- **Portable stack types**: hostcalls return only ints/strings/lists/cells/quotations (no opaque objects).
- **Undo correctness**: editor mutations should record undo in a predictable way.
- **Future per-plugin VMs**: hostcalls must not assume global shared VM state.


## Environment conventions (rev64)

These are *not* hostcalls, but agreed-upon conventions used by the reference editor and VM:

- `$MICROMAX_INIT` — override the user init/rc file path (default: `~/.config/micromax/init.mx`).
- `$MICROMAX_PATH` — module search path for `include`/`require` (split by `os.pathsep`, like `$PATH`).

See: `docs/87-editor-config.md` and `docs/88-require-and-paths.md`.
## Editor hostcalls (micromax-editor feature)

Current implemented hostcalls (rev63 reference editor):

### Reference host helpers

These are hostcalls (not VM primitives) installed by the editor embedding and
advertised via `host.feature?`:

- feature: `"mx.strings"`
- hostcalls/words: `s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower s-format (plus `format` alias word)`

### Capability registry (rev78)

Hosts can expose a tiny registry so scripts (and humans) can discover what
optional/unsafe features exist:

- `host.capabilities` ( -- rows ) returns `[[feature option kind enabled doc] ...]`

The reference editor gates unsafe surfaces behind `cap.*` options.
See: `docs/32-capabilities.md`.

Currently registered unsafe capabilities:

- `ed.open-url` — open external URLs (used by the docs browser)
- `ed.shell` — run a shell command and capture output
- `ed.clipboard-export` — allow scripts to export clipboard to system clipboard via privileged UI backends (OSC 52 / external tools)
- `ed.clipboard-import` — allow scripts to import/read system clipboard via external tools
- `ed.persist` — allow editor-owned persistence files (recent/history) to be read/written
- `ed.open` — open a file from disk into a buffer
- `ed.save` — save the current buffer to disk
- `ed.fs-read` — read an arbitrary file from disk as UTF-8 text (capability-gated; optional `cap.fs-root` sandbox)
- `ed.fs-list` — list directory entries from disk (capability-gated; optional `cap.fs-root` sandbox)
- `ed.fs-stat` — stat a path (exists/kind/size/mtime) (capability-gated; optional `cap.fs-root` sandbox)

### Messaging + command surface
- `ed.msg` ( "s" -- ) show a message
- `ed.messages` ( -- msgs ) return current message list as ["...", ...]
- `ed.last-message` ( -- "s" ) return last message (or "")
- `ed.pop-message` ( -- "s" ) pop oldest message (or "")
- `ed.clear-messages` ( -- ) clear message list
- `ed.with-messages` ( q -- ok ) run quotation and restore message log
- `ed.capture-messages` ( q -- msgs ok ) capture messages emitted by quotation
- `ed.command` ( "cmdline" -- ok )
- `ed.cmd-add` ( xt "name" "doc" -- ok ) define or replace a command-bar command
- `ed.cmd-rm` ( "name" -- ok ) remove a command-bar command
- `ed.cmds` ( -- names ) list command names
- `ed.cmd-rows` ( -- [[name doc group|0 [file line col]|0] ...] ) list command metadata
- `ed.command-edit` ( "prefill" -- ) open command prompt with text
- `ed.command-palette` ( query -- ) open the searchable command/action palette prefilled with `query`
- `ed.command-palette-rows` ( query -- rows ) ranked command/action palette rows as `[[name kind menu info] ...]`
- `ed.command-palette-section-rows` ( query -- sections ) grouped palette rows as `[[label [[name kind menu info] ...]] ...]`; empty queries can include a `Recent` section
- `ed.run` ( "action-chain" -- ok )
- `ed.bind` ( "key" "action-chain" -- )
- `ed.bind-mode` ( "mode" "key" "action-chain" -- ) bind a key in a named keymap mode
- `ed.bind-doc` ( "key" "doc" -- ok ) attach/replace a human description for a global binding
- `ed.bind-mode-doc` ( "mode" "key" "doc" -- ok ) attach/replace a human description for a mode binding
- `ed.bind-prefix` ( "key" "mode" doc|0 -- ok ) bind a global prefix key that enters a one-shot mode
- `ed.bind-mode-prefix` ( "owner-mode" "key" "mode" doc|0 -- ok ) bind a mode-local prefix key that enters a one-shot mode
- `ed.unbind` ( "key" -- ok ) remove a global key binding
- `ed.unbind-mode` ( "mode" "key" -- ok ) remove a mode-specific key binding
- `ed.bindings` ( -- [[key action-spec [file line col]|0] ...] ) list bindings with best-effort provenance
- `ed.binding-detail` ( -- [[key action-spec group|0 [file line col]|0] ...] ) list binding metadata
- `ed.binding-modes` ( -- [[mode key action-spec group|0 [file line col]|0] ...] ) list bindings with mode metadata
- `ed.binding-rows-for` ( mode|0 -- [[key action-spec group|0 [file line col]|0] ...] ) list bindings for one mode
- `ed.binding-info-for` ( mode|0 -- [[key action-spec desc|0 group|0 [file line col]|0] ...] ) list bindings for one mode with human descriptions
- `ed.available-bindings` ( -- [[mode key action-spec group|0 [file line col]|0] ...] ) list precedence-resolved current bindings
- `ed.available-binding-info` ( -- [[mode key action-spec desc|0 group|0 [file line col]|0] ...] ) list precedence-resolved current bindings with human descriptions
- `ed.resolve-key` ( key -- [mode key action-spec group|0 [file line col]|0] | 0 ) resolve one key through active keymodes
- `ed.resolve-key-info` ( key -- [mode key action-spec desc|0 group|0 [file line col]|0] | 0 ) resolve one key with human description through active keymodes
- `ed.keymode!` ( mode|0 -- ) set active key mode
- `ed.keymode@` ( -- mode|0 ) query active key mode
- `ed.keymode-push` ( "mode" -- ) push active key mode
- `ed.keymode-push-once` ( "mode" -- ) push a one-shot active key mode
- `ed.prefix-mode` ( "mode" -- ok ) enter a one-shot prefix mode and immediately emit `whichkey`
- `ed.keymode-pop` ( -- mode|0 ) pop active key mode
- `ed.keymodes` ( -- active known ) list active mode stack and known binding modes
- `ed.keymode-rows` ( -- active known ) list `[[mode once?] ...]` plus known binding modes
- `ed.press-key` ( "key" -- ok ) resolve + execute a bound key through active keymodes
- `ed.group!` ( group|0 -- ) set default editor registration group
- `ed.group@` ( -- group|0 ) query default editor registration group

### Status / infobar model
- `ed.status` ( -- m ) return a portable statusline/infobar map (`keymode_once` included when a one-shot mode is active)
- `ed.status-summary` ( -- "s" ) return a compact summary string for debug/headless use
- `ed.statusfmt` ( "template" -- "s" ) render a statusformat template against the current status model
- `ed.statusline-text` ( width -- "s" ) render the full statusline string for a given width
- `ed.filetype` ( -- "s" ) return detected filetype for the active buffer

### Viewport + line access
- `ed.viewport` ( -- m ) return viewport map `{top_line,top_subline,left_col,height,width}` (height/width may be 0 until a UI sets them)
- `ed.viewport!` ( top left height width -- ) set viewport model and keep the cursor visible
- `ed.with-viewport` ( q -- ok ) run quotation and then restore the viewport model
- `ed.line` ( line -- "s" ) get one buffer line (0-based; clamped)
- `ed.lines` ( start count -- lines ) get a range of lines as `["...", ...]`

Current status map fields include:

- `mode`, `keymode`, `buffer_name`, `file_name`, `filetype`, `path`, `cwd`
- `dirty`, `readonly`
- `line`, `col`, `display_line`, `display_col`, `position`
- `line_count`, `cursor_count`, `primary_cursor_index`
- `selection_count`, `primary_selection_chars`
- `prompt_kind`, `prompt_text`, `prompt_cursor`
- `prompt_current_insert`, `prompt_current_kind`, `prompt_current_menu`, `prompt_current_info`
- `prompt_current_section`, `prompt_current_preview`
- `viewport_top_line`, `viewport_left_col`, `viewport_height`, `viewport_width`
- `last_message`
- `macro_recording`, `macro_playing`, `macro_name`

### Prompt interaction
- `ed.prompt-kind` ( -- "kind" )
- `ed.prompt-text` ( -- "text" )
- `ed.prompt-set` ( "text" -- ) set active prompt text; `find` keeps `incsearch`, and searchable `palette` / `topic` / `binding` prompts now live-refresh ranked rows
- `ed.prompt-submit` ( -- ok )
- `ed.prompt-suggestions` ( -- suggs ) list of completion candidates
- `ed.prompt-suggestion-rows` ( -- rows ) aligned `[[insert kind menu info] ...]` metadata for active suggestions
- `ed.prompt-current-row` ( -- row|[] ) current selected suggestion row as `[insert kind menu info]`
- `ed.prompt-current-section` ( -- "label" ) coarse section for the current item (`Command`, `Action`, `Word`, `Binding`, or `""`)
- `ed.prompt-current-preview` ( -- "text" ) compact current-item preview string
- `ed.prompt-suggest-index` ( -- i ) current candidate index (-1 if none)
- `ed.prompt-complete` ( dir -- ok ) cycle completion (dir>=0 forward, dir<0 backward)
- `ed.prompt-clear-suggestions` ( -- ok ) clear suggestion session
- `ed.topic-rows` ( -- rows ) searchable command/action/word topic rows
- `ed.topic-section-rows` ( -- sections ) grouped topic rows as `[[label [[name kind menu info] ...]] ...]`
- `ed.apropos-rows` ( query -- rows ) ranked topic rows for a search query
- `ed.apropos-section-rows` ( query -- sections ) grouped apropos rows in the same shape
- `ed.topic-prompt` ( query -- ) open the searchable topic/help prompt prefilled with `query`; ranked rows refresh as the query changes
- `ed.binding-prompt` ( query -- ) open the searchable current-binding prompt prefilled with `query`; ranked rows refresh as the query changes
- `ed.binding-prompt-rows` ( query -- rows ) searchable current-binding rows as `[[key kind menu info] ...]`


Prompt-completion hook note: Micromax completion words may return either `( cmd tok_i prefix toks -- cands mode )` or `( cmd tok_i prefix toks -- cands rows mode )`; `rows` uses the same `[insert kind menu info]` shape returned by `ed.prompt-suggestion-rows`. Future UIs can pair those rows with `ed.prompt-current-row`, `ed.prompt-current-preview`, the grouped topic section hostcalls, and `ed.binding-prompt-rows` without redoing ranking.

### Inputs (for parameterized actions)

`editor.input` is a transient host-owned dict used to pass parameters into actions.
Macros snapshot it per action step.

- `ed.input-set` ( key val -- ) set input value
- `ed.input-get` ( key -- val|0 ) get input value (or 0 if missing)
- `ed.input-keys` ( -- keys ) sorted keys
- `ed.input` ( -- [[key val] ...] ) current inputs as pairs
- `ed.input-clear` ( -- ) clear input dict

### Macros

- `ed.macro-names` ( -- names )
- `ed.macro-get` ( name -- steps )
- `ed.macro-set` ( steps name -- )
- `ed.macro-record` ( name -- ok )
- `ed.macro-stop` ( -- ok )
- `ed.macro-cancel` ( -- ok )
- `ed.macro-play` ( name n -- ok )
- `ed.macro-recording?` ( -- flag )
- `ed.macro-playing?` ( -- flag )

### Basic buffer IO
- `ed.open` ( "path" -- ok err ) open a file into a buffer (**capability-gated** by `cap.fs-open`; respects `cap.fs-root` when set)
- `ed.save` ( -- ok err ) save the current buffer (**capability-gated** by `cap.fs-save`; respects `cap.fs-root` when set)
- `ed.text` ( -- "text" )
- `ed.set-text` ( "text" -- )

### Recent files
- `ed.recent` ( -- xs ) return recent file paths (MRU order)
- `ed.recent-clear` ( -- ) clear the recent file list
- `ed.recent-section-rows` ( query -- sections ) grouped recent rows by project root (for pickers)
- `ed.recent-dir-section-rows` ( query -- sections ) grouped recent rows by directory

### Docs / help buffers
- `ed.doc-rows` ( -- rows ) docs picker rows as `[[topic kind menu info] ...]`
- `ed.help-doc` ( "topic" -- ok ) open a docs page into a protected help buffer
- `ed.help-follow` ( -- ok ) follow a markdown link under cursor in a help buffer
- `ed.help-back` ( -- ok ) go back to the previous docs help page
- `ed.help-link-rows` ( query -- rows ) markdown links in the current docs buffer as `[[label kind target info] ...]`
- `ed.helplink-section-rows` ( query -- sections ) grouped markdown links as `[[label [[label kind target info] ...]] ...]` (grouping controlled by `help.linksections`)
- `ed.help-outline-rows` ( query -- rows ) markdown headings in the current docs buffer as `[[title kind level info] ...]`
- `ed.helpnav-section-rows` ( query -- sections ) grouped headings + grouped links as `[[label [[name kind menu info] ...]] ...]`

### Editor lifecycle hooks (VM hooks, not hostcalls)

The editor defines hook words you can attach handlers to with `hook-add`:

- `ed.on-open` ( "buffer" "path" "filetype" -- )
- `ed.on-save` ( "buffer" "path" -- )
- `ed.on-change` ( "buffer" "action" -- )

See `docs/86-editor-lifecycle-hooks.md` for stack contracts and the per-handler
stack isolation rule.



### Plugins
- `plugin.list` ( -- xs ) return loaded plugin names
- `plugin.reload` ( "name" -- ok ) reload a plugin by name (ok is 0/1)
- `plugin.errors` ( -- xs ) return captured plugin load errors as `[[name,err] ...]`

### Buffers + marks (navigation helpers)
- `ed.buffers` ( -- names ) list open buffer names
- `ed.active-buffer` ( -- "name" ) current active buffer name (or "")
- `ed.set-active-buffer` ( "name" -- ok ) switch active buffer
- `ed.with-buffer` ( "name" q -- ok ) switch to buffer for duration of quotation, then restore

- `ed.marks` ( -- [[name buffer line col] ...] ) list named marks
- `ed.mark-set` ( "name" -- ok ) set a named mark at the primary cursor
- `ed.mark-jump` ( "name" -- ok ) jump to a named mark (pushes jumplist)

### Cursor + selection (primary cursor)
- `ed.cursor` ( -- line col )
- `ed.set-cursor` ( line col -- )
- `ed.has-selection` ( -- flag )
- `ed.selection` ( -- "text" )
- `ed.clear-selection` ( -- )

### Multi-cursor + selections
- `ed.cursors` ( -- [[line col] ...] ) cursor list in document order
- `ed.set-cursors` ( [[line col] ...] -- ) set cursor list, clear selections
- `ed.primary` ( -- i ) primary cursor index
- `ed.set-primary` ( i -- ) set primary cursor index
- `ed.selections` ( -- [[aL aC cL cC] ...] ) selections per cursor (directed), [] if none
- `ed.set-selections` ( sels -- ) set directed selections per cursor (cursor positions may update)
- `ed.selection-range` ( -- [line1 col1 line2 col2] | [] ) normalized primary selection range
- `ed.set-selection-range` ( line1 col1 line2 col2 -- ) set primary selection from a range (clamped)

### Cursor/selection state snapshots

These are *state* tools (cursor+selection only) and do not mutate buffer text.

- `ed.cursorstate` ( -- state ) where `state` is `[primary [[id line col aL aC] ...]]` and `aL/aC` are `-1/-1` if no anchor
- `ed.set-cursorstate` ( state -- ) restore cursor/selection state
- `ed.with-cursorstate` ( q -- ok ) run quotation and then restore cursor/selection state (save-excursion style)

### Jumplist (navigation history)

These are navigation tools (not undo): a small per-buffer history of cursor/selection states.

- `ed.push-jump` ( -- ok ) save current cursor/selection state to jumplist
- `ed.jump-back` ( -- ok )
- `ed.jump-forward` ( -- ok )
- `ed.jump-info` ( -- [index size] ) current index and total size
- `ed.clear-jumps` ( -- )

### Orthogonal text primitives (undoable)
- `ed.range-text` ( line1 col1 line2 col2 -- "text" )
- `ed.replace-range` ( line1 col1 line2 col2 "text" -- line col )
- `ed.delete-range` ( line1 col1 line2 col2 -- line col )
- `ed.replace-selections` ( replacements -- line col )

### Undo + grouping
- `ed.with-undo` ( "desc" q -- ok ) execute quotation as a single undo step (transactional for active buffer)

### Clipboard
- `ed.clipboard` ( -- "text" )
- `ed.set-clipboard` ( "text" -- )
- `ed.clipboard-items` ( -- items kind ) where `kind` is `"items"` or `"lines"`
- `ed.set-clipboard-items` ( items kind -- )

### Selection recovery stack
- `ed.push-selections` ( -- ) save current cursor+selection state
- `ed.pop-selections` ( -- ok ) restore last saved cursor+selection state
- `ed.clear-saved-selections` ( -- )

### Search
- `ed.find` ( "query" -- ok )
- `ed.find-next` ( -- ok )
- `ed.find-prev` ( -- ok )

### Options
- `ed.opt-get` ( "name" -- value )
- `ed.opt-set` ( "name" "raw" -- value )
- `ed.opt-set-local` ( "name" "raw" -- value )

Convenience words (editor):
- `set` — immediate; parses `OPTION VALUE` and sets the option
- `show` — immediate; parses `OPTION` and pushes its value
- `toggle` — immediate; parses `OPTION` and toggles it (bool only)
- `opt@` ( "name" -- value ) — stack-oriented synonym for `ed.opt-get`
- `opt!` ( "name" "raw" -- value ) — stack-oriented synonym for `ed.opt-set`

### Loading micromax code
- `ed.require` ( "path" -- ) load and eval a micromax file

## Planned near-term hostcalls (rich-but-stable)

- `ed.with-undo`-style grouping for *cursor/selection-only* edits (no buffer mutation)
- Multi-cursor batch primitives that preserve deterministic ordering (`ed.replace-selections` already covers many cases)

## Safety note

Hosts SHOULD:
- enforce step budgets when running untrusted scripts
- apply capability allowlists per plugin
- keep filesystem/network access out of the default capability set
