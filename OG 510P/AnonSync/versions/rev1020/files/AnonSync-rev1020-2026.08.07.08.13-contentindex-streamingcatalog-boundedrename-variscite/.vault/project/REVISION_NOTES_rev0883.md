# AnonSync rev0883 revision notes

## Mission-level correction

AnonSync treats exact authorized evidence and live capabilities as the owners of
identity, causality, dispatch, retry, receipt, and visible effect. A C++ move may
transfer a wrapper value, but it cannot silently transfer the process/thread
authority to mutate the authenticated TLS stream beneath it.

Rev0882 enforced exclusive unfinished-record ownership for ordinary reads and
writes. Its no-throw continuation cleanup still permitted a foreign thread to
set the shared stream's poison and active-reservation flags before the final SSL
destructor noticed the affinity contradiction. Rev0883 fences the first
mutation, not merely the eventual free.

## C++ implementation

### Central no-throw owner fence

`detail::SyncReplicaTlsAuthenticatedState` now owns one
`require_owner_or_fail_stop_noexcept()` helper. It verifies the exact process
incarnation, then the exact thread incarnation, and terminates immediately on a
contradiction without C++ unwinding or teardown hooks.

The helper runs before:

- successful continuation completion clears `record_write_active_`;
- abandonment/failure poisoning changes `poisoned_` or reservation state; and
- `release_ssl_noexcept()` calls `SSL_free()`.

The last path previously duplicated its own process/thread checks. Centralizing
all no-throw enforcement reduces drift while preserving the separate throwing
contract used by ordinary live I/O.

### Explicit continuation contract

The public header now states that finishing, abandoning, destroying, or
move-assigning an active continuation from another process or thread fails
stopped before shared TLS state can be mutated. Same-owner abandonment continues
to poison the stream. An accepted record prefix cannot be separated from its
exact body and then treated as a reusable framing boundary.

## Runtime proof

The TLS test creates a real TLS 1.3 connection and authenticates a sender channel
inside an isolated child process. It begins a nine-byte record continuation,
moves that active capability into a foreign `std::thread`, and abandons it there.
The destructor must terminate the child with
`kSyncProcessCapabilityViolationExitCode`; returning a sentinel or surviving the
join fails the test.

This adds one compiled check to the existing continuation, socket/BIO,
claim-retry, and ambiguity matrix. The focused TLS executable reports 75/75.

## Audit/refactor

`tools/audit_sync_file_tls_dispatch.py` advances to format v2 and grows from 28
to 32 deterministic checks. New checks require:

- one process-then-thread no-throw fence;
- that completion, poison, and `SSL_free()` call it before mutation;
- an explicit foreign-owner cleanup contract;
- the process-isolated foreign-thread destructor case; and
- the rev0883 design/package record.

The release verifier now requires
`TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md` for rev0883 and later packages.
Lexical structure remains hygiene evidence only; it does not establish C++
object lifetime, OpenSSL semantics, or race freedom.

## Rejected scope and waste correction

A separate mutable workspace acquired a 578-line incremental nonblocking receive
prototype during the review. The prototype changed public APIs, failed its first
clean compile, and had no runtime coverage for the new state machine or failure
frontiers. It was rejected rather than repaired opportunistically. Rev0883 was
rebuilt from the independently verified rev0882 archive and keeps the change
narrow and attributable.

The receive direction is still strategically necessary. It should return in a
separate revision with explicit prefix/body offsets, bounded allocation,
WANT_READ/WANT_WRITE ownership, peer-close and cancellation policy, stream
poisoning, backpressure tests, and restart nonclaims.

## Online primary-source review

OpenSSL documents that most objects are not safe for simultaneous use. It also
documents that `SSL_free()` may release the SSL object, buffering BIO, read and
write BIOs, cipher lists, and session references. Those facts support treating
cleanup as owner mutation under the same affinity fence as record progress.
OpenSSL's write documentation also preserves the requirement to retry a blocked
write with the same arguments, reinforcing the need for a stable event-loop
owner before AnonSync claims resumable nonblocking progress.

Sources and exact rationale are recorded in
`TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md`.

## Validation

Fresh cloudtainer evidence for rev0883 records:

- clean GCC 14.2 Debug graph: 381 fresh Ninja actions across the focused-first
  build and resumed all-target closure; interruptions were command-window
  limits, not compiler failures;
- complete registered CTest gate: 192/192 in one final parallel invocation;
- complete audit-named CTest block: 61/61;
- focused GCC Debug: 13/13 executables, 5,199/5,199 checks;
- focused Clang 17 Release with C++ `-Werror`: 5,199/5,199 checks;
- focused GCC ASan/UBSan with leak detection and bundled SQLite C
  instrumentation: 5,199/5,199 checks;
- repeated mixed authority gate: 20 iterations, 100/100 executions,
  5,940/5,940 checks;
- targeted TLS continuation gate: 100/100 executions, 7,500/7,500 checks;
- selected lexical source audits: 509/509 checks across 17 audits; and
- final no-work dependency closure in GCC, Clang, and sanitizer build graphs.

The first complete CTest attempt correctly failed two exact process-topology
audits after the new child-process test increased the TLS translation unit from
one to two inherited spawn sites. A third cross-audit check then exposed its old
aggregate total. All three inventories were updated without relaxing discovery:
15 consumer translation units, 27 inherited spawn sites, and 35 inherited or
fresh-image process campaigns. The final 192/192 gate is the claimed result.

## Deliberate nonclaims

Rev0883 does not claim:

- that C++ move syntax transfers live process/thread authority;
- arbitrary concurrent-use safety or ThreadSanitizer coverage;
- a receive continuation or production receiver loop;
- resumable WANT_READ/WANT_WRITE state;
- durable dispatch-started/body-offset recovery;
- atomic SQLite-plus-TLS delivery;
- peer receipt, receiver admission, or visible effect from local write progress;
- exactly-once network delivery;
- use of the newer stack by the shipped executable;
- complete retry, membership, revocation, compaction, rejoin, or anonymity; or
- externally trusted signed provenance, formal proof, full-project Clang, or
  full-project sanitizer coverage.

## Next engineering sequence

The next high-value slice remains a production-shaped single-owner replica
service. It should receive exact framed messages over one authenticated event
loop, drive receiver evidence and bounded payload state, publish an immutable
file effect, return a terminal effect receipt, and settle the sender only from
that receipt. Crash and backpressure injection should cover every prefix byte,
body offset, receiver transaction, payload write, rename, directory durability,
receipt byte, and sender settlement frontier.
