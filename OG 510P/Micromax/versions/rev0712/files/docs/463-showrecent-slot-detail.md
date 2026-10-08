# Recent slot-addressed exact inspection

Rev521 closes one small trust/flow/headless-first seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed visible 1-based MRU slot numbers plus tiny file/action truth
- `recent N` reopened one numbered entry directly
- exact `showrecent PATH` / `ed.recent-detail-row` already gave one side-effect-free recent-file answer by path
- rev520 exposed the live recent-picker row surface headlessly without prompt scraping

But one small mismatch still lingered exactly where humans and future LLMs often started:

- the visible recent inventory and picker rows already spoke in stable `#N` slot numbers
- the side-effect-free exact inspection path still only understood paths
- that forced one extra mental or scripted translation step from `#N` back to a path before you could ask what one numbered entry really was

## What changed

Rev521 keeps the change deliberately small.

- `showrecent` now accepts a visible MRU slot number as well as a path
- new hostcall `ed.recent-slot-detail-row ( n -- row|0 )` exposes the same exact recent-file row by 1-based slot
- new convenience word `recent-slot-detail ( n -- row|0 )` mirrors that slot-addressed hostcall inside Micromax scripts
- command-bar completion for `showrecent` now offers numbered slot targets and reuses the same exact recent-file row metadata for them
- focused tests pin the command, hostcall, convenience word, and completion contract

## Why it matters

This is tiny, but it keeps the recent-file loop more coherent.

If Micromax already shows one recent entry as `#N`, exact no-side-effect inspection should understand that same numbered truth directly. Keeping slot-addressed inspection first-class makes the archive easier for humans, scripts, and future LLMs to drive without re-parsing inventory text or translating slots back into paths by hand.

## Focused tests

- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`
