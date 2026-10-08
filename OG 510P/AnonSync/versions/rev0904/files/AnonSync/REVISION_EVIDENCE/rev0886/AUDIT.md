# rev0886 authority audit

## Heart of the correction

AnonSync's mission is exact authority accounting: a readiness hint, descriptor number, timeout, local TLS write completion, filename, or cached build product must never silently become identity, durable receipt, or visible effect authority. Rev0886 closes one transport scheduling gap while preserving that boundary.

The transport already retained exact read and write continuations across OpenSSL `WANT_READ`/`WANT_WRITE`. It did not have one symmetric bounded owner for waiting and advancing those continuations. Callers could therefore renew relative waits, cache a stale descriptor target across interruption, duplicate scheduling logic, or accidentally turn one wakeup into an unbounded progress loop.

`sync_replica_tls_poll` now owns exactly one readiness wait and at most one continuation advance. It requires a continuation already at a genuine WANT frontier; re-proves the exact typed target before each `poll`; retains one absolute `steady_clock` deadline across `EINTR` and `EAGAIN`; rounds positive sub-millisecond waits upward; checks the cutpoint after wakeup; and delegates hangup, close, truncation, and protocol classification back to the re-attesting continuation and OpenSSL. Read and write mappings are exhaustive and unsupported platforms fail closed.

## Runtime evidence

The staged source passed all 200 registered tests in ten exact non-overlapping ranges. One initial range exposed a legacy monolithic self-test termination after transient SQLite lock diagnostics; the failed log is retained, and both the isolated test and complete range passed on rerun. The independent audit/policy selection passed 72/72.

The real TLS matrix reports 726/726 checks under GCC 14 Debug, Clang 17 Release with C++ `-Werror`, and GCC 14 ASan/UBSan with leak detection and bundled SQLite instrumentation. Fifty GCC repetitions passed 36,300/36,300 checks; ten sanitizer repetitions passed 7,260/7,260. The matrix exercises expired and idle deadlines without consuming retry state, prefix-only progress, read/write target changes, signal interruption, clean close, exact two-megabyte transfer, and the existing session/BIO/socket lifetime fences.

Eight selected structural audits passed 189/189; the two release path matrices add 27 passing cases. These are hygiene and inventory, not semantic proof.

## Release verifier correction

The prior verifier rejected a legitimate evidence basename containing `build-` while allowing an actual directory named `build/`. The classifier now applies build-directory rules only to path components known to be directories and keeps suffix/basename rules on the final file. The positive/negative matrices preserve build-named evidence and reject real build trees, CMake products, binaries, caches, VCS metadata, and core dumps.

## Cloudtainer waste audit

Retained reproducible build trees filled the filesystem and blocked validation. Conservative cleanup removed only older generated compiler trees, preserving source, evidence, parent archives, sealed revisions, and current lanes. Approximately 21 GiB was recovered. `CLOUDTAINER_BUILD_RETENTION_AUDIT_rev0886.md` defines a quota/expiry boundary so generated caches do not become accidental archival policy.

## Missing mission composition

This remains a tested authority leaf rather than the shipped end-to-end product path. The largest gap is still one process/thread-affine service that composes authenticated accept/connect, bounded framed receive, canonical operation validation, receiver SQLite idempotency, bounded payload/effect staging, atomic visible publication, terminal effect receipt, and exact sender settlement. Local TLS completion is not peer receipt. Partial TLS byte state is not durable message state.

## Nonclaims

No claim is made for a production event loop, bounded wall-clock time inside OpenSSL, concurrent unsynchronized SSL/BIO/fd mutation, thread/process migration of pending I/O, durable partial TLS record resume, peer receipt from local completion, exactly-once remote effect, complete retry/dead-letter or membership/key lifecycle, compaction/rejoin, full-project Clang or sanitizer coverage, ThreadSanitizer, formal proof, signed provenance, anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance.
