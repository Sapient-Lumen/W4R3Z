# Removable-media local fallback post-detach derivative slot stays append-open and append-only-protected on seekable file delivery

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, digest-bound continuity between the preserved capture and the later worker-visible object, launcher-preopened read-only delivery instead of later path re-open, broker-collected derivative egress instead of trusting `/work/output/...` as authoritative derivative identity, one declared writable derivative slot with no extra worker result surface, and an empty launcher-precreated derivative file with no worker readback or truncate.

This page closes the next smaller execution seam:

> **if the first lane keeps a seekable regular-file derivative sink on FreeBSD, the archive must say how that remains forward-only without pretending `CAP_WRITE` alone is enough on a seekable file.**

See also:
- ADR: `adrs/ADR-0335-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`
- previous cut: `docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The archive already says the later worker gets one declared derivative sink and that the worker cannot read back or truncate that sink.
But one practical ambiguity remains:
**what exact FreeBSD-shaped delivery posture keeps a seekable regular-file sink forward-only enough without silently lying about required rights?**

Without a tighter contract, implementations can still drift between incompatible stories:

- keep a regular-file sink but quietly re-add `CAP_SEEK` with no explanation,
- switch to a stream-only sink and force path-shaped sanitizers through a broader launcher redesign,
- or keep the regular-file sink while making the worker-visible descriptor append-open and append-only-protected, keeping `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL` out, and treating any `CAP_SEEK` there as seekable-file ballast rather than rewrite authority.

The smaller honest answer is:
**the first lane keeps the regular-file sink, but it is append-open, append-only-protected, no-readback, no-truncate, and no-fcntl-clear while the worker runs.**

The archive now says the declared derivative slot stays append-open and append-only-protected on seekable file delivery in the first lane.

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The declared derivative slot stays empty and regular-file-shaped

The later worker may still emit a sanitized derivative.
The canonical slot remains `/work/output/invoice.sanitized.pdf`, and it still begins as a launcher-precreated empty regular file.
This cut does **not** widen the lane into a directory-shaped outbox or extra result surface.

### 2) The launcher hands that sink to the worker append-open

The later worker must not create or reopen the sink itself.
Instead, the launcher preopens the one declared sink `O_APPEND` (or implementation-equivalent append-open posture) before later-worker execution starts.
The worker-visible pathname remains compatibility plumbing; the already-opened sink descriptor is the real authority object.

### 3) The sink stays append-only-protected while the worker runs

If the first lane keeps a seekable regular file as the sink, the launcher must keep it append-only-protected during worker execution (`UF_APPEND` or equivalent host-enforced append-only posture).
The worker still gets no readback or truncate authority.
The worker also gets no `CAP_FCNTL`, so it cannot clear the append-open posture itself.

### 4) Any `CAP_SEEK` on that sink is implementation ballast, not rewrite authority

FreeBSD's Capsicum documentation is explicit that for files and other seekable objects, `CAP_SEEK` may also be required for write-class operations.
So the canonical later-worker map now carries `CAP_SEEK` alongside `CAP_WRITE` on this one sink.
That is not a policy widening.
It is the archive becoming honest about a seekable regular file on FreeBSD.
The *design* boundary remains: append-open, append-only-protected, no readback, no truncate, no `CAP_FCNTL`, one declared sink, broker collection before authority.

## Canonical first-cut example stack

The append-open-derivative-slot cut is now explicit too:

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
- that slot stays a launcher-precreated empty regular file,
- that slot is handed over append-open and append-only-protected for the worker lifetime,
- any `CAP_SEEK` on that sink is seekable-file ballast rather than rewrite authority,
- and the launcher/broker still collects + remeasures bytes from that sink before the receipt names the authoritative derivative locator.

## Why this cut is worth making now

Without this decision, the archive would still contain a quiet platform mismatch inside the first coding target:

- the sink would be a seekable regular file,
- the worker would be expected to write it,
- but the canonical example would still pretend `CAP_SEEK` simply stays out.

This page keeps the first coding target both small **and** implementable: one preserved input object, one append-open append-only-protected output sink, one worker write path, one broker collection step, one authoritative derivative.

## What remains open

Still intentionally open:

- whether a later explicit lane should switch derivative egress to a pipe/stream sink instead of a seekable file,
- exact launcher mechanics for append-only protection setup/clear-down,
- and whether some later explicit lane should admit richer mutable output staging.

Last updated: 2026-03-28r476
