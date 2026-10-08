# Micromax Cookbook (draft)

Pragmatic patterns you’ll use a lot when micromax is an editor’s plugin system.

## 1) “Config file” pattern (idempotent)

```forth
( config.mmx )
module config

variable tab-width
4 tab-width !

endmodule
```

Load once:

```
"config.mmx" require
```

Reload when editing:

```
"config.mmx" reload
```

## 2) Keybinding / callback as quotation

```forth
( pretend: host binds a quotation to a key )
[ "hello" . cr ]   \ a callback value
```

## 3) Hook-based extension points

```forth
hook on-save
: ensure-newline ( -- )  ... ;
' ensure-newline hook-add on-save
```

## 4) Namespaces for plugins

Each plugin should use a module:

```forth
module myplugin
  : init ( -- ) ... ;
endmodule
```

Then a loader can do:

```
use myplugin
myplugin.init
```

## 5) Locals for readability

```forth
: between? ( x lo hi -- flag )
  ->hi ->lo ->x
  x lo >= x hi <= and ;
```

## 6) Postfix dispatch for “object-ish” code

```forth
( list pipeline )
1 list push dup .len
```

## 7) Defensive calls

Dynamic execution:

```forth
"maybe-word" responds? [ "maybe-word" send ] [ drop ] if
```

## 8) Hot reload pattern

When we implement a plugin loader, it will likely:
- `unrequire` the plugin path
- clear plugin module wordlist (optional later)
- `reload` the plugin
- run `init`

## 9) Grouping multi-step edits into one undo step

```forth
"Replace greeting" [
  0 0 0 5 "hello" "ed.replace-range" hostcall drop drop
  0 5 0 5 "!" "ed.replace-range" hostcall drop drop
] "ed.with-undo" hostcall
```

## 10) Helper navigation without moving the cursor (save-excursion)

```forth
[ "needle" "ed.find" hostcall drop ] "ed.with-cursorstate" hostcall
```

This runs the search (which moves the cursor), then restores the original
cursor/selection state.

## 10b) Compute multiple derived values from the same thing with `bi` / `tri`

When editor scripts need several facts about the same value, `bi`/`tri` are often clearer
than a nest of `dup`/`over`/`swap` operations.

```forth
: buffer-text+len ( -- text n )
  "ed.text" hostcall
  [ ]
  [ len ]
  bi ;
```

Even if the exact hostcalls evolve, the pattern is stable: keep one source value, run two
small quotations against it, and leave both results on the stack.

## 11) Plugin state with maps

Micromax maps are mutable, string-keyed dictionaries. A common pattern is to keep a
single map in a `variable` and store plugin state under readable keys.

```forth
module myplugin

variable state
map state !

: bump-counter ( -- )
  state @ dup "count" swap m@ 1 +  "count" rot m!  state ! ;

: init ( -- )
  bump-counter
  state @ "count" swap m@  "." .  cr ;

endmodule
```

Notes:
- `m@` returns `0` if the key is missing.
- `m!` mutates the map *and* returns it (handy for chaining), but you’ll still
  usually store it back into a `variable` (as shown).


## 12) Give bindings short human labels

When you want `whichkey` (or future UIs) to show something friendlier than the
raw action spec, attach a description after binding the key:

```forth
"Ctrl-x" "command:quit" "ed.bind" hostcall
"Ctrl-x" "quit editor" "ed.bind-doc" hostcall drop

"goto" "g" "command:goto 1" "ed.bind-mode" hostcall
"goto" "g" "go to first line" "ed.bind-mode-doc" hostcall drop
```

This changes **discovery text**, not behavior. `showbindings` still shows the
exact action spec; `whichkey` prefers the human label.


## Prefix keys without hand-written action chains

When you want a small “leader” or prefix key, define the target mode bindings
first and then use `bindprefix` (or `ed.bind-prefix`) instead of spelling out
`command:pushkeymode-once ...,command:whichkey` by hand each time.

```
bindmode goto g command:goto 1
bindmode goto j command:jump +10
bindprefix Ctrl-g goto goto menu
```

This keeps the actual binding fully inspectable (`showkey Ctrl-g` still shows an
ordinary action spec), while making the prefix-map intent obvious in configs.


## Mode-local prefix keys

When you want a prefix key that only exists inside another mode, use
`bindmodeprefix` (or `ed.bind-mode-prefix`). This is the small “local leader”
sibling of `bindprefix`.

```
bindmode goto g command:goto 1
bindmode nav x command:showkeymodes
bindmodeprefix nav z goto goto menu
```

Now `z` only acts as a prefix key while `nav` is active; it enters `goto` as a
one-shot keymode and immediately surfaces the reachable bindings with
`whichkey`.


## Inspect a word

```
: inc ( n -- n ) ( add one ) 1 + ;
' inc xt-kind    \ => "colon"
' inc xt-effect  \ => "( n -- n )"
' inc xt-doc     \ => "add one"
words-rows        \ => searchable rows [name kind effect doc wid wl]
help inc
```

This is the current recommended path for stack-effect-aware tooling: inspect the metadata first, and only propose checker behavior once real scripts need it. In the editor command bar, `showword inc` gives the same live word summary without dropping into the REPL.


## 13) Give custom command completions richer metadata

A Micromax-defined command can now return completion rows in the same shape the
editor already uses for built-in suggestion metadata:

```forth
: greet-row-alice ( -- row )
  list "alice " swap push "person" swap push "friendly default" swap push "example completion row" swap push
;

: greet-row-bob ( -- row )
  list "bob " swap push "person" swap push "friendly default" swap push "second example completion row" swap push
;

: greet-rows ( -- rows )
  list greet-row-alice swap push greet-row-bob swap push
;

: ed.complete.greet ( cmd tok_i prefix toks -- cands rows mode )
  drop drop drop drop
  "alice " list push "bob " swap push
  greet-rows
  2
;
```

Each row is `[insert kind menu info]`. Future UIs (or debugging scripts using
`ed.prompt-suggestion-rows`) can show the same metadata for plugin completions
that they already show for built-in commands/options/words.

If you do not need richer metadata, the original simpler contract still works:

```forth
: ed.complete.greet ( cmd tok_i prefix toks -- cands mode )
  drop drop drop drop
  "alice " list push "bob " swap push
  2
;
```


## 14) Inspect the active topic-prompt item

The searchable `topic` prompt is now a decent substrate for future pickers.
You can open it from Micromax and inspect the currently selected row:

```forth
"visible micromax" "ed.topic-prompt" hostcall

\ later, while the prompt is active:
"ed.prompt-current-row" hostcall .
"ed.prompt-current-section" hostcall .
"ed.prompt-current-preview" hostcall .
```

That row has the same shape used elsewhere in prompt metadata:

```
[insert kind menu info]
```

So a future TUI/LLM helper can render a tiny preview/statusline from the active row
without recomputing topic ranking itself. If you want grouped sections for a picker,
`ed.topic-section-rows` / `ed.apropos-section-rows` expose the same topics as
`Commands` / `Actions` / `Words` buckets.


## Inspect the active binding picker from Micromax

```forth
: binding-preview-demo ( -- row preview )
  "quit" "ed.binding-prompt" hostcall
  "ed.prompt-current-row" hostcall
  "ed.prompt-current-preview" hostcall
;
```

This opens the searchable current-binding prompt, then returns the active binding row plus a compact preview string. It is a tiny building block for future statuslines, overlays, or LLM-facing inspection helpers.


## Inspect the active command palette from Micromax

```forth
"status" "ed.command-palette" hostcall
"ed.prompt-current-row" hostcall .
"ed.prompt-current-preview" hostcall .
```

This opens the searchable command/action palette with a prefilled query, then returns the active row plus a compact preview string. It is a tiny substrate for future statuslines, overlays, or LLM helpers that want to inspect the command palette without reimplementing ranking.

If you also want grouped palette sections (including the `Recent` bucket when present), call `ed.command-palette-section-rows` with the current query.
