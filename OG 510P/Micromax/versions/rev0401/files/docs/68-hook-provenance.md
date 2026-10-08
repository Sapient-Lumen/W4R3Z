# Hook provenance + inspection (rev31)

Micromax hooks started as tiny ordered callback lists. In rev31 they become
slightly richer: hook definitions and hook handler registrations can now carry
**best-effort source spans**, and the VM exposes a machine-readable inspection
surface.

## Why

As micromax becomes the live environment for editor config/plugins, hooks stop
being abstract language features and become active system wiring. When something
behaves oddly, we need quick answers to:

- what handlers are attached to this hook right now?
- in what order will they run?
- where did each handler registration come from?

This mirrors a common need in editor/plugin ecosystems: cheap extensibility is
great, but only if you can inspect it after the fact.

## Data model

- `hook NAME` now records the hook definition span on the `HookWord` itself.
- `hook-add NAME` stores handler entries as `{xt, span}` internally.
- `hook@ NAME` remains backward-compatible and returns only a plain xt list.
- `hook-rows NAME` returns portable inspection data:

```
[[handler-name [file line col]|0] ...]
```

This keeps runtime execution tiny while giving tools, tests, and future LLMs a
stable structure to reason about.

## Examples

```
: h1 1 ;
hook on-save
' h1 hook-add on-save
hook-rows on-save

\ => [["h1" ["config.mx" 12 3]]]
```

Hook words themselves now participate in `xt-span`:

```
' on-save xt-span
\ => ["config.mx" 10 1]
```

## Editor surface

The headless editor command bar now has:

```
showhook NAME
```

This now starts with a tiny count-aware handler prefix and then prints the
current handler chain, including per-handler provenance when available. If the
looked-up word is not actually a hook, the command now fails plainly as
`showhook: not a hook: NAME`. For editor-owned hooks such as `ed.pre-action` /
`ed.on-action`, this makes it much easier to answer “what plugin/script is
observing this event?” without scraping logs or reading the whole config tree.

## Portability notes

- Hook execution stays portable: it is still just an ordered callback list.
- Provenance is **best-effort** and debugging-oriented.
- `hook-rows` is reference/tooling surface, not required for the smallest Rust/WASM VM.
