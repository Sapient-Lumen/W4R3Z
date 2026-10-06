# Removable-media local fallback post-detach later-tool code enters capability mode before mainline and stays there

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, digest-bound continuity between the preserved capture and the later worker-visible object, launcher-preopened read-only delivery instead of later path re-open, broker-collected derivative egress instead of trusting `/work/output/...` as authoritative derivative identity, one declared writable derivative slot with no extra worker result surface, and an append-open append-only-protected seekable-file sink that still keeps readback/truncate/fcntl-clear out.

This page closes the next smaller execution seam:

> **the first lane already says later work gets only a tiny reviewed capability set; it must also say that actual later tool code starts only after capability mode is entered, not before.**

See also:
- ADR: `adrs/ADR-0336-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
- previous cut: `docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- post-detach delivery floor: `docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`

## Why this needs a hard decision

The archive already says the later worker gets one preserved input object and one declared derivative sink.
It already says those objects are preopened and rights-limited.
But one honest implementation question remained open:
**when does the worker actually enter capability mode relative to later tool mainline code?**

If that stays vague, an implementation can still smuggle ambient authority through startup:

- dynamic plugin or helper discovery before capability mode entry,
- late absolute-path opens during wrapper glue,
- or “we only entered capability mode once the interesting part started” folklore.

That is exactly the kind of drift the removable-media line has been cutting away.
The smaller honest answer is:
**later tool mainline code begins only after the launcher or its approved shim has entered capability mode on the reviewed preopened set.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Capability mode entry happens before later tool mainline code

The launcher or its approved shim must finish opening and rights-limiting the exact preserved-subject input object, the one declared derivative sink, and any other explicitly admitted helper descriptors before handing control to the later classify/scan/sanitize tool code.
Later tool mainline execution starts only after that `cap_enter()` boundary.

### 2) Descendants stay inside that boundary

Capability mode is not an optional launcher optimization in this lane.
Descendants inherit it, and it may not be cleared.
So the first-lane story is no longer “the launcher probably preopened enough stuff”; it is “the later worker and its descendants stay capability-mode-bounded once tool code starts.”

### 3) Ambient late path discovery stays out

After `cap_enter()`, no ambient absolute-path opens remain part of this first lane.
If some relative `openat()` behavior is still needed, it must stay beneath already preopened descriptors and must not widen authority beyond the reviewed preopen map.

### 4) Tools that cannot run on the preopened capability set stay out unless a later wrapper/broker cut admits them

This is the hard product decision in this page.
The archive does **not** widen the first removable-media lane just to keep convenient path-hungry tools.
If a sanitizer/classifier cannot run after capability-mode entry on the reviewed preopened set, it is not in the first lane unless a later explicit wrapper/broker contract earns it.

## Canonical first-cut example stack

The capability-mode-entry cut is now explicit too:

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
- the later worker gets exactly one declared append-open append-only-protected derivative sink slot,
- the launcher or its approved shim enters capability mode before handing control to later tool code,
- descendants inherit that mode and may not clear it,
- ambient absolute-path opens after `cap_enter()` stay out,
- and tools that cannot run on the preopened capability set stay out unless a later explicit wrapper/broker contract earns them back.

## Why this cut is worth making now

Without this decision, the archive would still contain one implementation-sized escape hatch inside the first coding target:

- the post-detach worker would look descriptor-bounded on paper,
- but actual later tool code could still start outside capability mode,
- and startup-time path discovery would quietly become the real authority story.

This page keeps the first coding target both small **and** honest: the reviewed preopen map becomes real before later tool mainline begins.

## What remains open

Still intentionally open:

- exact launcher mechanics (`fexecve()`, already-linked jump, or another equivalent) for satisfying this rule,
- which later explicit wrappers/brokers are worth admitting for tools that cannot meet the first-lane floor directly,
- and whether a later explicit lane should admit richer helper/service ecosystems after capability-mode entry.

Last updated: 2026-03-28r478
