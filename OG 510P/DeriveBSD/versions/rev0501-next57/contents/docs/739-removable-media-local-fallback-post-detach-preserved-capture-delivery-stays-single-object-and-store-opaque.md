# Removable-media local fallback post-detach preserved-capture delivery stays single-object and store-opaque

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, and authoritative quarantine-store commit before detach.

This page closes the next smaller authority seam:

> **after detach, later work may receive only the one preserved selected subject it needs; it must not get a browseable authoritative-store namespace just to read that file.**

See also:
- ADR: `adrs/ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`
- previous cut: `docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`
- Capsicum posture: `docs/49-capsicum-casper-hardening.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability-mode naming constraints: `docs/180-capability-mode-dynamic-linking.md`

## Why this needs a hard decision

The archive already says the preserved capture commits into authoritative quarantine store before detach.
But “later work reads a projection of the stored preserved capture” still leaves one implementation-sized ambiguity open:
what exactly is exposed to the fresh later worker?

If the later worker receives a whole authoritative-store subtree or a reopenable direct store pathname, then the first lane quietly widens from:

- one reviewed selected subject,

to:

- namespace access over quarantined stored artifacts.

That is larger authority than the lane has earned.
The first local fallback needs the smaller honest answer:
**post-detach delivery stays single-object only, and the authoritative store stays opaque to the later worker.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The later worker receives one preserved selected subject, not a store namespace

After detach and restart, the later worker may consume only the preserved selected subject needed for classify/scan/sanitize.

It may receive that subject through:

- a brokered read handle, or
- a synthetic worker-local single-object projection path such as `/work/input/preserved-subject.bin`.

It may **not** receive a browseable authoritative-store mount, directory preopen, or subtree view in this first cut.

### 2) The authoritative locator remains receipt-visible evidence

The canonical stored locator still matters for receipts, support, and deterministic exports.
But that locator is evidence and bookkeeping, not the worker’s namespace contract.

The worker-visible path remains a synthetic execution path, visibly distinct from the authoritative locator.

### 3) Delivery remains read-only and attenuated

Whatever delivery mechanism is used, the later worker’s access must remain read-only and limited to the preserved selected subject.
No broader quarantine-store discovery or path-reopen authority should arrive as a side effect of “reading the imported file.”

### 4) Exact mechanism stays open in the first cut

The archive does not force one exact delivery mechanism yet.
A brokered read handle, launcher-preopened descriptor, or synthetic single-object projection are all acceptable first-cut shapes if they preserve the same boundary:

- single preserved subject only,
- read-only,
- authoritative locator recorded in receipts,
- and no browseable authoritative-store namespace in the later worker.

## Canonical first-cut example stack

The single-object delivery cut is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- the selected regular file is captured and verified,
- the preserved capture commits into authoritative quarantine store before detach,
- the host detaches the medium and restarts later work in a fresh worker,
- later work receives only a synthetic single-object projection of the preserved capture,
- the authoritative stored locator remains receipt-visible evidence,
- and the sanitized output is still a separate derivative from that preserved capture.

## Why this cut is worth making now

Without this decision, the archive would still let first implementations smuggle in extra authority under “projection” wording:

- a store subtree mount,
- a reopenable store path,
- or an overly broad preopen map.

This page keeps the first coding target smaller and more aligned with DeriveBSD’s capability-shaped posture: preserve the exact imported subject, then hand later tools **only that one subject**.

## What remains open

Still intentionally open:

- exact read-handle vs synthetic-path mechanics,
- whether later richer intake lanes should ever expose reviewed finite collections instead of one selected subject,
- and how trusted UI should summarize “authoritative stored locator + worker-visible synthetic path” compactly.

Last updated: 2026-03-28r470
