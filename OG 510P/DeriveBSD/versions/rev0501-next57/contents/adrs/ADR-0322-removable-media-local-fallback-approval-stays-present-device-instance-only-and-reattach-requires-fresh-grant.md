# ADR-0322: Removable-media local fallback approval stays present-device-instance-only and reattach requires fresh grant

Date: 2026-03-28  
Status: Accepted

## Context

`ADR-0313` through `ADR-0321` already made the first honest host-local removable-media fallback for imperfect B/C hardware finite enough to implement:

- storage-only, session-scoped, quarantine-first,
- host-controlled `fstyp` admission and read-only mount,
- disposable no-network jail,
- inert mounted trees,
- physical root-pinned walk,
- one portable member-path grammar,
- path/kind/payload-first reviewed/import identity,
- single-selected-subject only,
- and regular-file-only selected subjects in the first cut.

One practical seam still remained half-open:
**does approval survive unplug/replug, or is approval only for the currently present device instance?**

Leaving that vague is expensive.
If detach/reattach quietly reuses authority, the fallback drifts back toward “automount with a policy dialog”.
That would make the real product semantics depend on remembered device folklore instead of on the archive’s ordinary lease and revocation model.

FreeBSD provides useful event and identity hints, but not a reason to pretend continuity is solved for the first cut:

- `devd.conf(5)` exposes USB attach/detach notifications and VFS mount/unmount notifications.
- USB events may carry attributes like vendor/product/serial.
- `camcontrol(8)` and `diskinfo(8)` can surface device serial or disk-ident values.

Those are good evidence surfaces for *the current event*.
They are not strong enough reason to standardize durable “same stick, auto-resume the old grant” semantics in the first buildable lane.
The safest small decision is therefore to keep approval scoped to the currently present device instance and make `reattach requires a fresh grant` the explicit rule for this lane.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0321`:

1. Approval stays **present-device-instance-only in the first cut**.
2. The approved authority window is the current `device.attach.grant` lease for the currently present removable-storage instance.
3. Physical detach, explicit revoke, lease expiry, or failure to keep the required host-controlled mount state ends that authority.
4. Reattaching the same nominal medium requires a **fresh grant** and fresh trusted-UI or policy evaluation, even when vendor/product/serial or disk-ident hints look the same.
5. Remembered approval may suppress repeated sub-step prompts only inside the current live presence/lease window; it does **not** survive detach, reboot, or later lease issuance.
6. Any future durable remembered-device lane must return as a **separate explicit RFC/ADR cut** instead of widening this first fallback lane.

## Consequences

- The first removable-media fallback now composes cleanly with the archive’s lease/revocation model instead of inventing a device-specific exception.
- Implementations have a smaller and safer target: approve current presence, complete the bounded ingest flow, revoke on detach/end.
- B keeps humane local fallback on imperfect hardware without quietly reopening ambient automount or durable “trust this USB stick forever” policy.
- C keeps explicit local-admin viability without teaching the baseline archive to treat advisory removable-device identifiers as durable trust roots.

## Alternatives considered

- **Allow reattach to auto-resume the prior grant when serial/vendor/model match:** rejected because the first cut should not treat advisory identity hints as durable authority continuity.
- **Persist remembered approvals across reboots/detach as a convenience baseline:** rejected because it quietly turns the local fallback into a remembered automount/allowlist subsystem.
- **Leave continuity unspecified until coding:** rejected because the first implementation would become the real policy surface.

## Related

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
- `adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`
- `adrs/ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`
- `adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- `adrs/ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
- `docs/732-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`
