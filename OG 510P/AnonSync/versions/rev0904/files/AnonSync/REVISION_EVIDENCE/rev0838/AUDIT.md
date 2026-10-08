# rev0838 audit: heartbeat meaning and takeover authority

## Heart of the correction

rev0837 had already solved the opened-file identity problem: heartbeat bytes were bounded, no-follow, type-checked observations from one opened object. The next boundary was still unsafe. A 15k-line domain translation unit parsed those bytes permissively, trusted relationships that were only fields, and let operator status use a weaker policy than daemon preflight.

rev0838 extracts a typed heartbeat-document owner and changes the consuming policy from “JSON fields exist” to “the document proves one coherent lifecycle, then the domain binds that lifecycle to the exact durable owner generation.”

## Corrected defects

- `stale_at_epoch` is recomputed from `heartbeat_epoch + stale_after_seconds`, with overflow and JSON exact-integer fences.
- Final documents require a recognized final state and, when ownership is required, exact release evidence at the heartbeat epoch.
- Released owner evidence cannot remain non-final; lockless mode cannot carry latent owner authority fields.
- Daemon preflight compares daemon ID, worker ID, owner ID, owner epoch, acquisition, expiry, release state, and release epoch to the durable row.
- `service_instance_id` is recomputed from session, daemon, worker, and restart epoch rather than accepted as a digest-shaped string.
- Release failures publish retained-owner, non-final states instead of minting false completion.
- Operator status uses the same decoder and reports malformed or fresh non-final blockers even after owner expiry.
- Successful sidecar recovery now supplies a nonempty canonical reason rather than relying on an empty diagnostic.

## Refactor

`src/sync_daemon_heartbeat_document.{hpp,cpp}` is a dedicated static leaf. Its focused corpus links only that leaf; configure-time guards reject reabsorption into core sources or a core backedge. The leaf has one object and no unresolved first-party symbols. The runtime core consumes it privately.

The existing sync-domain separation audit also had a false-red design: it required exactly ten private fixture functions. The real invariant is a nonempty exact declaration/definition set. rev0838 replaces the inventory count with that parity check; the bridge now has eleven explicit fixture functions and passes **13/13** structural checks.

## Proof surface

- Focused heartbeat corpus: **39/39**, repeated ten times (**390/390**).
- Heartbeat structural audit: **26/26**.
- Sync-domain separation audit: **13/13**.
- Existing opened-object audit regression: **21/21**.
- Clang 17 `-Werror`: **39/39**.
- GCC 14 ASan+UBSan with leak detection: **39/39**.
- Project CTest: **129/129** across seven exact non-overlapping ranges.
- Parent verifiers: directory **21/21**, ZIP **25/25**.
- Source patch replay: **PASS**, 224 active files, zero mismatches.

## What this does not prove

The heartbeat remains observational evidence. It is not signed, it uses a wall-clock freshness horizon, and its `process_id` is not yet a kernel process-incarnation capability. Durable owner-generation comparison prevents the file from independently authorizing takeover in owner-required mode, but lockless configurations have a materially weaker trust model.
