# Research notes — inherited lock authority and self-exec boundaries

Accessed 2026-07-18.

## Primary sources

- Linux `fork(2)`: https://man7.org/linux/man-pages/man2/fork.2.html
  - A child inherits descriptors referring to the same open file descriptions and inherits `flock(2)` locks.
  - In a multithreaded process, only async-signal-safe operations are generally safe before `execve()`.
- POSIX `fork`: https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html
  - The child of a multithreaded process must restrict work to async-signal-safe operations until exec.
- SQLite “How To Corrupt An SQLite Database File”: https://www.sqlite.org/howtocorrupt.html
  - An SQLite connection opened in the parent must not be used or even closed through SQLite in the child; child connections must be opened in the child.

## Design inference

The generic holder scenarios should self-exec and reacquire filesystem/SQLite authority in a fresh image. A raw fork remains justified only when inherited open-file-description lock semantics or inherited process-incarnation invalidation is exactly the property under test. Such probes should perform the smallest possible child path, avoid SQLite, terminate through the fail-stop or `_Exit` path, and be bounded and reaped by the parent.

## Speculation

The next raw-fork reductions should split mixed tests into an inheritance micro-oracle plus a self-exec integration oracle. Over time, this can leave raw fork concentrated in a small process-capability test library rather than scattered across persistence and publication tests.
