# Exact transient-namespace retention cutpoint — rev0976

## Mission boundary

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Bounded storage and user-visible retained history are required for that
mission, but a collector must not delete immutable payloads while a live or
restart-recoverable transfer still names them. Rev0976 strengthens the existing
deletion-free retention observation. It adds no automatic policy, durable
collection plan, collection quarantine, or unlink authority.

## Defect found

Rev0975's payload snapshot digest bound the committed payload inventory plus the
aggregate number and physical bytes of transient payload-store files. It did not
bind either:

- the exact staged-prefix, staged-range, assembly, or atomic-publication
  residue identities; or
- the full reserved completion extent of staged prefixes.

Two different restart obligations could therefore have the same payload
snapshot digest when their transient entry count and currently written bytes
matched. For example, externally renaming one valid staged-prefix basename to a
different target digest with the same declared total while preserving its short
physical prefix kept the old aggregate count, physical bytes, and reservation.
Separately, changing only the declared completion extent was invisible because
reserved bytes were absent. The rev0975 exact deletion-free mark inherited both
aliases through `payload_snapshot_digest`.

This was not yet an active data-loss path because the planner remains
non-authoritative and deletion-free. It was, however, an unsafe cutpoint to
persist or later consume as collection authority.

## Canonical transient namespace witness

A complete rooted payload-store scan now canonically orders all four transient
classes and hashes one domain-separated stream:

```text
anonsync:sync-replica-file-payload-store-transient-namespace:v2

"staged_prefix", count
  repeated basename, target_digest, declared_total,
           committed_prefix, actual_size, canonical_POSIX_observation
"staged_range", count
  repeated basename, target_digest, offset, chunk_digest, actual_size,
           canonical_POSIX_observation
"assembly_residue", count
  repeated basename, actual_size, canonical_POSIX_observation
"publication_residue", count
  repeated basename, actual_size, canonical_POSIX_observation

aggregate_transient_count
aggregate_physical_transient_bytes
aggregate_reserved_transient_bytes
```

All strings and integers use the payload store's existing length-framed and
big-endian digest encoding. Each inode observation uses the shared fixed-width
eleven-field POSIX regular-file snapshot codec under the exactly-one-link
policy. This makes same-name, same-size inode replacement invalidate the
cutpoint without claiming complete-byte truth for opaque transient content.
Staged-prefix and range observations were already sorted for mutation ownership. Rev0976 also sorts assembly and publication
residues, then reuses one named comparator per class for both sorting and the
canonical-order assertion. This adjacent refactor prevents the scanner and
witness from silently acquiring different ordering rules.

The witness binds restart-obligation identity, inode observation, and
capacity, not opaque transient-file byte truth. Committed payload bytes retain their complete SHA-256
verification path. Transient corruption and every root outside this store need
separate protocol rules before collection can exist.

## Payload snapshot v4

The complete payload snapshot domain advances to:

```text
anonsync:sync-replica-file-payload-store-snapshot:v4
```

In addition to its previous folder, rooted identity, limit, committed inventory,
and aggregate fields, it now binds:

- `transient_reserved_bytes`; and
- `transient_namespace_digest`.

The move-only snapshot exposes both values to the exact retention owner. A cold
restart over the same namespace reproduces the same witness; changing a staged
obligation's target or reservation changes both the transient witness and the
snapshot digest.

## Exact deletion-free mark v2

The retention mark domain advances to:

```text
anonsync:sync-replica-retention-plan-deletion-free-mark:v2
```

The v2 stream binds the prior folder, operation, inactive-evidence, pin,
visible-state, payload-snapshot, and complete candidate-set witnesses, and also
binds:

- the exact transient namespace digest;
- transient entry count;
- physical transient bytes; and
- reserved transient bytes.

The canonical retention-plan JSON exposes those four values and reports:

```json
{
  "payload_store_transient_namespace_bound": true,
  "durable_receiver_restart_obligations_bound": true,
  "active_pass_transient_roots_bound": false,
  "opened_sender_transient_roots_bound": false,
  "mutation_batch_transient_roots_bound": false,
  "external_transient_root_model_complete": false,
  "reclaimable_authority": false,
  "writer_fenced_collection": false,
  "durable_mark_persisted": false
}
```

Live and terminal service status advance to
`anonsync.peer-service.status.v21`. The owner-only retention-plan acceptance
response advances to `anonsync.local-retention-plan.response.v3`, following the
existing rule that an operator command's schema advances when the exact result
contract it initiates changes, even though the request frame itself remains
compatible.

## Executable proof

The payload-store regression constructs one short staged prefix and captures
its capacity plus transient and snapshot digests. It first renames the exact
file to another valid staged-prefix identity with a different target digest but
the same physical bytes, entry count, committed extent, and declared total. It
then renames it again to a valid identity with the same committed bytes but a
larger declared completion extent. The test independently proves:

- same-count, same-physical-byte, same-reservation obligations no longer alias;
- changing only the reserved completion frontier changes both witnesses;
- the complete payload snapshot digest changes at each exact transition; and
- the final witness is stable across owner restart.

The folder-owner regression inserts one valid four-byte atomic-publication
residue before retention inspection. Complete and paginated plans share one
mark, then the test renames that residue to another valid same-size basename and
requires a stale source cutpoint to fail at `PayloadSnapshot` before any plan
publishes. The independent test-side v2 digest builder includes the exact new
fields.

Stable and byte-bounded local status tests require the canonical witness,
aggregates, and explicit external-root nonclaim. The real configured-service
oracle accepts only a canonical v21 plan projection and verifies that reserved
bytes cannot fall below physical transient bytes.

## Authority still missing

Rev0976 models the complete transient namespace owned by the durable payload
store at one exact rooted scan. It does **not** yet model every lifetime that can
make a committed payload temporarily necessary. In particular, the following
remain incomplete collection roots:

- authenticated senders with opened payload descriptors;
- active reconciliation, folder-convergence, and publication passes;
- receiver or mutation objects whose obligations are held only in memory;
- policy grace, restore guarantees, quota pressure, and ENOSPC behavior;
- a crash-durable identity-bound mark intent;
- collection quarantine and restart repair; and
- final writer-fenced reobservation immediately before unlink.

The status field `external_transient_root_model_complete:false` is therefore
load-bearing. A future collector must not reinterpret the new witness as global
reclaim authority.

## External collector precedent

The next edge is intentionally conservative. Git documents that immediate
pruning can race concurrent writers and uses an age grace period (two weeks by
default) as a mitigation, while also warning that the mitigation is not a
complete concurrency solution. Git's cruft-pack design computes an exact
reachable/kept set before segregating unreachable objects and retains per-object
age evidence. Restic likewise separates reference removal from physical prune,
requires an exclusive lock for deletion, and requires indexes/references to be
updated before old packs are removed. These are not proofs for AnonSync, but
they reinforce the same protocol shape: exact roots, explicit policy/grace, a
writer fence, staged removal, and revalidation before destruction.

Official references:

- <https://git-scm.com/docs/git-gc>
- <https://git-scm.com/docs/gitformat-pack#_cruft_packs>
- <https://restic.readthedocs.io/en/stable/100_references.html#read-and-write-ordering>
- <https://restic.readthedocs.io/en/stable/060_forget.html>

## Cloudtainer authority audit

Several unsealed rev0976 source and build authorities were discovered outside
the active exact parent extraction. They included stale `/mnt/data` worktrees,
a separately mounted `/home/oai/share` authority, and live orphaned Ninja
drivers compiling those paths. Their command lines proved that their objects
were not rooted in the selected source owner. Every such process was stopped,
and the discarded source trees, build trees, launchers, and logs were removed.
No object or validation result from them is release evidence.

Before removal, the divergent sources were compared by path and bytes. One
review tree contained a stronger regression that the active merge had lost: it
separately changes a transient target identity while preserving count, bytes,
and reservation, then changes only the reservation while preserving the target.
That oracle was reviewed and merged into the active source. The final payload
store regression therefore proves both non-aliasing boundaries independently.
The `/home/oai/share` draft was otherwise byte-identical to the selected wrapper;
its build products were still excluded because source equality does not confer
build authority.

All authoritative compilation and runtime evidence is rebuilt from the one
active source path recorded in rev0976 build provenance. The release evidence
also records the exact source projection before and after validation so a
stale, timestamp-compatible object cannot silently become authoritative.

## Next safe edge

The next storage-lifecycle step remains a durable protocol, not `unlink`:

1. inventory sender, pass, receiver, mutation, and publication lifetimes and
   decide which require durable roots versus an exclusive writer fence;
2. define explicit per-share count, byte, age, grace, quota, and ENOSPC policy
   plus the precise restore loss visible to the owner;
3. persist a checksum-framed, store-identity-bound mark intent containing the
   exact v2 mark, policy, and creation cutpoint;
4. move candidates into a separate collection quarantine under the payload
   writer fence;
5. reobserve every persistent, policy, payload-store transient, and external
   transient root after restart; and only then
6. unlink an object whose quarantined inode and complete-byte digest still match
   the durable plan and final revalidation.
