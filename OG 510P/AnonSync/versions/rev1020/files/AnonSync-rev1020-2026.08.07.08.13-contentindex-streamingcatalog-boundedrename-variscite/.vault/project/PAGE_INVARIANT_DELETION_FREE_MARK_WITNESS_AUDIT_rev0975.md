# Page-invariant deletion-free retention mark witness — rev0975

## Mission boundary

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Storage that grows forever blocks that mission, but deleting immutable
payloads before every durable and transient root is defined would be worse.
Rev0974 therefore stopped at an exact, deletion-free physical retention plan.
Rev0975 strengthens that safe observation boundary. It does **not** add a
collector, retention policy, quota policy, grace period, quarantine-for-GC, or
unlink path.

## Problem found

Rev0974 recomputed the right logical classification, but its implementation had
two avoidable weaknesses.

First, it inserted one node into an ordered `std::map` for each distinct
`(content SHA-256, declared size)` reference and performed logarithmic lookup
for every physical payload. The retained causal model already owned immutable
operation strings for the entire call, so copying keys into separately allocated
tree nodes added allocator traffic and pointer-heavy traversal without adding
authority.

Second, pages carried exact source and partition totals but no constant-size
witness for the complete unreferenced physical set. An operator could compare
source cutpoints across pages, but there was no single digest stating that all
pages were projections of one exact deletion-free candidate set. That omission
would make a future durable mark journal harder to specify and audit.

## Borrowed sorted projection and linear merge

The shipping owner now records one borrowed projection entry for each retained
File-operation root and explicit pin. Each key is a `string_view` into the
restored immutable causal model plus the declared size; the model outlives the
entire plan operation. The owner:

1. bounds and reserves one contiguous vector by `operation_count + pin_count`;
2. appends root-mask observations without per-key tree allocation;
3. sorts by canonical `(digest, size)` order;
4. folds duplicate keys in place by ORing root masks;
5. derives each distinct-content count from the compacted projection; and
6. linearly merges that projection with the complete canonical physical digest
   inventory.

The complexity is `O(R log R + P)` comparisons for `R` raw retained references
and `P` physical payloads, followed by linear accounting. The prior hot path was
`O(R log U + P log U)` over `U` distinct references and required one separately
allocated tree node per unique key. The new vector is still bounded by the
already-bounded durable operation and pin sets. It does not make the entire
planner constant-memory, and it does not change the complete rooted payload
snapshot requirement.

A `(digest, size)` mismatch remains exact evidence, not a fuzzy match. A
reference that sorts before the physical key is counted missing; the physical
object is independently classified unreferenced. No size disagreement can lend
retention authority.

## Complete candidate-set digest

While merging the complete physical namespace, the owner incrementally hashes
every object with disposition
`unreferenced_by_retained_file_operations` in canonical digest order. The
framed stream is:

```text
anonsync:sync-replica-retention-plan-unreferenced-candidates:v1
repeated (content_sha256, size_bytes)
unreferenced_count
unreferenced_bytes
```

The resulting `unreferenced_candidate_set_digest` is independent of page limit,
page cursor, and status-byte truncation because it is computed from the complete
physical snapshot before one page publishes. It is exact only for the reported
source cutpoint. It says nothing about transfer, sender, pass, mutation-batch,
or future policy roots that are not yet modeled.

## Exact deletion-free mark digest

A second domain-separated digest binds that complete candidate set to every
persistent source owner used by the planner:

```text
anonsync:sync-replica-retention-plan-deletion-free-mark:v1
folder_id
operation_set_digest
evidence_set_digest
historical_version_pin_set_digest
visible_state_digest
payload_snapshot_digest
unreferenced_candidate_set_digest
unreferenced_count
unreferenced_bytes
```

The result is `exact_deletion_free_mark_digest`. Every page from one exact
observation carries the same value. Any operation, inactive evidence, explicit
pin, visible projection, physical payload, candidate membership, count, byte
total, or folder change changes the witness.

This is deliberately a **deletion-free mark witness**, not a durable mark plan.
Canonical JSON always reports:

```json
{
  "reclaimable_authority": false,
  "quota_policy_applied": false,
  "grace_period_applied": false,
  "writer_fenced_collection": false,
  "durable_mark_persisted": false
}
```

The local retention response advances to
`anonsync.local-retention-plan.response.v2`; live and terminal service status
advance together to `anonsync.peer-service.status.v20`.

## Executable proof

The focused folder-owner regression independently reconstructs both framed
SHA-256 streams rather than calling production serialization helpers. Its
fixture includes overlapping current and inactive-evidence roots, an explicit
pin whose payload is missing, and an unreferenced physical object. It proves:

- the exact candidate-set digest and exact deletion-free mark digest;
- canonical lowercase SHA-256 encoding;
- identical witnesses on a complete page, a truncated first page, and the exact
  cursor-bound second page;
- unchanged complete root and byte partitions; and
- stale source-cutpoint rejection.

The local status regression requires both digests and the explicit non-durable
flag in stable and byte-bounded JSON. The real configured-service oracle checks
that the v2 response and v20 status expose canonical digests while retaining all
collection nonclaims.

## Contamination and reconstruction audit

The first rev0975 worktree changed outside the reviewed patch. A fresh build
found a partially wired payload-usage prototype in the payload-store owner. The
changed payload-store source did not match the sealed rev0974 ZIP, and no
approved rev0975 change touched that subsystem. That worktree and its build
results were abandoned.

Rev0975 was reconstructed over a fresh extraction whose parent archive SHA-256
and payload-store file hashes matched the sealed release. Only the reviewed
retention projection, witness, schema, tests, audit, and documentation patch was
carried forward. The complete release patch must reconstruct against the exact
sealed parent before publication. This incident is validation evidence about
cloudtainer hygiene, not authority for the rejected prototype.

## Next safe edge

The witness is a useful input to a future collector protocol, but the next step
must not be `unlink`. A safe progression is:

1. define and expose transient roots for in-flight receives, mutation batches,
   active pass snapshots, opened senders, and restart obligations;
2. define explicit per-share age/count/byte policy, grace windows, quota and
   ENOSPC behavior, and the exact restore loss visible to the owner;
3. persist one checksum-framed, identity-bound mark record containing the
   complete root cutpoint, candidate witness, policy, and creation time;
4. under an exclusive writer fence, quarantine selected objects outside payload
   authority;
5. reobserve every durable, policy, and transient root and repair after restart;
   and only then
6. unlink objects whose exact quarantined identity still matches the durable
   plan and revalidation result.

Until that protocol is executable, rev0975 remains an exact and more efficient
dry-run explanation.
