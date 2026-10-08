# Exact same-owner live payload-capability cutpoint — rev0977

## Mission boundary

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Bounded retained history is part of that product, but storage cannot be
collected safely while a live capability can still reopen or consume an
otherwise unreferenced immutable payload. Rev0977 strengthens the existing
**deletion-free** retention explanation. It does not add policy, a durable mark,
collection quarantine, or unlink authority.

## Lifetime gap found

Rev0976 bound the complete durable payload namespace, including exact staged and
publication obligations. It still treated process-local payload objects as
external. That was too coarse for the shipping C++ owner:

- `SyncReplicaFilePayloadStoreSnapshot` releases its shared namespace lease when
  construction ends, yet the move-only snapshot can later reopen any payload in
  its frozen inventory;
- `SyncReplicaFilePayloadStoreOpenedPayload` owns a descriptor that can outlive
  both the issuing snapshot and its shared lease;
- `SyncReplicaFilePayloadStoreTargetedAccess` retains rooted authority that can
  later open one requested payload after its short per-operation lease; and
- `SyncReplicaFilePayloadStoreMutationBatch` owns an exclusive writer-fenced
  capability while a mutation protocol is active.

Aggregate object counts are not an exact cutpoint. Replacing one live snapshot
with another, for example, preserves the count while changing the capability
lifetime that a future collector would need to bracket. Likewise, one opened
payload descriptor is narrower than an all-inventory snapshot and must identify
its exact digest and size.

Registration-set identity closes replacements that span either observation, but
it has a classic interval ABA hole: a capability can be created and destroyed
after the opening cutpoint and before the final cutpoint, leaving the exact same
set at both ends. The planner is deletion-free today, so this was not an active
unlink race. It was still unsafe to leave as latent collection semantics.

This was not an active deletion bug because the planner still cannot delete.
It was a missing root model that had to be resolved before a dry-run mark could
be promoted into durable collection intent.

## Bounded same-owner registry

Each retained `SyncReplicaFilePayloadStore` owner now creates one private shared
`PayloadStoreLiveCapabilityRegistry`. It is process-local, filesystem-cold, and
not serialized. Its maximum record count is:

```text
payload_store_limits.max_entries + 4096
```

The addition is overflow checked. The fixed allowance covers owner-level
snapshots, targeted accessors, and mutation objects while the payload-entry
frontier covers one live opened descriptor per indexed object. Hitting the
frontier rejects construction; the registry never silently drops a root.

Every registration receives one monotonically increasing, non-wrapping
64-bit ID and one exact kind. The owner-incarnation sequence uses a saturating
compare-exchange allocator, so exhaustion remains fail-sticky rather than
wrapping before the exception:

```text
snapshot
opened_payload(content_sha256, size_bytes)
targeted_access
mutation_batch
```

A move-only RAII token is the first member of each capability state. It is
therefore destroyed last: an opened descriptor closes, or the remaining
capability state is released, before its root registration disappears. Missing
or duplicate unregister is fail-stop. Registration-set observation is protected
by one internal mutex, so capability creation, move destruction, and retention
inspection have one exact in-process order.

The same mutex protects a second non-durable 64-bit activity generation. Every
successful registration and unregister advances it. Registration refuses to
create new authority when the next generation cannot be represented; an
unregister at the terminal value makes future cutpoints fail closed. The
sequence never wraps and therefore detects a complete create-and-destroy
interval even when the active set returns to its prior value.

The registry also carries a fresh same-owner incarnation digest. It is an
identity discriminator, not a secret and not authentication authority. The
digest prevents two independently opened C++ store owners over the same durable
folder from appearing interchangeable. Snapshot-origin validation now requires
both the shared verification cache and the shared live-capability registry in
addition to the durable folder, root, marker, attestation, and limits.

## Exact capability-set cutpoint

The canonical set digest is domain separated as:

```text
anonsync:sync-replica-file-payload-store-live-capability-set:v1
```

It binds the store-owner incarnation and, in registration-ID order, every live
registration ID, kind, digest, and size. Counts by kind are appended as
cross-checks. Distinct opened-payload roots are then sorted and deduplicated by
`(content_sha256, size_bytes)`, with overflow-checked exact count and byte totals.

The activity generation is a bracket witness, not root identity. It participates
in whole-cutpoint equality but is deliberately excluded from the canonical set
digest, deletion-free mark, local response, and service status. A quiescent set
therefore returns to the same page-invariant root identity after harmless
activity, while one in-progress plan still rejects any activity across its
opening/final interval.

The retention planner necessarily creates one complete payload snapshot of its
own. That exact snapshot registration is excluded from the live set. Exclusion
is permitted only when the supplied snapshot proves exact origin and names one
currently live `snapshot` registration in the same registry. A foreign owner
cannot lend a snapshot and subtract an unrelated capability.

The resulting cutpoint is intentionally conservative:

- a live snapshot or targeted accessor may later reopen payloads, so every
  physical payload visible at the retention cutpoint is treated as rooted;
- a mutation batch is represented by the same all-current flag, although its
  exclusive payload writer lease ordinarily prevents it from coexisting with a
  complete retention snapshot; and
- an opened payload roots only its exact digest and size.

A snapshot's frozen inventory may be narrower than the current physical
namespace. Rooting all current payloads is an over-approximation, not an
under-approximation, and is appropriate for a non-authoritative dry run.

## Retention-plan bracketing and mark v3

After the complete payload snapshot has been obtained and before the physical
projection begins, the folder owner captures the exact live-capability set.
After projection it captures the set again while the planner snapshot remains
live. Whole-cutpoint equality includes the activity generation, so set drift,
same-count replacement, and complete create-and-destroy interval ABA all throw
the typed restartable source-change stage:

```text
retention_live_capability_set
```

The exact deletion-free mark advances to:

```text
anonsync:sync-replica-retention-plan-deletion-free-mark:v3
```

In addition to rev0976's durable, causal, payload-snapshot, transient-namespace,
and complete-candidate witnesses, mark v3 binds:

- store-owner incarnation digest;
- exact capability-set digest;
- snapshot, opened-payload, targeted-access, and mutation-batch counts;
- distinct opened-payload root count and bytes;
- physical payload count and bytes rooted by the live set; and
- otherwise-unreferenced physical count and bytes rooted by the live set.

Each physical entry separately reports
`same_store_owner_live_capability`. This bit overlaps the causal disposition; a
payload can remain `unreferenced_by_retained_file_operations` while being
temporarily rooted by an opened descriptor. Rev0977 does not mislabel a process
lifetime as retained causal history.

## Operator contract

Live and terminal service reporting advances to:

```text
anonsync.peer-service.status.v22
```

The owner-only retention-plan response advances to:

```text
anonsync.local-retention-plan.response.v4
```

The canonical plan reports:

```json
{
  "same_store_owner_live_payload_capabilities_bound": true,
  "independent_store_owner_live_payload_capabilities_bound": false,
  "cross_process_live_payload_capabilities_bound": false,
  "already_copied_response_bytes_bound": false,
  "active_pass_transient_roots_bound": false,
  "opened_sender_transient_roots_bound": false,
  "mutation_batch_transient_roots_bound": false,
  "external_transient_root_model_complete": false,
  "reclaimable_authority": false,
  "writer_fenced_collection": false,
  "durable_mark_persisted": false
}
```

`opened_sender_transient_roots_bound:false` remains a claim about the complete
transport-sender lifetime outside the payload-store object graph. The registry
does bind every same-owner `SyncReplicaFilePayloadStoreOpenedPayload` descriptor.
It does not bind an already copied outbound `std::string`, a sender or
continuation owned by another process/store owner, or any future buffer type
that no longer retains the store capability. The narrower true and false claims
are intentionally both visible.

The nested `live_payload_capabilities` object exposes the exact owner and set
digests, per-kind counts, distinct opened roots, all-current capability flag,
and rooted physical/unreferenced totals. Query-time status uses the already
computed bounded plan; it performs no capability-registry traversal by itself.

## Executable proof

The folder-owner regression starts from one current payload and one physical
payload not named by any retained file operation. It proves:

1. the planner's own snapshot is excluded and the empty external set is stable;
2. one independently live same-owner snapshot roots both physical payloads,
   including the unreferenced object;
3. replacing that snapshot with another preserves count one but changes the
   exact set digest and mark because registration identity changed;
4. releasing the snapshot restores the exact baseline set and mark;
5. a capability created and destroyed entirely between two private cutpoint
   observations leaves counts and canonical set digest unchanged but advances
   the activity generation, making the complete cutpoints unequal;
6. an opened descriptor survives destruction of its issuing snapshot and roots
   only the exact unreferenced digest/size while preserving its unreferenced
   causal disposition; and
7. releasing the descriptor restores the baseline again.

The independent test-side mark builder includes every v3 field. The stable local
socket regression requires the exact v4 JSON fields and entry bit. The real
configured-service oracle requires a canonical zero-external-capability plan in
its ordinary serialized operator path. A test-only friend bridge reaches only the private same-owner cutpoint; it adds
no shipping method and does not expose targeted access. Targeted-access and
mutation-batch registration sites, state-member lifetime ordering, record
bounds, exact-origin checks, activity-generation overflow behavior,
before/after bracket, typed source-change stage, schema surfaces, and nonclaims
are independently enforced by the structural authority audit.

## Adjacent audit/refactor

The audit also found an atomic overflow defect in the first owner-incarnation
sequence: `fetch_add` wrapped the counter before reporting exhaustion, allowing a
subsequent construction to restart at zero. A saturating compare-exchange loop
now leaves the counter at its terminal value and rejects every later attempt.

The audit found an accidental broad schema replacement in the unsealed worktree:
historical rev0976 prose and many revision-specific structural checks had been
rewritten to claim rev0977's v22/v4 schemas. Both files were restored from the
sealed rev0976 parent before the rev0977 section was added. Historical release
claims remain immutable and revision-specific.

An attempted direct regression for private targeted access was rejected at
compile time by the intended authority boundary. The shipping API remains
unchanged. A narrowly declared test-only friend now observes the private
cutpoint around a public snapshot lifetime, which proves the interval witness
without exposing targeted access or adding an operator surface.

## Authority still missing

Rev0977 binds only capabilities issued by the **same retained payload-store
owner** in the current process. It does not observe:

- another `SyncReplicaFilePayloadStore` opened over the same durable directory;
- another process, including a peer-service generation surviving independently;
- already copied outbound response bytes or transport continuation state;
- all reconciliation/pass, receiver, publication, or caller-owned buffers;
- future capability types not registered with this exact owner;
- explicit count/byte/age/grace/quota/ENOSPC retention policy;
- crash-durable mark intent;
- collection quarantine and restart repair; or
- final writer-fenced complete-byte and inode revalidation before unlink.

The registry itself is deliberately non-durable. A process restart makes every
old in-memory capability disappear, but it does not prove that another process
or durable operation cannot still require a payload. No v3 mark may be used as
collection authority.

## Next safe edge

The next storage-lifecycle move should define the global exclusion protocol
before any object is removed:

1. inventory outbound copied payloads, TLS continuations, active reconciliation
   passes, receive/assembly objects, and publication/mutation lifetimes;
2. decide which lifetimes require durable roots and which are mechanically
   excluded by one process/device writer fence;
3. define explicit per-share count, byte, age, grace, quota, ENOSPC, and owner-
   visible restore-loss policy;
4. persist a checksum-framed, store-identity-bound mark intent containing the
   exact v3 mark, policy, and creation cutpoint;
5. move candidates to a separate collection quarantine under the proven global
   fence; and
6. after restart-capable root reobservation, rehash and re-prove the exact
   quarantined inode immediately before unlink.
