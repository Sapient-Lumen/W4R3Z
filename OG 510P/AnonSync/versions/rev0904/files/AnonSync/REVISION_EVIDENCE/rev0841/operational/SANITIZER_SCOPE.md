# rev0841 sanitizer scope

GCC 14.2 AddressSanitizer and UndefinedBehaviorSanitizer were enabled with leak detection.
The new publication leaf ran its complete 34-check corpus. The exact relay implementation
and reporting selftest dependencies were sanitized and the 11-check crash/retry/idempotency
relay scenario completed under the hostile grouped locale.

A full monolithic `anonsync_core` sanitizer executable is not claimed. Compilation of the
very large `sync_domain_selftests.cpp` owner exceeded the cloud command window. This is
recorded as architecture/build debt rather than represented as a sanitizer failure or a
pass. The leaf and exact relay boundary were chosen so the changed production code still
received runtime sanitizer coverage.
