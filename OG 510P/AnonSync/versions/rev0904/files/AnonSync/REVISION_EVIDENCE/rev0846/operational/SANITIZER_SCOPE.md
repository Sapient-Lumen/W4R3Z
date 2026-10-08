# rev0846 sanitizer scope

The final-source sanitizer lane used GCC 14.2 with AddressSanitizer and
UndefinedBehaviorSanitizer enabled, leak detection active, and fail-fast runtime
options.

It built and executed six focused executables:

- generic thread incarnation: 14 checks;
- local JSONL directory authority: 26 checks;
- local JSONL composed namespace: 64 checks;
- local JSONL backend namespace integration: 30 checks;
- local JSONL crash state machine: 52 checks; and
- SQLite connection authority: 133 checks.

The total is **319/319** with no sanitizer, undefined-behavior, or leak report.
The same six executables pass **319/319** under Clang 17 with `-Werror`.

This is a focused changed-boundary claim. It is not a full-project sanitizer
claim and, critically for this revision, it is not a ThreadSanitizer claim.
Thread affinity rejects use from the wrong exact thread; it does not make
concurrent access to one C++ object legal, serialize mutations, or prove absence
of data races. It is also not a general post-fork, storage, filesystem,
power-loss, process-exclusivity, or distributed-convergence claim.
