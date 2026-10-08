# Revision notes — rev0973

## Product move

Rev0973 adds durable owner-controlled retention pins for causal file versions.
The private retained service accepts:

```text
anonsync_sync version-pin --socket ABSOLUTE_SOCKET \
    --operation LOWERCASE_SHA256
anonsync_sync version-unpin --socket ABSOLUTE_SOCKET \
    --operation LOWERCASE_SHA256
```

A pin names one exact retained immutable File operation. It survives restart,
can remain meaningful while payload bytes are absent, and is projected into
both metadata-only and exact history pages. It does not restore a path, copy
bytes, propagate to peers, or authorize collection.

## Durable authority

- SQLite schema advances from v5 to v6.
- `sync_replica_history_pins` is owned by the existing replica database.
- The canonical sorted pin set, count, and folder-bound digest are part of every
  replica cutpoint and snapshot re-attestation.
- Exact repeated pin/unpin requests are durable no-ops; only a real set
  transition advances state generation.
- The exact v5 migration seeds an empty pin set while preserving prior evidence,
  outbox, clock, limits, and policy authority.
- Pinning rejects missing evidence and tombstones. Unpinning an absent canonical
  ID is deliberately idempotent.

## History and status

- Source cutpoints advance to v4 exact and v4 metadata and bind the pin-set
  digest.
- Compatible v3/v1 exact and v2 metadata tokens are accepted only while the
  current pin set is empty; they never wildcard a nonempty policy set.
- Every inventory reports the pin-set digest/count and per-entry `pinned` state.
- Exact reachability adds an overlapping `explicit_pins` class, including
  present and missing content.
- Service status advances to `anonsync.peer-service.status.v18`.
- Owner-only pin/unpin acceptance responses use dedicated v1 schemas.
- Counters distinguish inspections, restores, pins, unpins, and failures.

## Audit/refactor corrections

An unsealed payload-side pin implementation was rejected because it created a
second policy truth beside the SQLite causal owner. The final implementation
keeps the payload store byte-only and routes pin/unpin through the existing
historical action lane.

The first real-process run found that peer-service validation accidentally sent
Pin and Unpin through the restore validator, terminating the daemon after a
valid request. Restore validation is now action-specific, and the configured
service regression proves pin, reinspection, unpin, reinspection, exact status,
and continued same-process operation.

The audit also closed a legacy-token consistency hole: a pre-pin token can no
longer act as a wildcard when any pin exists. Local-to-peer historical action
mapping is centralized in one exhaustive switch.


The complete registry caught a SQLite-owner source audit still hard-coded to the
old schema-v5 destination. Repairing that oracle exposed missing direct runtime
coverage for the exact v5-to-v6 migration. The new regression proves complete
prior authority preservation, one canonical empty pin root, post-migration pin
and restart behavior, and transaction rollback when the v5 cutpoint is wrong.

## Compatibility and nonclaims

Reconciliation protocol generation 2 is unchanged. Direct TCP, Tor, and I2P
continue to route into the same authenticated synchronization semantics. Pin
policy is local and is not transmitted.

Rev0973 does not add garbage collection. It also does not add automatic
retention, age/count/byte policy, quota eviction, Archive chronology, batch
restore, directory restore, selective sync, or deliberate remote-history
semantics after collection.
`reclaimable_authority:false` remains explicit.

See `HISTORICAL_VERSION_RETENTION_PIN_AUTHORITY_AUDIT_rev0973.md`.

## Validation

Exact rev0973 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 433 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 140 local-control, 87/87 observer, and 6/6 observer-race checks. The upgraded SQLite-owner source audit passed 43/43 checks, and the complete structural authority audit passed 292/292 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 320-check SQLite-owner suite in 2.89 seconds at 556,172 KiB peak RSS, the 433-check folder-owner suite in 26.11 seconds at 1,432,996 KiB peak RSS, and the 140-check local-control suite in 0.56 seconds at 94,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0972 parent SHA-256 matched 5d8c791ded176f4b76e685103bf75b7697d5e466f5f8236ef7bf822f03523ded and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,229,745 bytes with SHA-256 576051d058ff39a23b32d3aef2487e296a18a398a67e4e28bc5a331e4e8b043e. The registry-driven audit correction also added direct exact v5-to-v6 migration, restart, and malformed-cutpoint rollback proof.
