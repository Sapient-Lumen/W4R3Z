# Rev0847 sanitizer scope

The sanitizer claim is deliberately focused.

GCC 14.2 compiled and linked these four final-source targets with
AddressSanitizer and UndefinedBehaviorSanitizer instrumentation:

- `anonsync_sqlite_verification_budget_test` — 70 checks;
- `anonsync_thread_incarnation_test` — 14 checks;
- `anonsync_sqlite_persistence_process_authority_fork_test` — 21 checks; and
- `anonsync_inherited_test_process_test` — 23 checks.

All **128/128** checks passed with `ASAN_OPTIONS=detect_leaks=1`. No ASan,
UBSan, or leak report appears in the retained runtime log. The death probes use
fresh inherited children and are expected to terminate with the reviewed
capability-violation exit status; the parent verifies that status.

This is not a full-project sanitizer build. It is not ThreadSanitizer evidence,
not proof of race freedom, and not proof that concurrent misuse is safe. Exact
thread affinity rejects sequential transfer and fail-stops selected `noexcept`
misuse; it is not a mutex, executor, lifetime protocol, or happens-before edge.
