# Process-store live capability and writer-fenced retention audit — rev0978

## Mission boundary

AnonSync exists to replace Resilio Sync with one practical C++ synchronization
product. Storage retention matters because an append-only payload store cannot
run indefinitely, but deletion authority must never outrun the product's proof
of current files, retained versions, in-flight work, and live readers.

Rev0978 is intentionally deletion-free. It strengthens the observation from
which a future count/byte/age retention policy can be marked. It does not create
that policy, persist a collection intent, quarantine a collection candidate, or
unlink a payload.

## Defect 1: independently opened same-process owners were invisible

Rev0977 registered live snapshots, opened payload descriptors, targeted
accessors, and mutation batches in one bounded registry owned by the exact
retained `SyncReplicaFilePayloadStore`. That was exact for one owner but not for
two owners independently opened over the same durable store. A future collector
could observe an idle registry while another owner in the same process retained
an authority capable of reopening or consuming payload bytes.

Rev0978 introduces a bounded process-global broker. Its key is a deterministic
SHA-256 projection of:

- the descriptor-rooted payload-directory attestation;
- the current immutable identity-marker basename; and
- the complete immutable expected identity payload.

All independently opened owners with that exact key share one
`PayloadStoreLiveCapabilityRegistry`. At most 4,096 process-store scopes can be
retained, and each scope has a fixed record frontier equal to the production
payload-entry frontier plus a bounded 4,096-record allowance for non-payload
capabilities. Registration and unregister both advance a fail-closed activity
generation. Exact monotonically allocated registration IDs prevent same-count
replacement from aliasing. Expired weak broker entries are removed before a new
scope is admitted.

When the final owner and all issued capabilities release the scope, its registry
dies. A later owner receives a fresh process-store incarnation digest. The
incarnation mixes process identity, monotonic time, a non-wrapping process
counter, and operating-system entropy. It is not a secret and is not durable;
its job is to prevent a stale same-process deletion-free mark from surviving
scope destruction and recreation.

Sharing the registry does **not** share byte-integrity authority. Direct
snapshot handoff still requires the exact issuing owner's verification cache,
integrity epoch, rooted authority, folder identity, limits, and live
registration. A foreign same-store owner can make its capability visible to the
planner, but cannot lend its snapshot as a complete-byte proof.

### Runtime proof

The focused payload-store regression proves that:

- two independently opened same-process owners report one scope and one
  incarnation;
- a snapshot from either owner appears in the shared cutpoint;
- exact-owner snapshot handoff remains rejected across owners;
- releasing one owner removes only its capabilities;
- releasing the final owner and recreating the scope changes the incarnation;
- bounded registration and non-wrapping behavior remain fail-closed.

## Defect 2: planning did not hold the global writer fence

Rev0977 added a cooperative exact-inode payload-use lease, but the deletion-free
retention planner still obtained an ordinary complete payload snapshot beneath a
short shared store lease. It could compare before/after causal and capability
cutpoints, yet it did not mechanically exclude a new cooperating payload
namespace observation or mutation during the physical projection. Nor did it
test the returned candidate inodes while the exact scanned namespace remained
frozen.

Rev0978 first constructs and sorts the immutable causal, inactive-evidence,
explicit-pin, and visible-state projection from one SQLite snapshot. That work
does not touch the payload namespace and is deliberately completed before the
exclusive lease, limiting synchronization stall. The complete rooted payload
scan then takes the existing store identity's fail-fast exclusive lease and
moves that exact `StoreLease` into the returned snapshot. The folder owner keeps
it alive through:

1. complete physical payload enumeration and metadata/digest proof;
2. merge of the precomputed causal projection with that frozen physical set;
3. page-bounded exact-inode payload-use probes;
4. final SQLite operation/evidence/pin snapshots, which reject causal drift
   since the opening snapshot;
5. final payload root and identity-fence reproof; and
6. final process-store live-capability cutpoint comparison.

The private snapshot is metadata-only while fenced. Ordinary byte selection
would re-enter the shared store lease and is unavailable to the folder owner.
Current-byte recheck and writer-fenced retention modes are mechanically
mutually exclusive, and read-only inspection cannot request the writer fence.
Scrub work is deferred rather than scheduled while this exclusive observation
is retained.

### Exact returned-candidate probe

For every returned page entry classified as
`unreferenced_by_retained_file_operations`, the planner:

- requires the digest and size to name one exact entry in the retained snapshot;
- opens that basename beneath the retained rooted directory authority;
- proves private regular-file type, exact metadata/inode identity, size, root,
  pathname, and global identity lease;
- attempts a nonblocking exclusive lock using
  `anonsync:sync-replica-file-payload-use-flock-lease:v1`; and
- records `exclusive_available_at_cutpoint` or `busy_at_cutpoint`.

The probe descriptor closes before the response is returned. The result proves
only availability at that cutpoint. It is page-bounded and does not classify
unreturned candidates. A future collector must reacquire both the global store
exclusive lease and the candidate inode exclusive lease at its mutation
cutpoint.

The focused regression proves that an API-issued descriptor in the same process
and an inherited descriptor held by another process both produce a busy result;
new cooperating observation and mutation are rejected while the writer-fenced
snapshot is live; the namespace remains unchanged; and all operations become
available after the final reader and writer fence release.

## Digest separation

Rev0978 uses three distinct identities rather than overloading one digest:

- `exact_deletion_free_mark_digest` domain v4 binds the exact same-process scope
  incarnation, current live-capability set, complete causal/payload/transient
  source, and complete candidate-set aggregate. It is process-interval evidence.
- `durable_candidate_witness_digest` domain v1 excludes process-local scope and
  activity. It binds the folder, operation set, inactive evidence, explicit pin
  set, visible state, complete payload snapshot, exact transient namespace and
  capacity, complete candidate-set digest, candidate count, and candidate
  bytes. It can identify a future persisted grace-period observation across a
  restart, but rev0978 does not persist it.
- `writer_fenced_candidate_page_digest` domain v1 binds the exact causal/payload
  source, complete candidate-set digest, cursor, limit, returned entries,
  dispositions, and payload-use probe results. Different pages or changed
  reader activity cannot alias.

The durable witness deliberately does not claim that a candidate remains safe
after the fence releases. Future collection must compare a persisted
mark-plus-policy record with a fresh writer-fenced reobservation.

## Logical page versus presentation prefix

The planner probes every entry in its logical page, which is bounded by the
request limit and never exceeds 1,024 entries. Service status has an independent
byte frontier. It may therefore serialize only a canonical prefix of an already
probed logical page. Rev0978 records the complete logical cardinality in
`writer_fenced_candidate_page_entry_count`; the page digest and the
available/busy partition are computed before any presentation truncation. A
consumer must not infer that omitted status entries were unprobed or absent.

## Adjacent audit and refactor

The audit found an operator-contract ambiguity. Early unsealed JSON described
same-process independently opened owners as bound while retaining the older
field `independent_store_owner_live_payload_capabilities_bound:false`. Without
an explicit scope, an operator could read “independent owner” as contradicting
the new claim or, worse, infer cross-process authority.

The final response therefore states all boundaries separately:

- `same_process_store_live_payload_capabilities_bound:true`;
- `independently_opened_same_process_store_owner_live_payload_capabilities_bound:true`;
- `independent_store_owner_live_payload_capabilities_bound:false` for the legacy
  broader category;
- `cross_process_live_payload_capabilities_bound:false`.

The real configured-service oracle parses every new scope, incarnation,
writer-fence, candidate-page, count, and payload-use field instead of merely
checking the schema string. The local C++ JSON regression now uses the retained
JSON parser, replacing brittle substring-only inspection for the new response
shape.

A parallel unsealed prototype had also introduced a standalone durable-mark
codec, library, and test target. It had no shipping persistence owner, no policy
input, no recovery consumer, and no collection mutation. Retaining that branch
would have created a second format whose existence looked like progress while
leaving the authority gap unchanged. The codec and target were removed; the
next durable format must arrive with the operation that atomically writes,
recovers, compares, and consumes it.

## Primary-source lock model

The implementation and nonclaims were checked against primary operating-system
interfaces:

- Linux `open(2)` documents that each open creates an open file description,
  while `dup` and `fork` can share one; this is why an inherited descriptor can
  keep the inode lease live after the original process closes its copy:
  https://man7.org/linux/man-pages/man2/open.2.html
- Linux `flock(2)` and the kernel VFS documentation describe whole-file advisory
  locks associated with an open file description and mediated at the inode:
  https://www.kernel.org/doc/man-pages/online/pages/man2/flock.2.html
  https://docs.kernel.org/filesystems/api-summary.html
- POSIX `fcntl` states the central limitation: advisory locking constrains only
  cooperating processes:
  https://pubs.opengroup.org/onlinepubs/9699919799/functions/fcntl.html

These sources support the chosen lock order and the child-held-descriptor
regression. They do not justify claims about hostile same-UID writers, copied
buffers, or unqualified network filesystems.

## Explicit nonclaims

Rev0978 does not prove or implement:

- a durable retention mark or policy record;
- count, byte, age, quota, grace, or ENOSPC policy;
- collection quarantine, restart-safe collection staging, reclaim, or unlink;
- roots for bytes copied out of a descriptor into transport or publication
  buffers;
- every active pass, receiver, publication, or mutation lifetime outside the
  modeled payload-store capabilities and durable transient namespace;
- other-process capabilities before they open an exact payload inode;
- protection against noncooperating same-UID or privileged writers;
- lock behavior on unqualified remote/network filesystems;
- all unreturned candidate inodes: exact-inode probes are intentionally page
  bounded, so a future collector must inspect the complete candidate set;
- a short writer-fence interval on very large stores: physical merge and probe
  cost must be measured against the first named uninstall workload.

`writer_fenced_collection` and `reclaimable_authority` remain false. A busy
candidate is evidence of a live reader, not an error. An available candidate is
not reclaimable authority.

## Next safe product edge

Persist one identity-bound mark-plus-policy record keyed by the durable
candidate witness and explicit per-share count/byte/age/grace policy. A later
collection attempt must reacquire the store-global exclusive lease, completely
reobserve causal roots, durable transient obligations, candidate bytes and
metadata, process-store capabilities, and candidate inode leases, then move
eligible candidates to a collection-specific quarantine. After restart, it must
reprove every root, exact inode, and complete byte image before unlink. Diagnostic
corruption quarantine and user-restorable history must remain separate from
collection staging.
