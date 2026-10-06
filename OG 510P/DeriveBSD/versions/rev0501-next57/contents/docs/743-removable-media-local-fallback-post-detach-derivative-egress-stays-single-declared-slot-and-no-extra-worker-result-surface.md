# Removable-media local fallback post-detach derivative egress stays single declared slot and no extra worker result surface

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, digest-bound continuity between the preserved capture and the later worker-visible object, launcher-preopened read-only delivery instead of later path re-open, and broker-collected derivative egress instead of trusting `/work/output/...` as authoritative derivative identity.

This page closes the next smaller execution seam:

> **it is not enough that later-worker derivative egress stays broker-collected; in the first lane, that egress must also stay on one declared writable slot, and extra worker result surface must stay out.**

See also:
- ADR: `adrs/ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`
- previous cut: `docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The archive already says the later worker gets one read-only preserved subject and emits any receipt-visible derivative through broker-collected disposable sink objects.
But one practical ambiguity remains:
**how much result surface is the later worker actually allowed to have?**

Without a tighter contract, implementations can still drift between incompatible stories:

- show one writable sink in the example but quietly tolerate other output files,
- let the worker choose among multiple sink names and rely on launcher folklore to decide which one mattered,
- or declare one reviewed derivative slot in advance and require any receipt-visible derivative to come only from that slot while extra worker result surface stays out.

The smaller honest answer is:
**post-detach derivative egress stays single declared slot, and extra worker result surface stays out in the first lane.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Later-worker derivative egress stays on one declared writable slot

The later worker may still emit a sanitized derivative, but the first lane now declares exactly one writable derivative sink slot in advance.
In the canonical example, that slot id is `sanitized_derivative_slot` and it maps to `/work/output/invoice.sanitized.pdf`.

### 2) Any receipt-visible derivative must come from that declared slot

The launcher/broker may still collect and remeasure derivative bytes after worker exit.
But the authoritative derivative named in `content.import.receipt` must now be the collected result of the declared slot.
The worker does not get to create alternate receipt-visible derivatives by picking other filenames or extra sinks.

### 3) Extra worker result surface stays out in the first lane

The first removable-media lane does not admit:

- multiple writable derivative slots,
- directory-shaped outboxes,
- worker-chosen output discovery,
- or plural authoritative derivatives from one post-detach sanitize step.

If a future transform needs plural authoritative outputs, that must return as a later explicit lane instead of quietly widening this one.

### 4) The preopen map must stay tiny on the output side too

The post-detach `preopen.map` may still show:

- one read-only preserved selected subject file, and
- one declared writable derivative sink file.

But it may not quietly accumulate additional writable sink entries or writable directory authority.

## Canonical first-cut example stack

The single-declared-derivative-slot cut is now explicit too:

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
- the later worker writes receipt-visible derivative bytes only to one declared launcher-prepared writable sink slot,
- extra worker result surface stays out in the first lane,
- and the launcher/broker collects + remeasures the bytes from that declared slot before the receipt names the authoritative derivative locator.

## Why this cut is worth making now

Without this decision, the archive would still leave one quiet implementation guess in the first coding target:

- input authority would be one object,
- output egress would be broker-collected,
- but the number and identity of possible worker result surfaces would still be half-implied by example convention.

This page keeps the first coding target smaller and more reviewable: one preserved input object, one declared writable derivative slot, one broker collection step, one authoritative derivative.

## What remains open

Still intentionally open:

- exact launcher mechanics for creating the declared writable sink slot,
- whether a later explicit lane should admit multiple declared derivative slots for deterministic transforms,
- and how trusted UI should summarize “declared slot id” versus “authoritative stored locator” without clutter.

Last updated: 2026-03-28r474
