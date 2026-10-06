# Removable-media local fallback post-detach later ops require a fresh worker with no live ingest references

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing into `/work`, and early detach once verified capture completes.

This page closes the next smaller execution-boundary seam:

> **after verified capture and `device.detach.receipt`, later classify/scan/sanitize work must restart in a fresh disposable worker with `/ingest` absent and with no live inherited references to the old mounted medium.**

See also:
- ADR: `adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`
- previous cut: `docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- device authority: `docs/278-device-grants-and-devfs-rulesets.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`

## Why this needs a hard decision

The archive already says later work should not require continued medium presence.
But that still leaves one expensive ambiguity for the first implementation:
can the same pre-capture worker continue after detach, or does the runtime need a real execution fence?

FreeBSD makes the danger concrete rather than theoretical:

- `umount(8)` says a filesystem cannot be unmounted while it is busy, including when processes keep open files or a working directory there.
- `fuser(1)` can report processes using a filesystem through open files, current working directory, root directory, or jail root directory.
- `procstat(1)` can surface file-descriptor and working-directory state for diagnosis.

Without one more cut, implementations drift in opposite bad directions:

- detach “on paper” but keep the same worker alive with hidden `/ingest` references,
- or add ad hoc teardown folklore without saying what later operations are actually allowed to inherit.

The first local fallback needs the smaller honest answer:
**detach-early must also become fresh-worker-after-detach.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Later ops require a fresh post-detach worker

Once capture verifies and the host emits `device.detach.receipt`, the pre-capture worker should not continue into later classify/scan/sanitize work.
The canonical first cut tears that worker down and starts a fresh disposable worker for later operations.

### 2) `/ingest` must be absent in the later worker

The post-detach worker must not receive the mounted removable-medium view.
/ingest is gone from the later worker entirely.
Later work consumes only the captured file in `/work`.

### 3) No live ingest references may carry over

The later worker must not inherit open file descriptors, current working directory, root directory, or jail-root references that still point into the old mounted medium.
This is the smallest honest rule that keeps “later ops are device-independent” true in practice.

### 4) Busy-mount diagnostics stay implementation detail, not portable truth

If teardown or unmount reports busy state, implementations may use `fuser(1)` and `procstat(1)` to diagnose what kept the old mount alive.
That evidence can help support bundles, but the normative boundary is still the same: later ops only continue after the fresh-worker fence succeeds.

## Canonical first-cut example stack

The post-detach execution-fence example stack is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- selection still comes from the mounted inert tree,
- the first non-browsing step is capture,
- verified capture still enables early detach,
- and later work then restarts in a fresh disposable worker with `/ingest` absent and no inherited live medium references.

## Why this cut is worth making now

Without this decision, the archive still pays repeated implementation tax:

- coding teams can claim to detach early while still reusing a worker that holds the old mount busy,
- support receipts cannot clearly answer whether later failures happened before or after the execution fence,
- and the first lane keeps one last hidden coupling between later sanitize/scan work and the medium-facing execution context.

This page keeps the first coding target small and testable: browse/select from the mounted tree, capture and verify, detach, restart the worker, and continue later work from captured bytes only.

## What remains open

Still intentionally open:

- exact supervisor/runtime mechanics for tearing down and recreating the worker,
- how support UIs should summarize busy-mount teardown failures compactly,
- whether a later stronger lane may prove an equivalent no-live-reference fence without restarting the worker,
- and whether future broader staging lanes deserve their own typed execution-phase artifacts.

Last updated: 2026-03-28r467
