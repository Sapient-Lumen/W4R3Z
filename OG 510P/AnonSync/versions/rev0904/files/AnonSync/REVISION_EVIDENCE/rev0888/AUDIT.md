# rev0888 authority audit

## Heart of the correction

AnonSync is an authority-accounting system. Exact validated history and the live owner of the current cutpoint govern operation identity, dispatch, receiver effect, receipt, retry, settlement, and cleanup. A TLS return code, zero byte count, readiness event, local timeout, source token, or test summary remains subordinate evidence.

Rev0888 removes the last synchronous operation from the receiver's post-effect receipt path. One move-only heap-stable write owner now retains the exact 8-byte record prefix, exact canonical body, phase, offsets, pending operation range, readiness direction, and authenticated stream reservation from pre-I/O preparation through local completion. The receiver can therefore report a genuine zero-byte first-prefix WANT after durable publication without erasing the inbound decision or pretending that no operation began.

## Cutpoint behavior

`prepare_sync_replica_tls_record_write_or_throw` performs validation, allocation, exact body copying, prefix construction, channel re-attestation, and exclusive stream reservation before the first `SSL_write_ex`. Destroying that untouched owner releases the idle reservation. Once any write is attempted, including a WANT with zero accepted bytes, abandonment poisons the stream because the exact pending OpenSSL operation cannot be substituted safely.

Each advance issues at most one bounded prefix or body write. A successful complete prefix returns an observable progress frontier before any body operation. The legacy begin factory delegates to the same state but drives only to that frontier; sender file dispatch therefore does not retain a SQLite guard across network polling. Prefix WANT in the guarded sender path remains fail-closed and eligible for exact pre-prefix claim release.

The receiver exchange uses the prepared form. Its deadline result now distinguishes no receipt attempt, attempted first-prefix WANT, prefix progress, complete prefix, body progress, and local completion. Deadline expiry snapshots those facts, discards the application stream, retains any durable idempotent inbound decision, and leaves sender settlement unchanged.

## Validation synchronization audit

The first complete CTest invocation produced 202/203 because `anonsync_sqlite_connection_authority_test` timed out at 15.01 seconds. An immediate isolated rerun passed, but the contradictory observation was retained and investigated.

The test-only `PolicyRetirementMutexProbe` initialized its atomic wait baseline from the current requested ticket. If ticket one was published before the worker's first load, the worker could wait for a future value and lose the only request. The worker now compares requested work with an explicit completed-ticket frontier starting at zero. A deterministic regression constructs the probe with ticket one already published before worker entry. The corrected test passed 200 consecutive processes and 31,000 checks; the final complete suite passed 203/203.

## Runtime evidence

A fresh out-of-tree GCC 14 Debug build completed all 393 Ninja steps in 159 seconds and then reported no work. The corrected source passed all 203 registered tests in one invocation and all 75 audit/policy-selected tests.

The real TLS/SQLite/file-effect executable passed 1,867/1,867 assertions independently under GCC Debug, Clang 17 Release C++ `-Werror`, and GCC ASan/UBSan with leak detection. Fifty GCC repetitions passed 93,350/93,350 assertions; ten sanitizer repetitions passed 18,670/18,670. The SQLite connection-authority binary passed 155/155 in each focused compiler lane and 31,000/31,000 assertions across 200 GCC processes. Twelve selected source audits passed 358/358; package-path policy adds 27/27.

The new real-socket matrix forces untouched preparation, caller-buffer mutation, explicit prefix completion, saturated first-prefix WANT, continuation movement, attempted-WANT abandonment poison, durable visible publication followed by receipt-prefix timeout, unchanged sender outbox authority, and exactly one visible effect.

## Audit/refactor and waste correction

The retired synchronous prefix helper and its duplicate OpenSSL loop are gone. Prefix and body now share one retry implementation, one exact-pointer/range validator, one BIO/socket/policy reproof path, one bounded-step rule, one poll owner, and one abandonment rule.

Validation was moved out of the release surface. More than one gigabyte of in-source Debug, Clang, sanitizer, CMake, test, and Python cache products was removed before active projection. The final clean build ran in a separate directory that is not packaged. This prevents proof machinery from dominating source inventory or silently entering the manifest.

## Severe remaining composition gap

The receiver exchange remains a production C++ authority leaf with integration coverage, but source inventory still finds no production caller outside its declaration and definition, and the shipped `anonsync_core` target does not link it. The next useful milestone remains a small process/thread-affine replica service that owns authenticated acceptance, one bounded conversation, terminal close/discard, and persistent typed retry/dead-letter state.

The full-history causal and file-effect owners should remain correctness, repair, migration, and differential oracles while an indexed production owner is introduced. Long-running operation also still requires peer/folder quotas, staging expiry, fairness, garbage collection, membership/key lifecycle, compaction/rejoin authority, and crash injection across every durable and transport frontier.

## Nonclaims

No claim is made for peer receipt from local OpenSSL completion, exactly-once network delivery, atomicity across sender and receiver databases, durable partial TLS-record resume across restart, bounded time inside OpenSSL, sender prefix polling under a durable intermediate state, production listener/daemon behavior, complete retry/dead-letter policy, full-project Clang or sanitizer coverage, ThreadSanitizer, formal proof, anonymity, unlinkability, metadata privacy, traffic-analysis resistance, or externally trusted signed provenance.
