# Editor prefix maps (rev39)

Micromax-editor now has a tiny, explicit helper for **prefix maps** built on top
of the existing one-shot keymode substrate.

This keeps the core small:
- there is no special parser for multi-key chords
- prefix maps are just **one-shot keymodes**
- the user-facing helper immediately shows reachable bindings via `whichkey`

## Why this exists

Before rev39, scripts could already emulate a prefix key by binding something
like:

```
command:pushkeymode-once goto,command:whichkey
```

That worked, but it was clunky to write repeatedly and easy to forget.
Rev39 adds a small named helper so prefix maps become an obvious part of the
editor/plugin vocabulary.

## Command-bar surface

```
prefixmode MODE
bindprefix KEY MODE [DOC...]
```

### `prefixmode MODE`

- pushes `MODE` as a **one-shot** keymode
- immediately emits `whichkey` output for the reachable bindings

Example:

```
bindmode goto g command:goto 1
prefixmode goto
```

You should now see something like:

```
whichkey: g@goto!->goto absolute line
```

The `!` marker matches the existing one-shot keymode display.

### `bindprefix KEY MODE [DOC...]`

Bind a global key that enters a one-shot prefix mode. Internally this just
creates a normal binding with action-spec:

```
command:prefixmode MODE
```

That means prefix bindings remain:
- inspectable by `showkey`
- visible in `ed.resolve-key-info` / `ed.available-binding-info`
- compatible with grouping/provenance/cleanup

Example:

```
bindmode goto g command:goto 1
bindprefix Ctrl-g goto goto menu
```

Now `Ctrl-g` acts as a prefix key for the `goto` mode.

## Hostcalls

### `ed.prefix-mode`

```
( mode -- ok )
```

Enter a one-shot prefix mode and immediately emit `whichkey`.

### `ed.bind-prefix`

```
( key mode doc|0 -- ok )
```

Bind a global prefix key. If `doc` is `0` or empty, a small default label is
used (`prefix MODE`).

The resulting binding is still a normal keymap row, so this is a convenience
helper, not a separate binding class.

## Design note

This deliberately stops short of a full “transient UI” system. The stable core
contract is still:
- keymaps are data
- one-shot modes are data
- `whichkey`/discovery surfaces are renderers over that data

That keeps the feature portable to future runtimes and easy to validate in a
headless test suite.
