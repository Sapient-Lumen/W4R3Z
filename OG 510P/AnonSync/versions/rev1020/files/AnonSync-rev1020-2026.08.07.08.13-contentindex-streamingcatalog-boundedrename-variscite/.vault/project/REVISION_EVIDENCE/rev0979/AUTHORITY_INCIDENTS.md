# Rev0979 validation-authority incidents

The cloudtainer contained multiple stale or concurrent validation lanes. Two wrote one shared build cache; later launchers created `.validation-gcc` and orchestration scripts inside the active project and repeatedly restarted mutable-source builds. A rev0979-name cleanup family interrupted sanitizer commands based on process spelling rather than source identity.

Corrections:

1. compared the accepted implementation against a recovery snapshot and the exact sealed parent;
2. quarantined the mutable authority path and removed every in-project build/orchestration artifact absent from the parent;
3. froze one clean wrapper and preserved a deterministic compressed source snapshot;
4. built GCC and Clang from byte-reconciled clean source copies;
5. moved the final sanitizer lane to neutral process paths to avoid name-based termination; and
6. excluded every interrupted, overlapping, shared-cache, mutable-source, or source-divergent result.
