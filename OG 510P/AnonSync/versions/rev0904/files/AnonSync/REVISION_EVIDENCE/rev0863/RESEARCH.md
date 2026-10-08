# Rev0863 research

Primary SQLite sources consulted on 2026-07-20:

- Busy timeout API: https://sqlite.org/c3ref/busy_timeout.html
- Busy handler API: https://sqlite.org/c3ref/busy_handler.html
- Result and extended result codes: https://sqlite.org/rescode.html

The busy-timeout contract describes repeated sleeping until at least the
configured amount of sleep has accumulated. The busy-handler contract states
that the callback's second argument counts prior invocations for the same
locking event and that the handler may be skipped when invoking it could
encourage deadlock. `SQLITE_BUSY` can arise at transaction start, during
statements, or at commit.

Rev0863 therefore treats requested sleep—not scheduler elapsed time—as the exact
resource authority; shares one allowance across every locking event in the
owner lifetime; keeps the owner live through transaction cleanup; and translates
a busy result only when callback-owned sticky exhaustion evidence exists.
