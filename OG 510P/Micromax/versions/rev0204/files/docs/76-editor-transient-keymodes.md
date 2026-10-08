# Editor transient keymodes (rev36)

Rev36 adds a tiny but very useful refinement on top of named keymap modes:
**one-shot / transient keymodes**.

This is the missing piece for prefix-style keymaps and other short-lived contexts.

Examples of the shape this enables:

- `g` enters a one-shot *goto* layer
- a plugin opens a temporary command palette layer for the next key
- a future UI enters a temporary “peek” layer and then falls back automatically

## Why

Once named keymodes exist, the next pressure point is obvious:

- some modes should persist until explicitly changed
- some modes should only affect the **next key**

That pattern shows up all over editor ecosystems:

- **Helix** minor modes such as `g` or `z`
- **Kakoune** “next-key” style contexts
- **Emacs** transient keymaps via `set-transient-map`

Micromax-editor keeps the implementation intentionally tiny while still matching the
core idea.

## Model

The active keymode stack now distinguishes:

- **persistent** modes
- **one-shot** modes

Lookup behavior:

1. if the **topmost active mode** is one-shot, it gets first crack at the key
2. if that mode has a binding for the key, the binding runs and the mode pops
3. if that mode does **not** have a binding for the key, the mode pops and lookup
   falls through to the remaining active modes and global bindings
4. persistent modes continue to behave as before

This gives a compact approximation of “prefix maps” without introducing multi-key
parsing, timers, or a full modal editor architecture.

## Editor API

New editor method:

```text
Editor.dispatch_key(key) -> bool
```

This centralizes:

- resolve the effective binding
- honor one-shot keymode semantics
- run the resulting action chain

Future UIs should prefer `dispatch_key()` over open-coding
`resolve_key_binding()` + `run_action_chain()`.

## Command-bar surface

New command:

```text
pushkeymode-once MODE
```

Examples:

```text
bind Ctrl-g command:showstatus
bindmode goto Ctrl-g command:showkeymodes

pushkeymode-once goto
showkeymodes
# => active keymodes: goto!
```

The `!` suffix in `showkeymodes` means “one-shot”.

## Micromax hostcalls

New hostcalls:

```forth
ed.keymode-push-once ( mode -- )
ed.keymode-rows      ( -- active known )
ed.press-key         ( key -- ok )
```

Where `active` is:

```text
[[mode once?] ...]
```

Example:

```forth
"goto" "ed.keymode-push-once" hostcall
"Ctrl-g" "ed.press-key" hostcall
```

## Status model

`ed.status` now includes:

```text
keymode
keymode_once
```

This keeps transient state visible to future UIs and scripts without requiring them
to peek into editor internals.

## Design note

This is still deliberately smaller than:

- Helix nested minor-mode trees
- Kakoune’s built-in mode families
- Emacs’s general keymap machinery

The goal is to lock down the useful contract first:

- key lookup is centralized
- transient modes are explicit data
- one-shot behavior is deterministic
- status/introspection surfaces are machine-readable

That keeps the headless core testable while leaving room for richer prefix maps,
prompt-specific keymodes, or transient UI layers later.


Rev37 layers keymap discovery on top of this substrate.
See `docs/77-editor-keymap-discovery.md`.
