# Restore namespace-authority differential

`sqlite_restore_namespace_authority_test.cpp` has SHA-256 `11bb7d7f424dc05cae00eb694fe478f0f2e67d3996ad16072f44aedd5caaff48` and
is compiled unchanged against the sealed rev0820 parent and rev0821.

The harness first creates nine foreign names matching rev0820's predictable
`.destination.sqlite.restore-tmp-<pid>-<epoch-second>.sqlite` family around
the current second. Rev0820 exits 2 after deleting or changing one of those
names before it creates its writable staging database. Rev0821 exits 0 and
preserves all nine byte-for-byte because restore no longer creates or
pre-cleans that namespace.

The same current harness then places a foreign `-wal`, `-shm`, or
`-journal` beside an empty destination. Each restore is rejected, the sidecar
remains byte-exact, the main file remains empty, and no atomic-publisher temp
remains. Current output is 27 passed, 0 failed.

This is a same-source behavioral differential, not a proof against every
arbitrary same-UID namespace race. The restore lock and write gate coordinate
AnonSync participants; hostile principals that can mutate the destination
directory remain a broader isolation problem.
