# Editor keybinding provenance

A scriptable editor eventually needs to answer a very practical question:

- **what does this key do right now?**
- **where did that binding come from?**

Micromax-editor now treats bindings as small pieces of data with best-effort provenance,
not just raw `key -> action` strings.

## Current model

Each binding stores:

- `key`
- `action_spec`
- optional `span` (`file:line:col`)

The span is attached when a micromax script binds a key through the hostcall:

- `ed.bind` — `( "key" "action-chain" -- )`

The host uses `vm.last_span` as a best-effort provenance signal.
This means the span points at the currently executing source location, which is good enough
for debugging plugin/config reloads and answering "which file installed this?".

Interactive command-bar bindings created with:

- `bind KEY ACTIONSPEC`

currently do **not** attach a source span.
That is acceptable because they are usually ad-hoc session edits.

## Introspection surface

User-facing commands:

- `showkey KEY` — show the current binding
- `unbind KEY` — remove a binding

Successful keymap edits now keep the command family visible on both sides of the loop: `bind KEY ACTIONSPEC` reports `bind: KEY -> ACTIONSPEC`, `binddoc KEY DOC...` reports `binddoc: KEY -> DOC...`, `unbind KEY` reports `unbind: KEY`, and when a binding has provenance `showkey` includes it. When no binding exists, `showkey` still fails plainly as `showkey: no such binding: KEY` instead of collapsing to a raw `(unbound)` placeholder:

```text
Ctrl-h -> command:help (defined at plugins/demo/init.mf:12:5)
```

Micromax-facing hostcalls:

- `ed.bind` — bind a key
- `ed.unbind` — `( "key" -- ok )`
- `ed.bindings` — `( -- rows )`

`ed.bindings` returns sorted rows in a portable format:

```text
[[key action-spec [file line col]|0] ...]
```

Example shape:

```text
[
  ["Ctrl-h", "command:help", ["<test>", 1, 24]],
  ["Ctrl-s", "Save", 0]
]
```

## Why keep it this small?

Because the immediate win is **debuggability**, not a grand keymap architecture.
This gives us:

- better `showkey`
- reload-friendly plugins (`ed.unbind`)
- a machine-readable binding table for future tools / UIs / LLMs

Later, if we add modes/layers/stacks, this same shape can grow into:

```text
[key mode action-spec span]
```

without throwing away the current contracts.


Rev35 extends this by adding a `mode` field to bindings and a separate machine-readable `ed.binding-modes` surface. See `docs/75-editor-keymap-modes.md`.
