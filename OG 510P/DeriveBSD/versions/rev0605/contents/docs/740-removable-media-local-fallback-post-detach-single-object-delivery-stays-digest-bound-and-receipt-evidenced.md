# Removable-media local fallback post-detach single-object delivery stays digest-bound and receipt-evidenced

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** supply-chain, isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, and single-object store-opaque post-detach delivery.

This page closes the next smaller continuity seam:

> **after detach, it is not enough that later work sees one synthetic path; the delivered object must be digest-bound to the preserved capture and the receipt must say so.**

See also:
- ADR: `adrs/ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`
- previous cut: `docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`
- Capsicum posture: `docs/49-capsicum-casper-hardening.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`

## Why this needs a hard decision

The archive already says the later worker receives only one preserved selected subject and that the authoritative store stays opaque.
But a synthetic worker path like `/work/input/preserved-subject.bin` is still only plumbing.
By itself it does not prove that the worker got the same object named by:

- the planned selected subject digest,
- the authoritative preserved-capture store locator,
- and the later derivative relationship recorded in the receipt.

Without a tighter cut, the first implementation can still drift into “the launcher probably pointed the worker at the right file.”
That is too soft for a lane that otherwise tries to stay receipt-first and least-authority.
The smaller honest answer is:
**post-detach single-object delivery stays digest-bound, and the receipt records that binding explicitly.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Worker-visible delivery stays subordinate to the preserved-capture digest

After detach and restart, the later worker may still receive only one preserved selected subject.
But before later classify/scan/sanitize work begins, that delivered object must be bound to the exact preserved-capture digest already established by the plan and authoritative store.

The worker-visible projection path or delegated read handle is only execution plumbing.
The preserved-capture digest remains the authority anchor.

### 2) Mismatch fails closed before later work starts

The launcher/broker must not start later classify/scan/sanitize work unless the delivered object matches the preserved selected subject digest.
If the projection/handle points at a different object, stale scratch file, or mismatched digest, the lane fails closed before later work begins.

### 3) The canonical receipt must record the binding

The canonical `content.import.receipt` now records that the worker-visible single-object delivery was digest-bound to the preserved capture.
That gives support/export a compact continuity story:

- authoritative locator for the preserved capture,
- synthetic worker-visible delivery path,
- and exact digest binding between them.

### 4) Exact mechanism stays open in the first cut

The archive still does not force one exact implementation mechanism.
A preverified store projection, delegated read-only descriptor, or launcher-time re-hash are all acceptable first-cut shapes if they preserve the same contract:

- single preserved subject only,
- read-only,
- digest-bound before later ops,
- and receipt-evidenced.

## Canonical first-cut example stack

The digest-bound delivery cut is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- the selected regular file is captured and verified,
- the preserved capture commits into authoritative quarantine store before detach,
- the host detaches the medium and restarts later work in a fresh worker,
- later work receives only one synthetic single-object delivery for the preserved capture,
- that worker-visible delivery must match the preserved selected subject digest before later ops begin,
- and the canonical receipt records that digest binding explicitly.

## Why this cut is worth making now

Without this decision, the archive would still leave an implementation-sized ambiguity in a critical place:

- the authoritative store locator would be exact,
- the worker-visible delivery would be bounded,
- but continuity between them would still be partly folklore.

This page keeps the first coding target smaller and more testable: later tools may get one synthetic execution object, but the archive still demands proof that it is the exact preserved capture the receipts claim.

## What remains open

Still intentionally open:

- exact read-handle vs synthetic-path mechanics,
- whether the binding is proven by direct re-hash, descriptor lineage, or another capability-safe mechanism,
- and how trusted UI should summarize “authoritative locator + worker path + digest-bound continuity” compactly.

Last updated: 2026-03-28r471
