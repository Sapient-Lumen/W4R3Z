# rev0887 authority audit

## Heart of the correction

AnonSync is an authority-accounting system. A partial frame, readiness wakeup, local TLS write, timeout, filename, audit token, or summary cannot become durable receiver effect or sender settlement authority. Rev0887 centralizes the receiver's load-bearing order in one production C++ leaf:

> complete bounded authenticated request → durable idempotent effect/evidence decision → fresh live-channel re-attestation → exact terminal receipt

The request and receipt consume independent absolute monotonic cutpoints. Request expiry invokes no durable callback. Receipt expiry after a durable decision cannot roll that decision back or fabricate sender knowledge. Abandoned application conversations poison the local authenticated stream so a later record cannot be reinterpreted across a missing response boundary.

## Runtime evidence

The final GCC 14 Debug source passed all 203 registered tests in one invocation and all 75 audit/policy-named tests. The real TLS/SQLite/file-effect matrix reports 1,851/1,851 assertions independently under GCC Debug, Clang 17 Release with C++ `-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite instrumentation. Fifty GCC repetitions passed 92,550/92,550 assertions; ten sanitizer repetitions passed 18,510/18,510. Eleven selected source audits passed 273/273; the two package path-policy matrices add 27/27.

The receiver matrix covers exact success and sender settlement, a durable publication with an already-expired receipt budget and zero response-prefix bytes, a fresh exact claim/channel retry returning `AlreadyPublished`, a genuine partial-frame WANT timing out with unchanged durable snapshots, an already-expired request budget, and complete malformed-frame rejection with stream discard.

## Audit/refactor findings

The unfinished tree contained a concrete test abstraction break: one helper accepted only the raw TLS write continuation even though the file-dispatch continuation intentionally shares the same bounded progress interface. The helper now drives a stable lvalue template, avoiding duplicate loops and repeated moves. Two older lexical audits also depended on obsolete diagnostic literals; they now inspect the shared semantic owner rather than freezing incidental wording.

Projection generation itself found and removed a newly created `tools/__pycache__` bytecode file before sealing. That near miss validates the fail-closed staged-byte inventory: generated files are discovered from the release surface rather than assumed absent.

## Severe remaining composition gap

The new receiver exchange is production C++ and has real integration coverage, but source inventory finds no production caller outside its declaration/definition, and the shipped `anonsync_core` target does not link the exchange leaf. The newer causal SQLite, file-effect, sender dispatch, and receiver exchange stack therefore remains a correctness island beside the broad legacy executable path. The next milestone should be a small process/thread-affine replica service that owns authenticated connection acceptance, invokes exactly one exchange per application conversation, closes terminal channels, and persists bounded retry/dead-letter policy.

A second sharp edge remains: the current 8-byte TLS record-prefix writer is synchronous. On strict nonblocking readiness loss it throws and poisons rather than returning a resumable prefix continuation. After a durable effect this remains safe through idempotent retry, but the caller receives an exception rather than a typed result retaining the exact inbound decision. A future prefix continuation or typed post-effect transport-failure result would improve operability without weakening authority.

## Scale and waste

The full target graph remains expensive and semantically fragmented: many libraries/executables coexist with very large source centers. Rev0887 adds one narrow dependency leaf rather than extending the monolith, but it does not solve full-history re-attestation cost, build fan-out, staging quotas, fairness, payload expiry, garbage collection, compaction, or rejoin. The full-history owners should remain correctness/repair oracles while an indexed production owner is differentially tested against them.

## Nonclaims

No claim is made for a production listener, peer receipt from local OpenSSL completion, exactly-once network delivery, atomicity across sender and receiver databases, durable partial TLS-record resume, bounded time inside OpenSSL, complete crash injection, membership/key lifecycle, peer/folder quotas, dead-letter ownership, compaction/rejoin, full-project Clang or sanitizer coverage, ThreadSanitizer, formal proof, anonymity, unlinkability, metadata privacy, traffic-analysis resistance, or externally trusted signed provenance.
