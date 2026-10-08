# Borrowed compact-manifest direct-frame audit — rev1014

## Product reason

AnonSync's first supported workflow is Linux/headless synchronization of
multi-terabyte media trees. Delta transfer and selective synchronization are
mandatory, and memory use is an explicit product risk. Rev1013 reduced every
maximum complete source manifest to one contiguous vector of 8,192 fixed
40-byte records, but the shipping cache-cold source path still copied that
entire 327,680-byte sequence into a second vector solely so the first range
could be serialized into its final response frame.

That copy was bounded, but it had no independent semantic purpose. The retained
compact sequence was already canonical, complete, digest-bound, and immutable
through the synchronous publication call. The final generation-9 frame then
serialized the copy and immediately discarded it.

## Retained design

Rev1014 makes the existing cumulative record the shared source for both the
process-retained compact cache and one direct response-frame assembly:

- `SyncReplicaReconciliationCumulativeDeltaChunk` remains exactly 40 bytes: one
  exclusive cumulative end offset plus one fixed 32-byte SHA-256 value;
- `SyncReplicaReconciliationBorrowedDeltaManifest` carries canonical parameters,
  exact total extent, and a `std::span` over those records;
- the borrow owns no bytes and grants no durable, payload, replica, or wire
  authority;
- the caller must keep the exact compact manifest alive and immutable until
  `finish_or_throw()` returns; and
- the generated frame remains the ordinary released generation-9 representation
  with per-chunk sizes and lowercase hexadecimal digests.

The protocol implementation now uses one internal `DeltaManifestView` for
owned size-based manifests and borrowed cumulative manifests. Validation,
semantic digest construction, response-body measurement, serialization,
request-bound validation, and final frame validation all read through that same
view. Borrowed cumulative ends are converted to wire chunk sizes by subtracting
the preceding end; no chunk object or digest string is rebuilt.

## Authority and lifetime boundary

The borrow is deliberately confined to synchronous frame assembly. The service
retains the compact source manifest, builds a vector of non-owning views bounded
by the existing maximum payload count, reserves the one exact final frame,
fills payload ranges directly into frame holes, validates the complete response
against the original request, writes the structural digest, and only then
returns.

The returned process metadata intentionally omits an owning complete manifest
when the frame borrowed it. The returned frame is the complete canonical
response. The compatibility service API decodes that frame and therefore
retains its previous owning-response semantics at the explicit cost of one
receive-side manifest vector. The shipping TLS path uses only metadata needed
for scheduling and the canonical frame; it does not require the duplicate
manifest owner.

The assembler rejects:

- simultaneous owning and borrowed complete manifests;
- borrowed extents that differ from the payload extent;
- noncanonical parameters;
- zero, nonmonotonic, undersized, oversized, over-capacity, or incomplete chunk
  sequences;
- manifest digests that disagree with the exact borrowed records; and
- request/response placement that omits, repeats, or contradicts the first-range
  manifest contract.

These checks do not make a span self-owning. The lifetime rule remains an
ordinary C++ precondition, mechanically satisfied by the retained service owner
and documented on the public direct-assembly API.

## Measured maximum shape

The focused runtime oracle constructs the hard product shape:

- logical payload extent: 4 TiB;
- complete source manifest: 8,192 chunks;
- retained compact sequence: 327,680 bytes;
- first payload range: one byte; and
- final generation-9 response frame: roughly 640 KiB.

With allocation observation armed only for requests of at least 256 KiB:

- borrowed direct publication performs exactly one large allocation, the final
  frame;
- the owning baseline performs exactly two large allocations, the 327,680-byte
  manifest vector and the same final frame;
- requested bytes differ by exactly 327,680; and
- borrowed and owning response frames are byte-for-byte identical.

The maximum-shape test completes at approximately 11 MiB peak RSS in this
cloudtainer. That figure is a focused test-process observation, not the daemon's
whole-process multi-share RSS.

The shipping service regression independently proves that a cache-cold first
range selects one borrowed manifest, reports zero manifest-materialization
bytes, returns metadata with no owning manifest, and emits a frame that decodes
to the exact released complete manifest.

## Adjacent refactor

Before rev1014, manifest validation, digesting, body sizing, body serialization,
and request-bound validation were each hard-coded to the owning protocol
vector. Adding a second ad hoc serializer would have duplicated the most
security-sensitive generation-9 rules. Rev1014 instead centralizes those rules
behind one private read-only view. Ordinary encode/decode paths continue to
supply owned views; only direct assembly may supply borrowed cumulative views.

The public compact `materialize_or_throw()` remains for compatibility tests and
callers that genuinely need ownership. A source audit rejects its return to the
shipping `serve_request_frame_or_throw()` path.

The ordinary four-argument direct assembler no longer constructs a parallel
vector containing one absent optional per payload. It delegates with an empty
sidecar, and one checked helper interprets that empty vector as “no borrowed
manifests”; any nonempty sidecar must still match payload cardinality exactly. A
runtime differential proves the legacy frame remains byte-identical while an
explicit one-element absent sidecar costs exactly one additional allocation of
`sizeof(std::optional<SyncReplicaReconciliationBorrowedDeltaManifest>)`.

The shipping service now constructs ranged metadata once, moves any borrow into
the assembler, calculates the expected borrowed-manifest count and chunk count
before handoff, and compares both values with the completed frame result. It
also rejects any returned process metadata that unexpectedly retains an owning
manifest. These checks keep the optimized publication route from silently
falling back to dual authority.

## Compatibility

This is an in-process ownership change only:

- reconciliation protocol generation remains 9;
- request and response structural-digest domains are unchanged;
- content-defined manifest semantic digests are unchanged;
- per-chunk network fields remain an 8-byte size and framed 64-byte lowercase
  SHA-256 text; and
- the maximum-shape borrowed and owning frames are exact byte equals.

No peer rollout or durable migration is required.

## Nonclaims and next edge

Rev1014 does not make source-manifest memory constant. One active source still
retains one 327,680-byte O(chunk count) compact sequence, and a compatibility
caller may still allocate an owning copy. A cold 4 TiB source still requires
131,072 local 32 MiB hash pulses; restart may replay one 1 GiB checkpoint
interval. Receiver discovery, final publication, SQLite owners, directory
scans, payload indexes, page cache, TLS buffers, allocator behavior, and
concurrent shares remain part of whole-process RSS.

There is still no global, multi-file, or multi-share chunk database. This
revision does not solve rename/move identity, complete directory and empty-
directory semantics, conflict presentation, placeholders, automatic selective-
sync eviction, best-effort retention collection, quota/ENOSPC behavior,
Android lifecycle and scoped storage, or live public Tor/I2P qualification.

The immediate source-manifest publication copy is now gone. Product priority
should therefore return to measured whole-process multi-share behavior and then
to ordinary file semantics—especially identity-preserving rename/move,
directories, conflict handling, and selective-sync user surfaces—unless
measurement shows the one retained 327,680-byte sequence is material at target
concurrency.

## Evidence boundary

The focused source audit is lexical hygiene, not semantic proof. Compile-time
layout assertions, allocation probes, exact frame equality, service runtime
coverage, complete GCC and Clang sanitizer lanes, source reconstruction,
manifest sealing, and package verification remain load-bearing.

Validation: Exact rev1014 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges), a no-work bundled-SQLite re-attestation, independent 53/53 product accounting, and final 249/249 non-product accounting for all 302/302 registered tests. Focused GCC proofs passed 35 compact-manifest, 5,004 protocol, 25 memory-shape, 10 source-frame-memory, 30 checkpoint-codec, and 45 content-defined-chunker checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges; all 53/53 product tests and focused 35 compact, 5,004 protocol, and 10 source-frame checks passed with leak detection and halt-on-error. Source audits passed 32/32 borrowed-manifest, 30/30 fixed-binary, 29/29 compact-cache, 34/34 inherited direct-source, and 646/646 structural-authority checks. The exact rev1013 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Final staged-directory verification passed 32/32 checks; ZIP verification and CRC passed 41/41 checks; clean extraction matched every path, byte, type, and POSIX mode.

Archive: `AnonSync-rev1014-2026.08.06.18.37-borrowedmanifest-directframe-singleallocation-wulfenite.zip`

Codename: `wulfenite`
