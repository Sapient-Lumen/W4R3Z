# ADR-0350: Removable-media local fallback post-detach recovery evidence is typed and negative-tested

- Status: accepted
- Date: 2026-05-21
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0349-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md`, `docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md`, `spec/removable.media.local.post_detach.recovery.evidence.schema.json`, `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json`

## Context

ADR-0349 made FreeBSD launch evidence typed, but a clean launch is not the same as a trustworthy completed derivative. The first host-local removable-media fallback still needed a closed recovery story for worker death, host crash, failed cleanup, leftover scratch, orphan descendants, partial output, and late audit. Without that story, `scratch-destroyed-before-derivative-receipt` can silently degrade into best-effort cleanup and a derivative receipt can appear before the host has proved that no durable scratch, orphan worker, or rebinding output path survived.

## Decision

Add `spec/removable.media.local.post_detach.recovery.evidence.schema.json` with paired exact fixture schema `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json` and kind `removable.media.local.post_detach.recovery.evidence`, the canonical example `spec/examples/removable.media.local.post_detach.recovery.evidence.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-recovery-evidence/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded`, `sha256:5050505050505050505050505050505050505050505050505050505050505050`, and `known-bad-recovery-evidence-shapes-must-fail-validation` in the launch evidence, contract backend evidence, canonical plan, receipt, preopen map, attach grant, and detach receipt examples.

The recovery-evidence object is narrower than a future generic crash-recovery receipt. It covers this lane only: one selected regular-file subject, post-detach worker, memory-backed or key-discarded scratch, no media path reopen during recovery, worker tree reap, output slot sealing and remeasurement, and withholding derivative receipt visibility until recovery evidence validates.

## Consequences

- The persistent-state claim now survives interruption semantics instead of only clean-run semantics.
- A derivative receipt is not visible merely because launch evidence validated; it also waits for recovery/cleanup evidence or fails closed.
- Disk-backed scratch without key discard remains outside the first ordinary lane.
- Negative fixtures make false recovery explicit: missing cleanup, replayable scratch, missing scan, early receipt visibility, surviving orphan, unsealed output, disk scratch without key discard, and media path reopen all fail validation.

## Alternatives considered

- **Fold recovery into launch evidence only.** Rejected because launch facts and post-run/crash facts occur at different times and need different failure semantics.
- **Allow best-effort cleanup with a warning.** Rejected for the ordinary lane because hidden scratch is persistent state and therefore authority.
- **Treat crash recovery as implementation detail.** Rejected because the whole purpose of receipts is to prevent implementation detail from becoming invisible authority.

## Follow-up

- Teach the first launcher prototype to emit recovery evidence after normal exit, kill, timeout, or crash recovery.
- Add backend extraction notes for tmpfs teardown, memory-md destruction, encrypted ZFS key discard, worker-tree reap, and output slot sealing.
- Consider a future generic `sandbox.recovery.evidence` only after this narrow removable-media lane proves stable.

## Links

- boundary doc: `docs/761-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.recovery.evidence.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.recovery.evidence.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-recovery-evidence/`
- previous cut: `adrs/ADR-0349-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md`
