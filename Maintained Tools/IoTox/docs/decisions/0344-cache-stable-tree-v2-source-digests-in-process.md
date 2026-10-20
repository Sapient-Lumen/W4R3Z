# ADR 0344: Cache stable tree-v2 source digests in process

Status: accepted. Implemented 2026-09-09.

## Context

ADR 0342 deliberately stopped short of a durable source metadata cache. That remains correct:
signed tree-v2 manifests are authority over content and causality, but they are not a future proof
that a live filesystem path still has the same inode, timestamps, mode, link count, owner, size, and
content.

However, the Agent still paid a high steady-state cost after ADR 0342. A stable writable workspace
could skip CAS refresh and marker-only projection work, but the source scan still re-read and
re-hashed every selected regular file on every safe no-op reconcile. That is the next measured
bottleneck for larger ordinary directories.

## Decision

Add an in-process `TreeV2SourceDigestCache` and keep it out of signed policy, wire frames, durable
workspace state, branch records, and manifests.

The cache is intentionally narrow:

- entries are private and can be produced only by `scan_tree_v2_worktree()`;
- compatibility requires the same namespace ID, normalized source path, and projection policy;
- a regular file digest is reused only when path, device, inode, mode, link count, owner, size,
  mtime, and ctime all match the prior verified scan entry;
- any mismatch hashes the file normally and installs a fresh cache entry;
- process restart, missing cache, source-path change, projection-policy change, and namespace
  cleanup all fall back to ordinary hashing;
- if reconciliation performs a whole worktree projection exchange, the pre-exchange cache is
  cleared because the visible files may now be fresh copies with new inode identities.

The scanner and reconciler now return content-free counters for inspected source entries plus hashed
and reused source file digests. The Agent keeps one bounded per-namespace cache for local tree-v2
source reconciliation, prunes caches on automation reload, and reports `source-inspected=`,
`source-hashed=`, and `source-reused=` from `sync-publish`.

## Consequences

Repeated no-op or mostly unchanged writable reconciles can avoid reading unchanged file contents
again. This reduces local disk read pressure and CPU hashing cost without changing synchronization
authority: signed branches, immutable object identity, workspace transactions, explicit repair, and
periodic full tree walking remain in force.

This is not a durable trust root. It does not survive Agent restart, does not certify dishonest
storage, does not skip directory traversal, and does not implement path-level incremental
projection. A storage layer that can lie coherently about inode/timestamp/change metadata remains
outside the supported claim and belongs to the dishonest-storage frontier.

## Evidence

The owned unit/integration registry now covers:

- first scan hashes selected regular files and fills the private cache;
- unchanged scan with compatible cache reuses every stable digest;
- one changed file invalidates only that file while reusing the stable neighbor;
- reconcile clears stale pre-exchange cache state and later reuses a stable no-exchange scan cache;
- unchanged stable reconcile still does not repair a deliberately removed CAS object by accident.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
