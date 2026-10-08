# Rev551 - `recent N|#N` keeps exact missing-slot truth after Enter

## What changed

- direct `recent N` misses now report `recent: no such recent file: N`
- direct `recent #N` misses now report `recent: no such recent file: #N`
- the command bar and the executed command now stay in the same exact recent-slot dialect

## Why this matters

Micromax had already tightened the surrounding recent-file loop:

- plain `recent` previewed live MRU inventory before Enter
- completion rows for direct missing recent slots already said `no such recent file`
- adjacent exact recent inspectors and recent pickers already kept their miss dialects aligned before and after Enter

But `recent` itself still had one tiny trust seam: running `recent 9` or `recent #9` fell back to a bare numeric `out of range` message even though Micromax already knew the request was one exact recent-slot lookup.

This revision keeps the fix small and boring: once `recent` has accepted one `N|#N` token as an exact recent slot, a miss now stays in the same visible-token dialect all the way through execution.

## Example

Before:

```text
recent #9
recent: out of range: 9
```

After:

```text
recent #9
recent: no such recent file: #9
```

## Files to read next

- `src/micromax_editor/command_dispatcher.py`
- `tests/test_editor_buffer_lifecycle_recent.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `docs/486-recent-command-preview.md`
- `docs/487-recentpick-exact-slot-miss.md`
