# Search navigation feedback (rev340)

Recent tiny editor follow-ups have tried to enforce one simple rule:
ordinary successful movement should say where it actually landed.

Search already had most of the substrate:

- real `find` / `FindNext` / `FindPrevious` movement
- shared whole-buffer search-position state (`i/n`)
- visible TUI/statusline search summaries

But the movement loop itself still lagged behind:

- submitted `find` changed the cursor but did not confirm the landed target
- `find_next` / `find_prev` could move silently
- `find_next` / `find_prev` could also fail silently when there was no active
  search or no later/earlier hit

Rev340 keeps the change deliberately small and command-path-local:

- submitted `find` now reports `find: target @ line:col (i/n)`
- `find_next` now reports `findnext: target @ line:col (i/n)`
- `find_prev` now reports `findprev: target @ line:col (i/n)`
- no-query and no-hit paths now fail explicitly (`no active search`, `not found`)

The implementation intentionally does **not** turn incsearch into a chatty status
stream while the user is typing. Incremental search keeps its old behavior:
update the cursor and shared search state quietly, and reserve explicit success
messages for committed movement (`submit_prompt`, `FindNext`, `FindPrevious`).

That keeps the project aligned with the current editor goals:

- **trust**: search movement tells the truth about what happened
- **flow**: repeated next/prev movement preserves orientation instead of merely
  teleporting the cursor
- **taste**: the cue reuses the existing tiny `i/n` summary instead of inventing
  a larger search UI
