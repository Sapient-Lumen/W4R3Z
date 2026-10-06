# ADR-0325: Removable-media local fallback verified capture allows early detach and later ops stay device-independent

- Status: Accepted
- Date: 2026-03-28

## Context

`ADR-0313` through `ADR-0324` already made the first honest host-local removable-media fallback finite enough to implement:

- storage-only, session-scoped, quarantine-first fallback,
- host-controlled read-only mount into a disposable no-network jail,
- finite filesystem admission and inert mounted-tree posture,
- physical root-pinned traversal with one portable path grammar,
- path/kind/payload-first reviewed identity,
- one selected regular-file subject only,
- present-device-instance-only approval,
- attach receipts that keep observed current-presence hints evidence-only,
- and capture-first processing once the subject is selected.

That still left the next authority-lifetime seam open.
If later classify/scan/sanitize operations already consume the captured file in `/work`, should the removable medium stay mounted and leased until all later processing finishes, or should the host end the device session as soon as verified capture makes the medium unnecessary?

Leaving the medium mounted for the full later pipeline keeps authority around longer than the work needs and makes support/tooling guess whether later failures still depended on live device presence.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0324`:

1. Once capture of the selected regular-file subject verifies against the planned subject digest, the host should end the removable-medium session immediately rather than keeping the mount and device lease alive for later classify/scan/sanitize work.
2. Ending the session means host-side unmount/cleanup and emission of a `device.detach.receipt` tied to the same `lease_id`.
3. Later non-capture operations in this first lane must be able to proceed using only the captured bytes in `/work`; they must not require continued medium presence, a live `/ingest` mount, or renewed device authority.
4. Physical detach, lease expiry, or explicit revoke **before** verified capture still fail the flow closed as already decided by earlier ADRs.
5. This decision does **not** widen the lane into background tree mirroring, remembered-device continuation, or detached multi-subject staging; it only shortens the authority lifetime for the one already-selected regular-file subject.

## Consequences

- The first removable-media fallback now has a smaller authority window: browse/select from the mounted tree, capture and verify the one selected file, then end the device session before later classify/scan/sanitize work continues.
- Support and forensics can distinguish “capture failed while the medium was still required” from “later sanitize/scan failed after the medium had already been detached cleanly.”
- The first implementation target becomes more honest about least authority: later work runs on captured bytes, not on a live storage lease kept around out of convenience.

## Alternatives considered

- **Keep the mount/lease alive until the final `content.import.receipt`:** rejected because it extends device authority past the point where the first lane no longer needs it.
- **Allow either early detach or full-session mount lifetime as implementation choice:** rejected because it preserves archive ambiguity right at an implementation-critical authority boundary.
- **Design a richer staged-import/session-resume subsystem now:** rejected because the first lane only needs a smaller rule about when the removable-medium session can end.

## References

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- `adrs/ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
- `adrs/ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`
- `adrs/ADR-0323-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`
- `adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`
- `docs/735-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`
