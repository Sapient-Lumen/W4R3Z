# Removable-media local fallback selected-subject processing stays capture-first and later ops consume the capture

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, and attach receipts that keep observed hints evidence-only.

This page closes the next smaller implementation seam:

> **once one selected regular file is chosen, the first non-browsing step must capture that exact subject into `/work`, and later operations consume the captured bytes rather than the live mounted `/ingest` path.**

See also:
- ADR: `adrs/ADR-0324-removable-media-local-fallback-selected-subject-processing-stays-capture-first-and-later-ops-consume-the-capture.md`
- previous cut: `docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- device authority: `docs/278-device-grants-and-devfs-rulesets.md`
- lease/revocation spine: `docs/249-lease-registry-and-cross-lane-revocation.md`

## Why this needs a hard decision

The archive already says the first lane is one selected regular-file subject only.
But that still leaves an expensive ambiguity for the first implementation:
after selection, do classify/scan/sanitize keep reading the live mounted path, or do they switch to a captured stable subject?

Without one more cut, implementations drift in opposite bad directions:

- keep reading the live mounted path and therefore keep hidden dependence on mount lifetime,
- or silently stage the subject into working storage without saying when that happens or what later steps actually consumed.

The first local fallback needs a safer middle:
**selection still happens from the mounted tree, but later processing becomes capture-first and then works from `/work`.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Capture is the first required processing step after selection

The canonical `content.import.plan` example now starts with `op: "capture"`.
That operation copies the exact selected regular-file subject from `/ingest/...` into `/work/capture/...`.
This is a subject-stability cut, not a new tree-import subsystem.

### 2) Later operations consume the captured file only

After `capture`, later classify/scan/sanitize steps consume the captured file path in `/work`.
They do not keep reopening the live mounted source path under `/ingest`.
This keeps later processing dependent on one stable captured subject instead of the continuing mount lifetime.

### 3) Digest verification is required before later ops proceed

Capture is not complete until the captured bytes verify against the planned selected-subject digest.
If capture fails, or digest verification fails, the flow fails closed.
There is no partial-import success for this lane.

### 4) This does not widen subject scope

This page composes with `docs/730-*` and `docs/731-*`.
The lane is still:

- one selected subject only,
- regular-file-only in the first cut,
- and out of scope for direct directory/tree capture.

The archive is only deciding **when processing stops depending on the live mounted path**.

## Canonical first-cut example stack

The subject-processing example stack is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`

Together they now say:

- selection still comes from the mounted inert tree,
- the first non-browsing step is capture,
- later operations consume the captured file from `/work`,
- digest verification must succeed before later operations proceed,
- and capture failure or digest mismatch fails closed.

## Why this cut is worth making now

Without this decision, the archive still pays repeated implementation tax:

- coding teams can disagree about whether later operations may keep reading the live mounted path,
- support receipts cannot clearly answer whether scan/sanitize ran on the captured bytes or on the mounted source path,
- and the first lane keeps one hidden mount-lifetime dependency even after subject selection is already explicit.

This page keeps the first coding target small and honest: browse/select from the mounted tree, capture the selected regular file, verify it, and then make later operations read the captured file.

This page therefore keeps one rule explicit in plain language too: **later operations consume the captured bytes, not the live mounted path.**

## What remains open

Still intentionally open:

- the exact implementation mechanism for capture in a given runtime,
- whether later richer lanes should add broader staging or tree-capture semantics,
- trusted-UI wording for how capture progress and verification are shown,
- and how later lanes may optimize or deduplicate capture when stronger storage isolation exists.

Last updated: 2026-03-28r465
