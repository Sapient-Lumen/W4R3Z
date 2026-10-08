# Rev412 — same-topic dormant help reopen preserves exact landing

Rev406, rev410, and rev411 already made dormant docs state part of the same
session-local replay story: Micromax could keep one explicit off-screen current
help target, branch from it when opening a different docs page, and preserve it
when replaying `helpback` / `helpforward` from outside the help buffer.

But one same-topic seam still lingered. If the user left a docs page, closed the
old help buffer, and later reopened that *same* docs topic by name, Micromax
still treated that as a fresh top-of-file open. The session already knew the
exact current landing, yet reopening the current page silently reset the cursor
back to `1:0`.

Rev412 keeps the fix deliberately small:

- reopening the current dormant docs topic now restores the remembered
  session-local cursor target when the old help buffer has been closed
- same-topic reopen still does **not** invent a new history entry or clear the
  forward stack
- active same-topic opens remain the existing no-surprise case: switching back
  to an already-open help buffer preserves its live cursor naturally

The goal is simple: once Micromax witnesses the current dormant docs landing,
reopening that same page should preserve it instead of demoting it to a fresh
file open.
