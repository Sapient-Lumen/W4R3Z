# ADR-0330: Removable-media local fallback post-detach single-object delivery stays digest-bound and receipt-evidenced

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `adrs/ADR-0328-removable-media-local-fallback-verified-capture-commits-into-authoritative-quarantine-store-before-detach.md`, `adrs/ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`

## Context

The recent removable-media first-cut stack already made several expensive choices explicit:

- capture first,
- authoritative quarantine-store commit before detach,
- fresh worker after detach,
- preserved capture instead of in-place rewrite,
- and single-object store-opaque post-detach delivery.

That still leaves one implementation seam open:
if the later worker receives only `/work/input/preserved-subject.bin`, what proves that this worker-visible delivery is the same preserved capture named by the authoritative store locator and the subject digest?

Without a tighter contract, implementations can drift between incompatible stories:

1. trust the synthetic path name alone,
2. trust that the launcher probably pointed it at the right object,
3. or require the delivered object to be digest-bound to the preserved capture and record that binding in receipts.

Only the third answer keeps the worker-visible projection from becoming a soft alias with ambiguous lineage.

## Decision

For the first host-local removable-media fallback lane:

1. **Post-detach single-object delivery stays digest-bound.**
   - Before later classify/scan/sanitize work starts, the launcher/broker must bind the worker-visible delivery object to the exact preserved-capture digest.
   - The worker-visible projection path or delegated read handle is only plumbing; the preserved-capture digest remains the authority anchor.

2. **Later work may proceed only after the binding matches the preserved capture.**
   - The delivered object must match the preserved selected subject digest already recorded in the plan/store/receipt chain.
   - Digest mismatch fails closed before later work begins.

3. **The receipt must say that this happened.**
   - The canonical `content.import.receipt` must record that the worker-visible single-object delivery was digest-bound to the preserved capture.
   - The receipt-visible authoritative locator remains evidence, and the worker-visible path remains synthetic plumbing.

4. **Exact mechanism stays open in the first cut.**
   - A preverified store projection, delegated read-only descriptor, or launcher-time re-hash are all acceptable first-cut shapes if they preserve the same contract:
     - one preserved subject only,
     - read-only,
     - digest-bound to the preserved capture before later ops,
     - and receipt-evidenced.

## Consequences

### Positive

- The first implementation floor becomes more testable: later work cannot silently consume "whatever appeared at `/work/input/preserved-subject.bin`".
- This keeps worker-visible delivery subordinate to the authoritative digest chain instead of turning synthetic paths into soft authority.
- Support/export can reconstruct the exact continuity story from plan, detach receipt, and import receipt without reading implementation folklore into the path.

### Negative / costs

- Launchers/adapters must perform and record one more exact check before later work begins.
- Canonical examples now need to distinguish authoritative locator evidence, worker-visible delivery path, and delivery-to-source digest binding.

## Rejected alternatives

- **Treat the worker-visible projection path as self-authenticating.** Rejected because synthetic execution paths are convenience plumbing, not stable authority.
- **Rely on store opacity alone.** Rejected because opaque delivery still leaves "did the worker get the right object?" half-implicit.
- **Force one exact broker implementation now.** Rejected because the archive only needs the binding/evidence contract in the first cut, not one mandatory transport mechanism.

## Follow-up

- Update the canonical removable-media local-ingest examples so post-detach delivery is explicitly digest-bound to the preserved capture and the receipt records that binding.
- Add a drift check that fails if the canonical examples slide back toward path-only synthetic delivery without digest-bound evidence.

## Links

- boundary doc: `docs/740-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`
- previous cut: `adrs/ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`
