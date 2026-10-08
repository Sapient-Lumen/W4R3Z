# rev0845 sanitizer scope

The final-source sanitizer lane used GCC 14.2 with AddressSanitizer and
UndefinedBehaviorSanitizer enabled, leak detection active, and fail-fast runtime
options.

It built and executed five focused local JSONL executables:

- frozen publication owner: 42 checks;
- directory authority: 23 checks;
- composed namespace: 58 checks;
- backend namespace integration: 30 checks; and
- crash state machine: 52 checks.

The total is **205/205** with no sanitizer or leak report.

This is a focused changed-boundary claim. It is not a full-project sanitizer
claim, not a ThreadSanitizer claim, not a process-exclusivity proof, and not a
filesystem or storage power-loss claim.
