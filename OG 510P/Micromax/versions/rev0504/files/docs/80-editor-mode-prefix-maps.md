# Editor mode-local prefix maps (rev40)

Rev40 adds a tiny sibling to the existing global prefix-map helper:

```
bindmodeprefix OWNERMODE KEY MODE [DOC...]
```

and the matching hostcall:

```
( owner-mode key mode doc|0 -- ok )  ed.bind-mode-prefix
```

This is the **mode-local** version of `bindprefix` / `ed.bind-prefix`.

## Why this exists

Global prefix keys are useful for “leader” style menus. In practice, editors also
want **context-local** prefixes: a key that only acts like a prefix inside one
mode, then temporarily enters another small key layer.

Examples:
- a `nav` mode that exposes a `g` prefix into a `goto` submenu
- a `prompt` mode that exposes a one-key completion menu
- a future language/filetype mode with its own local leader

The important design choice is that this still does **not** introduce a new
binding class. A mode-local prefix binding is just a normal binding whose
action-spec is:

```
command:prefixmode MODE
```

living inside `OWNERMODE`.

## Command-bar surface

```
bindmodeprefix OWNERMODE KEY MODE [DOC...]
```

Example:

```
bindmode goto g command:goto 1
bindmodeprefix nav z goto goto menu
```

Now, while `nav` is active, pressing `z` enters `goto` as a **one-shot** mode
and immediately shows the reachable bindings via `whichkey`.

You should see something like:

```
whichkey: 2 binding(s), g@goto!->goto absolute line, z@nav->goto menu
```

## Hostcall

### `ed.bind-mode-prefix`

```
( owner-mode key mode doc|0 -- ok )
```

- binds `key` inside `owner-mode`
- entering the binding pushes `mode` as a one-shot keymode
- if `doc` is `0` or empty, a small default label is used (`prefix MODE`)

Because the resulting row is still an ordinary keymap binding, all the existing
tooling keeps working unchanged:
- `showkey`
- `ed.resolve-key-info`
- grouping / provenance / reload cleanup
- `whichkey` and other discovery surfaces

Successful command-bar mode-local prefix creation now also reports `bindmodeprefix: KEY@OWNERMODE -> MODE`, keeping the command family visible in logs instead of falling back to an older bare `bound prefix ...` line.

## Design note

This intentionally stays tiny. It is not a full nested-prefix parser, timeout
mechanism, or UI popup contract. It is a little convenience layer over the
existing, portable keymode model.
