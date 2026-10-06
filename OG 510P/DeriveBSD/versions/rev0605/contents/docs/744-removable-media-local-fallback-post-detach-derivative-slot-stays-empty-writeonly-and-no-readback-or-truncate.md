# Removable-media local fallback post-detach derivative slot stays empty write-only and no readback or truncate

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, digest-bound continuity between the preserved capture and the later worker-visible object, launcher-preopened read-only delivery instead of later path re-open, broker-collected derivative egress instead of trusting `/work/output/...` as authoritative derivative identity, and one declared writable derivative slot with no extra worker result surface.

This page closes the next smaller execution seam:

> **it is not enough that later-worker derivative egress stays on one declared slot; in the first lane, that slot must also start empty and the worker must not read back or truncate it, and any exact seek/open mechanics on a seekable regular-file sink are refined by the next cut.**

See also:
- ADR: `adrs/ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`
- previous cut: `docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The archive already says the later worker gets one read-only preserved subject and one declared writable derivative slot.
But one practical ambiguity remains:
**is that writable slot still allowed to behave like an ordinary mutable scratch file?**

Without a tighter contract, implementations can still drift between incompatible stories:

- precreate one output file but let the worker read it back while it is still under construction,
- precreate one output file but let the worker seek or truncate inside it and quietly treat it as general scratch state,
- or keep the first lane on one launcher-precreated empty regular file whose worker authority is write-only and forward-only with no readback or truncate.

The smaller honest answer is:
**the declared derivative slot starts empty, worker authority on it stays no-readback and no-truncate, and any exact seek/open mechanics on a seekable regular-file sink must return as the next explicit cut rather than hiding in folklore.**

The archive now says the declared derivative slot starts empty write-only and no readback or truncate in the first lane.

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The declared derivative slot starts as a launcher-precreated empty regular file

The later worker may still emit a sanitized derivative.
But the first lane now fixes that the declared slot begins as a launcher-precreated empty regular file before later-worker execution starts.
In the canonical example, `sanitized_derivative_slot` still maps to `/work/output/invoice.sanitized.pdf`, but it must begin zero-length.

### 2) Worker authority on that slot stays write-only and forward-only

The later worker may write bytes into the declared slot.
But it may not read back or truncate that slot.
The exact seek/open mechanics for a seekable regular-file sink are refined by `docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`; this page keeps only the smaller boundary that readback and truncate stay out.

### 3) The first lane does not treat the derivative slot as mutable scratch state

The declared slot exists to receive one authoritative later-worker derivative candidate for broker collection.
It is not a general-purpose temporary file for reread/overwrite cycles.
If some future transform needs richer mutable output staging, that must return as a later explicit lane or RFC instead of quietly widening this baseline.

### 4) Broker collection still names authority

This cut does not change where authoritative derivative identity comes from.
The launcher/broker still collects and remeasures bytes from the declared slot after worker exit before `content.import.receipt` names the authoritative derivative locator.
What changes here is only the worker-side authority floor before that collection step.

## Canonical first-cut example stack

The empty-write-only-derivative-slot cut is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- the selected regular file is captured and verified,
- the preserved capture commits into authoritative quarantine store before detach,
- the host detaches the medium and restarts later work in a fresh worker,
- later work receives only one digest-bound preserved subject on launcher-preopened read-only delivery,
- the later worker gets exactly one declared writable derivative sink slot,
- that slot starts as a launcher-precreated empty regular file,
- that slot stays write-only and forward-only with no worker readback, seek, or truncate,
- and the launcher/broker still collects + remeasures bytes from that slot before the receipt names the authoritative derivative locator.
- the next cut refines the exact append-open / append-only-protected posture required when that slot is a seekable regular file on FreeBSD.

## Why this cut is worth making now

Without this decision, the archive would still leave one quiet implementation guess inside the first coding target:

- input authority would be one object,
- output surface would be one declared slot,
- but the worker could still quietly treat that slot as mutable scratch state.

This page keeps the first coding target smaller and more reviewable: one preserved input object, one empty declared output slot, one forward-only worker write path, one broker collection step, one authoritative derivative.

## What remains open

Still intentionally open:

- exact launcher mechanics for zero-length sink creation and cleanup,
- whether some later explicit lane should admit bounded mutable output staging,
- and whether a later explicit lane should admit multiple declared derivative slots with richer per-slot I/O posture.

Last updated: 2026-03-28r476
