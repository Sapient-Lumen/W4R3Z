# Process-local SQLite authority research — rev0801

Retrieved and reviewed on 2026-07-15.

## SQLite: carrying a connection across `fork()`

SQLite's official corruption guidance says an application must not use a
connection in a child when that connection was opened in the parent. It also
warns that even child-side `sqlite3_close()` can perform cleanup that removes
content needed by the parent. This directly supports fail-stopping inherited
connection-adjacent cleanup rather than treating a duplicated descriptor as an
independent owner.

Reference: <https://www.sqlite.org/howtocorrupt.html#_carrying_an_open_database_connection_across_a_fork_>

## POSIX: `fork()` handlers and child ordering

POSIX specifies that child and parent handlers registered with
`pthread_atfork()` run in registration order, while prepare handlers run in
reverse registration order. The rev0801 token uses a child handler to advance
its copied lineage before ordinary `fork()` returns to application code. The
runtime PID check remains a fallback, so a handler registered earlier that
queries AnonSync authority cannot resurrect the parent token.

Reference: <https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_atfork.html>

## POSIX/Linux: the post-fork execution boundary

A child created from a multithreaded process contains only the calling thread
but inherits memory containing the states of other synchronization objects.
Until `exec`, only async-signal-safe work is generally permitted. Rev0801's
child hook is deliberately limited to `getpid`, lock-free atomic load/store,
and direct `_Exit` on malformed state. This is a denial boundary, not a claim
that arbitrary C++ or SQLite work after multithreaded `fork()` is safe.

References:

- <https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html>
- <https://man7.org/linux/man-pages/man2/fork.2.html>

## `_Fork()` and raw process creation

POSIX.1-2024 `_Fork()` does not invoke handlers registered with
`pthread_atfork()`. A direct `_Fork()` descendant is still rejected when it
first asks for the current token because its kernel PID differs. An entire
unobserved `_Fork()` or raw-clone lineage that eventually reuses an ancestor PID
is outside rev0801's proof boundary and remains documented as residual risk.

Reference: <https://man7.org/linux/man-pages/man3/_Fork.3.html>

## SQLite VFS lifetime

SQLite states that an application must not modify a registered `sqlite3_vfs`
object and that the VFS object and its methods form SQLite's operating-system
interface. Rev0801 does not rush a process-filtering VFS wrapper into this
trusted boundary. The existing seal continues to pin and re-observe the exact
registered VFS object; process denial is added to the C++ owners and hostile
verification callback. A complete wrapper would need to cover every
`sqlite3_io_methods` version and remain alive until all opened files close.

Reference: <https://sqlite.org/c3ref/vfs.html>
