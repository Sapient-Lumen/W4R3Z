# Retained payload reachability inside the canonical status frontier — rev0972

## Product problem

AnonSync keeps immutable payload objects after files change. Rev0970 made causal
history browsing payload-cold when availability is not requested, and sealed
rev0971 made every accepted history page publishable through one exact 256 KiB
status frontier. The missing storage-lifecycle measurement was still exact:
which payloads are named by current visible file operations, which are named
only by superseded active history, which are named by retained but inactive
pending or quarantined evidence, which referenced payloads are absent, and
which physical objects are named by no retained file operation at the same
bracketed cutpoint.

A catalog path count cannot answer this. One path can retain many causal values,
several operations can share one immutable object, inactive evidence can later
become relevant, and a matching digest with a different declared size is not
the same content identity. Rev0972 adds exact accounting without adding
collection.

## Exact share-level reachability

Every exact history inspection now returns one share-global
`retained_payload_reachability` object, even when the page itself is path
filtered. It classifies exact `(lowercase SHA-256, declared byte size)`
references into:

- `current_visible`: active file operations that are visible heads;
- `superseded_active`: active file operations no longer visible at their path;
- `inactive_evidence`: pending or quarantined retained file operations; and
- `retained_union`: the deduplicated union of those three classes.

Each class reports file-operation references, distinct exact content, present
exact content and bytes, and missing exact content. Class totals deliberately
overlap when the same immutable content is named by more than one class;
`retained_union` counts it once. The complete payload snapshot is partitioned
between objects named by the retained union and objects named by no retained
file operation. Entry, byte, and operation-reference equations are checked
before publication.

The JSON deliberately says `reclaimable_authority:false` and
`class_totals_overlap:true`. “Unreferenced” means only “not named by a retained
file operation in this exact observation.” It is not permission to unlink.

## Inactive evidence is load-bearing

An active-only mark would misclassify bytes referenced by pending or quarantined
evidence as unreferenced. A child waiting for a predecessor, a dependency-cycle
quarantine, or another retained fork remains durable evidence even though it is
not active.

Rev0972 adds a compile-time borrowed `SyncReplicaModel` evidence visitor. It
walks the operation and evidence-state maps together in canonical operation-ID
order and fails closed if they diverge. The callback is held by const reference,
not copied or type-erased; a non-copyable visitor regression proves that API
boundary. Exact history uses this pass only for inactive evidence after its
existing grouped active projection.

## Evidence-bound exact source cutpoint

Rev0968's exact v1 token bound the active operation set and payload snapshot.
That is insufficient once inactive evidence participates in exact output,
because inactive evidence can change without changing the active operation-set
digest. New exact pages therefore emit:

```text
v3:exact:<operation-set-sha256>:<evidence-set-sha256>:<payload-snapshot-sha256>
```

A supplied v3 token is checked against both replica digests before payload-store
work. The complete payload observation remains bracketed by a second replica
snapshot, and both operation and evidence digests must remain exact across it.
Typed stages distinguish `evidence_set_before_payload_observation` and
`evidence_set_during_payload_observation` from operation-set or payload drift.

Compatible v1 exact tokens remain accepted and successful output upgrades to
v3. Metadata-only v2 tokens remain unchanged. Metadata mode performs no payload
observation, publishes no evidence or payload digest, and returns null
reachability.

## Canonical frontier integration and schema collision

The retained-reachability donor and sealed rev0971 independently evolved the
same service schema name to incompatible v16 shapes. Keeping either name would
let clients silently accept a different object under one version. The merged
contract therefore advances live and terminal status to
`anonsync.peer-service.status.v17`; the owner-only history response is
`anonsync.local-historical-versions.response.v5`.

The first merge also carried two serializers: rev0971's counted canonical
history encoder and an inline reachability renderer in service status. That
would have allowed new fixed fields to escape the 256 KiB page budget or drift
between counting and emission. Rev0972 removes the duplicate. Source evidence
and reachability are emitted by the same canonical stream used for exact byte
counting and final status output. The byte-frontier regression now constructs a
v3 exact inventory with reachability, proves the unbounded combined object is
over budget, and proves the retained prefix is at or below budget while keeping
its exact source cutpoint, reachability object, ordering, cursor, and single
stable-copy rule.

## Cost and authority boundary

The result reuses exact history's already-paid complete payload snapshot. Active
history selection and active reachability share one grouped borrowed traversal;
inactive evidence uses one linear borrowed traversal; the physical payload
inventory is consumed once. Exact references are borrowed `(string_view,
size)` keys while the immutable model owns their bytes. There is no second
payload query, no new control command, no operation-by-payload cross product,
and no cloned digest list beyond the existing complete snapshot inventory.

Metadata mode remains payload-cold and does not construct the reference map,
walk inactive evidence for reachability, acquire a payload lease, enumerate the
payload namespace, or serialize false zero-valued authority.

## Research and design context

Git makes object reclamation reachability-driven and retains a grace period for
unreachable objects because pruning concurrently with writers can corrupt a
repository. Its current `git gc` documentation describes cruft packs and a
default two-week `gc.pruneExpire` grace. Syncthing exposes version retention as
an explicit per-folder, per-device policy with age/count strategies and defaults
to no versioning. Syncthing's block exchange protocol also demonstrates the
value of explicit source identities and monotonic cutpoints for incremental
state. These are design precedents, not behavior AnonSync claims to implement:

- https://git-scm.com/docs/git-gc
- https://docs.syncthing.net/users/versioning.html
- https://docs.syncthing.net/specs/bep-v1.html

## Why this is not collection authority

A safe collector must additionally account for catalog publication, prepared
mutations, range transfers, active pass snapshots, reconciliation obligations,
operator pins, retention windows, quotas, grace periods, writer exclusion, and
restart-safe mark/quarantine/revalidate/unlink state. It must re-prove those
authorities at its mutation cutpoint rather than trust a prior status page.

Rev0972 does not add retention expiry, user pins, quota eviction, garbage
collection, Archive browsing, friendly chronology, conflict-copy UX, batch
restore, directory restore, or remote transfer semantics for deliberately
collected history. Diagnostic corruption quarantine remains separate from user
versions.

## Validation

Exact rev0972 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 421 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 279/279 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 421-check folder-owner suite in 33.17 seconds at 1,376,128 KiB peak RSS and the 132-check local-control suite in 0.57 seconds at 91,608 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0971 parent SHA-256 matched 7212288343824982bfc5c505cf32c39c9ec920d84850103daeafdbd8187f8c33 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,108,596 bytes with SHA-256 e226a95f2c0bf343ad4ff41353415686ea78bde24bcf3ea12c615eaac745d912. Validation also removed multiple orphaned divergent rev0972 build and prototype trees so only the sealed reachability/frontier source and its isolated build directories contributed release authority.
