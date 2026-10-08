# Deletion-free exact payload-retention plan — rev0974

## Heart of the mission

AnonSync exists to replace Resilio Sync for real folders on a person's own
machines. A usable replacement eventually needs understandable storage policy:
people must be able to see why historical bytes are kept, deliberately protect
important versions, recover space under a stated policy, and know what recovery
is lost. Rev0972 measured aggregate retained-payload reachability and rev0973
added durable causal-version pins. Neither revision could answer the next
operator question:

> For this exact physical payload object, which current, historical, evidence,
> or explicit-policy roots keep it relevant?

Rev0974 answers that question without introducing deletion. The shipping owner
command is:

```text
anonsync_sync retention-plan --socket ABSOLUTE_SOCKET \
    [--after LOWERCASE_SHA256] [--limit 1..1024] \
    [--source-cutpoint \
      v4:exact:OPERATION_SET:EVIDENCE_SET:PIN_SET:PAYLOAD_SNAPSHOT]
```

The result is an exact, digest-ordered, paginated observation of the complete
physical payload namespace. It is diagnostic evidence. It is not a collector,
a quota policy, an age policy, a grace-period decision, or unlink authority.

## One exact source cutpoint

The planner composes the four authorities already used by exact historical
inspection. It does not create a second database, marker namespace, or policy
owner.

The C++ owner performs this order:

1. Validate a page limit from 1 through 1,024, an optional lowercase SHA-256
   physical-object cursor, and an optional current exact-v4 source cutpoint.
2. Take one SQLite replica snapshot.
3. Reject a known-stale operation-set, inactive-evidence-set, or pin-set digest
   before opening the payload store.
4. Restore the immutable causal model from that snapshot.
5. Take one complete rooted payload-store snapshot and require the exact folder
   identity.
6. Take a second SQLite snapshot and reject operation, evidence, or pin drift
   across the payload observation.
7. Reject an expected payload-snapshot mismatch.
8. Project roots, classify every physical object, prove all aggregate
   partitions, and only then publish one page.

The returned source token is the existing exact-v4 token. It binds the active
operation set, inactive retained evidence, the local durable pin set, and the
complete payload snapshot. A caller that copies this token into the next page
cannot silently combine roots from one observation with physical objects from
another. The generic replica state generation is reported for diagnosis but is
not pagination authority; unrelated durable liveness changes need not change
these four source sets.

## Canonical physical order and page reachability

Physical objects are ordered by their lowercase SHA-256 filenames. The optional
cursor must name one object in the current exact payload snapshot. The next page
begins strictly after that digest. A missing, malformed, or stale cursor fails
closed rather than being treated as a lexical insertion point.

Every page reports:

- the exact number of physical objects after the supplied cursor;
- whether the entry-count frontier was reached;
- whether the independent encoded-byte frontier was reached;
- the exact last emitted digest as the next cursor; and
- the same complete-scope disposition and reachability totals.

The owner first applies the 1,024-entry semantic frontier. Before retaining the
completed result in service status, the canonical JSON stream applies a 224 KiB
presentation frontier. That envelope is intentionally below the largest valid
1,024-entry encoding, so the independent byte boundary is real and executable,
not dead defensive code. Binary search retains the largest fitting nonempty
prefix and its exact digest cursor. The one-megabyte local response therefore
retains independent room for service health, lifecycle, and failure evidence.

## Root vocabulary and dispositions

One shared C++ `(content SHA-256, declared size)` key and one shared root-mask
vocabulary feed both historical reachability and retention planning. The four
root flags are:

- `current_visible`: at least one currently visible File operation names the
  exact content;
- `superseded_active`: an active causal predecessor names it;
- `inactive_evidence`: pending or quarantined retained causal evidence names it;
- `explicit_pin`: the local durable pin set names an immutable File operation
  with this content.

Each physical object receives exactly one explanatory disposition:

- `current_or_explicit_pin` when it has a current-visible or explicit-pin root;
- `retained_history_or_evidence` when it has only superseded-active or inactive-
  evidence roots; or
- `unreferenced_by_retained_file_operations` when no retained File
  operation names it at this exact cutpoint.

The priority is deliberate. A shared immutable object can have several roots;
one current or explicit owner-policy root is enough to keep it in the strongest
class. The output retains every individual root boolean so the disposition does
not conceal overlap.

The complete reachability aggregate is still emitted. It includes referenced
content that is missing physically, whereas the plan entries enumerate only
physical objects. The owner validates:

- present plus missing distinct content for every root class;
- the deduplicated retained union;
- current, superseded, and inactive File-operation partitions;
- the exact durable pin count;
- retained-union present objects plus unreferenced objects against the complete
  payload count and bytes; and
- the three plan disposition classes against the same complete payload count
  and bytes.

Any inconsistency is terminal and publishes no plan.

## One operator lane and one stable result

`retention-plan` reuses the existing mutex-linearized historical operator lane.
The local mode-0600 Unix socket admits a strict three-field frame containing the
limit, digest cursor or dash, and source cutpoint or dash. The response is bound
to the connected daemon PID. Requests coalesce only when the complete plan query
is equal; a different pending history, restore, pin, unpin, or plan request is
rejected rather than replacing accepted work. Drain closes admission through the
same action seal.

The peer-service owner, not the socket worker, opens SQLite and the payload
store. Live and terminal reporting advance together to
`anonsync.peer-service.status.v19`. The local acceptance response is
`anonsync.local-retention-plan.response.v1`. One completed bounded plan lives in
the stable `historical_versions.last_retention_plan` domain. The generic
`last_step` retains the action and generation but drops the duplicate page, so
status does not carry two copies of the largest result.

## Adjacent audit and refactor

The first implementation duplicated several concepts that already existed in
exact historical reachability. Rev0974 centralizes the physical-content key,
root bits, root tests, and disposition mapping in one owner vocabulary. It also
reuses the canonical reachability serializer, exact-v4 cutpoint codec, one local
action lane, and one service-status renderer. No second payload inventory or
query-time traversal was introduced.

A focused status audit found that the original 256 KiB plan frontier was
unreachable: the largest valid 1,024-entry plan encoded to 245,443 bytes. The
binary-search truncation path could therefore never execute for owner-produced
input. The plan envelope is now 224 KiB, and the focused regression constructs a
maximum valid page, proves byte truncation, exact prefix order, cursor
reachability, deletion-free flags, and remaining one-megabyte socket headroom.

The real two-service process oracle pins an exact predecessor, requests a plan
from the same retained daemon, and requires that physical object to report the
explicit-pin root and `current_or_explicit_pin` disposition. It also requires
v19 status and the explicit absence of reclaim, quota, grace, and writer-fenced
collection authority.

A cloudtainer hygiene audit also found a second unsealed rev0974 prototype and
an orphaned registry runner operating on it. That branch added count, byte, and
mtime-age policy plus a second retention-plan codec and four additional C++
files. Its process tree was stopped and its source/build tree removed before
release validation. None of its build or test output contributes authority.
The policy branch was not merged: private payload-object mtime is not causal
version chronology, and selecting apparent policy excess before defining
writer-fenced collection, transient transfer roots, user-visible recovery loss,
and crash repair would turn a diagnostic surface into premature policy. The
retained implementation keeps only exact root explanation and also corrects its
public vocabulary: pending or quarantined evidence is not mislabeled as merely
"recoverable history," and an unreferenced classification names its precise
retained-File-operation scope.

## Why unreferenced is not reclaimable

`unreferenced_by_retained_file_operations` means only that no retained
File operation in this bracketed replica observation names the object. A safe collector still
needs roots and policy that do not exist in rev0974, including at least:

- current mutation batches and range-transfer destinations;
- pass-scoped snapshots and opened-payload senders;
- restart-safe in-flight transfer obligations;
- a stated version-retention and grace-window policy;
- per-share byte/count quotas and ENOSPC behavior;
- durable collection intent and crash recovery;
- exclusive writer fencing across mark, quarantine, revalidation, and unlink;
- post-quarantine re-observation of every causal, policy, and transient root;
- directory durability and restart repair at every filesystem transition; and
- a user-visible statement of which restore outcomes are intentionally lost.

For that reason every canonical plan carries:

```json
{
  "reclaimable_authority": false,
  "quota_policy_applied": false,
  "grace_period_applied": false,
  "writer_fenced_collection": false
}
```

No code path in rev0974 renames, quarantines, or unlinks a planned object.
Diagnostic corruption quarantine remains a separate exact-pair evidence
mechanism and is not user version retention.

## External design precedent

The official restic retention documentation separates snapshot-root policy
(`forget`) from physical repository reclamation (`prune`). It describes prune as
an exclusive repository operation, supports dry-run inspection, and recommends
repository checking around destructive maintenance. That separation reinforces
AnonSync's current boundary: decide and explain roots first; only later design a
writer-fenced physical collector with independent recovery proof.

Reference consulted:

- https://restic.readthedocs.io/en/latest/060_forget.html

This is precedent, not borrowed authority. AnonSync's payload namespace, causal
operation model, transfer pins, and crash protocol require their own proof.

## Next safe collection protocol

The next product slice should define a durable retention policy and transient
root model before adding unlink:

1. Record explicit keep policy, grace, quota, and version-loss semantics in one
   owner-controlled durable cutpoint.
2. Add exact in-flight, mutation, sender, and pass-snapshot roots.
3. Produce a durable mark plan bound to all roots and the physical snapshot.
4. Acquire the exact payload writer fence.
5. Re-observe every root and reject any drift.
6. Move one candidate by no-replace rename into a collection quarantine and
   synchronize the directories.
7. Re-observe roots again; restore the object if it became reachable.
8. Unlink only the still-unreachable quarantine object, synchronize, and record
   completion.
9. Make every intermediate state restart-repairable and expose progress and
   irreversible version loss to the owner.
10. Re-run full namespace integrity and policy accounting after a collection
    cycle.

Until those stages exist and survive fault injection, rev0974's plan remains
explanation only.

## Nonclaims

Rev0974 does not add garbage collection, automatic retention, age/count/byte
policy, quota eviction, grace windows, Archive chronology, remote historical
transfer, batch restore, directory restore, selective synchronization, or
in-flight/pass roots. It does not claim that an unreferenced object is safe to
delete. Reconciliation protocol generation 2, direct TCP, Tor, and I2P routing
are unchanged.

Exact rev0974 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 305/305 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed across bounded serial shards with leak detection and halt-on-error. One superseded combined sanitizer shard let the unchanged service lifecycle oracle reach its 30-second runtime cap after four of five cycles; the isolated authoritative rerun passed in 12.79 seconds with no sanitizer diagnostic. Focused sanitizer proof passed the 320-check SQLite-owner suite in 3.33 seconds at 556,136 KiB peak RSS, the 441-check folder-owner suite in 21.71 seconds at 1,412,208 KiB peak RSS, and the 155-check local-control suite in 0.63 seconds at 98,620 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0973 parent SHA-256 matched 62d265f026db82c946fe86df8700c6019826afc86604242716e9af564b84f7cd and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,336,658 bytes with SHA-256 1eb35263f32e14bb15be047a6bcadc88eb7aaac6bd5bcb9fd0898bf593b3377b. Validation excluded the rejected duplicate age-based planner prototype and every interrupted or timing-only non-authoritative run.
