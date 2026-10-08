# Rev672 - let idle `macro status` mention the default slot

## What changed

Micromax now keeps the default replay slot visible in the broad macro-status lane when idle.

- idle `macro status` / `macro st` prompt rows now say `idle · default=last (N steps) · ...`
- idle `macro status` runtime messages now say `macro status: idle, default=last (N steps), ...`
- recording and playing status messages stay unchanged

## Why it matters

The exact macro surfaces already taught that replay defaults to `last`, but the broad state lane still flattened back to a generic idle summary. That was small, but it made the top-level status witness less trustworthy than the exact/action surfaces around it.

This rev keeps the macro dialect aligned:

- broad idle status says which slot replay defaults to
- exact inspection says the same
- playback actions still use the same default-slot language

## Verification

Focused prompt/runtime tests pin both the idle preview row and idle runtime status message wording.
