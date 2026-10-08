# Revision notes — rev0957

## Mission

Keep advancing the one retained C++ product spine toward replacing Resilio Sync.
This revision removes avoidable payload-store work from fail-closed recovery and
audits adjacent operator evidence rather than adding a new sync engine or a
recovery-only semantics path.

## Primary implementation

- Added a move-only complete payload-snapshot handoff from the retained
  peer-service recovery owner through `SyncReplicaFolderProcessOwner` into
  `SyncReplicaFolderScanOwner`.
- Kept one convergence implementation. Ordinary operation and recovery handoff
  both delegate to `run_convergence_pass_impl_or_throw()`.
- Added an exact-origin composition fence in
  `SyncReplicaFilePayloadStore`. Matching folder ID, root path, identity marker,
  attestation, and limits are insufficient; the candidate must share the exact
  process-local verification cache and current integrity epoch of the retained
  store owner.
- Validated the supplied snapshot before catalog, replica, or rooted shared-tree
  work.
- Counted supplied handoffs and complete payload-root observations separately,
  including represented entry counts.
- Added peer-service counters for recovery handoffs, convergence-owned snapshot
  observations, and fallback mutation full scans.
- Rendered the new pass and service counters through the shipping folder and
  sync command surfaces.

## Hard regression

The focused folder-owner test holds a live exclusive payload mutation lease
after taking the recovery snapshot. A second complete snapshot is proven to fail
busy, yet handoff convergence succeeds and reports zero new snapshot
observations and zero mutation full scans. A snapshot from an independently
opened owner over the same durable store is rejected, and catalog/replica state
is proved unchanged.

A second regression freezes an empty handoff, appends one digest afterward, and
then makes local admission encounter that digest through mutation authority as
`AlreadyPresent`. The same pass also contains a ready remote path for that
digest. This mechanically distinguishes a historical append-only inventory from
a current one: remote planning must discard the cutpoint after any mutation put,
use targeted exact-digest access, and publish the remote file without another
complete payload-root scan. The pre-correction source failed this regression.

## Adjacent audit/refactor

- Corrected process-local integrity evidence so `failure_persisted` applies only
  to the exact expected/observed digest pair. Changing corrupt bytes resets that
  flag to the new exception's publication result instead of inheriting an older
  durable witness.
- Refactored the evidence merger around `std::string_view` and direct retained
  state. Repeated reports of the exact same digest pair no longer copy the
  expected digest, observed digest, or whole evidence object; transitions still
  construct replacement strings before changing counters or persistence state.
- Added `observed_content_change_count` with saturating arithmetic and a focused
  unit test covering exact repetition, changed images, return to an older image,
  expected-digest replacement, saturation, and retained digest storage across a
  repeated exact alarm.
- Advanced live/terminal status to
  `anonsync.peer-service.status.v4`.
- Refreshed capability-free native-I2P worker state during fault backoff and at
  the recovery cutpoint so readiness cannot be restored from stale pre-fault
  ingress state.
- Audited pass-local payload-cutpoint freshness and corrected a one-pass
  false-absence defect: any mutation put, including `AlreadyPresent`, now
  invalidates a frozen complete inventory before remote planning.
- Expanded the payload-store structural audit and release-package verifier to
  bind the new owner fence, single implementation, cutpoint-freshness fence,
  hard lease oracle, evidence semantics, diagnostics, documentation, and tests.

## Preserved boundaries

- Complete current-byte payload reproof remains mandatory before recovery.
- Ordinary folder convergence remains mandatory before authority is restored.
- Catalog, scan-journal, rooted filesystem, replica-effect, and terminal
  settlement cutpoints are unchanged.
- Snapshot exact-thread, epoch, descriptor, path, and root checks remain active.
- A foreign owner cannot lend verification authority merely because durable
  paths and identity fields match.
- Operator evidence and counters remain non-authoritative.
- Direct TCP, Tor, and I2P remain routes into the same authenticated semantics.

## Nonclaims and remaining product work

This revision does not provide a durable remote index, delta block transfer,
rename identity, directory semantics, conflict UX, version restore, retention or
garbage collection, selective synchronization, cross-platform metadata, live
route-leakage qualification, or the first measured Resilio uninstall workload.
It does not claim every recovery pass is filesystem-cold: changed paths and
fallback mutations may still require bounded work, which is why both duplicate
complete-scan routes are reported separately.

## Validation

Final compiler, registry, sanitizer, structural-audit, lineage, manifest, and
package results are recorded under `REVISION_EVIDENCE/rev0957/` and in
`RELEASE_GATE.json`. Publication is permitted only after those records bind the
exact sealed source and wrapper.
