# ADR-0329: Removable-media local fallback post-detach preserved-capture delivery stays single-object and store-opaque

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/180-capability-mode-dynamic-linking.md`, `docs/294-oblivious-sandboxing-launchers.md`, `adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`, `adrs/ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`

## Context

The recent removable-media first-cut stack already made several expensive choices explicit:

- capture first,
- early detach after verified capture,
- a fresh worker after detach,
- preserved capture instead of in-place rewrite,
- and authoritative quarantine-store commit before detach.

That still leaves one practical authority seam open:
if the fresh later worker gets a browseable view of authoritative quarantine store just to read one preserved capture, then the archive quietly widens from “one selected imported subject” into “ambient access to stored quarantined evidence.”

Implementations would then drift between incompatible stories:

1. mount or preopen the whole store subtree in the later worker,
2. reveal a direct store pathname and let later tools reopen around it,
3. or attenuate delivery to only the preserved selected subject.

Only the third answer matches the archive’s capability-brokered and least-authority posture.

## Decision

For the first host-local removable-media fallback lane:

1. **Post-detach preserved-capture delivery stays single-object only.**
   - The fresh later worker may receive only the preserved selected subject needed for classify/scan/sanitize.
   - It may receive that subject through a brokered read handle or a synthetic worker-local single-object projection path.
   - It may not receive a browseable authoritative-store directory/subtree view in this first cut.

2. **The authoritative store locator stays evidence, not worker namespace.**
   - The canonical stored locator remains important in receipts and support/export reasoning.
   - But later execution must not depend on reopening that locator through ambient namespace access.
   - Worker-local execution paths are synthetic plumbing, visibly distinct from the authoritative locator.

3. **Delivery is read-only and capability-shaped.**
   - The later worker’s read access to the preserved capture must be attenuated to read-only.
   - The worker should not gain broader path-discovery authority as a side effect of “reading the preserved subject.”

4. **Exact delivery mechanism stays open in the first cut.**
   - The archive does not force one exact mechanism yet.
   - A brokered read handle, a launcher-preopened descriptor, or a synthetic single-object projection are all acceptable shapes if they preserve the same authority boundary.

## Consequences

### Positive

- The first implementation target gets smaller and more honest: one preserved subject enters later work, not a quarantine-store namespace.
- This composes directly with Capsicum-first launchers and preopened-handle workflows already favored elsewhere in the archive.
- Support/export can still name the authoritative stored locator without making that locator ambient execution authority.

### Negative / costs

- Launchers/adapters now need one more explicit handoff step between preserved storage and later tools.
- Canonical examples must distinguish receipt-visible authoritative locator from worker-visible synthetic delivery path.

## Rejected alternatives

- **Expose a browseable authoritative-store subtree to the later worker.** Rejected because it widens authority from one reviewed import subject into general quarantine-store discovery.
- **Let later tools reopen the direct store pathname themselves.** Rejected because it turns receipt evidence into ambient namespace authority.
- **Invent a new removable-media-only broker subsystem now.** Rejected because existing capability-shaped launcher/handle patterns are enough for the first cut.

## Follow-up

- Update the canonical removable-media local-ingest examples so post-detach delivery is explicitly single-object only and the authoritative locator stays receipt-visible rather than worker-browseable.
- Add a drift check that fails if the canonical examples slide back toward browseable authoritative-store exposure after detach.

## Links

- boundary doc: `docs/739-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`
- previous cut: `adrs/ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`
