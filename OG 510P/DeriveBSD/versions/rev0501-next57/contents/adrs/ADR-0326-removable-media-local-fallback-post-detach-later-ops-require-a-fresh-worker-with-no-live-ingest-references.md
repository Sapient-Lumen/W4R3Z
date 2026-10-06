# ADR-0326: Removable-media local fallback post-detach later ops require a fresh worker with no live ingest references

- Status: Accepted
- Date: 2026-03-28

## Context

`ADR-0313` through `ADR-0325` already made the first honest host-local removable-media fallback finite enough to implement:

- storage-only, session-scoped, quarantine-first fallback,
- host-controlled read-only mount into a disposable no-network jail,
- finite filesystem admission and inert mounted-tree posture,
- physical root-pinned traversal with one portable path grammar,
- path/kind/payload-first reviewed identity,
- one selected regular-file subject only,
- present-device-instance-only approval,
- attach receipts that keep observed current-presence hints evidence-only,
- capture-first processing once the subject is selected,
- and early detach once verified capture makes the medium unnecessary.

That still leaves one more implementation seam open.
If the pre-capture worker keeps `/ingest` as its current working directory, root, jail root, or open-file source, then “detach early” is only partly true: the runtime can still hold the mount busy or keep hidden dependence on the old medium-facing execution context.

The platform substrate reinforces that this is a real seam rather than theoretical purity work:

- `umount(8)` documents that a filesystem cannot be unmounted while it is busy, including when processes have open files on it or keep a working directory there.
- `fuser(1)` can report processes that keep a filesystem busy through open files, current working directory, root directory, or jail root directory.
- `procstat(1)` can surface file-descriptor and working-directory state for diagnosis.

The archive therefore needs one more hard decision about the post-detach execution boundary itself, not just about device lifetime.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0325`:

1. Later classify/scan/sanitize work may not continue inside an execution context that still carries live `/ingest` references from the pre-detach phase.
2. The canonical first-cut posture is therefore **fresh worker before later ops**: once verified capture completes and the host emits `device.detach.receipt`, the pre-capture worker is torn down and later work starts in a fresh disposable worker with /ingest absent.
3. That fresh worker must start with `/ingest` absent and with no inherited file-descriptor, current-working-directory, root-directory, or jail-root references to the removable medium.
4. `fuser(1)` / `procstat(1)` remain useful implementation diagnostics and support evidence when teardown fails or unmount reports busy state, but they are not substitutes for the normative boundary above.
5. This decision does **not** widen the lane into persistent staging services, background mirroring, or remembered continuation; it only fixes the smallest honest post-detach execution fence for the one already-selected regular-file subject.

## Consequences

- The first removable-media fallback now has a full post-capture authority fence, not merely an intent to detach early.
- Implementations get a smaller and more testable sequence: browse/select, capture and verify, detach, tear down the pre-capture worker, then continue later ops in a fresh worker with `/ingest` absent.
- Support and forensics can distinguish “detach failed because something still held the mount busy” from “later sanitize/scan failed in the post-detach worker.”
- The first B/C compatibility lane stays honest about least authority without inventing a larger staging subsystem.

## Alternatives considered

- **Let later ops continue in the same worker after detach as long as code tries not to touch `/ingest`:** rejected because it leaves open-file/cwd/root leakage as hidden implementation state.
- **Require only best-effort teardown diagnostics, not a fresh worker boundary:** rejected because it keeps the archive ambiguous exactly where the platform exposes real busy-mount failure modes.
- **Design a richer multi-phase orchestrator now:** rejected because the first lane only needs a small execution fence, not a new subsystem.

## References

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`
- `adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`
- `docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`
