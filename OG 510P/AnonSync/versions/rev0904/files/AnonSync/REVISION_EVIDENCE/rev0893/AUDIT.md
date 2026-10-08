# rev0893 audit — durable payload ownership and cube refactor

## Heart of the mission

The project succeeds only when exact durable evidence and live owned
capabilities—not a cache, pathname, successful callback, transport return, or
human interpretation—own every irreversible transition. Rev0893 applies that
rule to sender payload availability.

## Material finding

Rev0892's callback retirement was correct but operationally expensive: a caller
had to retain or reconstruct a complete payload working set in memory. That
made the call boundary deterministic while leaving restart availability and
content lifecycle informal. The new durable store closes that seam without
creating a second claim or dispatch implementation.

## Correctness boundary added

The store is content-addressed, descriptor-relative, bounded, create-new, and
restart reconstructible. A versioned identity marker binds the private root to
one folder. Bootstrap can adopt only a fully validated legacy namespace and
performs no mutation before that full scan succeeds. A conflicting marker
rejects folder relabeling.

The canonical service sequence remains:

1. Re-attest channel and folder scope.
2. Present immutable content inventory inside exact SQLite claim selection.
3. Skip unavailable operations without consuming attempt authority.
4. Reopen and rehash the selected object after claim.
5. Exact-release that same claim on pre-dispatch local failure.
6. Re-attest claim and live TLS channel before application bytes.
7. Preserve existing ambiguity and terminal receipt semantics after the write
   frontier.

The store neither settles an outbox nor asserts receiver effect.

## Refactor findings

### Resolver duplication

The first implementation direction risked a second pathname-resolution policy.
The final code centralizes directory and regular-file opens in one internal
flags-parameterized resolver. File-specific no-follow, nonblocking, type, and
identity checks are additive.

### Private temp grammar duplication

The store initially copied the atomic publisher's temporary basename spelling.
That would make a future publisher migration look like hostile corruption.
Classification now belongs to the publisher and grants only exact recognition,
not unlink or payload authority.

### Descriptor transfer leak

`fdopendir()` consumes its descriptor only on success. The scan now retains the
duplicate in `OwnedFd` until the call returns non-null, then transfers ownership
to the directory stream. Repeated exceptional scans cannot leak descriptors at
that frontier.

### Stale lexical authority

Five source audits failed after legitimate template and resolver refactors.
They were rewritten to locate the shared semantic owner rather than an obsolete
wrapper spelling. Lexical audits remain hygiene evidence only; compiler,
runtime, sanitizer, stress, and package evidence are load-bearing.

## Waste still present

The CMake file still contains 84 literal library calls, 92 literal executable
calls, and 126 literal `add_test` calls. The largest production translation
units remain approximately:

- `src/sync_domain.cpp`: 15,167 lines;
- `src/sync_domain_selftests.cpp`: 9,601 lines;
- `src/reporting_selftests.cpp`: 4,992 lines;
- `src/sqlite_replay_ledger.cpp`: 4,529 lines; and
- `src/sync_replica_sqlite_owner.cpp`: 3,906 lines.

This is link-target modularity without equivalent semantic or compile-time
modularity. Narrow authority work still fans into a broad legacy graph. The
correct long-term response is gradual decomposition by durable owner and state
machine, declarative CMake helpers, a fast affected-authority gate, and a
periodic complete legacy gate—not deletion of the oracle tests.

The new store deliberately performs O(total indexed bytes) work for every
snapshot and pre-publication check. That is expensive but honest. It should
remain a migration/repair/differential oracle when a separately indexed owner
is introduced.

## Severe remaining gap

The carefully owned causal SQLite/file/TLS path is still not the shipped
`anonsync_core` executable's sole replica authority. More isolated hardening can
raise assurance counts while leaving product behavior on the older path. The
next milestone must compose one narrow end-to-end executable rather than add
another correctness island.

## Nonclaims

No same-UID or privileged concurrent-writer defense, cross-process capacity
serialization, garbage collection, signed store identity, hardware rollback
witness, production accept pool, complete retry/dead-letter policy, streaming,
chunking, cross-resource transaction, exactly-once network delivery, formal
proof, confidentiality, anonymity, unlinkability, endpoint hiding, or traffic
analysis resistance is claimed.
