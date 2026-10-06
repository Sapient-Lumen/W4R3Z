# ADR-0332: Removable-media local fallback post-detach derivative egress stays broker-collected and worker outbox paths stay non-authoritative

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `spec/preopen.map.schema.json`, `adrs/ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`, `adrs/ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`

## Context

The recent removable-media first-cut stack already made the input side of post-detach execution explicit:

- authoritative quarantine-store commit before detach,
- fresh worker after detach,
- single-object store-opaque delivery,
- digest-bound continuity to the preserved capture,
- and launcher-preopened read-only delivery instead of path re-open folklore.

That leaves the output side underspecified.
The current canonical receipt still risks implying that a later sanitized derivative is just “whatever bytes remained at `/work/output/...`”.
Without a tighter contract, implementations can drift between incompatible stories:

1. treat the worker-visible output path as the authoritative derivative identity,
2. let the later worker write directly into a wider authoritative-store namespace,
3. or keep worker output disposable, have the launcher/broker collect it after worker execution, remeasure it, and only then name the authoritative derivative in the receipt.

Only the third answer keeps the first lane aligned with DeriveBSD’s broader brokered-authority posture.

## Decision

For the first host-local removable-media fallback lane:

1. **Receipt-visible derivative egress stays broker-collected.**
   - Later classify/scan/sanitize work may emit derivative bytes only into launcher-prepared disposable outbox sink objects (or an equivalent bounded scratch sink).
   - The worker-visible outbox path is not the authoritative identity of the derivative.

2. **Authoritative derivative identity is assigned only after collection and remeasurement.**
   - After later worker execution completes, the launcher/broker must collect the derivative bytes from the disposable outbox sink, compute the authoritative digest, and then commit or name the authoritative derivative locator recorded in `content.import.receipt`.
   - The receipt may preserve the worker-visible outbox path as execution evidence, but not as authority.

3. **Writable authoritative-store namespace stays out.**
   - The later worker may not receive writable directory authority to the authoritative quarantine store or a broader receipt-visible output namespace.
   - The first lane keeps writable output authority on prepared sink objects, not ambient directory creation/rename/rebind rights.

4. **The canonical example stack must say this explicitly.**
   - The canonical removable-media local-ingest examples must distinguish the worker-visible outbox sink path from the authoritative stored derivative locator.
   - The later-worker `preopen.map` may show one read-only preserved-subject file plus one launcher-precreated writable derivative sink file, while keeping authoritative-store directory authority out.

## Consequences

### Positive

- The first implementation floor becomes more honest on the output side: receipt-visible derivatives are no longer “whatever the worker left in `/work/output`”.
- This keeps authoritative result identity in the same brokered/receipted pattern as preserved input authority.
- Support/export can reconstruct both the execution sink path and the authoritative stored derivative without reading broker folklore into a scratch path.

### Negative / costs

- Launchers/brokers must own one more explicit step: collect and remeasure later-worker outputs before the receipt is final.
- Canonical examples now need to carry both worker-visible outbox evidence and authoritative derivative locator data.

## Rejected alternatives

- **Treat `/work/output/...` as the authoritative derivative by convention.** Rejected because disposable worker paths are execution plumbing, not durable identity.
- **Let the later worker write directly into authoritative store.** Rejected because that widens post-detach write authority beyond the first lane’s carefully brokered shape.
- **Force one exact collection implementation now.** Rejected because the archive only needs the contract and evidence shape in the first cut, not one mandatory launcher design.

## Follow-up

- Update the canonical removable-media local-ingest examples so sanitized derivative output leaves through a launcher-precreated disposable outbox sink, is broker-collected afterward, and records a separate authoritative derivative locator in the receipt.
- Add a drift check that fails if the examples slide back toward treating worker outbox paths as authoritative derivative identity.

## Links

- boundary doc: `docs/742-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`
- previous cut: `adrs/ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`
