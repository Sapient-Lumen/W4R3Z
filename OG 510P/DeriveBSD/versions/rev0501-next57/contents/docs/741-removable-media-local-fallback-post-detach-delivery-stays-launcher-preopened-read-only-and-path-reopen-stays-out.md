# Removable-media local fallback post-detach delivery stays launcher-preopened read-only and path re-open stays out

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, and digest-bound continuity between the preserved capture and the later worker-visible object.

This page closes the next smaller execution seam:

> **after detach, it is not enough that the worker gets one digest-bound object; that delivery must stay launcher-preopened read-only (or equivalent), and later path re-open must stay out.**

See also:
- ADR: `adrs/ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`
- previous cut: `docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The archive already says the later worker gets only one preserved subject and that the delivery must match the preserved-capture digest.
But one practical ambiguity still remains:
what stops implementations from proving the digest once and then letting later tools reacquire the subject by path afterward?

That would quietly reintroduce execution authority through the same place the archive just demoted to plumbing:

- reopen the synthetic worker path,
- reopen a store path or directory “because the tool wants a filename”,
- or widen the worker's view just enough that the single-object boundary becomes advisory.

The smaller honest answer is:
**the later delivery stays launcher-preopened read-only (or equivalent), and any worker-visible path remains compatibility-only rather than the authority anchor.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The launcher/broker prepares one read-only execution object before later ops begin

After detach and before later classify/scan/sanitize work begins, the launcher/broker must prepare exactly one read-only execution object for the preserved selected subject.
That may be:

- a launcher-preopened file descriptor,
- another already-bound read-only handle,
- or a compatibility shape proven equivalent to one already-bound single object.

The key contract is that the worker starts from one prepared object, not from later ambient path reacquire.

### 2) Any worker-visible path is compatibility-only plumbing

A worker-visible compatibility path such as `/work/input/preserved-subject.bin` may still exist so ordinary tools can read the file.
But that path names the already-bound object prepared by the launcher/broker.
It is not the reviewed or authoritative identity of the imported subject.

### 3) Path re-open and broader store rebind stay out

The later worker may not rely on:

- reopening the authoritative store locator,
- opening a broader authoritative-store directory,
- or rebinding to another object through path lookups after delivery preparation.

The first lane still grants one preserved selected subject only.
This cut keeps that boundary true at execution time, not only in receipt prose.

### 4) Canonical receipts and examples must record the posture

The canonical removable-media examples now record:

- launcher-preopened read-only delivery (or equivalent),
- worker-visible path as compatibility-only plumbing,
- and explicit no-reopen/no-store-rebind posture.

The example stack may also show this through a tiny `preopen.map` for the fresh later worker while still keeping authoritative-store directory authority out.

### 5) Exact kernel mechanism still stays open

The archive still does not force one exact implementation mechanism for the first cut.
Capsicum capability mode, rights-limited descriptors, and launcher-managed compatibility projections all fit if they preserve the same contract:

- one preserved subject only,
- read-only,
- digest-bound before later ops,
- and no later path-based reacquire of broader authority.

## Canonical first-cut example stack

The launcher-preopened delivery cut is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- the selected regular file is captured and verified,
- the preserved capture commits into authoritative quarantine store before detach,
- the host detaches the medium and restarts later work in a fresh worker,
- later work receives only one digest-bound preserved subject,
- that delivery stays launcher-preopened read-only (or equivalent),
- any synthetic worker path is compatibility-only plumbing,
- and the later worker does not reacquire the subject through broader path or store lookup.

## Why this cut is worth making now

Without this decision, the archive would still leave one implementation-sized escape hatch in a critical place:

- the worker would get only one digest-bound object on paper,
- but the execution story could still quietly drift back into path reopen folklore.

This page keeps the first coding target smaller and more aligned with DeriveBSD's existing capability posture: bind one preserved subject, preopen it read-only for the later worker, keep compatibility paths secondary, and keep wider reopen authority out.

## What remains open

Still intentionally open:

- exact launcher mechanics for path-compat tools,
- that open question is now resolved by `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`: the launcher or its approved shim must enter capability mode before handing control to later tool mainline code,
- and how trusted UI should summarize “authoritative locator + digest-bound delivery + compatibility path” compactly.

Last updated: 2026-03-28r477
