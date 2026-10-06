# Removable-media local fallback post-detach recovery evidence is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt, Registry→Diff→Gate, Quarantine→Promote

r505 closed the launch-evidence seam. r506 closes the interruption seam: recovery evidence is now typed, negative-tested, and wired into derivative receipt visibility.

See also:
- ADR: `adrs/ADR-0350-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.recovery.evidence.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.recovery.evidence.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-recovery-evidence/`
- previous cut: `docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded`
- `sha256:5050505050505050505050505050505050505050505050505050505050505050`
- `known-bad-recovery-evidence-shapes-must-fail-validation`

Launch evidence proves how the worker started. Recovery evidence proves that a completed or interrupted run did not leave durable hidden authority behind and that no derivative receipt became visible before cleanup/recovery facts validated.

## Evidence object shape

`spec/removable.media.local.post_detach.recovery.evidence.schema.json` requires these closed-world sections:

- `contract_binding`: binds recovery evidence to the contract digest, launch-evidence digest, preopen-map digest, plan digest, and receipt-visibility posture;
- `trigger_model`: states that normal exit, worker kill, timeout, and host crash all require cleanup/recovery evidence before ordinary success;
- `recovery_scan`: proves host-state scan, scratch-registry consultation, worker-tree scan, fd rescan, and no media/store path reopen by the worker;
- `scratch_recovery`: admits only `tmpfs`, `md-memory`, or `encrypted-zfs-key-discard`; proves no replayable persistent scratch and cleanup/key-discard evidence;
- `worker_recovery`: proves the worker tree was reaped and no orphan, daemonized child, peer IPC leftover, or peer signal authority survived;
- `output_recovery`: proves the single derivative slot was sealed, remeasured after recovery, not visible early, and not rebindable;
- `receipt_visibility`: keeps ordinary derivative receipt visibility `withheld-until-recovery-evidence-validates`;
- `failure_policy`: fails closed on missing recovery evidence, unobserved cleanup, replayable scratch, surviving orphan, unsealed output, media reopen, or disk-backed scratch without key discard.

## Red corpus

The recovery-evidence red corpus starts under `spec/examples/invalid/removable-media/post-detach-recovery-evidence/` with:

- `cleanup-not-observed.json`
- `persistent-scratch-replayable.json`
- `crash-scan-missing.json`
- `derivative-receipt-visible-before-recovery.json`
- `orphan-worker-survived.json`
- `output-slot-unsealed.json`
- `disk-backed-scratch-without-key-discard.json`
- `media-path-reopened.json`

Each fixture is intentionally close to the canonical object and must fail validation. This prevents recovery from degenerating into a log warning or a best-effort cleanup claim.

## What this changes in implementation terms

A launcher prototype now has three separate artifacts to emit for this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived, what was destroyed, what was quarantined, and whether an ordinary derivative receipt may become visible.

This split matters because cleanup and crash semantics happen after launch. `cap_enter` evidence is necessary, but it does not prove scratch teardown, descendant reap, or output slot sealing.

## Notes for backend implementers

For the first lane, prefer memory-backed scratch or encrypted/key-discarded scratch. Disk-backed scratch without key discard is not ordinary-lane-admitted. If a prototype cannot prove cleanup after interruption, it should emit failure/quarantine evidence rather than a successful derivative receipt.

The recovery evidence should be collectable after normal worker exit, timeout kill, launcher restart, or host reboot. The recovery pass must not reopen the removable-media path or grant the worker any new store browsing authority. It should consult launcher-owned registries and host-side evidence only.

## r507 query-projection continuation

Recovery evidence now also points at the r507 query-projection boundary: `typed-post-detach-query-projection-positive-and-negative-fixture-guarded`, `sha256:5656565656565656565656565656565656565656565656565656565656565656`, and `spec/removable.media.local.post_detach.query.projection.schema.json`. Cleanup/recovery validation is therefore a precondition for derivative receipt visibility, but not a grant for ambient search. Queryability must pass through the redacted, lease-bound projection surface.

## r555 runtime/fixture split

r555 keeps the canonical fixture exact in `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json` and turns `spec/removable.media.local.post_detach.recovery.evidence.schema.json` into the generic runtime contract. The checker validates the positive fixture and the red corpus against both schemas so future dynamic digests/schema paths can vary without losing the historical literal regression surface.

## Hygiene

`tools/check_removable_media_local_post_detach_recovery_evidence.py` validates the positive recovery fixture against both the generic runtime schema and `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json`, proves the red corpus fails against both, and keeps `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded`, `sha256:5050505050505050505050505050505050505050505050505050505050505050`, and `known-bad-recovery-evidence-shapes-must-fail-validation` wired through the canonical stack.

Last updated: 2026-06-09r555
