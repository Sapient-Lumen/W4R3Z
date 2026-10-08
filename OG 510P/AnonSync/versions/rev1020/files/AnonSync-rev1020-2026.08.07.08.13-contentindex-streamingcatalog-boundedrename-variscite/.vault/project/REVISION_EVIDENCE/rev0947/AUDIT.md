# Rev0947 implementation and cube audit

## Decision

Retain the authenticated epoch-journal implementation and discard the lighter
cursor-only prototype as the shipping choice. A cursor alone solves repeated
payload work in one process, but it cannot safely infer deletion across restart
because it does not preserve which paths were actually adjudicated. The selected
owner records an ordered, bounded, domain-separated seen-path cutpoint and
requires a complete rehash before absence authority.

## Shipping changes

Ten active files changed:

- `src/sync_replica_folder_observer.{hpp,cpp}` add component-wise traversal order
  and cooperative resumable segments;
- `src/sync_replica_folder_scan_owner.{hpp,cpp}` add schema-v3 epoch state,
  migrations, batched journal publication, completion proof, deletion fences,
  and diagnostics;
- `src/anonsync_folder.cpp` and `src/anonsync_sync.cpp` publish the new status;
- observer and owner tests add ordering, restart, tamper, batching, mutation, and
  restoration-race regressions;
- `tools/test_anonsync_folder_cli.py` proves continuation across real processes;
- `tools/audit_sync_file_payload_store.py` now binds the source-order contract to
  resumable traversal plus one segment publication instead of the obsolete
  assignment-before-callback shape.

The exact patch from rev0946 is retained as
`SOURCE_DIFF_rev0946_to_rev0947.patch`.

## Correctness findings

### Fixed: deterministic prefix starvation

The old full pass could repeatedly process the same sorted prefix whenever its
aggregate byte frontier was smaller than the stable prefix. The durable cursor
makes each successful segment advance in the observer's real component preorder.

### Fixed: flat-string cursor mismatch

A raw canonical-path comparison does not reproduce recursive directory order.
The new comparator treats path components and subtree-before-sibling ordering as
load-bearing persisted semantics.

### Fixed: transaction-per-file journal prototype

The prototype would commit one immediate SQLite transaction per observed path.
The final code publishes one complete segment with one prepared INSERT loop and
one progress-head compare-and-swap. Path effects remain independent and
idempotent, so failed journal publication causes safe replay.

### Fixed: exact predecessor restoration after post-visit deletion

A nominally completed epoch could contain a path that had been deleted after it
was visited. The exact old remote predecessor is now fenced while local absence
is unadjudicated. A later complete epoch publishes deletion rather than allowing
immediate restoration.

### Fixed: remote tombstone over an unadjudicated local file

Remote tombstones are skipped while a local regular file is present and outside
current-epoch authority. The periodic scan later reconciles it under ordinary
causal rules.

## State-machine findings

- Path effect before journal commit: safe replay.
- Journal commit before completion proof: resume and re-attest.
- Partial absence mutation before epoch reset: idempotent replay.
- Epoch reset before remote apply: new epoch begins; remote state remains visible.
- Already-seen local mutation: next epoch, not snapshot fiction.
- Unseen cataloged path behind cursor and physically present: epoch restart.
- New uncataloged path behind cursor: next epoch.

No sequence grants deletion authority from an incomplete or unverified journal.

## Watcher findings

The watcher is correctly subordinate. Queue overflow, invalidation, topology
change, and watcher observation-bound exhaustion request rebuild/wake. The peer
service still schedules periodic repair scans and caps long waits. No code path
was found that treats event delivery as proof of a complete namespace view.

## Capacity and performance findings

Semantic fairness does not eliminate root-prefix metadata work. Every segment
still enumerates and classifies skipped names. The next scale owner should be a
crash-consistent metadata/subtree index with the current scanner retained as a
rebuild and rotating-scrub oracle.

The traversal entry limit counts all namespace objects, whereas the catalog and
payload capacities describe synchronized regular-file identities. These are not
the same dimension. A directory-heavy tree can exhaust the former before the
100,000-current-file contract. Configuration and status should eventually name
both explicitly.

A segment of many zero-byte files may stage up to the bounded path-count ceiling
inside one immediate journal transaction. Splitting it safely requires an
identity reproof boundary; arbitrary commit chunking would be a correctness
regression.

## Cube/process findings

The active implementation remains surrounded by a much larger historical cube.
Rev0947 does not destructively prune evidence, but the audit confirms the same
long-term waste pattern as rev0946:

- copied revision evidence dominates active-source growth;
- a nested historical parent archive remains a large single blob;
- the default complete graph builds legacy donor/oracle bodies not linked into
  `anonsync_sync`;
- repeated prose and release views are manually synchronized.

Use the 35-test product lane for ordinary C++ iteration and the 254-test graph as
release/scheduled assurance. Future cube consolidation should preserve one
content-addressed historical checkpoint plus generated current-state views,
rather than copying every prior evidence file into every revision. Do not prune
blindly: the existing verifier, source diff, lineage hash, and restart page make
history auditable.

## Product finding

The most important missing input remains the first named Resilio uninstall
workflow. Without its path count, bytes, largest file, churn, rename pattern,
routes, filesystems, and acceptable catch-up/recovery times, admission ceilings
and performance work remain weakly prioritized. The fair epoch is a necessary
correctness correction, not evidence of huge-tree readiness.

## Validation conclusion

The exact frozen source built under GCC 14.2 and Clang 17. GCC passed all 254
registered tests, including the 35 product tests. The sanitizer product lane
passed 35/35 serial tests with leak detection in 87.99 seconds. Focused observer
and owner executables passed 49 and 225 checks. The updated structural audit
passed 51/51 and retains its explicit nonclaim: lexical source shape is not
runtime, crash, filesystem, or cryptographic proof.
