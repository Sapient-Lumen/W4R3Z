# Editor keymap modes (rev35)

Rev35 adds a small but very useful layer on top of keybindings:
**named keymap modes** with global fallback.

This is intentionally *not* a full modal editor architecture.
It is a compact substrate for things like:

- transient command groups
- goto/view/user prefixes
- plugin-owned temporary maps
- future minor-mode style behavior

## Why

Micromax-editor already had:

- bindable action chains
- provenance-bearing keybindings
- cleanup groups for plugin reloads

What it did **not** yet have was an answer to:

- "what if this key should mean something different in a temporary context?"

Helix, Kakoune, and Emacs all point in the same direction: keep a global baseline,
then layer mode-specific maps on top.

## Model

Each binding now stores:

- `mode` (string, default `"global"`)
- `key`
- `action_spec`
- optional `group`
- optional `span`

Lookup order is:

1. active key mode stack, top-first
2. global bindings

This means the editor can support context-sensitive bindings without losing a stable
fallback map.

## Command-bar surface

New commands:

```text
bindmode MODE KEY ACTIONSPEC
unbindmode MODE KEY
keymode [MODE|global]
pushkeymode MODE
popkeymode
showkeymodes
```

`showkey KEY` now reports the **resolved** binding, including `[mode NAME]` when the
winning binding came from a named mode.

Examples:

```text
bind Ctrl-x command:help
bindmode nav Ctrl-x command:quit
showkey Ctrl-x
# => Ctrl-x -> command:help

keymode nav
showkey Ctrl-x
# => Ctrl-x -> command:quit [mode nav]
```

## Micromax hostcalls

```forth
ed.bind-mode    ( mode key action-spec -- )
ed.unbind-mode  ( mode key -- ok )
ed.binding-modes ( -- [[mode key action group|0 [file line col]|0] ...] )

ed.keymode!     ( mode|0 -- )
ed.keymode@     ( -- mode|0 )
ed.keymode-push ( mode -- )
ed.keymode-pop  ( -- mode|0 )
ed.keymodes     ( -- active known )
```

Where:

- `active` is the current active mode stack, top-first
- `known` is the sorted list of modes that currently have bindings

## Status model

`ed.status` now includes:

```text
keymode
```

This lets future UIs render transient/keymap state without inventing their own
parallel bookkeeping.

## Plugin reload hygiene

Mode-specific bindings still participate in registration groups.
That means plugin reload/unload can remove them with the same grouped cleanup path
already used for hooks, commands, and global bindings.

## Design note

This is smaller than Helix-style nested minor-mode trees and smaller than Kakoune's
built-in normal/insert/prompt/user/goto/view contexts.
That is deliberate.

The goal here is to establish a **portable inspection + resolution contract** first:

- a binding belongs to a mode
- the editor has an active mode stack
- lookup is deterministic
- introspection is machine-readable
- plugin cleanup still works

Later, richer mode entry/exit commands can grow on top of this without rewriting the
core data model.


## Rev36 follow-on

Rev36 adds **one-shot / transient keymodes** on top of this substrate.
See `docs/76-editor-transient-keymodes.md`.
