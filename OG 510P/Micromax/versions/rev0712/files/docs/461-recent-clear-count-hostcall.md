# Recent clear count at the host boundary

Rev519 closes one small host-boundary trust seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- `Editor.clear_recent_files()` already returned the forgotten count
- rev513 made the human `recent clear` command report `forgot N recent file(s)`
- the scripting boundary already exposed `ed.recent`, `ed.recent-clear`, and the richer recent inventory/detail rows

But one tiny mismatch still lingered exactly where live scripting should have matched the human command:

- the host boundary still only exposed fire-and-forget `ed.recent-clear ( -- )`
- scripts and future LLMs could clear the MRU list, but they could not directly observe how many remembered entries were actually forgotten
- that made the destructive host path thinner than the command surface beside it

## What changed

Rev519 keeps the change deliberately small and compatibility-safe.

- existing `ed.recent-clear ( -- )` stays intact for fire-and-forget scripts
- new hostcall `ed.recent-clear-count ( -- n )` clears the MRU list and returns the forgotten entry count
- new convenience word `recent-clear-count ( -- n )` exposes the same count inside Micromax scripts
- both host paths reuse the same tiny internal helper, so command, hostcall, and future script flows all agree on one destructive-action truth
- focused tests pin the new hostcall, the convenience word, and the old compatibility path

## Why it matters

This is tiny, but it makes the host boundary more honest.

If Micromax already knows exactly how many recent entries were forgotten — and the human command already reports that count — the live scripting surface should be able to observe the same fact without scraping messages or re-counting state before and after a destructive action.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_capabilities_registry.py`
