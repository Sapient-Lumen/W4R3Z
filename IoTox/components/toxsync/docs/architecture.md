# toxsync architecture

## Publication model

Toxsync represents a mutable namespace as one small Ed25519-signed HEAD over immutable revision
objects. A HEAD binds the namespace, generation, engine, complete artifact identity and size,
index/root identity and size, optional parent record, and snapshot flag. The application supplies
publisher authorization and rollback/fork policy; transport friendship has no authority meaning.

Two byte-compatible engines remain available:

- `range-v1` uses a deterministic `.txi` target index and receiver-side reuse from one verified
  basis artifact;
- `content-store-v2` uses content-defined SHA-256 chunks, either a flat manifest or a bounded paged
  root/page graph, and can schedule immutable objects across separately authorized sources.

A directory first becomes a deterministic, bounded `treepack` artifact. The publication transaction
builds and commits the immutable content graph, constructs and signs the linked HEAD, optionally
lands retained publication inputs as one atomic revision directory, and mutates the HEAD last. An
exact retry accepts a retained directory only after checking its complete entry set, regular-file
shape, sizes, and SHA-256 identities against that newly derived signed HEAD.

## Range-v1 receiver pipeline

1. Decode and validate the complete index under configured count and size ceilings.
2. Inspect an arbitrary older verified basis artifact.
3. Produce one basis offset or `missing` marker per target block.
4. Coalesce adjacent missing target blocks into ranges.
5. Reconstruct into an unpublished `.toxsync.part` file using one bounded work buffer.
6. Hash while writing and require the complete target SHA-256.
7. Sync according to caller policy and atomically replace the destination.
8. Permit the verified immutable artifact to seed another receiver.

Adaptive planning probes expected offsets first and avoids an exhaustive rolling scan when its
configured reuse threshold remains attainable. Exhaustive rolling indexes only unresolved target
blocks. Aligned-only mode is the minimum-CPU policy for stable-offset formats.

## Content-v2 receiver pipeline

The paged fabric authenticates the root before dependent metadata, loads only a caller-bounded page
and chunk window, treats availability as an untrusted scheduling hint, and publishes every received
object only after exact size and SHA-256 verification. The scheduler is allocation-stable after
construction, bounded by explicit source/pending/in-flight limits, uses rarest-first selection and
goodput/RTT hints, retries with bounded backoff, fences late leases, and reconstructs only after the
complete graph is present.

Same-filesystem ingest can publish a verified staging object by hard link; cross-filesystem ingest
uses a reusable bounded copy buffer and verifies during the copy. Existing immutable names are
reused only after revalidation. Pin records protect accepted graphs, and conservative mark/sweep may
retain false positives but fails closed rather than deleting through missing or corrupt pinned
metadata.

## Activation and recovery

Tree activation verifies the signed HEAD and complete artifact before unpacking into a private
staging directory. It writes a checksum-protected, identity-bound activation receipt, atomically
lands the immutable revision directory, and switches a relative `current` symlink. A retry resumes
only the exact receipt-bound revision. It never overlays an unrelated directory.

Publication and activation have distinct mutable commit points. Receiving or storing bytes does not
activate them. The embedding application must separately authorize and serialize activation.

## Memory and backend model

Artifact payloads are streamed. Range-v1 retains index and plan state proportional to block count;
paged content-v2 retains only configured metadata windows and fixed scheduler capacity. Treepack
uses caller-bounded external sort runs and a bounded merge fan-in. Workspaces expose resident-byte
accounting so an embedding can admit them before network effects.

`ArtifactSha256` uses OpenSSL EVP when selected and available, otherwise the project-owned C++
SHA-256. Ed25519 is intentionally unavailable in the dependency-minimum build. Rolling-checksum
initialization selects baseline x86-64 SSE2 or AArch64 NEON when enabled and otherwise uses the
scalar path. All paths preserve identical wire and disk bytes. The packaged binary does not require
host-specific `-march=native` instructions.

## IoTox embedding boundary

IoTox compiles a deliberate component subset directly into `iotox_core`: hashing, range index,
planning/apply, treepack, content store/paged fabric, multisource scheduling, and range sources.
IoTox deliberately owns the production signed HEAD, authority-ledger v3 policy, durable attempt and
FileId records, connection epochs, store quotas, activation truth, retention witnesses, transport
frames, and route scheduling. The standalone toxsync HEAD keys, wire records, pin journal,
publication convenience transaction, and CLI remain independent laboratory/reference surfaces; they
are not a second production trust root.
