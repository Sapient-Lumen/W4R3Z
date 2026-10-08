# rev0783 primary references

Accessed 2026-07-14. These references support the boundary choice; they do not
replace AnonSync's executable tests.

- SQLite, “How To Corrupt An SQLite Database File,” section “Carrying an open
  database connection across a fork”:
  https://sqlite.org/howtocorrupt.html#_carrying_an_open_database_connection_across_a_fork_
- SQLite FAQ, process/fork guidance: https://sqlite.org/faq.html
- SQLite `sqlite3_close()` / `sqlite3_close_v2()` contract:
  https://sqlite.org/c3ref/close.html
- SQLite `sqlite3_finalize()` contract: https://sqlite.org/c3ref/finalize.html
- SQLite open contract, including output handles on failure:
  https://sqlite.org/c3ref/open.html
- SQLite threading modes: https://sqlite.org/threadsafe.html
- The Open Group Base Specifications, `_Exit()`:
  https://pubs.opengroup.org/onlinepubs/9799919799/functions/_Exit.html
- The Open Group Base Specifications, `fork()`:
  https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html

## Interpretation

SQLite's serialized mode does not make a connection inherited across a process
boundary valid. The child has copied userspace state, while kernel-visible file
and lock effects persist under different lifetime rules. An inherited
`sqlite3_close_v2()` or `sqlite3_finalize()` is not harmless cleanup. AnonSync
therefore checks process incarnation before ownership use or destruction and
uses `_Exit()` when continuing would risk SQLite undefined behavior.

A controlled child may open a new connection after it has entered an ordinary
single-threaded execution path. Rev0783 does not relax POSIX's rule that after a
fork from a multithreaded process, only async-signal-safe operations are allowed
until `exec()`.
