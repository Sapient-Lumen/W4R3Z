# Removable-media local fallback stays storage-only, session-scoped, and quarantine-first

**Tier:** B (Base contract boundary)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

`docs/458-removable-media-and-usb-posture-by-profile.md` already fixed the product-shape defaults:
no ambient trusted-plane automount, quarantine-first removable-media handling, and device domains preferred where hardware supports them.

This page closes the next implementation seam:

> when hardware cannot isolate USB/removable-media controllers cleanly, what is the *smallest* honest local fallback that preserves DeriveBSD’s security story?

The answer is deliberately narrow:

> **a storage-only, session-scoped, quarantine-first fallback built from existing typed artifacts — not a generic USB passthrough or host automount convenience lane.**

See also:
- ADR: `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- profile baseline: `docs/458-removable-media-and-usb-posture-by-profile.md`
- workflow doc: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `/dev` authority and devfs compilation: `docs/278-device-grants-and-devfs-rulesets.md`
- HID danger boundary: `docs/207-input-authority-secure-attention-and-hid-risk.md`
- hardware support / trusted-UI floor: `docs/410-desktop-viability-checklist.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`

## Accepted boundary

### 1) This fallback is for storage-shaped removable media only

The first local fallback is only for media whose primary role is **block-storage ingest/export**.
It is not a generic answer for arbitrary USB peripherals.

Allowed first-cut intent:
- importing files from a thumb drive or external disk,
- exporting files to explicitly chosen removable storage,
- ingesting signed offline kits through a quarantine→verify→promote path.

Out of scope for this lane:
- raw HID,
- network dongles,
- serial/debug bridges,
- webcams/microphones,
- smart-card / FIDO devices,
- and generic “attach this USB device to some workload” passthrough.

Those classes either stay on device-domain/broker lanes or come back as their own RFC/ADR work.

### 2) Session-scoped means fresh authority every time

The fallback is **never** “remember this device forever.”
The first implementation should treat each use as a fresh host-local session with:

- explicit authorization,
- a fresh `device.attach.grant`,
- a fresh `device.attach.receipt`,
- and a matching `device.detach.receipt` when the session ends.

That keeps removable-media use queryable and explainable instead of collapsing into a background convenience helper.

### 3) Quarantine-first still means “not mounted into the trusted host UI plane”

The fallback does **not** permit direct trusted-plane automount.
Instead, the first implementation attaches the selected device or partition into a disposable ingest lane and keeps the host on the control/evidence side.

The ordinary path is still:

1. classify device/media,
2. authorize the exact storage session,
3. expose the minimal device view to a disposable ingest lane,
4. mount read-only first,
5. sanitize/import or verify an offline kit,
6. detach and emit receipts.

The fallback is therefore a **quarantine path that happens to be host-local in control**, not a return to ambient host-local use.

### 4) `read-only-first` is part of the contract

The first host-local fallback should prefer read-only mount posture and require an explicit stronger step for write access.
That matches the archive’s wider device-authority rule that raw block access is high-risk and should not silently expand.

### 5) The implementation stack is existing DeriveBSD nouns

This lane does not need a new artifact family.
The implementation-shaped stack is already present:

- `device.profile` classifies the media and marks it removable/storage-shaped.
- `device.attach.grant` authorizes a narrow storage session.
- `device.attach.receipt` says what the runtime actually attached.
- `devfs.view.plan` renders a minimal device view for the disposable ingest jail/lane.
- `mount.view` can project the read-only mounted ingest tree into that lane without spreading raw storage-node authority further.
- `content.import.receipt` records imported content lineage, sanitization, and quarantine handling.
- `device.detach.receipt` closes the session.

`docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` now fixes the first concrete execution choice inside that stack too: host-controlled read-only mount, then a disposable no-network jail consuming the mounted tree through `mount.view`, with a **block-empty** `devfs.view.plan` and **no raw block device nodes** inside the jail.

This is the practical bridge from archive prose toward implementable specs.

## Profile consequences

### B) Secure workstation

B may use this fallback on imperfect hardware **only** for storage-class removable media and only without weakening host-owned HID / trusted-UI authority.
This keeps B viable on more real laptops while still refusing the larger “USB is just another host convenience surface” lie.

### C) General-purpose OS

C may use the same narrow fallback as its explicit compatibility path.
That keeps C broadly viable without forcing A/B/D to inherit the same looseness.

### A) Secure fleet host

A does not gain a normal local USB workflow from this doc.
At most, this boundary helps explain why “storage-only local fallback” is a compatibility lane elsewhere, not the fleet baseline.

### D) Appliance factory / regulatory

D keeps its stronger `device-domain-or-ingest-station` posture.
This boundary does not redefine production/factory ingest as ordinary host-local attach.

## Why this improves coherence across all product shapes

This is the smallest decision that keeps “one archive, no forks” believable:

- B stays usable on imperfect hardware,
- C stays broadly compatible,
- A and D stay stricter,
- and the implementation target is now a finite stack using existing BSD primitives and DeriveBSD artifacts.

Without this cut, the archive keeps oscillating between two bad extremes:

- “require device domains everywhere,” which makes B/C viability brittle,
- or “just allow local USB with prompts,” which quietly reintroduces ambient authority.

This boundary avoids both.

## What remains open

Still intentionally open:
- exact trusted-UI prompt wording,
- whether later B/C releases should prefer a stronger microVM-backed ingest lane when practical,
- integrated-device families,
- final remembered-policy posture for non-storage devices,
- and exact filesystem-specific attachment details.

The point here is smaller and more actionable:
**the first local fallback is now small enough to spec and build without reopening the whole device-security model.**

Last updated: 2026-03-26r455
