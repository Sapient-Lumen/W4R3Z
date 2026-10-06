# Removable-media local fallback approval stays present-device-instance-only and reattach requires fresh grant

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md` already made the first host-local removable-media fallback finite enough to code: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected subject, and a regular-file-only selected-subject floor.

This page closes the next smaller implementation seam:

> **the first removable-media local-ingest approval stays present-device-instance-only; detach revokes it, and reattach requires a fresh grant.**

See also:
- ADR: `adrs/ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`
- previous cuts: `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- removable-media posture by profile: `docs/458-removable-media-and-usb-posture-by-profile.md`
- lease/revocation spine: `docs/249-lease-registry-and-cross-lane-revocation.md`

## Why this needs a hard decision

The first local fallback is now narrow enough to build, but approval continuity still matters.
Without one more cut, implementations can still disagree about whether the user approved:

- this currently present removable-storage instance,
- this nominal model/serial forever,
- or a remembered “USB allow” that silently survives detach, reboot, and later insertions.

That ambiguity is expensive.
It is how a carefully bounded fallback turns back into “automount plus scary dialog”.
DeriveBSD already has a better general model for temporary authority: **leases that expire, can be revoked, and leave receipts**.
The removable-media fallback should compose with that model, not create a durable remembered-device side system in the first cut.

FreeBSD’s substrate makes the safe split practical:
- `devd.conf(5)` already exposes USB attach/detach and VFS mount/unmount event classes.
- USB/device tooling can expose serial or disk-ident hints (`camcontrol(8)`, `diskinfo(8)`).

That is enough to drive detection, current-instance review, receipts, and revocation.
It is **not** a reason to standardize durable auto-resume authority in v0.
The first lane should treat those identifiers as evidence and operator hints, not as a substitute for fresh approval.

## Accepted cut

For the first host-local removable-media ingest lane:

- approval stays **present-device-instance-only in the first cut**
- the approved authority window is the current `device.attach.grant` lease for the currently present removable-storage instance
- physical detach, explicit revoke, lease expiry, or loss of the required host-controlled mount state ends that authority
- reattaching the same nominal medium requires a **fresh grant** and fresh trusted-UI or policy evaluation, even if vendor/product/serial or disk-ident hints appear unchanged
- remembered approval may suppress repeated prompts only inside the current live presence/lease window; it does **not** survive detach, reboot, or later lease issuance
- any future durable remembered-device lane must return as a **separate explicit RFC/ADR cut** instead of widening this first fallback

## Why this is the right first cut

### 1) It keeps the fallback aligned with the archive’s existing authority model

Temporary authority in DeriveBSD is supposed to look like a lease with expiry and revocation.
The removable-media fallback now follows that rule instead of becoming a remembered-device exception.

### 2) It prevents “policy dialog automount” from sneaking back in

If detach/reattach can silently reuse authority, the real behavior quickly becomes “this stick is trusted now”.
That is exactly the drift this fallback was supposed to avoid.

### 3) It is practical on imperfect hardware without pretending continuity is solved

B and C still get a humane local fallback.
The host can detect attach/detach, present current-device hints, issue a bounded lease, and revoke on detach.
That is enough to implement the first lane without pretending that removable-media identity continuity is stronger than it is.

## What this still does not decide

This page does **not** finish the entire local authorization UX.
It does **not** standardize a durable remembered-device allowlist.
It does **not** decide how a later richer lane might safely reuse stronger hardware identity, organization policy, or maintenance enrollment.
It only removes the ambiguity in the first buildable lane.

## Related docs

- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`
- `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`

Last updated: 2026-03-28r463
