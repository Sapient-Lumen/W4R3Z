# Rev0848 sanitizer scope

The GCC 14 focused sanitizer tree enables AddressSanitizer and
UndefinedBehaviorSanitizer with frame pointers. Runtime execution sets leak
detection and abort-on-error/halt-on-error options.

Instrumented and executed focused surfaces:

- `SqliteBusyHandlerOwner` and its 32-check direct test;
- the persistence process/fork consumer and its 31-check corpus;
- the focused peer-ingress lifecycle consumer and its 49-check corpus.

Total focused runtime: **112/112**.

The CMake sanitizer graph explicitly includes the owner library, owner test,
process/fork test, and focused lifecycle driver. Command evidence records
`-fsanitize=address,undefined` on their compile/link paths.

Not claimed:

- full-project sanitizer completion;
- sanitizer instrumentation of bundled SQLite (`ANONSYNC_SANITIZE_BUNDLED_SQLITE=OFF`);
- ThreadSanitizer or general race-freedom;
- Release-mode sanitizer behavior;
- Windows sanitizer behavior.

The large monolithic `anonsync_core` sanitizer executable was not used as a
release gate. The focused driver was introduced specifically to cover the
modified runtime consumer without rebuilding unrelated selftest corpora.
