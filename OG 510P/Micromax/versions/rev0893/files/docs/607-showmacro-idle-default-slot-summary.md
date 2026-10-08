# Rev666 - keep plain `showmacro` centered on `last` while idle

## What changed

Micromax now keeps the default slot visible in plain `showmacro` summaries throughout idle states, not just on a fresh editor.

- no-arg command-bar and runtime `showmacro` summaries now prefer `default=last (N steps)` whenever the editor is idle
- those summaries suppress redundant `e.g. last (...)` noise
- when another saved macro is useful, it still appears as the example sample

## Why

Rev665 fixed the first important root-summary seam: a fresh editor stopped showing plain `showmacro` as only `idle · 0 macros` and started hinting `default=last (0 steps)`.

But once saved macros existed, the root summary could still drift back to a broad inventory witness and stop mentioning `last`, even though `showmacro` is an exact inspector and `last` remains the default exact target while idle.

## Result

The root exact-inspector path now stays centered on the default slot across idle states.

Examples:

- fresh editor: `showmacro: idle · default=last (0 steps) · 0 macros`
- idle with `last` saved and `demo` also saved: `showmacro: idle · default=last (1 step) · 2 macros · e.g. demo (2 steps)`

This is deliberately small, but it improves both **trust** and **flow**:

- trust, because the root exact inspector now keeps the most relevant exact slot visible instead of sliding back to broader inventory prose
- flow, because humans/scripts/LLMs get a better first hint about which slot matters before they type a name
