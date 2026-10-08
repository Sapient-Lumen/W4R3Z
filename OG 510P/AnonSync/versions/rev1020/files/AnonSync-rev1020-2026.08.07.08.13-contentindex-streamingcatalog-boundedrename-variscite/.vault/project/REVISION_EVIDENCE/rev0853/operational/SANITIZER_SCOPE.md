# Rev0853 sanitizer scope

The focused sanitizer lane used GCC 14.2 with
`-fsanitize=address,undefined`, frame pointers, leak detection, and
halt-on-error behavior. Ninja command expansion was captured and checked to
confirm that the busy-owner implementation, SQLite support gateway, focused
tests, and executable link steps carried the sanitizer flags.

Nine focused executables passed **1107/1107** checks. They cover the new busy
owner and timeout gateway plus the retained authorizer, connection authority,
transaction exception/allocator campaigns, process authority, and peer-ingress
schema composition.

The bundled SQLite 3.53.3 C translation unit was deliberately not instrumented,
matching the project's established focused boundary. This is not a full-project
sanitizer claim. ThreadSanitizer, MemorySanitizer, Release-mode sanitizers,
Windows, arbitrary concurrent close/use, and foreign raw SQLite API replacement
remain outside this lane.
