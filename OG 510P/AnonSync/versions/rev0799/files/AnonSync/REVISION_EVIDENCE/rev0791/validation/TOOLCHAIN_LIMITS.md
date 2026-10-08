# Validation limits

The pure replay-record boundary completed GCC ASan/UBSan five times. The
integrated sanitizer target did not finish building: compilation remained in
the large core archive, including `sync_domain.cpp`, `sqlite_replay_ledger.cpp`,
`reporting_selftests.cpp`, and `runner.cpp`. No integrated sanitizer pass is
claimed. The bundled SQLite amalgamation was intentionally not instrumented in
the default first-party sanitizer lane.

The principal ceiling of 4096 bytes is a new fail-closed resource limit. A
pre-existing database containing a larger principal will now be rejected on
restart or restore; there is no silent migration or truncation.
