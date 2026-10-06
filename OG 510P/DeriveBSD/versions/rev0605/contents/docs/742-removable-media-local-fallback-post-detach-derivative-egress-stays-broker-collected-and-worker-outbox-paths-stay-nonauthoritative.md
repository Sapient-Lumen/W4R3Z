# Removable-media local fallback post-detach derivative egress stays broker-collected and worker outbox paths stay non-authoritative

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, digest-bound continuity between the preserved capture and the later worker-visible object, and launcher-preopened read-only delivery instead of later path re-open.

This page closes the next smaller execution seam:

> **it is not enough that post-detach later work receives one bounded read-only input object; receipt-visible derivative output must also stay broker-collected, and worker outbox paths must stay non-authoritative.**

See also:
- ADR: `adrs/ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`
- previous cut: `docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The archive already says the later worker gets one read-only preserved subject through a bounded post-detach delivery.
But one practical output ambiguity remains:
what is allowed to become authoritative when that worker emits a sanitized derivative?

Without a tighter contract, implementations can still drift between incompatible stories:

- let the worker write a file under `/work/output` and implicitly treat that scratch path as the authoritative derivative,
- let the worker write directly into a broader authoritative-store namespace “for convenience”,
- or keep later-worker output on launcher-prepared disposable sink objects and let the launcher/broker collect + remeasure those bytes before the receipt names the authoritative derivative.

The smaller honest answer is:
**post-detach derivative egress stays broker-collected, and any worker outbox path remains execution evidence rather than authority.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Later-worker derivative output leaves through launcher-prepared disposable sink objects

If later classify/scan/sanitize work emits a derivative that matters to the receipt, the later worker may write it only to launcher-prepared disposable sink objects or an equivalent bounded outbox.
The current canonical example uses one precreated writable outbox file for the sanitized derivative.

### 2) The worker outbox path is execution plumbing, not authoritative identity

A worker-visible sink path such as `/work/output/invoice.sanitized.pdf` may still exist so ordinary tools can emit bytes.
But that outbox path is not the authoritative identity of the derivative.
It is merely where the later worker left bytes for collection.

### 3) The launcher/broker collects and remeasures before the receipt names the derivative

After later-worker execution ends, the launcher/broker must collect the derivative bytes from the disposable outbox sink, compute the authoritative digest, and only then commit or name the authoritative derivative locator recorded in `content.import.receipt`.
That keeps the receipt-visible derivative identity on explicit brokered evidence instead of worker scratch folklore.

### 4) Writable authoritative-store namespace stays out

The later worker may not receive writable directory authority to the authoritative quarantine store or a broader receipt-visible output namespace.
In the current canonical example, the later-worker `preopen.map` may show:

- one read-only preserved selected subject file, and
- one launcher-precreated writable derivative sink file.

But it may not show authoritative-store directory creation or browse authority.

### 5) Exact collection mechanics stay open

The archive still does not force one exact collection implementation for the first cut.
A launcher-owned writable file sink, a bounded scratch sink that the launcher later seals and digests, or another equivalent brokered pattern all fit if they preserve the same contract:

- read-only single-object input,
- worker-visible output sink is disposable plumbing only,
- launcher/broker remeasures after worker execution,
- and the receipt names a separate authoritative derivative locator.

## Canonical first-cut example stack

The broker-collected derivative-egress cut is now explicit too:

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
- the later worker writes receipt-visible derivative bytes only to launcher-prepared disposable outbox sink objects,
- the worker outbox path is evidence of execution plumbing rather than the authoritative derivative identity,
- and the launcher/broker collects + remeasures the derivative before the receipt names its authoritative stored locator.

## Why this cut is worth making now

Without this decision, the archive would still leave the output side of the first coding target half-ambient:

- preserved input authority would be explicit and brokered,
- but derivative result authority would still quietly depend on whatever scratch path happened to survive under `/work/output`.

This page keeps the first coding target smaller and more aligned with DeriveBSD’s existing capability posture: one bounded read-only input object, one bounded disposable output sink, and one brokered collection step before a derivative becomes receipt authority.

## What remains open

Still intentionally open:

- exact broker collection mechanics for one or more deterministic derivative outputs,
- how to summarize “worker outbox evidence + authoritative derivative locator” compactly in trusted UI,
- and whether some later explicit lane should admit bounded multi-sink output maps for more complex transforms.

Last updated: 2026-03-28r473
