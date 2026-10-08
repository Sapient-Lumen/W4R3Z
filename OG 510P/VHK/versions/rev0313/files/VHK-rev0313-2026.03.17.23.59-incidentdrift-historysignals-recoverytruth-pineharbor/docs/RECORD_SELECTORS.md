# Recording selectors

VHK includes a few "macro authoring" helpers aimed at the same pain point that
AutoHotkey users solve with Window Spy: *stop guessing window identifiers*.

## `vhk record-selectors`

This command records active-window observations for a short period and suggests
selectors you can paste into:

- `bindings[].when`
- `hotstrings[].when`
- `window_watchers[].when`
- `vhk run --require-window '{...}'`

Example:

```bash
vhk record-selectors --duration-ms 3000
```

If you want a minimal snippet for `project.yaml`, use:

```bash
vhk record-selectors --no-json
```

### Title handling

Titles are often unstable. `record-selectors` therefore tries to be conservative:

- The `stable` suggestion **avoids titles** by default.
- The `exact` suggestion will include a title matcher when possible.

When multiple different titles are observed during recording, VHK may generate a
safe `title_regex` matcher:

- If there are only a few unique titles, it emits an exact alternation like
  `^(?:Title A|Title B)$`.
- If there are many titles but they share a meaningful prefix, it emits a prefix
  regex like `^Firefox — .*`.

If neither strategy looks safe, it omits the title and recommends relying on
class/app identifiers.

## Related tools

- `vhk window-spy` prints a single active-window snapshot.
- `vhk wm-events --with-window` streams raw WM events to help debug what your
  compositor emits.
