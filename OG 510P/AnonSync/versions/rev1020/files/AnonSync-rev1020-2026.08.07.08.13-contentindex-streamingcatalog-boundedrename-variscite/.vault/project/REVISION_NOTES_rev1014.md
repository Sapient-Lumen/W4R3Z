# Revision notes — rev1014

## Direct publication borrows the retained compact manifest

Rev1014 removes the final publication-only copy of a completed source manifest.
The shipping cache-cold first-range path no longer calls
`SyncReplicaReconciliationCompactManifest::materialize_or_throw()`. It lends
the exact retained cumulative 40-byte-record sequence to the canonical
response-frame assembler until the frame is complete.

At the 4 TiB / 8,192-chunk product frontier, the direct path now performs one
large allocation—the final roughly 640 KiB generation-9 frame. The owning
baseline performs that allocation plus a 327,680-byte manifest-vector
allocation. The focused allocator oracle proves the exact 327,680-byte
difference and byte-identical frames.

## One validation and serialization path

A private `DeltaManifestView` reads either the ordinary owned size-based
manifest or the borrowed cumulative sequence. The same code now performs
canonical parameter and extent validation, semantic digesting, body sizing,
serialization, final response validation, and request-bound first-range checks.
The protocol remains generation 9 and network bytes do not change.

The assembler rejects double ownership and malformed borrowed sequences. The
borrow owns no authority and must remain alive only through synchronous
`finish_or_throw()`.

## Shipping metadata remains bounded

The direct service result reports borrowed-manifest count, chunk count, and
materialization bytes. When a manifest is borrowed, its process metadata omits
the complete owning vector; the canonical response frame remains complete. The
legacy compatibility API explicitly decodes the frame and preserves its old
owning-response behavior. The TLS service uses the metadata needed for control
flow and hands off the one final frame.

The production regression proves one borrowed manifest, zero materialization
bytes, no owning manifest in direct metadata, exact decode from the frame, and
ordinary receiver application.

## Adjacent audit/refactor

Rev1014 removes five parallel assumptions that a complete manifest must be an
owning vector. Metrics, serialization, validation, digesting, and request
binding now share one internal read-only projection. The source audit prevents
a future drive-by reintroduction of compact-manifest materialization in the
shipping service.

The ordinary direct-assembly overload also stopped allocating a parallel vector
of absent borrowed-manifest optionals. An empty sidecar now means “no borrows,”
while any present sidecar remains exact-cardinality. A focused allocation
differential proves the old explicit-null shape costs exactly one additional
`sizeof(optional)` allocation for a one-payload frame and produces identical
wire bytes. The shipping owner independently re-proves the borrowed count and
chunk count returned by the assembler and rejects any secondary owning
manifest in process metadata.

## Remaining boundary

One active source still retains one 327,680-byte O(chunk count) compact
sequence. This is not constant-memory multi-terabyte synchronization, a global
chunk index, a multi-share RSS proof, a reduction in cold 4 TiB hashing, or a
solution for rename/move, directories, conflicts, placeholders, automatic
eviction, retention collection, ENOSPC, Android, or live Tor/I2P qualification.

Validation: Exact rev1014 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges), a no-work bundled-SQLite re-attestation, independent 53/53 product accounting, and final 249/249 non-product accounting for all 302/302 registered tests. Focused GCC proofs passed 35 compact-manifest, 5,004 protocol, 25 memory-shape, 10 source-frame-memory, 30 checkpoint-codec, and 45 content-defined-chunker checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges; all 53/53 product tests and focused 35 compact, 5,004 protocol, and 10 source-frame checks passed with leak detection and halt-on-error. Source audits passed 32/32 borrowed-manifest, 30/30 fixed-binary, 29/29 compact-cache, 34/34 inherited direct-source, and 646/646 structural-authority checks. The exact rev1013 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Final staged-directory verification passed 32/32 checks; ZIP verification and CRC passed 41/41 checks; clean extraction matched every path, byte, type, and POSIX mode.

Archive: `AnonSync-rev1014-2026.08.06.18.37-borrowedmanifest-directframe-singleallocation-wulfenite.zip`

Codename: `wulfenite`
