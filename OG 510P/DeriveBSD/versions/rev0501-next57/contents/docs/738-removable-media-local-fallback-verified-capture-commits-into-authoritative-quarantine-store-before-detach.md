# Removable-media local fallback verified capture commits into authoritative quarantine store before detach

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, and preserved capture instead of in-place rewrite.

This page closes the next smaller lifetime seam:

> **the verified capture may not remain authoritative only under disposable `/work`; before detach it must commit into authoritative quarantine store, and later work must read that stored capture or a read-only projection of it.**

See also:
- ADR: `adrs/ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`
- previous cut: `docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`
- origin/quarantine spine: `docs/280-origin-labels-and-quarantine-attributes.md`
- metadata authority boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- query/index guidance: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Why this needs a hard decision

The archive already says “capture first”, “detach early”, “restart in a fresh worker”, and “preserve the exact capture.”
But if the preserved capture still lives only at `/work/capture/subject.bin`, then the evidence story still depends on disposable scratch lifetime.

That would leave first implementations guessing:

- is `/work/capture/...` supposed to survive worker restart,
- does some hidden host process have to save it later,
- or is the archive accidentally treating a scratch path as durable evidence?

The first local fallback needs the smaller honest answer:
**verified capture must commit into authoritative quarantine store before detach, and later work must read the stored preserved capture rather than the old scratch path.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Verified capture commits into authoritative quarantine store before detach

Once capture verifies against the planned selected-subject digest, that exact captured subject must be committed into authoritative quarantine store before `device.detach.receipt` and before later work continues.

### 2) `/work/capture/...` becomes staging only, not lasting authority

A pre-detach worker may still stage bytes under `/work` while capture runs.
But that staging path is not the authoritative preserved-capture address after verification.

### 3) Later work reads the stored preserved capture or a read-only projection of it

The fresh post-detach worker may consume:

- the authoritative preserved-capture locator directly, or
- a read-only worker-local projection of that stored capture.

Either way, later classify/scan/sanitize work is now visibly downstream of stored preserved evidence rather than silently downstream of pre-detach scratch.

### 4) Canonical receipts name both authority and projection when both exist

The canonical `content.import.receipt` example now names:

- the authoritative stored preserved capture, and
- the later worker projection path when that projection exists.

That keeps detached support/export honest about which path is the durable evidence anchor and which path is only execution plumbing.

### 5) Exact backend layout stays open in the first cut

The archive does not yet force one exact quarantine-store layout or projection mechanism.
It does force the contract shape: authoritative quarantine-scoped preserved capture before detach, and later work reads that stored copy rather than treating disposable scratch as authority.

## Canonical first-cut example stack

The authoritative-store cut is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- one selected regular file is staged and verified,
- the verified capture commits into authoritative quarantine store before detach,
- the host then detaches the medium and restarts later work in a fresh worker,
- later work reads a read-only projection of the stored preserved capture,
- the authoritative stored capture remains exact evidence,
- and sanitized output is still a separate derivative from that preserved capture.

## Why this cut is worth making now

Without this decision, the archive still pays repeated implementation tax:

- the preserved-capture cut would still hide authority in a scratch path,
- post-detach worker reset would still depend on invisible persistence rules for `/work`,
- and detached support/export would still have to guess which pathname was the real preserved artifact.

This page keeps the first coding target small and honest: capture, verify, commit preserved evidence into authoritative quarantine store, detach, restart, read the stored copy, and derive later outputs separately.

## What remains open

Still intentionally open:

- exact quarantine-store backend layout,
- exact projection/mount mechanics for the fresh later worker,
- whether richer future lanes should preserve broader staged sets than one selected file,
- and how trusted UI should summarize “stored original + projected execution path + later derivative” compactly.

Last updated: 2026-03-28r469
