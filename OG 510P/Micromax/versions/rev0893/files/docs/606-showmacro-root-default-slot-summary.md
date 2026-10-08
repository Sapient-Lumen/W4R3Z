# Rev665 - make plain `showmacro` mention the default slot

## What changed

Micromax now gives plain `showmacro` a slightly more exact fresh-editor summary.

- command-bar `showmacro` rows now say `idle · default=last (0 steps) · 0 macros` on a fresh editor
- raw runtime `showmacro` prints that same summary before `usage: showmacro NAME`
- both paths reuse one shared `_showmacro_root_preview_summary()` helper

## Why

Rev664 fixed the important exact-inspection seam: `showmacro last` and `ed.macro-detail-row` stopped pretending the empty default slot was missing. But there was still one quieter follow-up gap.

The first thing a human is likely to try is plain `showmacro`, not `showmacro last`. On a fresh editor that root command still only said `idle · 0 macros`, which was true as broad inventory, but misleading for an exact inspector that already had one meaningful default target.

## Result

The root exact-inspector path now hints the one slot it can already inspect honestly.

Examples:

- fresh editor: `showmacro: idle · default=last (0 steps) · 0 macros`
- after typing `showmacro last`: `showmacro last [default]: 0 steps · default replay slot`

This is deliberately small, but it improves both **trust** and **flow**:

- trust, because the root exact inspector no longer hides the default-slot truth behind a broader inventory-only summary
- flow, because humans/scripts/LLMs get a stronger hint about what to inspect next without having to guess that `last` remains special
