# Rev1006 authority incidents and exclusions

Several cloudtainer remounts removed unsealed worktrees and disposable build
caches. A discarded validator also overlaid an unrelated status-v26 branch and
reported 558 GCC / 269 sanitizer edges. Independent clean configuration of the
canonical source proved the actual graphs are 557 GCC edges and 268 sanitizer
product edges; every 558/269 record and archive is excluded.

A duplicate Ninja invocation briefly entered a shared cache and was terminated.
The final source was reconstructed from the exact rev1005 baseline and the
canonical binary patch, validated from immutable source, and copied into the
retained wrapper only after changed-path equality. Interrupted aggregate CTest
wrappers and the pre-correction sanitizer fixture-link failure are also excluded.
