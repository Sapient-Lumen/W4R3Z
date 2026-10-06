# ADR-0333: Removable-media local fallback post-detach derivative egress stays single declared slot and no extra worker result surface

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `spec/preopen.map.schema.json`, `adrs/ADR-0331-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`, `adrs/ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`

## Context

The recent removable-media first-cut stack already made post-detach input and output authority much smaller:

- one preserved selected subject committed into authoritative quarantine store before detach,
- one fresh post-detach worker,
- one launcher-preopened read-only input object,
- and broker-collected derivative egress instead of trusting `/work/output/...` as authoritative identity.

That still leaves one practical output ambiguity.
The current canonical example names one writable sink path, but it does not yet state whether that sink is merely an example or the actual reviewed extent of worker-visible result surface.
Without a tighter contract, implementations can drift between incompatible stories:

1. treat one sink as normal but quietly tolerate additional ad hoc output files,
2. let the worker pick among multiple writable sink names and trust the broker to guess which one matters,
3. or declare one reviewed derivative slot in advance and require any receipt-visible derivative to come from that slot while extra worker result surface stays out of lane.

Only the third answer keeps the first lane small enough to build without turning the outbox into a hidden namespace protocol.

## Decision

For the first host-local removable-media fallback lane:

1. **Post-detach derivative egress stays single declared slot.**
   - The canonical post-detach worker receives exactly one declared writable derivative sink slot.
   - In the first lane, the canonical slot id is `sanitized_derivative_slot` and it maps to `/work/output/invoice.sanitized.pdf`.

2. **Any receipt-visible derivative must come from the declared slot.**
   - The authoritative derivative named in `content.import.receipt` must be the broker-collected, remeasured result of that declared slot.
   - The worker does not get to mint receipt-visible derivatives by picking alternate filenames or extra sink objects.

3. **Extra worker result surface stays out.**
   - The first lane does not admit multiple writable derivative slots, directory-shaped outboxes, or worker-chosen output discovery.
   - If a transform needs plural authoritative outputs, that must return as a later explicit lane instead of widening the first removable-media baseline.

4. **The canonical examples and preopen map must say this explicitly.**
   - `device.attach.grant`, `content.import.plan`, `device.detach.receipt`, `content.import.receipt`, and the post-detach `preopen.map` example must all carry the single-declared-slot rule.
   - The later-worker `preopen.map` must continue to show one read-only preserved-subject handle plus one writable derivative sink handle, and no extra writable result surface.

## Consequences

### Positive

- The first implementation floor becomes easier to reason about: one preserved input object, one declared output slot, one broker collection step.
- Support and forensics can tie the authoritative derivative back to a reviewed slot id instead of inferring intent from whatever remained in `/work/output`.
- This keeps the first removable-media lane aligned with DeriveBSD’s existing single-selected-subject discipline instead of reintroducing multi-object ambiguity on the egress side.

### Negative / costs

- Some legitimate transforms that naturally emit plural artifacts need a later explicit lane instead of piggybacking on this first baseline.
- Canonical examples and receipts now need to carry one more small binding field for the declared derivative slot.

## Rejected alternatives

- **Treat one sink as conventional but allow other worker output files to exist silently.** Rejected because the broker would then have to guess which worker result actually mattered.
- **Let the worker choose among multiple writable sink names.** Rejected because that quietly reintroduces namespace-shaped result authority after we already removed path authority from the input side.
- **Force a fully generic multi-output manifest now.** Rejected because that is a broader RFC-sized lane, not the next small implementation floor.

## Follow-up

- Update the canonical removable-media local-ingest examples so the post-detach worker names exactly one declared derivative slot and the receipt binds the authoritative derivative back to that slot.
- Add a drift check that fails if the examples or docs slide back toward extra writable result surface or unnamed worker-selected derivative authority.

## Links

- boundary doc: `docs/743-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`
- previous cut: `adrs/ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`
