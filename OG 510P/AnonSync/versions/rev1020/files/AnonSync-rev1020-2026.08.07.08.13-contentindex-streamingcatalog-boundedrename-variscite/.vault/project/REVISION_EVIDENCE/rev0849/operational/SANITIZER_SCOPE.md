# Rev0849 sanitizer scope

The GCC 14 focused sanitizer tree enables AddressSanitizer and
UndefinedBehaviorSanitizer with frame pointers. Runtime execution sets leak
detection and abort-on-error/halt-on-error options.

Instrumented and executed focused surfaces:

- shared `SqliteRetainedCallbackClaim` through verification-budget and
  busy-handler consumers;
- `SqliteVerificationBudget` and its 107-check direct corpus;
- typed sealed-database open and its 97-check direct corpus;
- `SqliteBusyHandlerOwner` and its 32-check direct corpus;
- persistence process/fork ownership and its 37-check direct corpus;
- integrated restore prefix-continuity and SQLite hardening paths, 5 and 12
  checks respectively.

Total focused runtime: **290/290**. Command-graph evidence proves
`-fsanitize=address,undefined` on the changed C++ implementation/test compile
paths and on all five focused executable links.

Not claimed:

- full-project sanitizer completion;
- sanitizer instrumentation of bundled SQLite
  (`ANONSYNC_SANITIZE_BUNDLED_SQLITE=OFF`);
- ThreadSanitizer or general race-freedom;
- safe use after a caller enters SQLite `close_v2` zombie state outside the
  typed ownership protocol;
- Release-mode or Windows sanitizer behavior.
