# Audit — AnonSync rev0833

## Boundary under review

The reviewed question was not merely whether a child eventually execs. It was whether application code, C++ exception machinery, SQLite state, allocator state, or filesystem authority can be exercised in the fork-derived image before a fresh executable boundary establishes a new process owner.

Four tests failed that standard in rev0832:

1. the multi-process atomic writer executed the publication stack directly in eight fork children;
2. the atomic cutpoint corpus executed publication and observer code directly in fork children;
3. the payload crash corpus opened/configured SQLite and ran a transaction after fork; and
4. the peer-schema owner-close proof created SQLite and schema-attestation owners after fork.

Rev0833 gives each campaign an exact versioned self-exec instruction. The fresh image first verifies the canonical test-process boundary, then parses and binds the instruction, then creates application/SQLite state.

## Prepared publication correction

The prior inherited-capability path detected process mismatch by concatenating the caller label into a `std::runtime_error` and unwinding through publication error composition. In a fork child that path could allocate, enter exception machinery, and destroy copied C++ owners before termination.

The revised path consumes the child copy of the one-shot capability, calls the shared process-incarnation fail-stop primitive with a static string literal, and never reaches filesystem mutation or C++ unwinding on mismatch. The parent copy remains valid and is proven to publish afterward.

## Exact raw-fork fence

The executable audit lexically removes comments and ordinary/raw literals before counting calls. It proves:

- production inventory is empty;
- the test allowlist and per-file counts are exact;
- the four migrated campaigns contain no raw fork or `waitpid` and do contain the fresh-image owner protocol;
- the retained prepared-publication probe is minimal and bounded;
- the allocator-fault fork-exec child is restricted to descriptor operations, exec, and `_Exit`;
- the production mismatch path is direct fail-stop and does not concatenate the dynamic label;
- CMake links the test-only process owner to all four campaigns; and
- the audit itself is a timed CTest obligation.

The result is **10/10**, with **16 remaining test calls in 9 files** and **0 production calls**.

## Important residual finding

The remaining inventory is not uniformly mature. Fifteen calls are inheritance/lineage probes, but several older units still use blocking pipe reads or unbounded `waitpid`. The allocator-fault bridge also needs capture-capable self-exec supervision so a wedged worker cannot hold the parent on a blocking output pipe. These are recorded as next work, not silently treated as proved.

## Validation

The source and runtime boundary is covered by **278/278** focused audit checks, **327/327** direct runtime checks, **50/50** repeated focused executions, **120/120** complete batched CTest coverage, a GCC all-target build, a no-work dependency closure, Clang 17 `-Werror` compile of six changed translation units, and exact patch replay over **207/207** active files.

## Claim boundary

Self-exec test infrastructure is not a hostile-input sandbox. The revision does not prove arbitrary power loss, every kernel/filesystem behavior, Windows equivalence, or the project-level confidentiality/anonymity and distributed-convergence properties still missing from AnonSync.
