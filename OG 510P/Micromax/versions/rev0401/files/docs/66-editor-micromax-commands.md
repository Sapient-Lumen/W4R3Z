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
Built-in commands have built-in completion rules, but plugins can provide extra candidates.

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

- `help NAME` first checks editor commands/actions, then falls back to the visible Micromax word named `NAME`
- `showword NAME` explicitly prints the visible word's kind/effect/doc/provenance

This means plugin-defined commands and ordinary Micromax words can now share the same command-bar discovery surface without needing a separate browser yet.

## Searchable topic rows

The editor now also exposes the broader discovery surface used by `apropos QUERY`:

The human-facing `apropos QUERY` command now keeps that discovery inventory count-aware too: empty searches say `apropos QUERY: 0 topic(s)`, non-empty searches start with `apropos QUERY: N topic(s), ...`, and the existing preview rows still end with `... (+N more)` when only the first slice is shown.


- `ed.topic-rows` — `( -- rows )` returns `[[name kind menu info] ...]` for commands, actions, and visible Micromax words
- `ed.topic-section-rows` — `( -- sections )` returns grouped topic rows as `[[label [[name kind menu info] ...]] ...]`
- `ed.apropos-rows` — `( query -- rows )` returns the same rows ranked by the editor's tiny deterministic subsequence matcher; name matches win first, then summary/doc text can rescue broader discovery queries, and multi-term/out-of-order queries are matched term-by-term across those fields
- `ed.apropos-section-rows` — `( query -- sections )` returns the same grouped shape for a ranked query
- `ed.buffer-section-rows` — `( query -- sections )` groups buffer picker rows by visible picker bucket (`Help`, `Scratch`, project roots, `Buffers`)
- `ed.plugin-section-rows` — `( query -- sections )` groups plugin picker rows by `Errors` / `Loaded` / `Available`
- `ed.mark-section-rows` — `( query -- sections )` groups marks by owning buffer
- `ed.jump-section-rows` — `( query -- sections )` groups jumplist rows by `Current` / `Back` / `Forward`
- `ed.binding-section-rows` — `( query -- sections )` groups current bindings by winning mode (`Prompt`, active mode names like `nav`, `Global`)
- `ed.doc-section-rows` — `( query -- sections )` groups docs picker rows by numbered docs family (`00–09 Project`, `10–19 Research`, `20–29 Language + VM`, ...)
- `ed.recent-section-rows` — `( query -- sections )` groups recent-file rows by project root; `recentpick` now reuses those same buckets live too
- `ed.recent-dir-section-rows` — `( query -- sections )` groups recent-file rows by parent directory; `recentdirpick` now reuses those same buckets live too

The same picker family now also keeps failed submits explicit on the human side: `bufferpick`, `pluginpick`, `recentpick`, `recentdirpick`, `helppick`, `helplinkpick`, `helpoutlinepick`, `helpnavpick`, `markpick`, and `jumppick` report tiny `0 ...` summaries on zero-result submit instead of collapsing to `(none)`.

This is the intended substrate for future picker-style UIs and for LLM/tooling integrations that want a single searchable model of the live editor environment. `help NAME` also uses this surface as a fallback when no exact topic exists, so typo recovery and fuzzy discovery share one ranking path.

The editor now also exposes a tiny canonical interaction flow on top of those rows:

- command `topicpick [QUERY]`
- action `TopicPrompt`
- hostcall `ed.topic-prompt` — `( query -- )` opens the searchable topic/help prompt prefilled with `query`

That prompt reuses the normal prompt suggestion-session model: changing the query live-refreshes ranked topics, `Tab` / `Shift-Tab` cycle them, and `Enter` opens help for the selected/best-ranked topic. The same ranking path now also supports small multi-term/out-of-order queries. The live `topicpick` prompt now flattens the same grouped topic families already exposed through `ed.topic-section-rows` / `ed.apropos-section-rows`, and empty-query browse windows budget rows across `Commands` / `Actions` / `Words` so Actions/Words remain visible on the first page instead of being crowded out by the command list cap. Failed submit on a zero-result query now says `topicpick QUERY: 0 topic(s)` instead of collapsing to `(none)`. Scripts/UIs can inspect the active row through `ed.prompt-current-row`, grouped sections through `ed.topic-section-rows` / `ed.apropos-section-rows`, and preview text through `ed.prompt-current-preview`.


## Searchable command/action palette

The editor now also exposes an execution-oriented search surface over **commands + actions**:

- `commandpick [QUERY]` — open the searchable command/action palette
- `CommandPalette` — action form of the same prompt
- `ed.command-palette` — hostcall form
- `ed.command-palette-rows` — ranked rows in `[name kind menu info]` shape
- `ed.command-palette-section-rows` — grouped rows as `[[label [[name kind menu info] ...]] ...]`

Behavior:

- it uses the same tiny ranking + row metadata substrate as `topicpick`
- successful palette submissions are remembered in a small palette-local MRU
- empty queries surface a `Recent Files` section (opens files immediately) and then the palette-local command/action MRU as `Recent`
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

That prompt reuses the normal prompt suggestion-session model: changing the query live-refreshes ranked bindings, `Tab` / `Shift-Tab` cycle them, and `Enter` runs `showkey KEY` for the selected/best-ranked binding. Failed submit on a zero-result query now says `bindingpick QUERY: 0 binding(s)` instead of collapsing to `(none)`. Failed `showkey KEY` lookups now also stay explicit as `showkey: no such binding: KEY` instead of falling back to a raw `(unbound)` placeholder. The row substrate is exposed separately through `ed.binding-prompt-rows`, where each row is `[key kind menu info]` and `menu` includes the winning mode + action-spec while `info` carries the resolved human description. Grouped winning-mode sections are available through `ed.binding-section-rows`, and `ed.prompt-current-section` / `ed.prompt-current-preview` now reuse those same visible labels instead of a generic `Binding` bucket.
- missing `showcmd NAME` / `showword NAME` lookups now fail plainly as `showcmd: no such command: NAME` / `showword: no such word: NAME` instead of placeholder strings
- mistyped ordinary command-bar commands now fail plainly as `command: no such command: NAME` instead of the older `Unknown command: NAME`
- known commands that raise unexpectedly now fail as `command NAME: error: DETAILS` instead of a generic `Command error: ...`
- Micromax-defined commands registered via `ed.cmd-add` now keep that same `command NAME: error: DETAILS` prefix on Micromax/runtime faults too, while preserving formatted span/trace detail after the prefix

  - `help NAME` shows command/action/micromax-word help and falls back to opening a docs topic when possible
  - misses are now typed explicitly too: `help docs TOPIC` -> `help docs: no such doc: TOPIC`; ordinary misses -> `help: no such topic: QUERY`
