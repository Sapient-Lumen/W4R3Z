# Sanitizer scope

The rev0863 GCC sanitizer lane builds the two extracted focused tests and the
integrated `anonsync_core` domain-model executable with AddressSanitizer and
UndefinedBehaviorSanitizer.

The generated command graph contains 89 first-party C++ compile commands; all
89 carry `-fsanitize=address,undefined`. This includes the three sources in
`anonsync_sqlite_database_mutex_guard`, the retained busy owner, and the sidecar
adapter. All three selected executable link commands carry the same sanitizer
set.

The one uninstrumented compile command is the bundled SQLite 3.53.3 C
amalgamation. This is deliberate and remains a stated nonclaim. The lane is not
full-project sanitizer coverage and is not ThreadSanitizer coverage.
