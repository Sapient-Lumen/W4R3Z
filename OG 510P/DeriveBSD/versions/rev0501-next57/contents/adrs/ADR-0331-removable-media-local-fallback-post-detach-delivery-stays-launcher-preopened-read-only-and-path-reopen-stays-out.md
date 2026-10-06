# ADR-0331: Removable-media local fallback post-detach delivery stays launcher-preopened read-only and path re-open stays out

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `spec/preopen.map.schema.json`, `adrs/ADR-0329-removable-media-local-fallback-post-detach-preserved-capture-delivery-stays-single-object-and-store-opaque.md`, `adrs/ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`

## Context

The recent removable-media first-cut stack already made several expensive choices explicit:

- authoritative quarantine-store commit before detach,
- fresh worker after detach,
- single-object store-opaque post-detach delivery,
- and digest-bound continuity between the preserved capture and the later worker-visible object.

That still leaves one practical execution seam open:
how should the later worker *hold* that one delivered object once continuity is established?

Without a tighter contract, implementations can still drift between incompatible stories:

1. bind the digest, then let the worker reopen a path later,
2. hand the worker one launcher-preopened read-only object and treat any synthetic path as compatibility-only plumbing,
3. or mount/preopen a broader namespace so tools can reopen things by habit.

Only the second answer keeps the first lane aligned with the archive's existing launcher/preopen posture without widening post-detach authority back into path reopen folklore.

## Decision

For the first host-local removable-media fallback lane:

1. **Post-detach delivery stays launcher-preopened read-only or equivalent.**
   - Before later classify/scan/sanitize work begins, the launcher/broker must acquire one read-only handle for the preserved selected subject (or an equivalent already-bound single-object delivery primitive).
   - That already-bound object, not a later path lookup, is the authority anchor for worker execution.

2. **Any worker-visible path is compatibility-only.**
   - A synthetic path such as `/work/input/preserved-subject.bin` may still exist for compatibility with off-the-shelf tools.
   - But that path names the already-bound object; it is not permission for the worker to reacquire the subject through broader path lookups.

3. **Path re-open stays out in the first cut.**
   - Later work must not require or rely on reopening the authoritative store locator, opening a broader store directory, or rebinding by some other ambient path after the delivery object has been prepared.
   - The first lane stays on one preserved subject and one bounded execution object.

4. **Receipts and examples must say this explicitly.**
   - The canonical removable-media plan, detach receipt, and import receipt must record that later delivery is launcher-preopened read-only (or equivalent) and that path reopen/store rebinding stay out.
   - The concrete first-cut example stack may also show this through a tiny `preopen.map` for the later worker, while still keeping authoritative-store directory authority out.

## Consequences

### Positive

- The first implementation floor becomes more honest: the worker no longer gets “one path that hopefully still means the same thing.”
- This composes directly with the archive's existing Capsicum/preopen posture instead of inventing a removable-media-specific exception.
- The archive stays compatible with path-expecting tools while keeping actual authority on one already-bound object.

### Negative / costs

- Launchers/adapters must explicitly own one more detail: the later worker's single object must be prepared before tool execution begins.
- Canonical examples now need to distinguish digest binding from the execution-shape decision that keeps path reopen out.

## Rejected alternatives

- **Let the worker reopen the synthetic path after digest binding.** Rejected because it quietly turns a compatibility path back into ambient execution authority.
- **Expose a broader directory/store handle for convenience.** Rejected because the first lane earned one selected subject, not namespace authority.
- **Force one exact kernel mechanism now.** Rejected because the archive only needs the delivery contract and evidence shape in the first cut, not one mandatory launcher implementation.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record launcher-preopened read-only delivery and explicit no-reopen posture.
- Add a drift check that fails if the examples slide back toward path reacquire or broader store reopening.

## Links

- boundary doc: `docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`
- previous cut: `adrs/ADR-0330-removable-media-local-fallback-post-detach-single-object-delivery-stays-digest-bound-and-receipt-evidenced.md`
