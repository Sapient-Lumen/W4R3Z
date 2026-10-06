# Removable-media local fallback verified capture allows early detach and later ops stay device-independent

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, and capture-first processing into `/work`.

This page closes the next smaller authority-lifetime seam:

> **once capture of the selected regular file verifies against the planned subject digest, the host should end the removable-medium session and emit `device.detach.receipt` before later classify/scan/sanitize work continues.**

See also:
- ADR: `adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`
- previous cut: `docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- device authority: `docs/278-device-grants-and-devfs-rulesets.md`
- lease/revocation spine: `docs/249-lease-registry-and-cross-lane-revocation.md`

## Why this needs a hard decision

The archive already says later non-capture work consumes the captured file in `/work`.
But that still leaves one expensive ambiguity for the first implementation:
should the medium stay mounted and leased until the end of scan/sanitize/import anyway, or should verified capture let the host end the device session immediately?

Without one more cut, implementations drift in opposite bad directions:

- keep the storage lease alive for the whole later pipeline even though later work no longer depends on the medium,
- or silently detach early without making that authority boundary explicit in docs, plans, and receipts.

The first local fallback needs the smaller honest answer:
**capture-first should also become detach-early once capture verifies.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Verified capture is the earliest detach point

The host may not end the removable-medium session before capture verifies against the planned selected-subject digest.
But once that verification succeeds, the medium is no longer required for later work in this lane.
That verified-capture point is therefore the first accepted early-detach boundary.

### 2) The host should end the device session before later ops continue

After verified capture, the host should:

- unmount the removable-medium view,
- end the attach lease,
- and emit a `device.detach.receipt` for the same `lease_id`

before later classify/scan/sanitize work continues.

### 3) Later ops must stay device-independent

After that detach point, later non-capture operations consume only the captured bytes in `/work`.
They do not require:

- continued physical device presence,
- a live `/ingest` mount,
- or renewed attach authority.

This keeps later work aligned with the earlier capture-first cut instead of carrying unnecessary medium lifetime dependence.

### 4) Earlier failure posture stays fail-closed

This page does **not** weaken earlier decisions.
If physical detach, lease expiry, or explicit revoke happens before verified capture completes, the flow still fails closed.
The archive is deciding the first honest **early end** point, not adding a resilience or resume subsystem.

## Canonical first-cut example stack

The subject-processing and detach example stack is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/device.attach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- selection still comes from the mounted inert tree,
- the first non-browsing step is capture,
- capture must verify against the planned selected-subject digest,
- the host then ends the removable-medium session and emits `device.detach.receipt`,
- and later operations continue from the captured file without needing the device to remain present.

## Why this cut is worth making now

Without this decision, the archive still pays repeated implementation tax:

- coding teams can keep the removable medium mounted much longer than necessary,
- support receipts cannot clearly answer whether later failures still depended on live device presence,
- and the first lane keeps a hidden long-lived authority tail even after capture-first already made later work medium-independent.

This page keeps the first coding target smaller and more coherent: browse/select from the mounted tree, capture and verify the one selected file, end the medium session, and then do later processing on the captured bytes only.

## What remains open

Still intentionally open:

- the exact host-side unmount/cleanup implementation mechanics,
- trusted-UI wording for showing “safe to remove” or equivalent operator state,
- whether later richer lanes should keep detachable staged collections rather than one-file capture,
- and how support UIs should render the attach→capture→detach timeline compactly.

Last updated: 2026-03-28r466
