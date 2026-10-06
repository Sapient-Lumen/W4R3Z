# ADR-0327: Removable-media local fallback preserves the verified capture and forbids in-place rewrite by later ops

- Status: Accepted
- Date: 2026-03-28
- Deciders: DeriveBSD archive
- Tags: removable-media, workstation, evidence, import, sanitization

## Context

`adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md` fixed the first post-selection execution cut:

- one selected regular-file subject is captured into `/work` before later work,
- later operations consume the captured bytes instead of the live mounted `/ingest` path,
- and capture failure or digest mismatch fails closed.

`adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md` then made verified capture the earliest honest detach point.
`adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md` then required a fresh post-detach worker with `/ingest` absent.

That still leaves one expensive implementation seam open:

**after later work restarts from `/work`, is it allowed to rewrite the captured subject in place, or must the verified capture remain a separately preserved evidence artifact while later sanitize/convert/classify outputs appear as new derivatives?**

Without one more cut, implementations drift in opposite bad directions:

- rewrite `/work/capture/...` in place and lose the only exact preserved record of the imported subject,
- or preserve the original capture only by local convention, with receipts unable to prove whether later outputs derived from a retained exact capture or from an overwritten working file.

For the first host-local removable-media lane, DeriveBSD needs the smaller honest answer.

## Decision

For the first host-local removable-media ingest lane:

1. **The verified capture remains preserved exact evidence.**
   - Once capture verifies against the planned selected-subject digest, that captured artifact remains separately addressable as the exact imported subject for the rest of the lane.

2. **Later operations may not rewrite the preserved capture in place.**
   - `scan`, `sanitize`, `convert`, and similar later steps must treat the preserved capture as read-only input.
   - They may emit new derivative outputs, but they may not replace or mutate the preserved capture path in place.

3. **Later outputs are separate derivatives from the preserved capture.**
   - The canonical `content.import.receipt` should therefore be able to name both:
     - the preserved captured subject, and
     - later derived outputs such as a sanitized PDF.
   - This is an evidence-shaping cut, not a new content-store subsystem.

4. **Implementation hardening may use existing host facilities, but the archive contract stays path/receipt-shaped.**
   - A runtime may enforce the preserved-capture posture with existing read-only placement, permissions, or local file-immutability controls.
   - The normative archive rule is still the same: preserve the verified capture separately and forbid in-place rewrite by later ops.

## Consequences

- Support/export/forensics can keep one stable exact-subject record even when later sanitization succeeds.
- The first lane stays understandable: browse/select → capture/verify → detach → fresh worker → later derivative outputs from preserved capture.
- Receipts can now prove that sanitized output did not silently replace the exact imported subject.
- We do **not** need a broader evidence-store or snapshot subsystem to make this first cut honest.

## What remains open

- Exact filesystem/runtime hardening details for the preserved capture on a given implementation.
- Whether later richer lanes should preserve larger staged sets rather than a single captured file.
- Whether future generalized `content.import.receipt` examples should standardize more derivative relationship roles beyond this first removable-media cut.

## References

- prior capture-first cut: `adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`
- prior early-detach cut: `adrs/ADR-0325-removable-media-local-fallback-verified-capture-allows-early-detach-and-later-ops-stay-device-independent.md`
- prior post-detach worker-reset cut: `adrs/ADR-0326-removable-media-local-fallback-post-detach-later-ops-require-a-fresh-worker-with-no-live-ingest-references.md`
- boundary doc: `docs/737-removable-media-local-fallback-preserves-the-verified-capture-and-forbids-in-place-rewrite-by-later-ops.md`
