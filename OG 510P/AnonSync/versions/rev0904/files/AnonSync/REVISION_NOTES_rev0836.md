# AnonSync rev0836 — post-reap authority fence

Rev0836 corrects a lifecycle-authority defect in the test-process capture
infrastructure. Rev0835 could reap the exact leader while retaining a numeric
process-group value; a later output-drain failure could then signal that group
number after the identity evidence that authorized it was gone.

The revision introduces one move-only `TestProcessTopologyOwner` and moves all
nine direct `kill`/`waitid`/`waitpid` sites into its compiled implementation.
Exact observation, surviving-group termination, exact reap, and authority
consumption are one transition. The inherited and self-exec wrappers retain no
numeric group escape and contain zero direct lifecycle syscalls.

A deterministic linker-wrap oracle adds 24 checks over success and syscall
failure branches. Linux integration tests force post-reap drain timeouts and
prove no stale group signal occurs. Intentionally infinite hostile descendants
now have independent fail-safe alarms.

Validation: 124/124 CTest tests, 36/36 source-audit tests, 60/60 repeated owner
executions, focused GCC ASan/UBSan and Clang 17 runs, exact source-patch replay,
and zero-step final dependency closure. See `REVISION_EVIDENCE/rev0836/` for the
complete evidence and claim boundary.
