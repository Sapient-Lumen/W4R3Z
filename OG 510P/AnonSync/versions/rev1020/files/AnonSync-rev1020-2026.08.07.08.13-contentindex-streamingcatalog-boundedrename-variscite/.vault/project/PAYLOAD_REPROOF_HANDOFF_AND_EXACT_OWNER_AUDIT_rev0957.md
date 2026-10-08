# Payload reproof handoff and exact-owner audit — rev0957

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. A storage proof is useful only when it makes ordinary continuous
convergence safer, faster, or easier to operate. Rev0957 removes repeated work
from the shipping integrity-recovery path without creating a second recovery
algorithm or weakening any authority boundary.

## The concrete waste

Rev0956 correctly required two things before a payload-integrity alarm could be
cleared:

1. a complete leased payload-store snapshot proving the current namespace and
   current bytes; and
2. the ordinary folder convergence pass.

Those two calls were composed independently. The first call returned a complete,
immutable `SyncReplicaFilePayloadStoreSnapshot`, but discarded it. The ordinary
convergence pass could then enumerate and verify the same payload namespace
again. On a large store, recovery could therefore pay twice for the same
namespace cutpoint immediately after an operator repaired a payload.

Deleting the first proof would be unsafe. Skipping convergence would be unsafe.
Teaching recovery a private fast path would fork synchronization semantics. The
useful correction is to move the exact completed proof into the existing
convergence implementation.

## One convergence algorithm, two entry points

`SyncReplicaFolderScanOwner` now has two public entry points:

- `run_convergence_pass_or_throw()` for ordinary operation; and
- `run_convergence_pass_with_payload_snapshot_or_throw()` for an immediate
  same-owner handoff after complete payload reproof.

Both delegate to one private `run_convergence_pass_impl_or_throw()`. Catalog
loads, scan-journal rules, rooted observations, path-local payload mutation,
replica effects, terminal catalog/replica cutpoints, and settlement are shared.
The handoff is not a recovery-only synchronization mode. It supplies only the
complete payload inventory that the same implementation would otherwise obtain
lazily.

The snapshot remains move-only. Its methods still enforce exact-thread use,
its issuing integrity epoch, rooted path reproof, and the existing capability
rules. The optimization does not turn snapshot metadata into perpetual trust.

## Why durable identity equality is insufficient

Two independently opened payload-store handles can name the same folder ID,
root path, identity marker, attestation digest, and limits. They nevertheless
own different process-local verification caches and different integrity epochs.
If a snapshot from one handle were accepted by another merely because durable
fields matched, the accepting handle could bypass its own active fail-closed
witness.

`SyncReplicaFilePayloadStore::require_exact_snapshot_origin_or_throw()` therefore
requires all of the following before the folder owner touches catalog, replica,
or rooted shared-folder state:

- the snapshot is active and usable on the current owner thread;
- both retained and candidate root authorities still verify;
- the snapshot's verification-cache object is the exact cache retained by the
  store handle;
- folder ID, root path, root attestation digest, and limits match exactly; and
- the snapshot's issued integrity epoch is still current, through its ordinary
  state validator.

The cache pointer is the process/store-owner identity. The snapshot itself keeps
that cache alive, so a later owner cannot acquire the same address while the
candidate snapshot remains live. The structural comparisons are retained so
future drift fails explicitly instead of silently relying on pointer identity.

## Mechanical no-second-scan oracle

The focused folder-owner regression does not infer reuse from timing. It:

1. performs ordinary convergence and observes one complete payload snapshot;
2. takes a complete snapshot for handoff;
3. holds a live exclusive payload mutation lease;
4. proves a direct second snapshot fails with `lease is busy`; and
5. runs handoff convergence successfully while that exclusion remains live.

Success under the exclusion is a hard oracle: convergence cannot have taken a
second shared snapshot. The report must show one handoff, zero new complete
snapshot observations, zero mutation batches, and zero mutation full scans.
The same test opens a second store owner over the identical durable root and
proves its snapshot is rejected before catalog or replica state changes.

Linux `flock(2)` documents that locks associated with separate open-file
descriptions may conflict even inside one process. That behavior makes the
exclusive-lease test materially stronger than a counter-only assertion:
<https://man7.org/linux/man-pages/man2/flock.2.html>.

## Adjacent cutpoint-freshness audit: append-only does not mean current

The first handoff implementation retained the supplied complete inventory for
remote planning unless local work had inserted a new payload. That condition was
too narrow. A complete snapshot is an exact historical cutpoint, not a promise
that the append-only namespace cannot gain later entries.

The concrete interleaving is:

1. take an exact empty payload snapshot from the retained owner;
2. append digest D after that snapshot;
3. observe a local file with digest D;
4. enter mutation authority because the frozen snapshot cannot prove D;
5. have the mutation batch find D and return `AlreadyPresent`; and
6. plan an independently visible remote file whose payload is also D.

The mutation batch has proved that the old cutpoint is incomplete for current
presence even though it inserted nothing. Retaining it makes remote planning
report a false absence and defer a ready path until another pass. That does not
publish wrong bytes, but it violates same-pass liveness, inflates recovery time,
and makes the handoff optimization look more complete than it is.

The freshness fence now discards the retained snapshot after any mutation
`put_count`, not only a positive `inserted_count`. Remote planning then opens one
pass-scoped targeted-access authority and proves the exact digest pathname. It
does not perform another complete payload-root scan. The focused regression was
first run against the narrow predicate and failed at the remote-publication
assertion; after the correction it requires one `AlreadyPresent` put, one
targeted probe and selection, zero convergence-owned complete snapshots, zero
remote deferrals, and exact publication of both local and remote files.

This is deliberately conservative. A put attempt is the precise signal that the
frozen snapshot was insufficient for a digest used by the pass. Discarding the
cutpoint may forgo reuse for later remote entries, but targeted access preserves
bounded work and current exact-name proof.

## Diagnostics make hidden work observable

`SyncReplicaFolderConvergencePassReport` now distinguishes:

- snapshots supplied by an exact retaining owner;
- entries represented by those handoffs;
- complete payload-root observations initiated by convergence; and
- entries represented by those observations.

The peer-service recovery counters additionally expose handoff count,
convergence snapshot-observation count, and fallback mutation full-scan count.
The configured-service regression requires successful recovery to report at
least one handoff and zero values for both possible duplicate complete-scan
routes. Live and terminal status use schema
`anonsync.peer-service.status.v4`.

This instrumentation is read-only accounting. It cannot schedule work or grant
payload authority.

## Adjacent evidence audit: persistence belongs to an exact byte image

Rev0956 accumulated `failure_persisted` with logical OR for every repeated
alarm whose *expected* digest matched. That was too broad. If an operator
changed corrupt bytes from observed digest A to observed digest B before
repairing the file, a durable witness for A could remain reported as though it
proved B.

Rev0957 centralizes process-local alarm merging in
`sync_replica_peer_service_integrity_evidence.hpp`:

- a different expected digest starts a new alarm;
- the exact same expected/observed pair may accumulate persistence truth;
- a changed observed digest resets `failure_persisted` to the new exception's
  exact publication result; and
- `observed_content_change_count` records byte-image transitions with saturating
  arithmetic.

A focused unit test covers repeated exact observations, changed corrupt bytes,
return to an earlier byte image, a new expected payload, counter saturation, and
stable non-SSO digest storage across an exact repeat. The status schema advances
because the semantic scope of `failure_persisted` changes and the new transition
counter is public.

The audit also found avoidable allocation churn in that fault loop. The first
implementation accepted both digests by value and copied the whole active
evidence into a temporary before it could classify an exact repetition. The
final merger accepts `std::string_view` and updates the retained evidence
directly. An identical expected/observed pair now leaves both long-string data
pointers unchanged, while changed-byte and changed-target paths first construct
all replacement string state and only then mutate counters or persistence
claims. This is operator-path efficiency, not a relaxation of the lower
allocation-independent payload-store fault witness.

This evidence remains operator presentation state. The lower fixed-width store
witness, complete current-byte scan, and integrity epoch remain the authority
boundaries.

## Adjacent asynchronous-readiness audit

Native I2P ingress publication proceeds on a capability-free worker while the
owner may spend substantial time in complete byte reproof and convergence.
Fault mode previously suppressed ordinary ingress events, so the owner could
clear its integrity alarm using a stale pre-fault ingress snapshot. Rev0957
refreshes worker state while faulted and once more at the recovery cutpoint,
without allowing an ingress event to preempt the fail-closed reproof state
machine. Direct TCP and Tor behavior are unchanged.

## Research-informed comparison

Syncthing's Block Exchange Protocol identifies a durable index point by index ID
and maximum sequence, allowing a peer to send only changes after that point
rather than rebuilding or retransmitting the whole index. Rev0957 is narrower:
it reuses one exact in-process payload cutpoint and does not introduce a remote
sequence protocol. The common lesson is that a named, validated cutpoint should
be composed rather than discarded:
<https://docs.syncthing.net/v1.22.2/specs/bep-v1.html>.

OpenZFS describes scrub as verification of all data and notes that the operation
is I/O intensive while exposing progress. That reinforces separating expensive
proof acquisition from later use and making accidental repetition visible:
<https://openzfs.github.io/openzfs-docs/man/master/8/zpool-scrub.8.html>.

Linux fs-verity offers read-only file authenticity through Merkle-tree-backed
verification and fails reads when verification fails. It is a useful future
option for immutable payload objects on supported Linux filesystems, but it is
not a portable replacement for AnonSync's mutable shared-folder observations,
store identity, restart witnesses, or userspace recovery semantics:
<https://docs.kernel.org/filesystems/fsverity.html>.

## What this proves

Rev0957 is intended to prove that the shipping same-process recovery path can
consume its just-completed payload proof through the ordinary convergence
algorithm, that exact-owner identity is enforced, that both possible duplicate
complete-scan routes are observable, and that durable-evidence truth is never
carried from one observed corrupt byte image to another.

## What this does not prove

- A handoff does not eliminate all recovery I/O. Rooted shared-folder work,
  catalog access, path reproof, and required mutations still occur.
- A changed or incomplete path may still require path-local hashing or mutation.
- The handoff does not survive process restart and is not serialized.
- The new counters are not latency, throughput, or maximum-recovery-time claims.
- Status history remains process-local and is not a durable audit log.
- fs-verity is not integrated.
- Rename identity, directories, version retention, garbage collection,
  selective sync, cross-platform metadata, and the first measured Resilio
  uninstall workload remain open product work.
