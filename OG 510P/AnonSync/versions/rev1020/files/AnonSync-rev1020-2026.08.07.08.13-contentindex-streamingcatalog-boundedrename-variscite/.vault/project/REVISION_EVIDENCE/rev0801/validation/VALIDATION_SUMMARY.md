# Rev0801 validation summary

- Complete rev0799 source parent: **25/25** package checks.
- GCC 14 Debug/`-Werror`: full build and **64/64 CTest**.
- Focused process/persistence repetition: **100/100 executions** across 20 iterations.
- GCC 14 ASan/UBSan: **25/25 focused executions**.
- Clang 17 conversion/sign-conversion/shadow `-Werror`: **25/25**.
- GCC 14 `-O3 -DNDEBUG -Werror`: **25/25 first-party focused executions**.
- Nine registered architecture audits passed; process authority: **83/83**.
- Preserved exploit changed from child exit 0 with parent-stage deletion to direct exit 86 with parent stage and verification intact.
- The strengthened package verifier rejects the incomplete rev0800 cube.

No full-core sanitizer or third-party optimized-warning-clean claim is made.
