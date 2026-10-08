# Editor keymap discovery (rev38)

Rev35/36 added named keymodes plus one-shot / transient keymodes.
The obvious next pressure point is **discoverability**:

- after pushing a transient mode, what keys are available *right now*?
- how can a headless UI or script inspect the current reachable keymap without scraping messages?
- how do we keep this small enough that future Rust/WASM ports can mirror it directly?

This revision adds a tiny **keymap discovery** surface.

## Design goals

- keep the core representation as plain binding records
- expose *resolved* bindings after keymode precedence is applied
- keep command-bar output deterministic and compact
- stay portable: only strings / ints / lists on the wire

## New hostcalls

```text
ed.binding-rows-for   ( mode|0 -- rows )
ed.available-bindings ( -- rows )
ed.resolve-key        ( key -- row|0 )
```

### `ed.binding-rows-for`

Returns exact bindings for one mode.

```text
[[key action-spec group|0 [file line col]|0] ...]
```

Passing `0` means the global map.

### `ed.available-bindings`

Returns the bindings that are currently reachable *after* active keymode
precedence is applied.

```text
[[mode key action-spec group|0 [file line col]|0] ...]
```

Rules:
- active modes are considered from top of stack to bottom
- global bindings are used as fallback
- if two modes bind the same key, the higher-precedence mode wins
- rows are sorted by key for deterministic tests and tooling

This is intentionally close to the question:

> what can I press right now?

### `ed.resolve-key`

Resolve one key through the active keymode stack.
Returns:

```text
[mode key action-spec group|0 [file line col]|0] | 0
```

This is the machine-readable sibling of `showkey KEY`.

## New command-bar surface

```text
showbindings [MODE|active]
whichkey
```

### `showbindings`

- no argument means `active`
- `showbindings active` shows the precedence-resolved current keymap
- `showbindings MODE` shows exact bindings for that mode
- `showbindings global` shows the global map
- empty and non-empty results both stay count-aware (`0 binding(s)` vs `N binding(s), ...`)

Example:

```text
bindings active: 3 binding(s), Ctrl-g@goto!->command:showkeymodes, Ctrl-x@nav->command:quit, Ctrl-z@global->command:help
```

The `!` suffix means the winning mode is currently one-shot / transient.

### `whichkey`

Originally this was just a tiny alias for `showbindings active`. In rev38 it now
prefers **human descriptions** when available (custom binding docstrings first,
then derived labels from command/action docs).

Example:

```text
whichkey: 2 binding(s), Ctrl-x@nav->request editor quit, Ctrl-z@global->show help for commands/actions
```

This is deliberately *not* a popup system or timeout-driven UI feature.
It is a headless discovery command that future UIs can render however they want.

## Why this shape

The goal is to separate:

- **semantic discovery data** (available bindings, resolved keys)
- **rendering policy** (popup, infobar, command-line text, etc.)

That keeps the editor core testable and portable while still learning from the
"show me what keys are available after a prefix" workflows found in other editors.

## Non-goals

- no timeout-based multi-key parser yet
- no popup/window UI contract yet

Binding descriptions now exist as data (see `docs/78-editor-binding-descriptions.md`).
The discovery wire format stays stable because the description-rich rows live in sibling hostcalls rather than replacing the exact rows introduced here.


## Search-first sibling

Later revisions added a separate **search-first** sibling to these exact discovery rows:

- `bindingpick [QUERY]`
- `BindingPrompt`
- `ed.binding-prompt` / `ed.binding-prompt-rows` / `ed.binding-section-rows`

That surface reuses the same resolved-binding substrate but adds ranked search over key, action-spec, and human description text. Recent revisions also let multi-term queries match across those fields out of order, so searches like `quit Ctrl` or `editor quit` can still find the right binding without requiring exact phrasing. The same visible winning-mode labels now also group the prompt into sections (`Prompt`, active mode names like `nav`, `Global`) so future UIs and scripts do not need to reverse-engineer picker headers from flat row text.
