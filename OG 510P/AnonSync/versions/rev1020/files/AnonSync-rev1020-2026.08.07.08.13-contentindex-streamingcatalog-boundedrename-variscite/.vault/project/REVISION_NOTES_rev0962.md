# Revision notes — rev0962

## Mission move

Rev0962 completes the first bounded lifecycle for corrupt-payload diagnostic
capacity. After ordinary authenticated recovery clears the active integrity
alarm, the owner may reclaim one exact retained image without editing the
private store:

```text
anonsync_sync quarantine-release --socket ABSOLUTE_SOCKET \
    --expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256
```

The command deletes only the canonical expected/observed quarantine selected by
the owner. It is explicit evidence release, not automatic retention, restore,
reachability, versioning, eviction, or garbage collection.

## C++ implementation

- Added `SyncReplicaFilePayloadStoreQuarantineAction::{Preserve,Release}` and
  carried the action through results, service state, status, local requests, and
  tests.
- Added `SyncReplicaFilePayloadStore::release_quarantined_payload_or_throw()`.
- Rejects noncanonical or equal digest pairs and read-only inspection owners.
- Returns typed `active_fault_present` without mutation while any process-local
  integrity fault remains active.
- Re-proves root and current reader-fenced identity, acquires the exact exclusive
  mutation lease, and completely validates the bounded quarantine namespace.
- Opens and re-proves the exact private regular file beneath the retained root,
  unlinks only the scanned inode, synchronizes the directory, proves absence,
  and re-proves lease plus both root authorities at the terminal cutpoint.
- Returns typed `released` or `exact_quarantine_absent` outcomes.
- Deliberately does not hash explicit diagnostic evidence solely to delete it;
  the claim is exact rooted inode removal, not byte authenticity.
- Leaves authoritative payload verification generations and durable checkpoints
  intact after release because quarantine files are outside payload inventory.

## Adjacent performance/correctness refactor

- Replaced rev0961's whole-generation invalidation after successful preserve.
- Unrelated exact process-local payload proofs now survive removal of the corrupt
  authoritative digest.
- The owner still forces durable checkpoint refresh, clears stale publication-
  capacity observation, resets scrub scheduling, and discards active scrub
  continuation when it targets the removed digest.
- Complete namespace enumeration remains mandatory, so a stale cache entry for
  the removed digest cannot create inventory authority.
- The focused regression proves the next complete scan after preserve and after
  release hashes zero unrelated payload bytes.

## Local control, service, and status

- Added exact request `quarantine-release EXPECTED64 OBSERVED64\n` and response
  schema `anonsync.local-quarantine-release.response.v1`.
- Preserve and release share the existing mutex-linearized quarantine slot,
  generation, condition variable, combined action snapshot, and shutdown seal.
- The operation kind is part of request identity; a pending release and preserve
  cannot coalesce accidentally.
- Added shipping CLI parsing, strict argument validation, PID-bound response
  validation, mode/owner/private-parent checks, and post-drain rejection.
- Service dispatches the typed action through one owner step and counts images
  released separately from images preserved.
- Release does not alter integrity recovery scheduling or clear/construct fault
  evidence.
- Status advances to `anonsync.peer-service.status.v9` and canonical live and
  terminal JSON report the exact action and release counter.

## Tests and audit

- Payload-store suite adds active-fault release refusal, unrelated byte-proof
  retention after preserve, exact rooted release, post-release proof retention,
  typed exact absence, and read-only rejection.
- Local-socket suite adds exact release framing, shared-generation ordering,
  operation-aware pending exclusion, post-drain rejection, permission failures,
  missing socket, malformed response, and identical-pair rejection.
- The configured-service process oracle performs preserve, authenticated
  re-admission, current-byte recheck, exact release, same-inode authoritative
  payload reproof, status/counter verification, and clean same-PID drain.
- The structural audit binds the exact release path, no-hash deletion boundary,
  narrow acceleration refresh, action linearization, status v9, process oracle,
  documentation, and release policy.
- See `EXACT_QUARANTINE_RELEASE_AND_PROOF_REUSE_AUDIT_rev0962.md`.

## Validation

- Fresh GCC 14.2 debug graph: **527/527 build edges**, followed by exact-source no-work re-attestation.
- Complete GCC registry: **258/258 tests** in bounded serial shards.
- Independent GCC product lane: **39/39 tests**.
- Focused GCC checks: **84** resumable SHA-256, **19** scrub-state, **26** verification-index, **562** payload-store, **30/30** rooted POSIX resolution, **92** network-model checks with **41** generated operations, **296** SQLite-owner, **360** folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, and **92** local-control checks.
- Fresh Clang 17 ASan/UBSan product graph: **238/238 build edges**.
- Clang ASan/UBSan product set: **39/39 tests** in bounded immutable shards with leak detection; the focused payload-store and local-control executables also passed **562** and **92** checks without sanitizer diagnostics.
- Structural payload-store authority audit: **186/186 checks** on the final source and documentation.
- Exact rev0961 parent archive SHA-256 and wrapper-aware release verification are bound in `REVISION_EVIDENCE/rev0962/validation/PARENT_RELEASE_VERIFICATION.json`.
- Source-patch reconstruction, active projection, manifest, directory/ZIP verification, CRC, and clean-extraction path/byte/type/mode equality are release-sealing preconditions recorded in `RELEASE_GATE.json` and `REVISION_EVIDENCE/rev0962/`.

## Nonclaims

- No automatic release, retention age, archive browser, restore, reachability
  pin, quota allocator, or garbage collector exists.
- Release is irreversible within AnonSync's current feature set.
- Local action requests and generations are not durable across daemon exit.
- Same-UID hostile code, portable Unix-socket semantics, network-filesystem
  locking, and universal power-loss behavior are not claimed.
- Rename identity, empty directories, portable metadata, conflict UX, selective
  sync, changed-block transfer, many-share supervision, live public Tor/I2P
  privacy qualification, and a measured first Resilio uninstall workflow remain
  incomplete.
