# Rev0862 research

Primary sources consulted on 2026-07-20:

- SQLite progress handler API: https://sqlite.org/c3ref/progress_handler.html
- SQLite interrupt API: https://sqlite.org/c3ref/interrupt.html
- SQLite result and extended result codes: https://sqlite.org/rescode.html

The progress-handler contract permits one handler per connection, invokes it
periodically after an approximate number of virtual-machine instructions, and
aborts the operation when the callback returns nonzero. SQLite then exposes an
interruption result. Rev0862 therefore reuses the existing singleton callback
owner, treats callback counts as cooperative work accounting rather than exact
opcode accounting, and translates the generic interruption back into the
owner's sticky typed reason before cleanup.
