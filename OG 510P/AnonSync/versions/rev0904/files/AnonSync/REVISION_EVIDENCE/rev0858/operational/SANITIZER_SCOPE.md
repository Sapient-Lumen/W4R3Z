# Rev0858 sanitizer scope

The GCC 14 lane enables AddressSanitizer and UndefinedBehaviorSanitizer through
`ANONSYNC_ENABLE_SANITIZERS=ON`, with leak detection and halt-on-error at
runtime. It exercises six programs totaling 728 checks:

- conflict resolution: 17;
- manifest validation: 34;
- manifest identity: 19;
- hostile-locale manifest hashing: 16;
- conflict convergence: 38; and
- integrated sync-domain model: 604.

The generated Ninja command graph is retained and proves sanitizer flags on the
new owner compile, the focused validation executable link, and the integrated
core link.

The bundled SQLite amalgamation is deliberately not instrumented in this lane.
No full-project sanitizer, ThreadSanitizer, MemorySanitizer, or Windows
sanitizer claim is made.
