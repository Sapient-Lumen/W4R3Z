# Recent command completion truth

Rev512 closes one small but very everyday flow/trust seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed the MRU list with active/open/dirty/readonly/cursor detail
- rev511 taught that same flat inventory to keep tiny `existing file` / `new file` plus `current buffer` / `switch buffer` / `empty buffer @ 1:0` truth
- exact `showrecent PATH`, `recentpick`, and palette `Recent Files` rows already let humans inspect one target before reopening it

But one small command-bar seam still lingered at the front of that loop:

- the verb that actually opens MRU entries by number still completed like a blind scalar
- choosing `recent 7` meant remembering or re-reading the plain inventory instead of seeing what that number would open
- `recent clear` also stayed one opaque token even though it is a destructive memory-reset action

## What landed

Rev512 keeps the change deliberately small.

- command-bar completion for `recent` now offers `1..N` plus `clear`
- numeric completion rows reuse the same `recent_inventory_rows()` truth Micromax already trusts for the plain inventory
- `clear` gets its own explicit `clear history` row with a tiny forget-count cue
- focused tests pin both numeric and `clear` completion behavior

## Why this matters

This is a tiny flow/trust cleanup.

The command that opens remembered files should not be the one place where MRU state becomes harder to read. Once Micromax already knows which file one recent slot points at — and whether it is saved, missing, current, or just another open buffer switch — the command bar should say that truth right where the number is chosen.

## Focused tests

- `tests/test_editor_prompt_completion_hostcalls.py`
