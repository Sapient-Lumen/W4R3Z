# AnonSync rev0881 revision notes

## Purpose

Rev0881 tightens three adjacent authority frontiers in the newer C++ delivery
slice:

1. canonical replicated path identity is separated from receiver-local filename
   capability before effect or causal authority is acquired;
2. a retained POSIX directory capability is re-proved in the caller's live Linux
   mount namespace, while process and outbox-clock boot identity share one strict
   bounded observer; and
3. an exact outbox claim is re-attested *after* arbitrary payload-source code and
   held under a scope-bound SQLite writer capability through bounded local frame
   construction.

The third correction closes the principal gap identified during the first
rev0881 pass. A normally returning callback could previously release, settle,
renew, replace, or simply age the durable attempt while the service continued
constructing a frame from its pre-callback C++ copy. Rev0881 now proves the live
row, owned time, retained operation, and complete staged cutpoint before any
frame can be returned.

This remains an authority-accounting revision rather than a claim of anonymous
networking or database-plus-socket atomicity. The returned frame is not itself
first-byte send authority and can become stale while queued outside the service.

## Exact parent

The exact lineage parent is the user-linked
`AnonSync-rev0880-2026.07.22.10.46-openat2mountfence-statxuniqueid-traversalowner-fdleakseal.zip`.
Its SHA-256 is
`3817a9bc7f84ed2bdcc4c27197515dd9aecf8223a85db90510e7b70691925639`.
No merge source or substituted parent is used.

## Receiver-local path capability

`validate_sync_relative_path_component_byte_limit()` first requires the existing
canonical relative-path grammar, then counts encoded bytes between `/`
separators. The local check is intentionally separate from canonical operation
validation: replicas with different filesystems must not disagree about global
operation identity.

On POSIX, `SyncReplicaFileEffectSqliteOwner::stage_or_throw()` derives a
conservative component ceiling from the retained root's frozen positive
`statvfs().f_namemax` and `_PC_NAME_MAX` observations. A canonical operation
that is provably unrepresentable returns `DestinationPathBlocked` after exact
operation/payload validation and an unchanged attested transaction. It creates
no effect row, retains no payload, advances no effect generation, admits no
causal evidence, and touches no namespace entry. The exact-ceiling boundary is
admissible. An unavailable or indeterminate ceiling is not guessed; the later
descriptor-relative publication syscall remains authoritative.

The outer file-delivery protocol is explicitly version 2. It adds
`EffectPathBlocked = 9` without renumbering earlier dispositions. Pre-effect
capacity/path receipts bind the exact request, authenticated channel, receiver
generation, and receiver cutpoint but carry neither an effect ID nor nested
causal evidence. Version-1 frames and pre-effect residue are rejected.

## Exact local retry release

Every validated nonterminal receipt releases the exact destination, operation,
and claim ID through the sender owner. Retry time is derived from the sender's
owned clock under a strictly positive, bounded local policy; the receiver does
not inject an absolute deadline.

Failures after claim minting but before a frame escapes use one centralized
`release_claim_after_pre_dispatch_failure_or_throw()` path. The original
failure is rethrown only after exact release succeeds. Missing, stale, expired,
or renewal-only contradictions are combined with the original error rather than
misreported as retry provenance.

## Post-callback outbox dispatch guard

`SyncReplicaSqliteOutboxDispatchGuard` is a noncopyable, nonmovable,
scope-bound C++ capability owning one live `BEGIN IMMEDIATE` transaction. The
service invokes arbitrary payload-source code *before* acquiring it. The owner
then:

1. validates the expected active claim identity;
2. begins writer authority and performs a complete durable restore;
3. returns typed `IntentMissing` or `StaleClaim` without sampling time;
4. permits only a nondecreasing deadline renewal on the same exact claim;
5. samples the injected owned clock and durably records/quarantines its result;
6. commits a clock-only revocation when the exact claim is expired;
7. proves the retained canonical operation is byte-for-byte identical; and
8. independently reloads and compares meta, clock, model, and outbox state before
   the transaction escapes as the guard.

While the guard is live, another SQLite writer cannot release, settle, renew, or
replace the row. The service re-proves channel liveness, builds and validates the
request, encodes the frame, and derives its digest under that bounded local
frontier. It statically requires no-throw movement into the returned optional,
commits the guard, and only then returns. Any construction failure destroys the
guard first, rolling back staged clock evidence and releasing the writer slot,
then performs the exact durable retry release.

The full staged-cutpoint verification was refactored into
`attest_staged_cutpoint_or_throw()` plus the existing commit wrapper. Ordinary
publication and dispatch guarding therefore share one independent reload and
comparison implementation instead of duplicating a security-critical sequence.

## Live mount namespace and shared boot observer

`SyncPosixMountNamespaceAuthority` retains `/proc/thread-self/ns/mnt`, freezes
its documented device/inode identity, and compares it with a freshly opened
current-thread handle on each proof. The original descriptor pins the observed
namespace; any failed proof permanently revokes the capability. Linux inability
to observe the namespace fails closed. `SyncDirectoryAuthority` captures this
capability before traversal and transfers it with move ownership.

`sync_system_epoch_identity.{hpp,cpp}` is now the single Linux boot-ID observer
used by process identity and the outbox clock. It uses `O_NOFOLLOW`,
`O_CLOEXEC`, bounded EINTR-aware reads, regular-file proof, explicit close
handling, and exact one-line lowercase UUID framing. Missing and
permission-hidden observations remain typed, but the current clock adapter still
throws before the SQLite owner can durably quarantine unavailable boot identity.

A draft schema that persisted boot UUID and mount ID as permanent root identity
was rejected. Those observations are reboot-ephemeral; without an authorized
rebind ceremony, exact cross-restart equality would turn an ordinary reboot into
permanent database lockout.

## Runtime and audit evidence

Fresh cloudtainer gates recorded under `REVISION_EVIDENCE/rev0881/validation/`
include:

- GCC 14.2 Debug complete all-target build, final no-work dependency closure,
  and 191/191 registered tests in one invocation;
- 60/60 audit-named registered tests;
- 13/13 focused executables and 5,149/5,149 assertions under GCC Debug;
- the same 13/13 and 5,149/5,149 under Clang 17 Release C++ `-Werror`;
- the same 13/13 and 5,149/5,149 under GCC ASan/UBSan with leak detection,
  halt-on-error, and bundled SQLite C instrumentation;
- 20 iterations across four authority executables: 80/80 runs and
  4,440/4,440 assertions; and
- 16 focused architecture/hygiene audits: 477/477 lexical checks.

The new behavioral matrix covers callback settlement, exact release,
exact-boundary expiry, valid same-claim renewal, malformed payload construction,
writer exclusion from a second SQLite connection, stale/missing no-clock
behavior, clock-only expiry revocation, one-shot guard commit, and TEMP-trigger
rollback. Lexical audits are explicitly not presented as semantic or formal
proof.

## Compatibility

- File-effect SQLite exact schema remains version 2.
- Causal SQLite exact schema remains version 5.
- File-delivery wire protocol is intentionally version 2; version 1 is rejected.
- Existing disposition numeric values remain stable; path blocking is value 9.
- Canonical operation/path identity and the 4096-byte model path limit are
  unchanged.
- The durable root-attestation digest remains v1 and excludes boot UUID, mount
  namespace inode, and mount ID.
- The local JSONL compatibility facade remains intact.

## Deliberate nonclaims and next frontier

Rev0881 does not claim that the returned outbound frame remains current until a
socket accepts its first byte. There is no atomic SQLite-plus-network
transaction, durable frame ownership, transport queue claim, exactly-once remote
effect, or proof that `send()` means delivery. A transport-facing authority must
re-attest immediately before first-byte dispatch, or a later design must persist
a frame/attempt state machine with explicit crash and retry semantics.

It also does not repair legacy effect databases already containing locally
impossible staged paths; durably quarantine unavailable boot identity; provide
restart-stable mount identity or an authorized root-rebind ceremony; protect
against same-UID/privileged process or namespace interference; provide Windows
retained-root/path-capability parity; or make `anonsync_core` consume the newer
causal, TLS, outbox, effect, and retained-root owners.

Update/delete/rename effects, complete retry jitter/dead-letter/wake policy,
payload availability lifecycle, enrollment and key rotation/revocation/recovery,
anti-entropy, causal stability, compaction/tombstone collection/rejoin,
production-scale indexed ownership, anonymity/unlinkability/endpoint hiding,
traffic-analysis resistance, externally trusted signed provenance,
full-project Clang/sanitizer coverage, ThreadSanitizer, Windows runtime, and
formal proof remain open. The O(history) causal and effect owners remain
correctness, repair, and differential oracles rather than production-scale
performance claims.
