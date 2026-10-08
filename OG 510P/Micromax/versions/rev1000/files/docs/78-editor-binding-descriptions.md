# Editor binding descriptions (rev38)

Rev37 added headless keymap discovery. The next obvious friction point was that
raw action specs are often too noisy for discovery surfaces:

- `command:quit` is okay
- `Autocomplete|IndentSelection|InsertTab` is truthful, but not a great label
- future prefix/transient maps will want short “menu item” names, not implementation details

This revision adds **binding descriptions** as first-class data.

## Design goals

- keep the exact action spec authoritative
- allow a short human label to travel with the binding
- keep fallback behavior useful even without custom labels
- keep the wire format portable (strings / ints / lists only)

## Binding model

Bindings may now carry:

```text
key
action-spec
desc        (optional short human description)
group       (optional cleanup/debug metadata)
span        (optional provenance)
mode        (binding mode; defaults to global)
```

`desc` is **metadata**, not behavior. Rebinding a key changes the actual action;
changing `desc` only changes what discovery surfaces show.

## Fallback derivation

If a binding has no explicit `desc`, the editor derives one on demand:

- single-step `command:NAME ...` bindings use the command doc
- single-step editor action bindings use the action doc
- multi-step action chains use the first step’s doc plus `…` when possible

This keeps `whichkey` immediately useful even before scripts/plugins start
attaching custom descriptions.

## New hostcalls

```text
ed.bind-doc             ( key doc -- ok )
ed.bind-mode-doc        ( mode key doc -- ok )
ed.binding-info-for     ( mode|0 -- rows )
ed.available-binding-info ( -- rows )
ed.resolve-key-info     ( key -- row|0 )
```

### `ed.binding-info-for`

Returns exact bindings for one mode with descriptions resolved:

```text
[[key action-spec desc|0 group|0 [file line col]|0] ...]
```

Passing `0` means the global map.

### `ed.available-binding-info`

Returns precedence-resolved current bindings with descriptions resolved:

```text
[[mode key action-spec desc|0 group|0 [file line col]|0] ...]
```

### `ed.resolve-key-info`

Machine-readable sibling of `showkey KEY`:

```text
[mode key action-spec desc|0 group|0 [file line col]|0] | 0
```

## New command-bar surface

```text
binddoc KEY DOC...
bindmodedoc MODE KEY DOC...
```

Examples:

```text
bind Ctrl-x command:quit
binddoc Ctrl-x quit editor

bindmode goto g command:goto 1
bindmodedoc goto g go to first line
```

Successful description edits now keep the command family visible too: `binddoc Ctrl-x quit editor` reports `binddoc: Ctrl-x -> quit editor`, and `bindmodedoc goto g go to first line` reports `bindmodedoc: g@goto -> go to first line`. Missing targets still fail plainly too: `binddoc` / `bindmodedoc` say `...: no such binding: ...` instead of collapsing to raw `(unbound)` placeholders.

## `showkey` and `whichkey`

`showkey KEY` now includes `[desc ...]` when a description exists or can be
derived.

`whichkey` now prefers the human description instead of the raw action spec.
This makes it a better “what does this key *mean*?” surface, while `showbindings`
remains the exact “what does this key *run*?” surface.

That split is deliberate:

- `showbindings` = precise execution-oriented inspection
- `whichkey` = compact human discovery

## Why this shape

This follows a pattern visible in other editors:

- mappings often want short user-facing labels
- discovery surfaces should not have to invent those labels in UI code
- exact machine-readable action specs should still be preserved underneath

Micromax-editor keeps both by making descriptions just another field on the
binding record.

## Non-goals

- no popup/menu rendering contract
- no nested prefix parser yet
- no requirement that every binding have a custom docstring

The point is to keep the data model useful **now** while staying small enough to
port and inspect easily.
