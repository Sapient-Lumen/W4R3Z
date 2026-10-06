# Removable-media local fallback preserves the verified capture and forbids in-place rewrite by later ops

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing into `/work`, early detach once capture verifies, and a fresh post-detach worker with `/ingest` absent.

This page closes the next smaller evidence-lifetime seam:

> **after verified capture and detach, the exact captured subject remains preserved evidence and later classify/scan/sanitize work must not rewrite that capture in place; later outputs are separate derivatives from the preserved capture.**

See also:
- ADR: `adrs/ADR-0327-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`
- previous cut: `docs/736-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- origin/anti-laundering spine: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`

## Why this needs a hard decision

The archive already says later work reads `/work` instead of the live mounted medium.
But that still leaves one expensive ambiguity for the first implementation:
should later sanitize/convert steps be allowed to rewrite the captured subject in place, or must the exact verified capture remain preserved while later outputs appear separately?

Without one more cut, implementations drift in opposite bad directions:

- keep only one mutable working file and lose the exact preserved imported subject,
- or preserve the exact capture only by local convention, leaving receipts unable to prove whether the later sanitized output replaced the original or derived from it separately.

The first local fallback needs the smaller honest answer:
**capture-first must also become preserve-the-capture and derive later outputs separately.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The verified capture remains preserved exact evidence

Once capture verifies against the planned selected-subject digest, that captured file remains the exact preserved imported subject for the rest of this lane.
This is the stable evidence anchor for later support, export, and forensics questions.

### 2) Later operations may not rewrite the preserved capture in place

Later `classify`, `scan`, `sanitize`, `convert`, or similar steps treat the preserved capture as read-only input.
They may not replace, truncate, or overwrite the capture path in place.

### 3) Later outputs are separate derivatives from the preserved capture

If later work emits a sanitized PDF or other transformed result, that output appears as a separate derivative with its own digest and path.
The canonical receipt example now names both:

- the preserved captured subject, and
- the sanitized derivative derived from that preserved capture.

### 4) Exact hardening mechanics stay implementation detail in the first cut

A host/runtime may enforce the preserved-capture posture using ordinary read-only placement, permissions, or local file-immutability controls.
But the archive contract stays portable and modest: the preserved capture remains separately addressable exact evidence, and later outputs do not rewrite it in place.

## Canonical first-cut example stack

The preserved-capture example stack is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- one selected regular file is captured and verified,
- the host detaches the medium and restarts later work in a fresh worker,
- the verified capture remains preserved exact evidence,
- later operations do not rewrite that capture in place,
- and sanitized output is a separate derivative from the preserved capture.

## Why this cut is worth making now

Without this decision, the archive still pays repeated implementation tax:

- coding teams can quietly turn the capture path into a mutable scratch file,
- support receipts cannot clearly answer whether the preserved imported subject still exists after sanitization,
- and the first lane loses one of its strongest practical forensics benefits right where it should become most concrete.

This page keeps the first coding target small and honest: browse/select, capture and verify, detach, restart the worker, preserve the capture, and derive later outputs separately.

## What remains open

Still intentionally open:

- exact file-hardening mechanics for the preserved capture on a given runtime,
- whether later richer lanes should preserve broader staged sets than one selected file,
- how trusted UI should summarize the “original preserved / sanitized derivative” pair compactly,
- and whether later generalized import lanes deserve a broader derivative-role vocabulary.

Last updated: 2026-03-28r468
