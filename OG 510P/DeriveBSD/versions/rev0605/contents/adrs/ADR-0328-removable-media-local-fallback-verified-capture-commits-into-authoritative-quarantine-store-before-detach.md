# ADR-0328: Removable-media local fallback verified capture commits into authoritative quarantine store before detach

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/484-origin-label-authority-and-anti-laundering-boundary.md`, `adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`, `adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`, `adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`, `adrs/ADR-0327-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`

## Context

The recent removable-media first-cut stack already made several expensive choices explicit:

- one selected subject only,
- regular-file-only selected subjects,
- current-presence hints stay evidence-only,
- capture-first into `/work`,
- early detach after verified capture,
- a fresh worker after detach,
- and preserved capture instead of in-place rewrite.

That leaves one practical lifetime ambiguity unresolved:
if the verified capture is still only a file under disposable `/work`, then the archive is preserving evidence in exactly the kind of scratch execution space that later cuts were trying to make non-authoritative.

Implementations would then drift between three incompatible stories:

1. keep the preserved capture only in pre-detach scratch,
2. copy it ad hoc into some later location after detach, or
3. silently treat an ephemeral worker path as if it were already durable evidence.

That is too vague for a first implementation and too weak for detached support/export reasoning.

## Decision

For the first host-local removable-media fallback lane:

1. **Verified capture must commit into authoritative quarantine store before detach.**
   - Once capture verifies against the planned selected-subject digest, the preserved capture stops being only a disposable worker file.
   - It must be committed into an authoritative quarantine store object before `device.detach.receipt` and before later work continues.

2. **Later work reads the stored preserved capture, not the old scratch path.**
   - Post-detach classify/scan/sanitize work must read the stored preserved capture and may consume either:
     - a digest-addressed authoritative store locator, or
     - a read-only projection of that stored capture into the fresh later worker.
   - It may not keep `/work/capture/...` as the authoritative evidence address.

3. **Receipts must name the authoritative preserved-capture locator.**
   - The canonical `content.import.receipt` example must record the authoritative preserved-capture locator/path.
   - If a later worker uses a projected local pathname, that projection is supplementary and must stay visibly distinct from the authoritative locator.

4. **Store backend mechanics remain implementation detail in the first cut.**
   - The archive does not yet force one exact backend layout.
   - It does require the contract shape: authoritative, quarantine-scoped, digest-addressed preserved capture before detach; later workers read a read-only stored copy or projection rather than a mutable disposable scratch artifact.

## Consequences

### Positive

- The preserved-capture cut becomes honest: preserved evidence no longer depends on disposable worker lifetime.
- The post-detach worker-reset cut becomes cleaner: later work does not need secret continuity with pre-detach scratch space.
- Detached support/export can point at a stable preserved-capture locator instead of reconstructing which scratch path “used to be important.”
- This composes with the archive’s accepted `content.origin` / xattr-pointer / authoritative-CAS posture instead of inventing a removable-media-only exception.

### Negative / costs

- The first implementation now needs a small commit boundary between verified capture and detach.
- Canonical examples need to distinguish authoritative stored location from a later worker projection path.

## Rejected alternatives

- **Keep `/work/capture/...` authoritative after detach.** Rejected because it contradicts the disposable-worker boundary and turns scratch lifetime into hidden authority.
- **Delay authoritative commit until after later sanitize/scan succeeds.** Rejected because the exact preserved imported subject should survive later-tool failure.
- **Invent a removable-media-specific evidence vault now.** Rejected because the archive already has broader quarantine/CAS authority patterns; the first cut only needs to commit into that broader family, not mint a new subsystem.

## Follow-up

- Update the canonical removable-media local-ingest examples so preserved capture is committed into authoritative quarantine store before detach.
- Add a drift check that fails if the canonical examples slide back toward disposable `/work/capture/...` authority after the preserved-capture cut.

## Links

- boundary doc: `docs/738-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`
- previous cut: `adrs/ADR-0327-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`
