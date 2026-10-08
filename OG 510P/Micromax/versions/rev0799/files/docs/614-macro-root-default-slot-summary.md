# Rev673 - let raw `macro` mention the default slot while idle

## What changed

Micromax now keeps the default replay slot visible in the broad raw `macro` summary when idle.

- plain `macro` prompt rows now say `idle · default=last (N steps) · ...`
- raw `macro` runtime no-arg failures now say `macro: idle · default=last (N steps) · ...`
- live-owned states like recording and playing still use the broader runtime/inventory summary path

## Why it matters

The narrower macro surfaces already taught that replay defaults to `last`, but the very first umbrella macro witness still flattened idle state back to a generic inventory summary. That was small, but it made the broadest entry point less trustworthy than the specific lanes beneath it.

This rev keeps the macro dialect aligned from the top:

- raw `macro` says which slot replay defaults to
- broad status/inspection/playback surfaces say the same
- live-owned states still preserve the broader fallback summary when that is more truthful

## Verification

Focused prompt/runtime tests pin both the idle raw `macro` preview row and the idle no-arg runtime summary wording.
