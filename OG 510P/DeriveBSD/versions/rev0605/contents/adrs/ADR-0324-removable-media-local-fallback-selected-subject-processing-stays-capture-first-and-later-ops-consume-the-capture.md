# ADR-0324: Removable-media local fallback selected-subject processing stays capture-first and later ops consume the capture

Date: 2026-03-28  
Status: Accepted

## Context

`ADR-0313` through `ADR-0323` already made the first honest host-local removable-media fallback for imperfect B/C hardware finite enough to implement:

- storage-only, session-scoped, quarantine-first,
- host-controlled `fstyp` admission and read-only mount,
- disposable no-network jail,
- inert mounted trees,
- physical root-pinned walk,
- one portable member-path grammar,
- path/kind/payload-first reviewed/import identity,
- single-selected-subject only,
- regular-file-only selected subjects in the first cut,
- present-device-instance-only approval with fresh grant required after reattach,
- and finite attach receipts that keep observed hints evidence-only.

One practical seam still remained half-open:
**after one selected regular file is chosen from the mounted tree, do later operations keep depending on that live mounted path, or do they switch to a captured working copy?**

Leaving that vague is expensive.
If later classify/scan/sanitize steps keep reading the live mounted `/ingest/...` path, the first lane quietly keeps a hidden dependency on the still-mounted medium and on later path resolution behavior.
That makes later receipts and failure handling harder to explain, and it widens the room for mount-lifetime folklore to creep back in.

The first lane does not need a bigger tree-import subsystem to close that gap.
It only needs one smaller rule:
**once the selected regular-file subject is chosen, the first non-browsing step must capture that exact subject into `/work`, verify the captured bytes against the planned subject digest, and make later operations consume the captured file rather than the live mounted path.**

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0323`:

1. After one selected regular-file subject is chosen, the next required step is `capture`.
2. `capture` copies that exact selected subject from `/ingest/...` into a receiver-local `/work/capture/...` path.
3. The captured bytes must verify against the planned selected-subject digest before any later non-capture operation proceeds.
4. Later operations in this first lane consume the captured file in `/work`, not the live mounted path under `/ingest`.
5. Capture failure or digest mismatch fails closed and yields no partial import success.
6. This decision does **not** widen the lane into directory capture, tree mirroring, or multi-subject import; it only stabilizes processing for the one already-selected regular-file subject.

## Consequences

- The first removable-media fallback now has a smaller, more implementable processing boundary: browse/select on the mounted tree, then switch to a captured stable subject.
- Receipts can explain whether later classify/scan/sanitize steps ran on the captured bytes and whether the capture verified correctly.
- The archive no longer leaves room for one implementation to keep reading the live mounted path while another silently snapshots first.
- This composes cleanly with the earlier decisions: the lane stays single-subject, regular-file-only, present-device-only, and attach-hints-evidence-only.

## Alternatives considered

- **Keep later operations reading the live mounted path:** rejected because it leaves hidden dependence on mount lifetime and later path resolution semantics.
- **Capture the whole mounted tree up front:** rejected because it widens the first lane toward directory/tree import semantics.
- **Design a richer subject-staging subsystem now:** rejected because the first lane only needs a smaller capture-first rule for one already-selected file.

## Related

- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- `adrs/ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
- `adrs/ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`
- `adrs/ADR-0323-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`
- `docs/734-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`
