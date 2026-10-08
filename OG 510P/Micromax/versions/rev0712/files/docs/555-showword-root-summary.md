# Rev614 — keep `showword` root inventory truth visible

## Why

`showword NAME` was already a trustworthy exact inspector once a user supplied a real visible Micromax word. But the root entry point still went generic in both places where confidence matters most: plain `showword` in command-bar completion only showed the ordinary command doc row, and raw runtime `showword` jumped straight to `usage: showword NAME` even though the editor already knew the current visible-word namespace.

That left a tiny trust seam in the live scripting loop. When Micromax already knows which words are visible in the active search order, the root exact inspector should surface one compact witness before it asks for a specific name.

## What changed

- added shared `Editor._word_inventory_preview_summary()`
- plain `showword` command-bar completion now reuses that summary before Enter
- raw runtime `showword` now prints the same summary before `usage: showword NAME`
- the root sample prefers one non-core documented word when present so test/plugin/local scripting state stays visible instead of getting lost behind boot/stdlib words
- focused prompt/runtime tests pin both surfaces to the same shared witness

## Shape

The change stays deliberately small:

- no new command syntax
- no wider VM or help-system refactor
- no duplication of word-detail formatting logic
- no hidden state; the preview is derived from the same visible words that `showword NAME` already inspects exactly

## Result

The root exact word inspector now behaves like the neighboring root inspectors (`showhook`, `showkeymode`, `showoption`, `showcmd`, `showaction`): it stays usage-shaped, but it no longer goes blind right before or right after Enter.
